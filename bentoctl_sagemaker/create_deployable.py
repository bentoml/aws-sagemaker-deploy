from __future__ import annotations

import os
from pathlib import Path
from sys import version_info
from typing import Any

from bentoml._internal.bento.bento import BentoInfo
from bentoml._internal.bento.build_config import DockerOptions
from bentoml._internal.bento.gen import generate_dockerfile
from bentoml._internal.utils import bentoml_cattr

if version_info >= (3, 8):
    from shutil import copytree
else:
    from backports.shutil_copytree import copytree

root_dir = Path(os.path.abspath(os.path.dirname(__file__)), "sagemaker")
SERVICE_PATH = os.path.join(root_dir, "service.py")
TEMPLATE_PATH = os.path.join(root_dir, "template.j2")
SERVE_PATH = os.path.join(root_dir, "serve")


def create_deployable(
    bento_path: str,
    destination_dir: str,
    bento_metadata: dict[str, Any],
    overwrite_deployable: bool,
) -> str:
    """
    The deployable is the bento along with all the modifications (if any)
    requried to deploy to the cloud service.

    Parameters
    ----------
    bento_path: str
        Path to the bento from the bento store.
    destination_dir: str
        directory to create the deployable into.
    bento_metadata: dict
        metadata about the bento.

    Returns
    -------
    docker_context_path : str
        path to the docker context.
    """
    deployable_path = Path(destination_dir)

    # copy over the bento bundle
    copytree(bento_path, deployable_path, dirs_exist_ok=True)

    bento_metafile = Path(bento_path, "bento.yaml")
    with bento_metafile.open("r", encoding="utf-8") as metafile:
        info = BentoInfo.from_yaml_file(metafile)

    options = bentoml_cattr.unstructure(info.docker)
    options["dockerfile_template"] = TEMPLATE_PATH

    dockerfile_path = deployable_path.joinpath("env", "docker", "Dockerfile")
    with dockerfile_path.open("w", encoding="utf-8") as dockerfile:
        dockerfile.write(
            generate_dockerfile(
                DockerOptions(**options).with_defaults(),
                str(deployable_path),
                use_conda=not info.conda.is_empty(),
            )
        )

    # copy sagemaker service.py
    shutil.copy(
        SERVICE_PATH,
        os.path.join(deployable_path, "service.py"),
    )

    # then copy the serve script
    shutil.copy(SERVE_PATH, dockerfile_path.parent.joinpath("serve"))
    # permission 755 is required for entry script 'serve'
    os.chmod(dockerfile_path.parent.joinpath("serve"), 0o755)

    return str(deployable_path)
