import sys
import logging

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


<<<<<<< HEAD
def update_deployment(bento_bundle_path, deployment_name, config_json):
=======
if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise Exception("Please provide deployment name, bundle path and API name")
    deployment_name = sys.argv[1]
    bento_bundle_path = sys.argv[2]
    api_name = sys.argv[3]
    config_json = sys.argv[4] if len(sys.argv) == 5 else "sagemaker_config.json"

>>>>>>> 267cbfc (small fixes and formating)
    (
        model_repo_name,
        model_name,
        endpoint_config_name,
        endpoint_name,
    ) = generate_resource_names(deployment_name)
    deployment_config = get_configuration_value(config_json)
    deployable_path, bento_name, bento_version = generate_deployable(
        bento_bundle_path, deployment_name
    )

    arn, aws_account_id = get_arn_from_aws()

    print(f"Create ECR repo {model_repo_name}")
    registry_id, registry_uri = create_ecr_repository_if_not_exists(
        deployment_config["region"], model_repo_name,
    )

    _, username, password = get_ecr_login_info(deployment_config["region"], registry_id)
    image_tag = generate_docker_image_tag(registry_uri, bento_name, bento_version)
    print(f"Build and push image {image_tag}")
    build_docker_image(
        context_path=deployable_path, image_tag=image_tag,
    )
    push_docker_image_to_repository(image_tag, username=username, password=password)

    model_info = generate_model_info(
        model_name,
        image_tag,
<<<<<<< HEAD
        deployment_config["api_name"],
        deployment_config["timeout"],
        deployment_config["num_of_workers"],
    )

    print(f"Create Sagemaker model {model_name}")
=======
        api_name,
        deployment_config["timeout"],
        deployment_config["num_of_workers"],
    )
>>>>>>> 267cbfc (small fixes and formating)
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
<<<<<<< HEAD
    print(f"Create Sagemaker endpoint confg {endpoint_config_name}")
=======
>>>>>>> 267cbfc (small fixes and formating)
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

<<<<<<< HEAD
    print(f"Update Sagemaker endpoint {endpoint_name}")
=======
>>>>>>> 267cbfc (small fixes and formating)
    run_shell_command(
        [
            "aws",
            "sagemaker",
            "update-endpoint",
            "--endpoint-name",
            endpoint_name,
            "--endpoint-config-name",
            endpoint_config_name,
        ]
    )
<<<<<<< HEAD


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise Exception("Please provide deployment name, bundle path and API name")
    deployment_name = sys.argv[1]
    bento_bundle_path = sys.argv[2]
    config_json = sys.argv[3] if len(sys.argv) == 4 else "sagemaker_config.json"

    update_deployment(bento_bundle_path, deployment_name, config_json)
=======
>>>>>>> 267cbfc (small fixes and formating)
