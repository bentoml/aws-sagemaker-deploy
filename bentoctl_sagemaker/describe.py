import boto3
import botocore.exceptions import ClientError

from .utils import console
from .generate_resource_names import generate_resource_names


def describe(deployment_name, deployment_spec, return_json=False):
    _, _, _, endpoint_name, _ = generate_resource_names(deployment_name)

    # if skip_stack_deployment is present in config.
    if deployment_spec.get("skip_stack_deployment", False):
        return None

    cf_client = boto3.client("cloudformation", deployment_spec["region"])
    try:
        stack_info = cf_client.describe_stacks(StackName=endpoint_name)
    except ClientError:
        console.print(f"Unable to find {deployment_name} in your cloudformation stack.")
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

    return info_json
