import os
from typing import Optional
import httpx
import yaml

from .base import BaseManager
from ..enums import InstanceStatus


class RunPodManager(BaseManager):
    def __init__(self) -> None:
        self.docker_suffix = "runpod"

        api_key = os.environ.get("RUNPOD_API_KEY", None)
        self._client = httpx.Client(
            base_url="https://rest.runpod.io/v1/",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        self.docker_user_name = os.environ.get("DOCKER_USER_NAME", "")

    def launch(
        self, do_wrapping: bool = True, yaml_file: Optional[str] = None, **kwargs
    ) -> str:
        # payload
        if yaml_file:
            with open(yaml_file, "r") as f:
                payload = yaml.safe_load(f)
        else:
            payload = {}
        payload.update(kwargs)

        # wrapping
        if do_wrapping:
            payload["imageName"] = self.build_wrapper(payload["imageName"])
            payload["dockerEntrypoint"] = ["bash", "wrapper_script.sh"] + payload[
                "dockerEntrypoint"
            ]

        # launch
        response = self._client.post("pods", json=payload)
        response.raise_for_status()
        data = response.json()
        pod_id = data.get("id")
        return pod_id

    def check(self, pod_id: str) -> InstanceStatus:
        data = self.check(pod_id)
        status = data.get("desiredStatus")
        if not status:
            return InstanceStatus.UNKNOWN
        try:
            return InstanceStatus(status.lower())
        except ValueError:
            return InstanceStatus.UNKNOWN

    def terminate(self, pod_id: str) -> None:
        response = self._client.delete(f"pods/{pod_id}")
        if response.status_code not in (
            httpx.codes.OK,
            httpx.codes.ACCEPTED,
            httpx.codes.NO_CONTENT,
        ):
            response.raise_for_status()

    def close(self) -> None:
        self._client.close()
