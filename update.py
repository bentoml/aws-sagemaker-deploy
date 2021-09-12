import sys

from utils import run_shell_command, console
from deploy import deploy
from describe import describe


def update(bento_bundle_path, deployment_name, config_json):
    """
    the cloudformation deploy command can be used to find the changesets and update
    the stack too.
    """
    deploy(bento_bundle_path, deployment_name, config_json)

    # point API Gateway to new the updated deployment
    deploy_desc = describe(deployment_name, config_json)
    api_gateway_id = deploy_desc.get('OutputApiId')
    run_shell_command(
        [
            "aws",
            "apigateway",
            "create-deployment",
            "--rest-api-id",
            api_gateway_id,
            "--stage-name",
            "prod",
            "--description",
            "deploying update at ",
        ]
    )
    print("Updating API Gateway")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception("Please provide deployment name, bundle path and config name")
    bento_bundle_path = sys.argv[1]
    deployment_name = sys.argv[2]
    config_json = sys.argv[3] if len(sys.argv) == 4 else "sagemaker_config.json"

    update(bento_bundle_path, deployment_name, config_json)
    console.print("[bold green]Updation Complete!")
