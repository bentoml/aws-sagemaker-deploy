import os
import shutil

from bentoctl.docker_utils import DOCKERFILE_PATH
from bentoml._internal.bento.build_config import DockerOptions
from bentoml._internal.bento.gen import generate_dockerfile

root_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "sagemaker")
SAGEMAKER_SERVICE_PATH = os.path.join(root_dir, "sagemaker_service.py")
BENTOCTL_USER_TEMPLATE = os.path.join(root_dir, "bentoctl_user_template.j2")
SERVE_SCRIPT_PATH = os.path.join(root_dir, "serve")


def generate_sagemaker_service_in(deployable_path):
    shutil.copy(
        SAGEMAKER_SERVICE_PATH,
        os.path.join(deployable_path, "sagemaker_service.py"),
    )


def generate_serve_script_in(deployable_path):
    serve_dest = os.path.join(deployable_path, os.path.dirname(DOCKERFILE_PATH), "serve")
    shutil.copy(SERVE_SCRIPT_PATH, serve_dest)
    # permission 755 is required for entry script 'serve'
    os.chmod(serve_dest, 0o755)

    return deployable_path


def generate_dockerfile_in(deployable_path, bento_metadata):
    docker_options_for_sagemaker = DockerOptions(
        dockerfile_template=BENTOCTL_USER_TEMPLATE
    )
    dockerfile_generate = generate_dockerfile(
        docker_options_for_sagemaker.with_defaults(), use_conda=False
    )
    breakpoint()
    
    dockerfile_path = os.path.join(deployable_path, DOCKERFILE_PATH)
    with open(dockerfile_path, "w") as dockerfile:
        dockerfile.write(dockerfile_generate)

    return dockerfile_path


def create_deployable(
    bento_path: str,
    destination_dir: str,
    bento_metadata: dict,
    overwrite_deployable=None,
):
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
    deployable_path = os.path.join(destination_dir, "bentoctl_deployable")
    docker_context_path = deployable_path

    # copy over the bento bundle
    shutil.copytree(bento_path, deployable_path)
    dockerfile_path = generate_dockerfile_in(deployable_path, bento_metadata)
    generate_sagemaker_service_in(deployable_path)
    generate_serve_script_in(deployable_path)

    additional_build_args = None
    return dockerfile_path, docker_context_path, additional_build_args
