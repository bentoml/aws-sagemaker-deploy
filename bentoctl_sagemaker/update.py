from .deploy import deploy

def update(bento_path, deployment_name, deployment_spec):
    """
    the cloudformation deploy command can be used to find the changesets and update
    the stack too.
    """
    deploy(bento_path, deployment_name, deployment_spec)
