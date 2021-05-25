import os
import click
from bentoml.saved_bundle import load_bento_service_metadata

from bento_sagemaker.bentoml_sagemaker import generate_sagemaker_target


@click.group()
def cli():
    pass


@cli.command()
@click.argument("bento_bundle_path")
@click.option('--target-dir', help='Target directory', default=os.getcwd())
def generate(bento_bundle_path, target_dir):
    try:
        bento_metadata = load_bento_service_metadata(bento_bundle_path)
        deployable_path = os.path.join(
            target_dir,
            f'{bento_metadata.name}_{bento_metadata.version}_sagemaker_deployable'
        )
        generate_sagemaker_target(bento_metadata, bento_bundle_path, deployable_path)
        click.echo('Built sagemaker deployable...\nread deployment_guide.md')
    except Exception as e:
        click.echo(e, color='red')
