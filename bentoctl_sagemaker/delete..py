from utils import console, run_shell_command
from .generate_resource_names import generate_resource_names

def delete(deployment_name, deployment_spec):
    (
        ecr_repo_name,
        _,
        _,
        endpoint_name,
        _,
    ) = generate_resource_names(deployment_name)

    if not deployment_spec.get('skip_stack_deployment', False):
        # Delete API gateway stac
        run_shell_command(
            [
                'aws',
                '--region',
                deployment_spec['region'],
                'cloudformation',
                'delete-stack',
                '--stack-name',
                endpoint_name,
            ]
        )
        console.print(f"Deleting Stack {endpoint_name}")

    run_shell_command(
        [
            'aws',
            '--region',
            deployment_spec['region'],
            'ecr',
            'delete-repository',
            '--repository-name',
            ecr_repo_name,
            '--force',
        ]
    )
    console.print(f'Deleting ECR Repository {ecr_repo_name}')
