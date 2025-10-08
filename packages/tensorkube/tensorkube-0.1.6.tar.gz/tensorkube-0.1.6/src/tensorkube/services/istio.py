import json
import os
import platform
import subprocess

import click
import semver
import yaml
from kubernetes import config, client
from pkg_resources import resource_filename

from tensorkube.configurations.cloudformation.configure.cluster_access_lambda_files.lambda_code import \
    get_managed_node_group_name
from tensorkube.configurations.configuration_urls import DOMAIN_SERVER_URL, KNATIVE_ISTIO_CONTROLLER_URL
from tensorkube.constants import CliColors, LOCKED_ISTIO_VERSION, get_cluster_name
from tensorkube.services.eks_service import get_pods_using_namespace, apply_yaml_from_url, delete_resources_from_url
from tensorkube.services.error import CLIVersionError
from tensorkube.services.k8s_service import get_tensorkube_cluster_context_name


def check_and_install_istioctl():
    """Check if istioctl is installed and install it if it's not."""
    try:
        output = subprocess.run(["istioctl", "version", "-o", "json"], check=True, stdout=subprocess.PIPE)
        version_dict = json.loads(output.stdout.decode("utf-8"))
        version = semver.VersionInfo.parse(version_dict["clientVersion"]["version"])
        locked_istioctl_version = semver.VersionInfo.parse(LOCKED_ISTIO_VERSION)
        print("istioctl is already installed.")
        if (version.major, version.minor) < (locked_istioctl_version.major, locked_istioctl_version.minor):
            text = f"istioctl version is {version}. Please upgrade istioctl to version above {LOCKED_ISTIO_VERSION}"
            click.echo(click.style(text, bold=True, fg=CliColors.ERROR.value))
            raise CLIVersionError(text)
    except Exception as e:
        if isinstance(e, CLIVersionError):
            raise e
        click.echo(
            click.style("istioctl not found. Proceeding with installation. Might require sudo password.", bold=True,
                        fg=CliColors.WARNING.value))
        if platform.system() == "Darwin" or platform.system() == "Linux":
            try:
                install_command = f"curl -sL https://istio.io/downloadIstioctl | ISTIO_VERSION={LOCKED_ISTIO_VERSION} sh -"
                # Download and install istioctl
                subprocess.run(install_command, shell=True, check=True)
                # the above script installs istioctl in ~/.istioctl/bin/istioctl
                istioctl_path = os.path.expanduser("~/.istioctl/bin/istioctl")
                subprocess.run(f"sudo mv {istioctl_path} /usr/local/bin/", shell=True, check=True)
                print("istioctl moved to /usr/local/bin successfully.")
            except subprocess.CalledProcessError as e:
                print("Unable to install istioctl using curl. Please install istioctl manually.")
                raise e
        else:
            print("Unsupported operating system. Please install istioctl manually.")
            raise Exception('Unsupported operating system.')

        # Verify istioctl installation
        try:
            subprocess.run(["istioctl", "version"], check=True)
            print("istioctl installed successfully.")
        except subprocess.CalledProcessError as e:
            print("istioctl installation failed. Please install istioctl manually.")
            raise e


def install_istio_on_cluster():
    """Install Istio with the default profile."""
    try:
        values_file = resource_filename('tensorkube','configurations/istio/istio.yaml')
        with open(values_file, 'r') as f:
            values = yaml.safe_load(f)
            nodegroup_name = get_managed_node_group_name(get_cluster_name())
            values['spec']['components']['ingressGateways'][0]['k8s']['affinity'][
                'nodeAffinity']['requiredDuringSchedulingIgnoredDuringExecution'][
                'nodeSelectorTerms'][0]['matchExpressions'][0]['values'][0] = nodegroup_name
            values['spec']['components']['pilot']['k8s']['affinity'][
                'nodeAffinity']['requiredDuringSchedulingIgnoredDuringExecution'][
                'nodeSelectorTerms'][0]['matchExpressions'][0]['values'][0] = nodegroup_name

        temp_file = '/tmp/tensorkube-istio.yaml'
        with open(temp_file, 'w') as f:
            istio_config = yaml.safe_dump(values, f)
        subprocess.run(["istioctl", "install", "--set", "profile=default", "-f", temp_file, "-y"])
        print("Istio installed successfully.")
    except Exception as e:
        print(f"Error installing Istio: {e}")
        raise e
    # finally using the kubeconfi
    pods = get_pods_using_namespace("istio-system")
    for pod in pods.items:
        click.echo(f"Pod name: {pod.metadata.name}, Pod status: {pod.status.phase}")


def remove_domain_server():
    delete_resources_from_url(DOMAIN_SERVER_URL, "removing Knative Default Domain")


def uninstall_istio_from_cluster():
    """Uninstall Istio from the cluster."""
    # remove knative istion controller
    delete_resources_from_url(KNATIVE_ISTIO_CONTROLLER_URL, "uninstalling Knative Net Istio")
    # remove istio
    try:
        subprocess.run(["istioctl", "x", "uninstall", "--purge", "-y"])
        click.echo("Istio uninstalled successfully.")
    except Exception as e:
        click.echo(f"Error uninstalling Istio: {e}")


def install_net_istio():
    apply_yaml_from_url(KNATIVE_ISTIO_CONTROLLER_URL, "installing Knative Net Istio")


def install_default_domain():
    apply_yaml_from_url(DOMAIN_SERVER_URL, "installing Knative Default Domain")


def configure_ssl_for_ingress_gateway(certificate_arn: str, ssl_ports: str = "443") -> bool:
    """
    Configure SSL certificate for istio-ingressgateway service
    Args:
        certificate_arn: ACM certificate ARN
        ssl_ports: Comma-separated list of SSL ports (default: "443")
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load kubernetes config
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return False
        api_client = config.new_client_from_config(context=context_name)
        v1 = client.CoreV1Api(api_client)

        # Get existing service
        service = v1.read_namespaced_service(
            name='istio-ingressgateway',
            namespace='istio-system'
        )

        # Prepare annotations
        if not service.metadata.annotations:
            service.metadata.annotations = {}

        service.metadata.annotations.update({
            'service.beta.kubernetes.io/aws-load-balancer-ssl-cert': certificate_arn,
            'service.beta.kubernetes.io/aws-load-balancer-ssl-ports': ssl_ports,
            'service.beta.kubernetes.io/aws-load-balancer-backend-protocol': "http"
        })

        # Update service
        v1.patch_namespaced_service(
            name='istio-ingressgateway',
            namespace='istio-system',
            body=service
        )

        return True

    except client.exceptions.ApiException as e:
        click.echo(f"Failed to configure SSL: {str(e)}")
        return False
    except Exception as e:
        click.echo(f"Unexpected error configuring SSL: {str(e)}")
        return False

def configure_443_port_for_gateway() -> bool:
    """
    Add port 443 support to knative-ingress-gateway
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load kubernetes config
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return False
        api_client = config.new_client_from_config(context=context_name)
        custom_api = client.CustomObjectsApi(api_client)

        # Get existing gateway
        gateway = custom_api.get_namespaced_custom_object(
            group="networking.istio.io",
            version="v1",
            namespace="knative-serving",
            plural="gateways",
            name="knative-ingress-gateway"
        )

        # Check if 443 port is already configured
        for server in gateway['spec']['servers']:
            if server.get('port', {}).get('number') == 443:
                click.echo("Port 443 already configured in gateway")
                return True

        # Add new server for port 443
        gateway['spec']['servers'].append({
            'hosts': ['*'],
            'port': {
                'name': 'http-443',
                'number': 443,
                'protocol': 'HTTP'
            }
        })

        # Patch gateway
        custom_api.patch_namespaced_custom_object(
            group="networking.istio.io",
            version="v1",
            namespace="knative-serving",
            plural="gateways",
            name="knative-ingress-gateway",
            body=gateway
        )

        click.echo("Successfully added port 443 to gateway")
        return True

    except client.exceptions.ApiException as e:
        click.echo(f"Failed to configure gateway: {str(e)}")
        return False
    except Exception as e:
        click.echo(f"Unexpected error configuring gateway: {str(e)}")
        return False
