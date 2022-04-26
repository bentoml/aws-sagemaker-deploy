import base64

import boto3


def get_ecr_login_info(region, repository_id):
    ecr_client = boto3.client("ecr", region)
    token = ecr_client.get_authorization_token(registryIds=[repository_id])
    username, password = (
        base64.b64decode(token["authorizationData"][0]["authorizationToken"])
        .decode("utf-8")
        .split(":")
    )
    registry_url = token["authorizationData"][0]["proxyEndpoint"]

    return registry_url, username, password


def get_repository(ecr_client, repository_name):
    result = ecr_client.describe_repositories(repositoryNames=[repository_name])
    repository_id = result["repositories"][0]["registryId"]
    repository_uri = result["repositories"][0]["repositoryUri"]

    return repository_id, repository_uri


def create_ecr_repository_if_not_exists(region, repository_name):
    ecr_client = boto3.client("ecr", region)
    try:
        result = ecr_client.describe_repositories(repositoryNames=[repository_name])
        repository_id = result["repositories"][0]["registryId"]
        repository_uri = result["repositories"][0]["repositoryUri"]
    except ecr_client.exceptions.RepositoryNotFoundException:
        result = ecr_client.create_repository(repositoryName=repository_name)
        repository_id = result["repository"]["registryId"]
        repository_uri = result["repository"]["repositoryUri"]
    return repository_id, repository_uri


def create_repository(repository_name, operator_spec):
    """
    Create ECR repository and return the information.
    """
    repo_id, _ = create_ecr_repository_if_not_exists(
        operator_spec["region"], repository_name
    )
    registry_url, username, password = get_ecr_login_info(
        operator_spec["region"], repo_id
    )
    repository_url = f"{registry_url}/{repository_name}"

    return repository_url, username, password


def delete_repository(repository_name, operator_spec):
    """
    Delete the ECR repository created
    """
    ecr_client = boto3.client("ecr", operator_spec.get("region"))
    try:
        get_repository(ecr_client, repository_name)
        ecr_client.delete_repository(repositoryName=repository_name, force=True)
    except ecr_client.exceptions.RepositoryNotFoundException:
        print(f"Repository {repository_name} not found. Skipping registry cleanup")
