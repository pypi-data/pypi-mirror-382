from tensorkube.services.istio import install_istio_on_cluster
import click

def apply(test: bool = False):
    try:
        install_istio_on_cluster()
        click.echo("Successfully increased connection idle timeout")

    except Exception as e:
        raise e
