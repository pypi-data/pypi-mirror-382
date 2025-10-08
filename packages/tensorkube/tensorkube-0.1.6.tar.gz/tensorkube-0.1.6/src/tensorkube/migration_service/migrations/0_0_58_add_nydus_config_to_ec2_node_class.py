from tensorkube.services.nodepool import get_gpu_ec2nodeclass, get_config_file, gpu_nodepool_version
from tensorkube.constants import EC2NODECLASS
from tensorkube.services.karpenter_service import apply_ec2nodeclass
import click

def apply(test: bool = False):
    try:
        apply_ec2nodeclass(get_config_file(EC2NODECLASS, gpu_nodepool_version()), get_gpu_ec2nodeclass(), update=True)
        click.echo(click.style("Successfully applied ec2nodeclass", bold=True, fg="green"))
    except Exception as e:
        raise e