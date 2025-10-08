import click
from pkg_resources import resource_filename

from tensorkube.services.k8s_service import get_tensorkube_cluster_context_name, list_all_namespaces
from tensorkube.services.knative_service import list_ksvc_in_namespace, apply_virtual_service_for_routing


def apply(test: bool = False):
    # list all ksvcs across all namespaces
    # apply a virtualservice for all those ksvcs
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise Exception(
            "No Kubernetes context found. Please ensure that you have a valid kubeconfig file and try again.")

    virtual_service_yaml_file_path = resource_filename('tensorkube',
                                                       'configurations/build_configs/virtual_service.yaml')

    all_namespaces = list_all_namespaces()
    for ns in all_namespaces:
        click.echo(f'Applying migration to all services in the {ns} environment')
        ksvcs = list_ksvc_in_namespace(ns)
        for ksvc in ksvcs['items']:
            service_name = ksvc['metadata']['name']
            apply_virtual_service_for_routing(service_name=service_name, yaml_file_path=virtual_service_yaml_file_path,
                sanitised_project_name=service_name.split('-')[0], env=ns, context_name=context_name)
            click.echo(
                f'Migrated routing for service {service_name} in namespace {ns}')
