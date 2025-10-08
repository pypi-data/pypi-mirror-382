import click
from tensorkube.services.configure_service import update_cfn_configure_stack

def apply(test=False):
    try:
        updated_params = {
            "TemplatesVersion": "v0.0.9",
            "CliVersion": "0.1.0",
            "AWSAccessLambdaFunctionImageVersion": "v1.0.2",
            "EksAccessLambdaFunctionImageVersion": "v1.0.5",
            "MonitoringLambdaFunctionImageVersion": "v1.0.0"
        }
        update_cfn_configure_stack(updated_parameters=updated_params, test=test)
    except Exception as e:
        click.echo(click.style(f"Failed to update base stack: {e}", bold=True, fg="red"))
        raise e