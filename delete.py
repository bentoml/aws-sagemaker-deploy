import sys

from utils import run_shell_command
from sagemaker.generate_resource_names import generate_resource_names


def delete_deployment(deployment_name):
    _, model_name, endpoint_config_name, endpoint_name = generate_resource_names(
        deployment_name
    )

    run_shell_command(
        ["aws", "sagemaker", "delete-endpoint", "--endpoint-name", endpoint_name]
    )
    run_shell_command(
        [
            "aws",
            "sagemaker",
            "delete-endpoint-config",
            "--endpoint-config-name",
            endpoint_config_name,
        ]
    )
    run_shell_command(["aws", "sagemaker", "delete-model", "--model-name", model_name])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Please provide deployment name, bundle path and API name")
    deployment_name = sys.argv[1]

    delete_deployment(deployment_name)
