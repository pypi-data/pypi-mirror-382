from typing import Optional

from kubernetes import config, client
from tensorkube.services.k8s_service import get_tensorkube_cluster_context_name
import importlib
from rich.table import Table
from rich.console import Console

def get_current_tensorkube_version():
    return importlib.metadata.version('tensorkube')

def get_cluster_tensorkube_version(context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    try:
        config_map = v1.read_namespaced_config_map("tensorkube-migration", "default")
        return config_map.data['version']
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return None
        else:
            raise e
        
def print_tensorkube_version():
    cli_version = get_current_tensorkube_version()
    cluster_version = get_cluster_tensorkube_version()
    console = Console()
    table = Table(title="TensorKube Versions")

    table.add_column("Component", justify="left", style="cyan", no_wrap=True)
    table.add_column("Version", justify="left", style="magenta")

    table.add_row("CLI Version", cli_version)
    table.add_row("Cluster Version", cluster_version)

    console.print(table)
    