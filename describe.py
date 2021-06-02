import sys
import json

from utils import run_shell_command
from sagemaker.generate_resource_names import generate_resource_names


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception('Please provide deployment name, bundle path and API name')
    deployment_name = sys.argv[1]
    _, _, _, endpoint_name = generate_resource_names(deployment_name)

    result = run_shell_command(
        ['aws', 'sagemaker', 'describe-endpoint', '--endpoint-name', endpoint_name]
    )
    print(json.dumps(result))
