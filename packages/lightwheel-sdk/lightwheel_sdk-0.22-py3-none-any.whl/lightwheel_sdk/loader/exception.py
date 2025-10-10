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

import requests


class ApiException(Exception):
    """
    Exception for API errors.

    Args:
        response (requests.Response): The response from the API
    """

    def __init__(self, response: requests.Response, path: str = ""):
        self.message = f"{path} {response.status_code} {response.text}"
        super().__init__(self.message)


class AuthenticationFailedException(Exception):
    """
    Exception for authentication failed.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnknownException(Exception):
    """
    Exception for unknown errors.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
