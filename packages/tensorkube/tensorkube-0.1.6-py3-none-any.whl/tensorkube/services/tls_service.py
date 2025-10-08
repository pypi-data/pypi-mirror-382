# Step 1: Ask the domain from the user and store it in a variable. Double confirm the domain from the user before setting up things
# Step 2: Check if a tensorkube certificate exists for the same domain. If it does, add the domain to the existing certificate.
# Step 3: If the certificate does not exist, create a new certificate for the domain.
# STep 4: Create a ClusterdomainClaim
# STep 5: Create a Cluster
import re
from dataclasses import dataclass
from typing import Optional, List, Dict

import click
from kubernetes import config, client
from pkg_resources import resource_filename

from tensorkube.constants import get_cluster_name
from tensorkube.services.aws_service import get_cloudformation_client
from tensorkube.services.cloudformation_service import deploy_generic_cloudformation_stack, \
    get_stack_status_from_stack_name, CfnStackStatus
from tensorkube.services.istio import configure_ssl_for_ingress_gateway
from tensorkube.services.k8s_service import get_tensorkube_cluster_context_name


@dataclass
class ServiceDomains:
    service_name: str
    domains: List[str]
    namespace: str



def get_all_virtualservices(namespaces: List[str]) -> List[Dict]:
    """
    Fetch all VirtualServices from a list of namespaces.

    Args:
        namespaces (List[str]): List of namespaces to query for VirtualServices.

    Returns:
        List[Dict]: A list of VirtualServices from all specified namespaces.
    """
    try:
        # Load Kubernetes configuration
        config.load_kube_config()
        k8s_client = client.CustomObjectsApi()

        # Initialize an empty list to store VirtualServices
        virtualservices = []

        # Fetch VirtualServices from each namespace
        for namespace in namespaces:
            vs_list = k8s_client.list_namespaced_custom_object(
                group="networking.istio.io",
                version="v1",
                namespace=namespace,
                plural="virtualservices"
            )
            virtualservices.extend(vs_list.get('items', []))

        return virtualservices

    except Exception as e:
        raise Exception(f"Failed to fetch VirtualServices: {e}")


def find_domains_for_service(virtualservices: List[Dict], service_name: str, namespace: str) -> ServiceDomains:
    """Process VirtualServices to find domains for a specific service"""
    domains = []
    for vs in virtualservices:
        vs_namespace = vs.get('metadata', {}).get('namespace')
        if vs_namespace != namespace:
            continue  # Skip if it's not in the same namespace
        for http in vs['spec'].get('http', []):
            for route in http.get('route', []):
                if route.get('destination', {}).get('host', '').startswith(service_name):
                    domains.extend(vs['spec'].get('hosts', []))

    return ServiceDomains(
        service_name=service_name,
        domains=list(set(domains)),
        namespace=namespace,
        # Remove duplicates
    )


def get_certificate_stack_name(domain: str) -> str:
    """
    Generate the CloudFormation stack name for the certificate.
    """
    return f"{get_cluster_name()}-cert-{domain.replace('.', '-')}"


def validate_domain(domain: str) -> bool:
    """
    Validates the domain format.
    :param domain: Domain name to validate
    :return: True if valid, False otherwise
    """
    pattern = re.compile(r'^(?:[a-zA-Z0-9-]{1,63}\.)+(?:[a-zA-Z]{2,})$')
    return bool(pattern.match(domain))


def deploy_certificate_stack(domain: str) -> bool:
    """
    Deploy ACM certificate stack using the generic deployment function
    """
    if not validate_domain(domain):
        click.echo(
            click.style(f'Invalid domain format: {domain}', fg='red')
        )
        return False
    stack_name = get_certificate_stack_name(domain)
    cluster_name = get_cluster_name()

    # Load certificate template
    template_file = resource_filename('tensorkube', 'configurations/cloudformation/certificate_manager.yaml')
    with open(template_file) as file:
        template_body = file.read()

    parameters = [{"ParameterKey": "DomainName", "ParameterValue": domain},
                  {"ParameterKey": "ClusterName", "ParameterValue": cluster_name}]

    queued = deploy_generic_cloudformation_stack(stack_name=stack_name, template_body=template_body,
                                                 parameters=parameters, capabilities=["CAPABILITY_NAMED_IAM"],
                                                 should_wait=False)
    if queued:
        click.echo(f'Certificate queued. Getting your validation records ready. Please wait.')
    else:
        click.echo(f'Failed to queue certificate.')
    return queued


def configure_certificate(domain):
    """Deploy ACM certificate for domain."""
    if not validate_domain(domain):
        click.echo(f"Invalid domain format: {domain}")
        return

    click.echo(f"Deploying certificate for *.{domain}")
    result = deploy_certificate_stack(domain)
    return result


def get_existing_ssl_config(namespace: str = 'istio-system', service_name: str = 'istio-ingressgateway') -> Optional[
    dict]:
    """
    Check if SSL annotations exist and get certificate ARN
    Returns:
        Optional[dict]: Dictionary with certificate_arn and ssl_ports if found, None otherwise
    """
    try:
        # Load kubernetes config
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
        api_client = config.new_client_from_config(context=context_name)
        v1 = client.CoreV1Api(api_client)

        # Get existing service
        service = v1.read_namespaced_service(name=service_name, namespace=namespace)

        # Check for annotations
        annotations = service.metadata.annotations or {}
        cert_annotation = 'service.beta.kubernetes.io/aws-load-balancer-ssl-cert'
        ports_annotation = 'service.beta.kubernetes.io/aws-load-balancer-ssl-ports'

        if cert_annotation in annotations:
            return {'certificate_arn': annotations[cert_annotation],
                    'ssl_ports': annotations.get(ports_annotation, '443')}
        return None

    except client.exceptions.ApiException as e:
        click.echo(f"Failed to get SSL config: {str(e)}")
        return None
    except Exception as e:
        click.echo(f"Unexpected error getting SSL config: {str(e)}")
        return None


def get_certificate_arn_from_stack(domain: str) -> Optional[str]:
    """Get certificate ARN from CloudFormation stack outputs"""
    stack_name = get_certificate_stack_name(domain=domain)
    cfn_client = get_cloudformation_client()

    try:
        response = cfn_client.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0]['Outputs']
        cert_arn = next(output['OutputValue'] for output in outputs if output['OutputKey'] == 'CertificateArn')
        return cert_arn
    except Exception as e:
        click.echo(f"Error getting certificate ARN: {str(e)}")
        return None

def check_if_a_domain_is_validated(domain:str):
    # extract the base domain from the subdomain
    # check if the cloudformation is created
    # check if the domain is attached to the load balancer
    base_domain = '.'.join(domain.split('.')[1:])
    stack_name = get_certificate_stack_name(domain=base_domain)
    stack_status = get_stack_status_from_stack_name(stack_name)
    if stack_status != CfnStackStatus.CREATE_COMPLETE:
        click.echo(
            click.style(
                "No such domain configured or validated. Please run `tensorkube configure domain` to configure a domain",
                fg="red"
            )
        )
        return False
    cert_arn = get_certificate_arn_from_stack(domain=base_domain)
    existing_config = get_existing_ssl_config()
    if existing_config is None:
        old_cert_arn = None
    else:
        old_cert_arn = existing_config["certificate_arn"]
    if old_cert_arn != cert_arn:
        return False
    return True


def attach_domain_name(domain_name, force: bool = False):
    # Check if the cloudformation stack for this name exists and is in successful state
    # if does note exist ask to create
    # if exists but not ready - ask to complete validation using validation command
    # if exists and ready check if the cluster has some other certificate arn configured
    # if yes then get the domain from the certificate arn and display that this has already been configured
    # with the following domain - and ask it to use the --force method to override
    # if no then get the certificate arn from the stack and attach it to the cluster
    # after attaching check if it has been successfully attached and display the message
    stack_name = get_certificate_stack_name(domain_name)
    print(f"Stack name : {stack_name}")
    stack_status = get_stack_status_from_stack_name(stack_name)
    print(f"Stack status : {stack_status}")
    if stack_status is None or (
            stack_status != CfnStackStatus.CREATE_IN_PROGRESS and stack_status != CfnStackStatus.CREATE_COMPLETE):
        click.echo(
            click.style("No such domain validated. Please wait for DNS validation"
                        " or create new mapping using `tensorkube domain create` command.",
                        fg="red"))
        return
    if stack_status == CfnStackStatus.CREATE_IN_PROGRESS:
        click.echo(click.style(
            "Domain validation pending. Please get validation details using `tensorkube domain get-validation-records` command"
            "or wait for your DNS provider to finish validating once this is done.",
            "yellow"))
    if stack_status == CfnStackStatus.CREATE_COMPLETE:
        new_cert_arn = get_certificate_arn_from_stack(domain=domain_name)
        existing_config = get_existing_ssl_config()
        if existing_config is None:
            old_cert_arn = None
        else:
            old_cert_arn = existing_config["certificate_arn"]
        print(f"Old cert arn: {old_cert_arn}")
        print(f"New cert arn: {new_cert_arn}")
        if old_cert_arn == new_cert_arn:
            print("Certificate already attached")
            configure_ssl_for_ingress_gateway(new_cert_arn)
        if old_cert_arn is not None and old_cert_arn != new_cert_arn:
            if not force:
                click.echo(click.style(
                    "Configuring multiple domains for the same cluster is not supported.", "red"))
            else:
                click.echo(click.style(
                    "Configuring multiple domains for the same cluster is not supported.", "red"))
        elif old_cert_arn is None:
            print("Attaching certificate to the cluster")
            configure_ssl_for_ingress_gateway(new_cert_arn)

def is_custom_domain(domain: str, service_env:str) -> bool:
    # Helper function to determine if a domain is custom/not generated by Knative or sslip.io
    return not (domain.endswith('.sslip.io') or 'svc.cluster.local' in domain or 'default.svc' in domain or domain.endswith('.default')
                or domain.endswith(f'.{service_env}') or domain.endswith(f'{service_env}.svc'))
