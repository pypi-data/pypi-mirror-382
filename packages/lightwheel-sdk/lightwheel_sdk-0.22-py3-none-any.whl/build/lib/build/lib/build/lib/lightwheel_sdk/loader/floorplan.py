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


import uuid
import os
from pathlib import Path
import zipfile
import threading
import shutil
import json
import time
from concurrent.futures import Future, ThreadPoolExecutor
import requests
from tqdm import tqdm
from .exception import ApiException
from .client import LightwheelClient

CACHE_PATH = Path("~/.cache/lightwheel_sdk/floorplan/").expanduser()
CACHE_PATH.mkdir(parents=True, exist_ok=True)


class FloorplanLoader:
    """
    Loader for floorplan USD files.

    Args:
        client (LightwheelClient): The client to use for the loader
        max_workers (int, optional): The maximum number of workers for downloading USD files. Defaults to 4.
    """

    _latest_future: Future = None

    def __init__(self, client: LightwheelClient, max_workers=4):
        self.client = client
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._should_stop_downloading = False
        self.usd_suffix = ".usd"

    def acquire_usd(
        self,
        layout_id: int = None,
        style_id: int = None,
        *,
        scene: str = "robocasakitchen",
        backend="robocasa",
        cancel_previous_download: bool = True,
        version=None,
        exclude_layout_ids: list[int] = None,
        exclude_style_ids: list[int] = None,
        split: str = None,
    ):
        if cancel_previous_download and self._latest_future and self._latest_future.running():
            self._should_stop_downloading = True
            # self._latest_future.cancel()
            while self._latest_future.running():
                time.sleep(0.1)
                print("waiting for cancel")
        self._latest_future = self.executor.submit(
            self.get_usd,
            scene,
            layout_id,
            style_id,
            backend,
            version=version,
            exclude_layout_ids=exclude_layout_ids,
            exclude_style_ids=exclude_style_ids,
            split=split,
        )
        return self._latest_future

    def check_version(self):
        """
        NOTICE! The method is DEPRECATED!
        """

    def get_usd(
        self,
        scene: str,
        layout_id: int = None,
        style_id: int = None,
        backend: str = "robocasa",
        version=None,
        exclude_layout_ids: list[int] = None,
        exclude_style_ids: list[int] = None,
        split: str = None,
    ):
        """
        Make a Get HTTP call to retrieve a bundle stream.

        Args:
            scene (str): The scene identifier
            layout_id (int): The layout ID
            style_id (int): The style ID

        Returns:
            str: The path to the downloaded USD file
        """
        if version:
            res_json = self.get_usd_by_id(version)
        else:
            data = {
                "scene": scene,
                "backend": backend,
            }
            if layout_id is not None:
                data["layout_id"] = layout_id
            if style_id is not None:
                data["style_id"] = style_id
            if exclude_layout_ids is not None:
                data["exclude_layout_ids"] = exclude_layout_ids
            if exclude_style_ids is not None:
                data["exclude_style_ids"] = exclude_style_ids
            if split is not None:
                data["split"] = split
            response = self.client.post("/floorplan/v1/usd/get", data=data, timeout=600)
            res_json = response.json()
        s3_url = res_json["fileUrl"]
        metadata = res_json["metadata"]
        version_uuid = res_json.get("versionUuid", None)
        metadata["version_id"] = version_uuid
        layout_id = metadata["layout_id"]
        style_id = metadata["style_id"]
        usd_name = self._usd_cache_name(backend, scene, layout_id, style_id)
        cache_version = self._get_usd_cache_version(usd_name)
        cache_dir_path = self._usd_cache_dir_path(usd_name)
        usd_file_path = cache_dir_path / f"scene{self.usd_suffix}"
        if cache_version and version_uuid and cache_version == version_uuid:
            if usd_file_path.exists():
                return usd_file_path, metadata
        self._clear_usd_cache(usd_name)
        total_size = 0
        response = requests.get(s3_url, stream=True, timeout=600)
        if response.status_code != 200:
            raise ApiException(response)
        package_file_path = cache_dir_path.with_suffix(".zip")
        with open(package_file_path, "wb") as f:
            for chunk in tqdm(response.iter_content(chunk_size=1024), desc="Downloading Floorplan Package"):
                if self._should_stop_downloading:
                    response.close()
                    print(f"stop downloading {layout_id}-{style_id}")
                    break
                f.write(chunk)
                total_size += len(chunk)
            print(f"dowloaded {total_size/1024/1024:.2f}MB")
        # decompress the package.zip to the cache_dir_path
        temp_extract_path = CACHE_PATH / f"temp_extract_{uuid.uuid4()}"
        os.makedirs(temp_extract_path, exist_ok=True)
        if not self._should_stop_downloading:
            with zipfile.ZipFile(package_file_path, "r") as zip_ref:
                zip_ref.extractall(temp_extract_path)
        dir_list = os.listdir(temp_extract_path)
        if len(dir_list) != 1:
            raise Exception(f"Invalid temp extract path: {temp_extract_path}")
        dir_name = dir_list[0]
        os.rename(temp_extract_path / dir_name, cache_dir_path)
        shutil.rmtree(temp_extract_path, ignore_errors=True)
        package_file_path.unlink()
        self._should_stop_downloading = False
        self._update_usd_cache_version(usd_name, version_uuid)
        return usd_file_path, metadata

    def get_usd_by_id(self, id: str):
        response = self.client.post("/floorplan/v1/usd/id-get", data={"uuid": id})
        return response.json()

    def _usd_cache_name(self, backend: str, scene: str, layout_id: int, style_id: int):
        return f"{backend}-{scene}-{layout_id}-{style_id}"

    def _usd_cache_dir_path(self, usd_name: str):
        return CACHE_PATH / usd_name

    def _clear_usd_cache(self, usd_name: str):
        if not self._usd_cache_dir_path(usd_name).exists():
            return
        for path in self._usd_cache_dir_path(usd_name).glob("*"):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    def _usd_cache_version_path(self):
        return CACHE_PATH / "usd_version.json"

    def _get_usd_cache_version(self, usd_name):
        if not self._usd_cache_version_path().exists():
            return None
        with open(self._usd_cache_version_path(), "r", encoding="utf-8") as f:
            versions = json.load(f)
            return versions.get(usd_name, None)

    def _update_usd_cache_version(self, usd_name: str, version: str):
        print(f"update USD cache version at {self._usd_cache_version_path()}")
        if not CACHE_PATH.exists():
            CACHE_PATH.mkdir(parents=True, exist_ok=True)
        versions = {}
        if self._usd_cache_version_path().exists():
            with open(self._usd_cache_version_path(), "r", encoding="utf-8") as f:
                versions = json.load(f)
        versions[usd_name] = version
        with open(self._usd_cache_version_path(), "w", encoding="utf-8") as f:
            json.dump(versions, f)
