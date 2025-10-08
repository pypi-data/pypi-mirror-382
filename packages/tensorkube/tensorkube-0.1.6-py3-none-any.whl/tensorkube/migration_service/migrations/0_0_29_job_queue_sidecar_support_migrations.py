from tensorkube.services.job_queue_service import create_sa_role_rb_for_job_sidecar
import click

def apply(test: bool = False):
    try:
        create_sa_role_rb_for_job_sidecar()
        click.echo("Successfully Created Service Account, Role and Role Binding for Job Sidecar")
    except Exception as e:
        raise e
