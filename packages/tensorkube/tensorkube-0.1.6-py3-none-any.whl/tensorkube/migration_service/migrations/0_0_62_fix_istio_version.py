import click

from tensorkube.services.istio import install_istio_on_cluster


def apply(test: bool = False):
    try:
        install_istio_on_cluster()
        click.echo("Successfully updated Istio version")

    except Exception as e:
        raise e