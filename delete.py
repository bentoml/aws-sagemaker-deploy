import sys

from utils import run_shell_command, console, get_configuration_value
from sagemaker.generate_resource_names import generate_resource_names


def delete(deployment_name, config_json):
    (
        ecr_repo_name,
        _,
        _,
        endpoint_name,
        _,
    ) = generate_resource_names(deployment_name)
    sagemaker_config = get_configuration_value(config_json)

    if not sagemaker_config.get('skip_stack_deployment', False):
        # delete API Gateway Cloudformation Stack
        run_shell_command(
            [
                "aws",
                "--region",
                sagemaker_config["region"],
                "cloudformation",
                "delete-stack",
                "--stack-name",
                endpoint_name,
            ]
        )
        print(f"Deleting Stack {endpoint_name}")

    # delete ECR Repository
    run_shell_command(
        [
            "aws",
            "--region",
            sagemaker_config['region'],
            "ecr",
            "delete-repository",
            "--repository-name",
            ecr_repo_name,
            "--force",
        ]
    )
    print(f"Deleting ECR Repository {ecr_repo_name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Please provide deployment name and config name")
    deployment_name = sys.argv[1]
    config_json = sys.argv[2] if len(sys.argv) == 3 else "sagemaker_config.json"

    delete(deployment_name, config_json)
    console.print("[bold green]Deletion complete!")
