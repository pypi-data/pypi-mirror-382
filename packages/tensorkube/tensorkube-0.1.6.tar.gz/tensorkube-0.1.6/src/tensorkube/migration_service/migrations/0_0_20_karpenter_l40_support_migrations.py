from tensorkube.services.karpenter_service import upgrade_karpenter_nodepools
import click
def apply(test: bool = False):
    try:
        upgrade_karpenter_nodepools()
        click.echo("Successfully upgraded Karpenter nodepools to L40")
    except Exception as e:
        raise e

    

