import sys

from utils import (
    run_shell_command,
    get_configuration_value,
    create_ecr_repository_if_not_exists,
    get_ecr_login_info,
    build_docker_image,
    push_docker_image_to_repository,
    gen_cloudformation_template_with_resources,
)
from sagemaker.generate_deployable import generate_deployable
from sagemaker.get_arn_from_aws import get_arn_from_aws
from sagemaker.generate_resource_names import generate_resource_names
from sagemaker.generate_docker_image_tag import generate_docker_image_tag
from sagemaker.generate_resources import (
    gen_model,
    gen_endpoint,
    gen_endpoint_config,
    gen_api_gateway,
)


def deploy_to_sagemaker(bento_bundle_path, deployment_name, config_json):
    # create deployable
    deployable_path, bento_name, bento_version = generate_deployable(
        bento_bundle_path, deployment_name
    )
    # generate names
    (
        model_repo_name,
        model_name,
        endpoint_config_name,
        endpoint_name,
        api_gateway_name,
    ) = generate_resource_names(deployment_name, bento_version)
    deployment_config = get_configuration_value(config_json)

    arn, aws_account_id = get_arn_from_aws(deployment_config.get("iam_role"))

    print(f"Create ECR repo {model_repo_name}")
    registry_id, registry_uri = create_ecr_repository_if_not_exists(
        deployment_config["region"],
        model_repo_name,
    )

    _, username, password = get_ecr_login_info(deployment_config["region"], registry_id)
    image_tag = generate_docker_image_tag(registry_uri, bento_name, bento_version)
    print(f"Build and push image {image_tag}")
    build_docker_image(
        context_path=deployable_path,
        image_tag=image_tag,
    )
    push_docker_image_to_repository(image_tag, username=username, password=password)

    # specifies resources - model, endpoint-config, endpoint and api-gateway
    sagemaker_resources = {}
    sagemaker_resources.update(
        gen_model(
            model_name,
            image_tag,
            arn,
            deployment_config["api_name"],
            deployment_config["timeout"],
            deployment_config["workers"],
        )
    )

    sagemaker_resources.update(
        gen_endpoint_config(
            endpoint_config_name,
            model_name,
            deployment_config["initial_instance_count"],
            deployment_config["instance_type"],
        )
    )

    sagemaker_resources.update(gen_endpoint(endpoint_name, endpoint_config_name))

    sagemaker_resources.update(
        gen_api_gateway(api_gateway_name, deployment_config["api_name"], endpoint_name)
    )

    template_file_path = gen_cloudformation_template_with_resources(
        sagemaker_resources, deployable_path
    )

    print(f"Deploying stack {deployment_name}")
    run_shell_command(
        [
            "aws",
            "cloudformation",
            "deploy",
            "--stack-name",
            endpoint_name,
            "--template-file",
            template_file_path,
            "--capabilities",
            "CAPABILITY_IAM",
        ]
    )


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise Exception("Please provide deployment name, bundle path and API name")
    bento_bundle_path = sys.argv[1]
    deployment_name = sys.argv[2]
    config_json = sys.argv[3] if len(sys.argv) == 4 else "sagemaker_config.json"

    deploy_to_sagemaker(bento_bundle_path, deployment_name, config_json)
    print("Done!")
