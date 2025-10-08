from tensorkube.services.job_queue_service import create_cloud_resources_for_queued_job_support
import click

def apply(test: bool = False):
    try:
        create_cloud_resources_for_queued_job_support()
        click.echo("Successfully Created Cloud Resources for Queued Job Support")
    except Exception as e:
        raise e