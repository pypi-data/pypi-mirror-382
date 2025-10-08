import click

from tensorkube.constants import CliColors
from tensorkube.services.aws_service import check_and_install_aws_cli
from tensorkube.services.eksctl_service import check_and_install_eksctl
from tensorkube.services.istio import check_and_install_istioctl
from tensorkube.services.kubectl_utils import check_and_install_kubectl, check_and_install_helm


def check_and_install_cli_tools():
    try:
        # check and install aws cli
        check_and_install_aws_cli()
        # check and install eksctl
        check_and_install_eksctl()
        # check if kubectl is present and if not install
        check_and_install_kubectl()
        # check and install istioctl
        check_and_install_istioctl()
        # check and install helm
        check_and_install_helm()
        return True
    except Exception as e:
        text = f"Error {e} while installing CLI tools."
        click.echo(click.style(text, bold=True, fg=CliColors.ERROR.value))
        return False
