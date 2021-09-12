import sys
import json

import boto3
from botocore.exceptions import ClientError
from utils import get_configuration_value
from sagemaker.generate_resource_names import generate_resource_names
from rich.pretty import pprint


def describe(deployment_name, config_file_path):
    _, _, _, endpoint_name, _ = generate_resource_names(deployment_name)
    sagemaker_config = get_configuration_value(config_file_path)

    # if skip_stack_deployment is present in config.
    if sagemaker_config.get('skip_stack_deployment', False):
        return None

    cf_client = boto3.client("cloudformation", sagemaker_config["region"])
    try:
        stack_info = cf_client.describe_stacks(StackName=endpoint_name)
    except ClientError:
        print(f"Unable to find {deployment_name} in your cloudformation stack.")
        return

    info_json = {}
    stack_info = stack_info.get("Stacks")[0]
    keys = [
        "StackName",
        "StackId",
        "StackStatus",
    ]
    info_json = {k: v for k, v in stack_info.items() if k in keys}
    info_json["CreationTime"] = stack_info.get("CreationTime").strftime(
        "%m/%d/%Y, %H:%M:%S"
    )
    info_json["LastUpdatedTime"] = stack_info.get("LastUpdatedTime").strftime(
        "%m/%d/%Y, %H:%M:%S"
    )

    # get Endpoints
    outputs = stack_info.get("Outputs")
    outputs = {o["OutputKey"]: o["OutputValue"] for o in outputs}
    info_json.update(outputs)

    info_json.update({'api_name': sagemaker_config['api_name']})

    return info_json


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Please provide deployment name and config name")
    deployment_name = sys.argv[1]
    config_json = sys.argv[2] if len(sys.argv) == 3 else "sagemaker_config.json"

    result = describe(deployment_name, config_json)
    pprint(result)
