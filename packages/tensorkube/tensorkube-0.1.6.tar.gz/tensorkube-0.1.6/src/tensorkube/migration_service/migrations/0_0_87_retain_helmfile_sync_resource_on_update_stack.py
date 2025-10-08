import click
import subprocess
from pkg_resources import resource_filename
from tensorkube.constants import get_cluster_name
from tensorkube.services.configure_service import update_cfn_configure_stack

def apply(test: bool = False):
    try:
        updated_params = {
            "TemplatesVersion": "v0.0.4",
            "AWSAccessLambdaFunctionImageVersion": "v1.0.2",
            "CliVersion": "0.0.87",
            "EksAccessLambdaFunctionImageVersion": "v1.0.2"
        }
        update_cfn_configure_stack(updated_parameters=updated_params, test=test)

    except Exception as e:
        click.echo(click.style(f"Failed to update CloudFormation Stack: {e}", bold=True, fg="red"))
        raise e