import os

from .utils import (
    console,
    run_shell_command,
    create_ecr_repository_if_not_exists,
    get_ecr_login_info,
    build_docker_image,
    push_docker_image_to_repository,
    gen_cloudformation_template_with_resources,
)
from .generate_deployable import generate_deployable
from .generate_resource_names import generate_resource_names
from .generate_resource import gen_model, gen_endpoint_config, gen_endpoint, gen_api_gateway
from .generate_docker_image_tag import generate_docker_image_tag



def deploy(bento_path, deployment_name, deployment_spec):
    # create deployable
    deployable_path, bento_name, bento_version = generate_deployable(
        bento_path, deployment_name
    )
    # generate names
    (
        model_repo_name,
        model_name,
        endpoint_config_name,
        endpoint_name,
        api_gateway_name,
    ) = generate_resource_names(deployment_name, bento_version)

    registry_id, registry_uri = create_ecr_repository_if_not_exists(
        deployment_spec["region"],
        model_repo_name,
    )
    console.print(f"Created ECR repo [[b]{model_repo_name}[/b]]")

    _, username, password = get_ecr_login_info(deployment_spec["region"], registry_id)
    image_tag = generate_docker_image_tag(registry_uri, bento_name, bento_version)
    with console.status("Building image"):
        build_docker_image(
            context_path=deployable_path,
            image_tag=image_tag,
        )

    with console.status("Pushing image to ECR"):
        push_docker_image_to_repository(image_tag, username=username, password=password)
    console.print(f"Image built and pushed [[b]{image_tag}[/b]]")

    # if skip_stack_deployment is given in the config file, return
    if deployment_spec.get("skip_stack_deployment", False):
        console.print(
            "Skipping creation of sagemaker resources. 'skip_stack_deployment'"
            " option is set in the config"
        )
        return

    # specifies resources - model, endpoint-config, endpoint and api-gateway
    sagemaker_resources = {}
    # generate the config for sagemaker model
    sagemaker_resources.update(
        gen_model(
            model_name,
            image_tag,
            deployment_spec["timeout"],
            deployment_spec["workers"],
        )
    )
    # generate config for sagemaker endpoint_config
    sagemaker_resources.update(
        gen_endpoint_config(
            endpoint_config_name=endpoint_config_name,
            model_name=model_name,
            initial_instance_count=deployment_spec["initial_instance_count"],
            instance_type=deployment_spec["instance_type"],
            enable_data_capture=deployment_spec.get("enable_data_capture", False),
            data_capture_s3_prefix=deployment_spec.get("data_capture_s3_prefix"),
            data_capture_sample_percent=deployment_spec.get(
                "data_capture_sample_percent"
            ),
        )
    )
    # generate config for sagemaker endpoint
    sagemaker_resources.update(gen_endpoint(endpoint_name, endpoint_config_name))
    # generae config for API Gateway
    sagemaker_resources.update(
        gen_api_gateway(
            api_gateway_name,
            endpoint_name,
            deployment_spec["timeout"],
            bento_path,
        )
    )

    template_file_path = gen_cloudformation_template_with_resources(
        sagemaker_resources, deployable_path
    )
    console.print(
        f"Built CloudFormation template [[b]{os.path.relpath(template_file_path)}[/b]]"
    )

    with console.status("Deploying to Sagemaker"):
        run_shell_command(
            [
                "aws",
                "--region",
                deployment_spec["region"],
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
