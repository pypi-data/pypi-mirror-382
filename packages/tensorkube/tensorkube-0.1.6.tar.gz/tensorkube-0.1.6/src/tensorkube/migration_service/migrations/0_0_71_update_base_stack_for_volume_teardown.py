from tensorkube.services.configure_service import update_cfn_configure_stack
import click

def apply(test: bool = False):
    try:
        updated_params = {
            "TemplatesVersion": "v0.0.2",
            "AWSAccessLambdaFunctionImageVersion": "v1.0.1",
            "CliVersion": "0.0.71",
            "EksAccessLambdaFunctionImageVersion": "v1.0.0"
        }
        update_cfn_configure_stack(updated_parameters=updated_params, test=test)
    except Exception as e:
        click.echo(click.style(f"Failed to update CloudFormation templates: {e}", bold=True, fg="red"))
        raise e
