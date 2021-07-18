import sys

from utils import (
    run_shell_command,
    get_configuration_value,
    create_ecr_repository_if_not_exists,
    get_ecr_login_info,
    build_docker_image,
    push_docker_image_to_repository,
)
from sagemaker.generate_data_capture_config import generate_data_capture_config
from sagemaker.generate_deployable import generate_deployable
from sagemaker.get_arn_from_aws import get_arn_from_aws
from sagemaker.generate_resource_names import generate_resource_names
from sagemaker.generate_endpoint_config import generate_endpoint_config
from sagemaker.generate_model_info import generate_model_info
from sagemaker.generate_docker_image_tag import generate_docker_image_tag
from sagemaker.cloudformation_template import generate_api_gateway_template


def deploy_to_sagemaker(bento_bundle_path, deployment_name, config_json):
    (
        model_repo_name,
        model_name,
        endpoint_config_name,
        endpoint_name,
        api_gateway_name,
    ) = generate_resource_names(deployment_name)
    deployment_config = get_configuration_value(config_json)
    deployable_path, bento_name, bento_version = generate_deployable(
        bento_bundle_path, deployment_name
    )

    # generate cf template for API Gateway for Sagemaker Endpoint
    template_file_path = generate_api_gateway_template(
        project_dir=deployable_path,
        api_gateway_name=api_gateway_name,
        api_name=deployment_config["api_name"],
        endpoint_name=endpoint_name,
    )

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

    model_info = generate_model_info(
        model_name,
        image_tag,
        deployment_config["api_name"],
        deployment_config["timeout"],
        deployment_config["workers"],
    )

    print(f"Create Sagemaker model {model_name}")
    run_shell_command(
        [
            "aws",
            "sagemaker",
            "create-model",
            "--model-name",
            model_name,
            "--primary-container",
            model_info,
            "--execution-role-arn",
            arn,
        ]
    )

    production_variants = generate_endpoint_config(
        model_name,
        deployment_config["initial_instance_count"],
        deployment_config["instance_type"],
    )
    print(f"Create Sagemaker endpoint confg {endpoint_config_name}")
    if deployment_config["enable_data_capture"] is False:
        run_shell_command(
            [
                "aws",
                "sagemaker",
                "create-endpoint-config",
                "--endpoint-config-name",
                endpoint_config_name,
                "--production-variants",
                production_variants,
            ]
        )
    else:
        data_capture_config = generate_data_capture_config(
            deployment_config["data_capture_sample_percent"],
            deployment_config["data_capture_s3_prefix"],
        )
        run_shell_command(
            [
                "aws",
                "sagemaker",
                "create-endpoint-config",
                "--endpoint-config-name",
                endpoint_config_name,
                "--production-variants",
                production_variants,
                "--data-capture-config",
                data_capture_config,
            ]
        )

    print(f"Create Sagemaker endpoint {endpoint_name}")
    run_shell_command(
        [
            "aws",
            "sagemaker",
            "create-endpoint",
            "--endpoint-name",
            endpoint_name,
            "--endpoint-config-name",
            endpoint_config_name,
        ]
    )

    print(f"Create API Gateway {api_gateway_name}")
    run_shell_command(
        [
            "aws",
            "cloudformation",
            "deploy",
            "--stack-name",
            api_gateway_name,
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
