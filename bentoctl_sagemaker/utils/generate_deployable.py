import os
import shutil

from . import is_present, get_metadata

BENTO_SERVICE_SAGEMAKER_DOCKERFILE = """\
FROM {docker_base_image}
RUN pip install git+https://github.com/bentoml/BentoML.git@main

ARG BENTO_PATH=/home/bento
ENV BENTO_PATH=$BENTO_PATH
ENV BENTOML_HOME=/home/

RUN mkdir $BENTO_PATH
WORKDIR $BENTO_PATH


# copy over env directory
COPY ./env ./env
RUN chmod +x ./env/docker/init.sh
RUN ./env/docker/init.sh ensure_python
RUN ./env/docker/init.sh restore_conda_env
RUN ./env/docker/init.sh install_pip_packages
RUN ./env/docker/init.sh install_wheels
RUN ./env/docker/init.sh user_setup_script

# copy over all remaining bento files
COPY . ./

# Default port for BentoServer
EXPOSE 5000
ENV PATH="$BENTO_PATH:$PATH"
"""  # noqa: E501


def generate_sagemaker_target(bento_metadata, bento_path, sagemaker_project_dir):
    # check if there is an existing sagemaker_target. prompt user to select
    if is_present(sagemaker_project_dir):
        return sagemaker_project_dir

    # docker_base_image formate "bentoml/bento-server:1.0.0a1-python3.8-debian-runtime"
    docker_base_image = f"bentoml/bento-server:{bento_metadata['bentoml_version']}-python{bento_metadata['python_version']}-debian-runtime"
    shutil.copytree(bento_path, sagemaker_project_dir)

    with open(os.path.join(sagemaker_project_dir, "Dockerfile"), "w") as f:
        f.write(
            BENTO_SERVICE_SAGEMAKER_DOCKERFILE.format(
                docker_base_image=docker_base_image
            )
        )

    dir_name = os.path.join(os.path.dirname(__file__))
    sagemaker_svc_path = os.path.join(dir_name, "../sagemaker_service.py")
    shutil.copy(
        sagemaker_svc_path, os.path.join(sagemaker_project_dir, "sagemaker_service.py")
    )

    serve_file_path = os.path.join(dir_name, "../serve")
    shutil.copy(serve_file_path, os.path.join(sagemaker_project_dir, "serve"))

    # permission 755 is required for entry script 'serve'
    os.chmod(os.path.join(sagemaker_project_dir, "serve"), 0o755)

    return sagemaker_project_dir


def generate_deployable(bento_bundle_path, deployment_name):
    bento_metadata = get_metadata(bento_bundle_path)
    bento_tag = bento_metadata["tag"]

    dir_name = f"{deployment_name}-{bento_tag.name}:{bento_tag.version:4}"
    sagemaker_project_dir = generate_sagemaker_target(
        bento_metadata, bento_bundle_path, os.path.abspath(dir_name)
    )
    return sagemaker_project_dir, bento_tag.name, bento_tag.version
