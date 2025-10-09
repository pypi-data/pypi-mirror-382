import os
import subprocess


class BaseManager:
    def __init__(self):
        self.docker_suffix = "base"

    def build_wrapper(self, base_image: str, do_push: bool = True) -> str:
        """
        Build and push wrapper docker image.
        """
        image_prefix = base_image.split(":")[0]
        image_tag = base_image.split(":")[1]
        wrapper_image = f"{image_prefix}:{image_tag}-{self.docker_suffix}"
        docker_conetxt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"../docker_wrapper/{self.docker_suffix}",
        )
        cmd = [
            "docker",
            "build",
            "--platform",
            "linux/amd64",
            "--build-arg",
            f"BASE_IMAGE={base_image}",
            "-t",
            wrapper_image,
            docker_conetxt_path,
        ]
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError as exc:  # pragma: no cover - docker missing
            raise RuntimeError(
                "Docker binary 'docker' not found while building wrapper image"
            ) from exc
        except (
            subprocess.CalledProcessError
        ) as exc:  # pragma: no cover - subprocess failure path
            raise RuntimeError(
                f"docker build failed for wrapper image '{image_tag}'"
            ) from exc

        if do_push:
            # tag
            if not wrapper_image.startswith(self.docker_user_name + "/"):
                wrapper_image_ = wrapper_image
                wrapper_image = (
                    self.docker_user_name + "/" + wrapper_image_.split("/")[-1]
                )
                cmd = ["docker", "tag", wrapper_image_, wrapper_image]
                try:
                    subprocess.run(cmd, check=True)
                except subprocess.CalledProcessError as exc:
                    raise RuntimeError(
                        f"docker tag failed for {wrapper_image}"
                    ) from exc

            # push
            cmd = ["docker", "push", wrapper_image]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as exc:
                raise RuntimeError(f"docker push failed for {wrapper_image}") from exc

        return wrapper_image

    def launch(self):
        """
        Launch an instance.
        """
        raise NotImplementedError

    def check(self):
        """
        Check state of the instance.
        """
        raise NotImplementedError

    def terminate(self):
        """
        Terminate the instance.
        """
        raise NotImplementedError

    def close(self):
        """
        Close client.
        """
        return
