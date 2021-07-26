import sys
import json

from utils import run_shell_command
from sagemaker.generate_resource_names import generate_resource_names


def describe_deployment(deployment_name):
    _, _, _, endpoint_name, _ = generate_resource_names(deployment_name)

    result, _ = run_shell_command(
        ["aws", "cloudformation", "describe-stacks", "--stack-name", endpoint_name]
    )

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Please provide deployment name, bundle path and API name")
    deployment_name = sys.argv[1]

    result = describe_deployment(deployment_name)
    print(json.dumps(result, indent=2))
