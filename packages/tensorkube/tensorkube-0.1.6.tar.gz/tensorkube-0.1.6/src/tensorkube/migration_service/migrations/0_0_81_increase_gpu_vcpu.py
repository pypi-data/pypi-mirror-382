import click
import subprocess
from pkg_resources import resource_filename
from tensorkube.constants import get_cluster_name, get_image_registry_id
from tensorkube.services.configure_service import update_cfn_configure_stack

def apply(test: bool = False):
    try:
        release_name = "karpenter-configuration"
        chart_version = "0.1.1"
        subprocess.run(["helm", "upgrade", "--install", release_name,
                        f"oci://public.ecr.aws/{get_image_registry_id(test)}/tensorfuse/helm-charts/tk-karpenter-config",
                        "--version", chart_version,
                        "--set", f"clusterName={get_cluster_name()}"
                        ],
                       check=True)
        updated_params = {
            "TemplatesVersion": "v0.0.2",
            "AWSAccessLambdaFunctionImageVersion": "v1.0.1",
            "CliVersion": "0.0.80",
            "EksAccessLambdaFunctionImageVersion": "v1.0.1"
        }
        update_cfn_configure_stack(updated_parameters=updated_params, test=test)

    except Exception as e:
        click.echo(click.style(f"Failed to apply karpenter configuration helm chart: {e}", bold=True, fg="red"))
        raise e