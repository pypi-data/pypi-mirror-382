# Geunduun

Geunduun is a lightweight toolkit for orchestrating remote GPU workloads on [RunPod](https://www.runpod.io/). It offers a Python interface for provisioning pods via the RunPod REST API, shaping lifecycle management, and building thin Docker wrappers that can wrap arbitrary commands in a reproducible environment.

## Features
- Build a RunPod-ready wrapper image on top of any base Docker image.
- Launch pods via the RunPod REST API and retrieve their identifiers for downstream tracking.
- Poll pod status and map responses to high-level lifecycle states.
- Terminate pods programmatically and close HTTP resources cleanly.

## Project Layout
- `src/geunduun/managers/`: lifecycle management primitives. `RunPodManager` implements create, check, terminate, and wrapper build helpers.
- `src/geunduun/docker_wrapper/runpod/`: Dockerfile and wrapper script. The script captures logs, optionally reports status, and tears down pods when the wrapped workload exits.
- `src/geunduun/enums.py`: shared enums for standard status values.
- `apps/`: placeholder for application-specific workloads that will be launched on RunPod.

## Requirements
- Python 3.11 or newer.
- Docker client available locally if you want to build wrapper images.
- RunPod API credentials (`RUNPOD_API_KEY` for workload pods, `ROOT_RUNPOD_API_KEY` for administrative calls used by the wrapper script).

## Installation
Clone the repository and install dependencies. You can use [uv](https://docs.astral.sh/uv/) (recommended) or plain `pip`.

```bash
# using uv
uv sync

# using pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

### Build a wrapper image
The `RunPodManager.build_wrapper` helper wraps a base image with the Dockerfile in `src/geunduun/docker_wrapper/runpod` so the RunPod runtime can stream logs and clean up pods automatically.

```python
from geunduun.managers.runpod import RunPodManager

manager = RunPodManager()
manager.build_wrapper("runpod/base:latest")
```

The command above produces a new image `runpod/base:latest-runpod` that can be referenced in your RunPod workload templates.

### Launch and manage a pod
Set your `RUNPOD_API_KEY` environment variable, construct the API payload, and invoke the manager:

```python
from geunduun.managers.runpod import RunPodManager
from geunduun.enums import InstanceStatus

manager = RunPodManager()

payload = {
    "name": "example-worker",
    "imageName": "runpod/base:latest-runpod",
    "gpuTypeId": "H100",
    "cloudType": "SECURE",
    "env": {"MY_ENV_VAR": "value"},
    "dataCenterId": "us-texas-1",
}

pod_id = manager.launch(payload)
status = manager.check(pod_id)

if status is InstanceStatus.RUNNING:
    print("Pod is live!")

# When finished
manager.terminate(pod_id)
manager.close()
```

Refer to the [RunPod pod launch API specification](https://docs.runpod.io/reference/create-pod) for all available payload fields.

### Wrapper script environment
When the wrapper script runs inside the pod it respects:

- `LOG_DIR` (default `/workspace/logs`): location for time-stamped combined stdout/stderr logs.
- `ROOT_RUNPOD_API_KEY`: bearer token for deleting the pod when the wrapped command exits.
- `RUNPOD_POD_ID`: pod identifier injected by RunPod.

Logs are captured under `LOG_DIR/<YYYYMMDD_HHMMSS>.txt`, and the pod is deleted after the wrapped workload finishes.

## Development
- Format and lint using [ruff](https://docs.astral.sh/ruff/): `uv run ruff check .` (or `pip install ruff` and call `ruff check .`).
- Add integration tests or scripts under `apps/` as needed.
- The CLI entry point `geunduun` declared in `pyproject.toml` is currently a placeholder; create a `main` callable under `geunduun/__init__.py` (or another module) before publishing to PyPI.

## Roadmap
- Implement a higher-level orchestrator or CLI around `RunPodManager`.
- Add status reporting back to a central service from the wrapper script.
- Expand support for additional cloud backends beyond RunPod.

## License
License information has not been specified yet.
