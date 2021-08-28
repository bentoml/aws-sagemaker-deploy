import os
import shutil
import sys

from bentoml.saved_bundle import load_bento_service_metadata

from utils import is_present

BENTO_SERVICE_SAGEMAKER_DOCKERFILE = """\
FROM {docker_base_image}

# the env var $PORT is required by heroku container runtime
ENV PORT 8080
EXPOSE $PORT

RUN apt-get update --fix-missing --allow-releaseinfo-change && \
    apt-get install -y nginx && \
    apt-get clean

# gevent required by AWS Sagemaker
RUN pip install gevent>=20.9.0

# copy over model files
COPY . /bento
WORKDIR /bento

RUN if [ -f /bento/bentoml-init.sh ]; then bash -c /bento/bentoml-init.sh; fi

ENV PATH="/bento:$PATH"
"""  # noqa: E501


def generate_sagemaker_target(bento_metadata, bento_path, sagemaker_project_dir):
    # check if there is an existing sagemaker_target. prompt user to select
    if is_present(sagemaker_project_dir):
        return sagemaker_project_dir

    docker_base_image = bento_metadata.env.docker_base_image
    shutil.copytree(bento_path, sagemaker_project_dir)

    with open(os.path.join(sagemaker_project_dir, "Dockerfile"), "w") as f:
        f.write(
            BENTO_SERVICE_SAGEMAKER_DOCKERFILE.format(
                docker_base_image=docker_base_image
            )
        )

    dir_name = os.path.join(os.path.dirname(__file__))
    nginx_conf_path = os.path.join(dir_name, "nginx.conf")
    shutil.copy(nginx_conf_path, os.path.join(sagemaker_project_dir, "nginx.conf"))

    wsgi_py_path = os.path.join(dir_name, "wsgi.py")
    shutil.copy(wsgi_py_path, os.path.join(sagemaker_project_dir, "wsgi.py"))

    serve_file_path = os.path.join(dir_name, "serve")
    shutil.copy(serve_file_path, os.path.join(sagemaker_project_dir, "serve"))

    # permission 755 is required for entry script 'serve'
    os.chmod(os.path.join(sagemaker_project_dir, "serve"), 0o755)

    return sagemaker_project_dir


def generate_deployable(bento_bundle_path, deployment_name):
    bento_metadata = load_bento_service_metadata(bento_bundle_path)

    dir_name = f"{bento_metadata.name}_{bento_metadata.version}_sagemaker_deployable"
    sagemaker_project_dir = generate_sagemaker_target(
        bento_metadata, bento_bundle_path, os.path.abspath(dir_name)
    )
    return sagemaker_project_dir, bento_metadata.name, bento_metadata.version
