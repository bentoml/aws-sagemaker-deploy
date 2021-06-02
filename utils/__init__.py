import boto3
import base64
import json
import subprocess


def run_shell_command(command, shell_mode=False):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell_mode
    )
    stdout, stderr = proc.communicate()
    if proc.returncode == 0:
        try:
            return json.loads(stdout.decode('utf-8')), stderr.decode('utf-8')
        except json.JSONDecodeError:
            return stdout.decode('utf-8'), stderr.decode('utf-8')
    else:
        raise Exception(
            f'Failed to run command {" ".join(command)}: {stderr.decode("utf-8")}'
        )


def get_configuration_value(config_file):
    with open(config_file, 'r') as file:
        configuration = json.loads(file.read())
    return configuration


def get_ecr_login_info(region, repository_id):
    ecr_client = boto3.client('ecr', region)
    token = ecr_client.get_authorization_token(registryIds=[repository_id])
    username, password = (
        base64.b64decode(token["authorizationData"][0]["authorizationToken"])
            .decode("utf-8")
            .split(":")
    )
    registry_url = token["authorizationData"][0]["proxyEndpoint"]

    return registry_url, username, password


def create_ecr_repository_if_not_exists(region, repository_name):
    ecr_client = boto3.client("ecr", region)
    try:
        result = ecr_client.describe_repositories(repositoryNames=[repository_name])
        repository_id = result['repositories'][0]['registryId']
        repositoryUri = result['repositories'][0]['repositoryUri']
    except ecr_client.exceptions.RepositoryNotFoundException:
        result = ecr_client.create_repository(repositoryName=repository_name)
        repository_id = result['repository']['registryId']
        repositoryUri = result['repository']['repositoryUri']
    return repository_id, repositoryUri


def build_docker_image(
        context_path, image_tag, dockerfile='Dockerfile', additional_build_args=None
):
    docker_client = docker.from_env()
    try:
        docker_client.images.build(
            path=context_path,
            tag=image_tag,
            dockerfile=dockerfile,
            buildargs=additional_build_args,
        )
    except (docker.errors.APIError, docker.errors.BuildError) as error:
        raise Exception(f'Failed to build docker image {image_tag}: {error}')


def push_docker_image_to_repository(
        repository, image_tag=None, username=None, password=None
):
    docker_client = docker.from_env()
    docker_push_kwags = {'repository': repository, 'tag': image_tag}
    if username is not None and password is not None:
        docker_push_kwags['auth_config'] = {'username': username, 'password': password}
    try:
        docker_client.images.push(**docker_push_kwags)
    except docker.errors.APIError as error:
        raise Exception(f'Failed to push docker image {image_tag}: {error}')
