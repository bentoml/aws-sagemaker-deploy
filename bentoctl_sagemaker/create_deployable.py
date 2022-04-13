import os
import shutil

root_dir = os.path.abspath(os.path.dirname(__file__))
SAGEMAKER_SERVICE_PATH = os.path.join(root_dir, "sagemaker_service.py")
DOCKER_TEMPLATE_PATH = os.path.join(root_dir, "Dockerfile.template")
SERVE_SCRIPT_PATH = os.path.join(root_dir, "serve")


def generate_sagemaker_service_in(deployable_path):
    shutil.copy(
        SAGEMAKER_SERVICE_PATH,
        os.path.join(deployable_path, "sagemaker_service.py"),
    )


def generate_serve_script_in(deployable_path):
    shutil.copy(SERVE_SCRIPT_PATH, os.path.join(deployable_path, "serve"))
    # permission 755 is required for entry script 'serve'
    os.chmod(os.path.join(deployable_path, "serve"), 0o755)

    return deployable_path


def generate_dockerfile_in(deployable_path, bento_metadata):
    # docker_base_image formate "bentoml/bento-server:1.0.0a1-python3.8-debian-runtime"
    docker_base_image = f"bentoml/bento-server:{bento_metadata['bentoml_version']}-python{bento_metadata['python_version']}-debian-runtime"

    dockerfile_path = os.path.join(deployable_path, "Dockerfile")
    with open(dockerfile_path, "w") as dockerfile, open(
        DOCKER_TEMPLATE_PATH, "r"
    ) as dockerfile_template:
        dockerfile_template = dockerfile_template.read()
        dockerfile.write(
            dockerfile_template.format(docker_base_image=docker_base_image)
        )
    return dockerfile_path


def create_deployable(
        bento_path: str, destination_dir: str, bento_metadata: dict
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
    dockerfile_path : str
        path to the dockerfile.
    docker_context_path : str
        path to the docker context.
    additional_build_args : dict
        Any addition build arguments that need to be passed to the
        docker build command
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
