import yaml
from .client import LightwheelClient


class SceneLoader:
    """
    Loader for scene yaml files.

    Args:
        client (LightwheelClient): The client to use for the loader
    """

    def __init__(self, client: LightwheelClient):
        self.client = client

    def get_scene(
        self,
        scene_type: str,
        index: int,
        name: str,
        *,
        backend: str = "robocasa",
        split: str = None,
    ):
        """
        Get a scene from the server.

        Args:
            scene_type (str): layout or style
            index (int): index of the scene
            backend (str, optional): backend of the scene. Defaults to "robocasa".
        """
        data = {
            "type": scene_type,
            "index": index,
            "name": name,
            "backend": backend,
        }
        if split:
            data["split"] = split
        res = self.client.post("/floorplan/v1/scene/get", data=data)
        res = res.json()
        scene_id = res["id"]
        scene_data = yaml.load(res["value"], Loader=yaml.FullLoader)
        return scene_id, scene_data

    def create_scene(
        self,
        scene_type: str,
        index: int,
        local_path: str,
        name: str,
        *,
        backend: str = "robocasa",
        split: str = None,
    ):
        if not local_path.endswith("yaml"):
            raise Exception(f"File {local_path} is not a yaml file")
        with open(local_path, "r", encoding="utf-8") as f:
            yaml_txt = f.read()
        data = {
            "index": index,
            "value": yaml_txt,
            "type": scene_type,
            "name": name,
            "backend": backend,
        }
        if split:
            data["split"] = split
        self.client.post("/floorplan/v1/scene/create", data=data)

    def update_scene(
        self,
        scene_type: str,
        scene_id: int,
        scene_data_path: str,
        name: str,
        *,
        backend: str = "robocasa",
        split: str = None,
        new_name: str = None,
        new_backend: str = None,
        new_split: str = None,
    ):
        sid, _ = self.get_scene(scene_type, scene_id, name, backend=backend, split=split)
        with open(scene_data_path, "r", encoding="utf-8") as f:
            scene_data = f.read()
        data = {
            "id": sid,
            "value": scene_data,
        }
        if new_name:
            data["name"] = new_name
        if new_backend:
            data["backend"] = new_backend
        if new_split:
            data["split"] = new_split
        self.client.post("/floorplan/v1/scene/update", data=data)
