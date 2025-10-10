# Copyright 2025 Lightwheel Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
from typing import Dict, Any
import getpass
from pathlib import Path
import requests
from termcolor import colored
from .exception import ApiException, UnknownException
from .exception import AuthenticationFailedException
from ..logger import get_logger

CACHE_PATH = Path("~/.cache/lightwheel_sdk/login/").expanduser()
CACHE_PATH.mkdir(parents=True, exist_ok=True)

AUTH_KEY = "Authorization"
USERNAME_KEY = "UserName"


class LightwheelClient:
    """
    Lightwheel client

    Args:
        host (str): The host of the Lightwheel API.
            If not provided, the host will be read from the LW_API_ENDPOINT environment variable.
            If the LW_API_ENDPOINT environment variable is not set, the default host will be https://api.lightwheel.net.
    """

    def __init__(
        self,
        *,
        host: str = "",
        base_timeout: int = 10,
    ):
        self.logger = get_logger("lightwheel_sdk.client")
        self.host = host
        self.base_timeout = base_timeout
        if self.host == "":
            env_host = os.environ.get("LW_API_ENDPOINT", "https://api.lightwheel.net")
            self.host = env_host
        self.host = self.host.rstrip("/")
        self.cache_path = CACHE_PATH / "account.json"
        self.headers = {}
        self.logger.info("Initializing LightwheelClient with host: %s", self.host)
        self._init_headers()

    def _init_headers(self):
        x_envs = [k for k in os.environ.keys() if k.startswith("LW_SDK_HEADERS_")]
        self.logger.debug("Found %d custom header environment variables", len(x_envs))
        for x_env in x_envs:
            self._update_header(x_env.replace("LW_SDK_HEADERS_", "").lower().replace("_", "-"), os.environ[x_env])
        if "LoaderUserName" in os.environ and "LoaderToken" in os.environ:
            self.logger.info("Using credentials from environment variables")
            self._update_header(AUTH_KEY, f"Bearer {os.environ['LoaderToken']}")
            self._update_header(USERNAME_KEY, os.environ["LoaderUserName"])
        elif self.cache_path.exists():
            self.logger.info("Using credentials from cache file")
            try:
                username = self._get_account_cache_username()
                token = self._get_account_cache_token()
                self._update_header(AUTH_KEY, f"Bearer {token}")
                self._update_header(USERNAME_KEY, username)
            except json.JSONDecodeError as e:
                self.logger.warning("Cache file is not a valid JSON: %s", e)
                self.cache_path.unlink(missing_ok=True)
            except KeyError:
                self.logger.warning("Credentials not found in cache file, can only access public resources")

    def _get_headers(self):
        return self.headers

    def _update_header(self, key: str, value: str):
        self.headers[key] = value

    def _get_account_cache_username(self):
        if not self.cache_path.exists():
            self.logger.debug("Cache file not found")
            raise FileNotFoundError("Cache file not found")
        with open(self.cache_path, "r", encoding="utf-8") as f:
            account_cache = json.load(f)
            if "username" not in account_cache:
                self.logger.warning("Username not found in cache file")
                raise KeyError("Username not found in cache file")
            self.logger.debug("Retrieved username from cache")
            return account_cache["username"]

    def _get_account_cache_token(self):
        if not self.cache_path.exists():
            self.logger.debug("Cache file not found")
            raise FileNotFoundError("Cache file not found")
        with open(self.cache_path, "r", encoding="utf-8") as f:
            account_cache = json.load(f)
            if "token" not in account_cache:
                self.logger.warning("Token not found in cache file")
                raise KeyError("Token not found in cache file")
            self.logger.debug("Retrieved token from cache")
            return account_cache["token"]

    def _get_account_cache_refresh_token(self):
        if not self.cache_path.exists():
            self.logger.debug("Cache file not found")
            raise FileNotFoundError("Cache file not found")
        with open(self.cache_path, "r", encoding="utf-8") as f:
            account_cache = json.load(f)
            if "refreshToken" not in account_cache:
                self.logger.warning("Refresh token not found in cache file")
                raise KeyError("Refresh token not found in cache file")
            self.logger.debug("Retrieved refresh token from cache")
            return account_cache["refreshToken"]

    def _cache_account(self, username: str, token: str, refresh_token: str = None):
        account_cache = {
            "username": username,
            "token": token,
            "refreshToken": refresh_token,
        }
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(account_cache, f, indent=4)

    def _refresh_token(self):
        self.logger.info("Refreshing authentication token")
        username = self._get_account_cache_username()
        refresh_token = self._get_account_cache_refresh_token()
        response = requests.post(
            f"{self.host}/api/authenticate/v1/user/refresh-token",
            data={},
            headers={USERNAME_KEY: username, AUTH_KEY: f"{refresh_token}", "Content-Type": "application/json"},
            timeout=self.base_timeout,
        )
        if response.status_code != 200:
            self.logger.error("Token refresh failed with status %d", response.status_code)
            raise ApiException(response)
        res = response.json()
        self._cache_account(username, res["token"], refresh_token)
        self._update_header(AUTH_KEY, f"Bearer {res['token']}")
        self._update_header(USERNAME_KEY, username)
        self.logger.info("Token refreshed successfully")

    def login(self, force_login=False, *, username: str = None, password: str = None):
        self.logger.info("Starting login process")
        if not self.cache_path.exists() or force_login:
            self.logger.info("Performing fresh login")
            username, token = self._login(username=username, password=password)
        else:
            try:
                self.logger.info("Attempting to use cached credentials")
                username = self._get_account_cache_username()
                token = self._get_account_cache_token()
                self.logger.info("Using cached credentials successfully")
            except KeyError:
                self.logger.warning("Cached credentials invalid, performing fresh login")
                username, token = self._login(username=username, password=password)
        self._update_header(AUTH_KEY, f"Bearer {token}")
        self._update_header(USERNAME_KEY, username)
        self.logger.info("Login successful for user: %s", username)
        return self._get_headers()

    def _login(self, username: str = None, password: str = None):
        self.logger.info("Performing authentication with API")
        username = username or input(colored("\nusername: ", "green"))
        password = password or getpass.getpass(colored("\npassword: ", "green"))
        self.logger.debug("Attempting login for user: %s", username)
        response = self.post("/api/authenticate/v1/user/login", data={"username": username, "password": password})
        if response.status_code != 200:
            if response.status_code == 500 and response.json().get("message", "").startswith("login failed"):
                self.logger.warning("Invalid username or password")
                print(colored("Invalid username or password", "red"))
                return self._login()
            self.logger.error("Login failed with status %d", response.status_code)
            raise ApiException(response)
        res = response.json()
        token = res["token"]
        self._cache_account(username, token, res.get("refreshToken", None))
        self.logger.debug("Refresh token received and cached")
        self.logger.info("Login credentials cached successfully")
        return username, token

    def logout(self):
        self.logger.info("Logging out user")
        self.cache_path.unlink(missing_ok=True)
        self._update_header(AUTH_KEY, "")
        self._update_header(USERNAME_KEY, "")
        self.logger.info("Logout completed successfully")

    def post(self, path: str, *, data: Dict[str, Any] = None, timeout: int = None):
        self.logger.debug("Making POST request to %s", path)
        try:
            res = self._post(path, data=data, timeout=timeout)
        except AuthenticationFailedException:
            self.logger.warning("Authentication failed, attempting token refresh")
            self._refresh_token()
            res = self._post(path, data=data, timeout=timeout)
        except (ApiException, UnknownException) as e:
            self.logger.error("API request failed for: %s", e)
            raise e
        except Exception as e:
            self.logger.error("Unexpected error during API request: %s", e)
            raise UnknownException(e) from e
        self.logger.debug("POST request to %s completed successfully", path)
        return res

    def _post(self, path: str, *, data: Dict[str, Any] = None, timeout: int = None):
        url = f"{self.host}/{path.lstrip('/')}"
        self.logger.debug("Making HTTP POST request to %s", url)
        try:
            res = requests.post(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=timeout or self.base_timeout,
            )
        except Exception as e:
            self.logger.error("HTTP request failed for path %s: %s", path, e)
            raise UnknownException(e) from e
        if res.status_code == 401:
            self.logger.warning("Authentication failed (401) with path: %s", path)
            raise AuthenticationFailedException(f"Authentication failed with path: {path}")
        if res.status_code != 200:
            self.logger.error("API request failed for path %s with status %d: %s", path, res.status_code, res.text)
            raise ApiException(res, path)
        self.logger.debug("HTTP POST request to %s completed with status %d", url, res.status_code)
        return res
