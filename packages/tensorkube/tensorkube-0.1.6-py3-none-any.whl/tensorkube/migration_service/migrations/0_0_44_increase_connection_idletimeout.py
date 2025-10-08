
from tensorkube.services.istio import install_istio_on_cluster
from tensorkube.services.nodepool import get_gpu_nodepool
from tensorkube.services.nydus import install_nydus_snapshotter_helm
import click

def apply(test: bool = False):
    try:
        install_istio_on_cluster()
        click.echo("Successfully increased connection idle timeout")
        install_nydus_snapshotter_helm(get_gpu_nodepool())
        click.echo("Successfully installed nydus snapshotter helm")

    except Exception as e:
        raise e
