import click
from tensorkube.services.configure_service import update_cfn_configure_stack

def apply(test: bool = False):
    try:
        updated_params = {
            "TemplatesVersion": "v0.0.5",
            "AWSAccessLambdaFunctionImageVersion": "v1.0.2",
            "CliVersion": "0.0.88",
            "EksAccessLambdaFunctionImageVersion": "v1.0.3"
        }
        update_cfn_configure_stack(updated_parameters=updated_params, test=test)

    except Exception as e:
        click.echo(click.style(f"Failed to apply karpenter configuration helm chart: {e}", bold=True, fg="red"))
        raise e