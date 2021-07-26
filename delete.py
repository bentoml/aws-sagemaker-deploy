import sys

from utils import run_shell_command
from sagemaker.generate_resource_names import generate_resource_names


def delete_deployment(deployment_name):
    (
        ecr_repo_name,
        _,
        _,
        endpoint_name,
        _,
    ) = generate_resource_names(deployment_name)

    # delete API Gateway Cloudformation Stack
    print(f"Deleting Stack {endpoint_name}")
    run_shell_command(
        ["aws", "cloudformation", "delete-stack", "--stack-name", endpoint_name]
    )

    # delete ECR Repository
    print(f"Deleting ECR Repository {ecr_repo_name}")
    run_shell_command(
        [
            "aws",
            "ecr",
            "delete-repository",
            "--repository-name",
            ecr_repo_name,
            "--force",
        ]
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Please provide deployment name, bundle path and API name")
    deployment_name = sys.argv[1]

    delete_deployment(deployment_name)
