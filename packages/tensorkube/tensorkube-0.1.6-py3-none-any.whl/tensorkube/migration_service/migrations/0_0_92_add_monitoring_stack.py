import click
from tensorkube.services.configure_service import update_cfn_configure_stack
from tensorkube.helpers import is_valid_email

def apply(test: bool = False):
    try:
        user_alert_email = click.prompt("Enter the email address for cluster issue alerts", type=str, )
        if not is_valid_email(user_alert_email):
            raise ValueError("Invalid email address provided for alerts.")
        updated_params = {
            "TemplatesVersion": "v0.0.7",
            "AWSAccessLambdaFunctionImageVersion": "v1.0.2",
            "CliVersion": "0.0.92",
            "EksAccessLambdaFunctionImageVersion": "v1.0.4",
            "MonitoringLambdaFunctionImageVersion": "v1.0.0",
            "UserAlertEmail": user_alert_email,
            "EvaluationPeriods": "45",
            "RepeatedNotificationPeriod": "900",
            "TagForRepeatedNotification": "TensorkubeRepeatedAlarm:true"
        }
        click.echo("Updating CloudFormation templates")
        update_cfn_configure_stack(updated_parameters=updated_params, test=test)
        click.echo("CloudFormation templates updated")

    except Exception as e:
        click.echo(click.style(f"Failed to update base stack: {e}", bold=True, fg="red"))
        raise e