from typing import Optional, List, Dict

import click
import inquirer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from tensorkube.constants import DEFAULT_NAMESPACE, DATASET_BUCKET_TYPE
from tensorkube.services.dataset_service import list_datasets
from tensorkube.services.k8s_service import start_streaming_pod, ssh_into_pod, list_jobs, get_pods_for_jobs, \
    delete_job, ssh_into_pod_with_podman
from tensorkube.services.knative_service import list_deployed_services, get_knative_service, get_ready_condition, \
    get_pods_for_service, get_istio_ingress_gateway_hostname, delete_knative_service_by_name
from tensorkube.services.tls_service import get_all_virtualservices, find_domains_for_service, is_custom_domain
from tensorkube.services.train import get_training_id_from_job_name, get_training_stats
from tensorkube.services.s3_service import get_bucket_name

# Message Constants

DELETION_CONFIRMATION_MESSAGE = "Are you sure you want to delete this deployment? This action cannot be undone."
DELETION_SECOND_CONFIRMATION_WITH_TYPING = "You have chosen to delete the deployment. Please type the service name to be deleted to confirm."


def list_tensorkube_deployments(env_name: Optional[str] = None, all: bool = False, old: bool = False):
    # set up the initial table
    table = Table(title="Tensorkube Deployments")
    trees = []
    table.add_column("Name", style="magenta", no_wrap=True)
    table.add_column("Latest Ready", style="green", no_wrap=False, overflow="fold")
    table.add_column("Ready", no_wrap=False, overflow="fold")
    table.add_column("Env", no_wrap=False, overflow="fold")
    table.add_column("Reason", no_wrap=False, overflow="fold")
    # get the ingress gateway
    elb_url = get_istio_ingress_gateway_hostname()

    # get the services either all or within a namespace
    deployed_services = list_deployed_services(env_name=env_name, all=all)
    if not deployed_services:
        return
    services = deployed_services['items']
    if all:
        namespaces = [service['metadata']['namespace'] for service in services]
    else:
        namespaces = [env_name if env_name else DEFAULT_NAMESPACE]
    virtual_services = get_all_virtualservices(namespaces=namespaces)
    for service in services:
        service_env = service["metadata"]["namespace"]
        ready_condition = get_ready_condition(service)
        service_name = service['metadata']['name']
        if 'latestReadyRevisionName' in service['status']:
            latest_ready_revision = service['status']['latestReadyRevisionName'][-4:]
        else:
            latest_ready_revision = "N/A"
        if old:
            service_url = service['status']['url']
        else:
            domains = find_domains_for_service(virtualservices=virtual_services,service_name=service_name, namespace= service_env)
            custom_domains = list(filter(lambda domain: is_custom_domain(domain, service_env), domains.domains))
            if custom_domains:
                service_url = f'https://{custom_domains[0]}/'
            else:
                service_url = f'http://{elb_url}/svc/{service_env}/{service["metadata"]["name"]}/'
        service_env = service['metadata']['namespace']
        tree = Tree("[bold][bright_magenta]" + service_name)
        tree.add("[bold]env:[/] " + service_env)
        tree.add("[bold]URL:[/] [cyan]" + service_url)
        trees.append(tree)
        table.add_row(service_name, latest_ready_revision, ready_condition['status'], service_env,
                      ready_condition.get('reason', None))

    console = Console()
    console.print(table)
    for tree in trees:
        console.print(tree)


def describe_deployment(service_name: str, env_name: Optional[str] = None):
    env_namespace = env_name if env_name else DEFAULT_NAMESPACE
    deployment = get_knative_service(service_name=service_name, namespace=env_namespace)
    if deployment is None:
        click.echo(f"Service {service_name} not found in environment {env_namespace}")
        return
    ready_condition = get_ready_condition(deployment)

    if ready_condition['status'] == 'True':
        ready_status_color = "green"
    elif ready_condition['status'] == 'False':
        ready_status_color = "red"
    else:
        ready_status_color = "yellow"
    tree = Tree("[bold][bright_magenta]" + service_name)
    url = f'http://{get_istio_ingress_gateway_hostname()}/svc/{env_namespace}/{service_name}/'
    tree.add("[bold]URL:[/] [cyan]" + url)
    tree.add("[bold]Latest Created Revision:[/] " + deployment['status']['latestCreatedRevisionName'])
    tree.add("[bold]Latest Ready Revision:[/] [green]" + deployment['status']['latestReadyRevisionName'])
    tree.add(f"[bold]Ready Status:[/] [{ready_status_color}]" + ready_condition['status'])
    tree.add("[bold]Reason:[/] " + deployment['status']['conditions'][0].get('reason', ""))
    tree.add("[bold]Last Deployed At:[/] " + deployment['spec']['template']['metadata']['annotations']['deploy_time'])
    console = Console()
    console.print(tree)

def delete_deployment(service_name: str, env_name:str):
    # First ask the user to confirm the deletion
    # Then ask them to type the service name in addition to a warning that this action is irreversible
    deployment = get_knative_service(service_name=service_name, namespace=env_name)
    if deployment is None:
        click.echo(f"Service {service_name} not found in environment {env_name}")
        return
    deletion_confirmation_message = DELETION_CONFIRMATION_MESSAGE
    if not click.confirm(click.style(deletion_confirmation_message, fg='red')):
        click.echo("Deletion cancelled.")
        return
    deletion_second_confirmation_with_typing = DELETION_SECOND_CONFIRMATION_WITH_TYPING
    # Now ask it to type the service name and if it matches then only delete
    if click.prompt(click.style(deletion_second_confirmation_with_typing, fg='red')) == service_name:
        click.echo("Deleting service... This process will exit once the service is deleted.")
        # TODO this only deletes the service - The repository and other resources are not deleted
        delete_knative_service_by_name(service_name=service_name, namespace=env_name, wait=True)
        click.echo(f"Service {service_name} deleted.")
    else:
        click.echo("Service name match failed. Deletion cancelled.")


def display_deployment_logs(service_name: str, namespace: str = "default"):
    services_in_namespaces = list_deployed_services(env_name=namespace)['items']
    # check if the service name is present in the namespace
    if service_name not in [service['metadata']['name'] for service in services_in_namespaces]:
        click.echo(f"Service {service_name} not found in environment {namespace}")
        return
    service_pods = get_pods_for_service(service_name=service_name, namespace=namespace)
    if service_pods is None:
        click.echo(
            f"Your service failed to initialise. No containers could be started. Check dockerfile or view deployment logs")
        return
    if len(service_pods.items) == 0:
        click.echo(f"No active pods found for service {service_name}.")
        return
    elif len(service_pods.items) == 1:
        pod_name = service_pods.items[0].metadata.name
    else:
        click.echo(f"Multiple pods found for service {service_name}. Please specify a pod name.")
        questions = [inquirer.List('pod', message="Please select a pod",
                                   choices=[pod.metadata.name for pod in service_pods.items], ), ]
        pod_name = inquirer.prompt(questions)['pod']

    start_streaming_pod(pod_name=pod_name, namespace=namespace, container_name="user-container")


def ssh_into_deployed_service(service_name: str, namespace: str = "default"):
    services_in_namespaces = list_deployed_services(env_name=namespace)['items']
    # check if the service name is present in the namespace
    if service_name not in [service['metadata']['name'] for service in services_in_namespaces]:
        click.echo(f"Service {service_name} not found in environment {namespace}")
        return
    service_pods = get_pods_for_service(service_name=service_name, namespace=namespace)
    if service_pods is None:
        click.echo(
            f"Your service failed to initialise. No containers could be started. Check dockerfile or view deployment logs")
        return
    if len(service_pods.items) == 0:
        click.echo(f"No pods found for service {service_name}")
        return
    elif len(service_pods.items) == 1:
        pod_name = service_pods.items[0].metadata.name
    else:
        click.echo(f"Multiple pods found for service {service_name}. Please specify a pod name.")
        questions = [inquirer.List('pod', message="Please select a pod",
                                   choices=[pod.metadata.name for pod in service_pods.items], ), ]
        pod_name = inquirer.prompt(questions)['pod']
    # Check the image of the pod if it is tensorfuse/podman-nvidia:v1 or quay.io/podman/stable use ssh_into_pod_using_podman
    # else use ssh_into_pod
    image = service_pods.items[0].spec.containers[0].image
    if image == "tensorfuse/podman-nvidia:v1" or image == "quay.io/podman/stable":
        click.echo(f"SSHing into pod: {pod_name}")
        ssh_into_pod_with_podman(pod_name=pod_name, namespace=namespace)
    click.echo(f"SSHing into pod: {pod_name}")
    ssh_into_pod(pod_name=pod_name, namespace=namespace)


def display_secrets(secrets, namespace: str = DEFAULT_NAMESPACE):
    if not secrets:
        click.echo(f"No secrets found in namespace {namespace}")
        return
    if namespace != DEFAULT_NAMESPACE:
        tree = Tree("[bold][bright_magenta]Secrets in env: " + namespace)
    else:
        tree = Tree("[bold][bright_magenta]Secrets")
    for secret in secrets:
        tree.add("[bold]Name:[/] " + secret.metadata.name)
    console = Console()
    console.print(tree)


def list_tensorkube_datasets():
    # Get datasets
    datasets = list_datasets()
    if datasets is None:
        return
    if len(datasets) == 0:
        click.echo(click.style("No datasets found.", fg='yellow'))
        return

    table = Table(title="Tensorkube Datasets")
    trees = []

    # Add columns for the main table
    table.add_column("Dataset ID", style="magenta", no_wrap=True)
    table.add_column("Last Modified", style="green", no_wrap=False, overflow="fold")
    table.add_column("Size", no_wrap=False, overflow="fold")

    # Get bucket name for URL construction
    bucket_name = get_bucket_name(type=DATASET_BUCKET_TYPE)

    # Populate table and create trees for detailed view
    for dataset in datasets:
        # Skip directories
        if dataset.is_directory:
            continue

        # Remove .jsonl extension from dataset ID
        dataset_id = dataset.key.rsplit('.jsonl', 1)[0]

        # Create S3 URL
        dataset_url = f"s3://{bucket_name}/{dataset.key}"

        # Add row to main table
        table.add_row(dataset_id, dataset.last_modified, dataset.size)

        # Create detailed tree view for each dataset
        tree = Tree(f"[bold][bright_magenta]{dataset_id}")
        tree.add(f"[bold]Size:[/] {dataset.raw_size}")
        tree.add(f"[bold]Last Modified:[/] {dataset.last_modified}")
        tree.add(f"[bold]URL:[/] [cyan]{dataset_url}")
        if dataset.owner != '--':
            tree.add(f"[bold]Owner:[/] {dataset.owner}")
        trees.append(tree)

    # Print both table and trees
    console = Console()
    console.print(table)
    for tree in trees:
        console.print(tree)


def display_job_logs(job_prefix: str, container_name: str = "user-container", namespace: str = "default"):
    """
    Displays logs from a specified job's pods

    Args:
        job_prefix: Prefix of the job name
        namespace: Kubernetes namespace where the job exists
        container_name: Name of the container whose logs to display
    """
    # Get all jobs in the namespace with the prefix
    jobs_in_namespace = list_jobs(namespace=namespace, job_name_prefix=job_prefix)
    if not jobs_in_namespace or len(jobs_in_namespace.items) == 0:
        click.echo(click.style(f"No jobs with prefix '{job_prefix}' found in environment {namespace}", fg='red'))
        return

    # If multiple jobs found, ask user to select one
    if len(jobs_in_namespace.items) > 1:
        click.echo("Multiple jobs found. Please select a job.")
        questions = [inquirer.List('job', message="Please select a job",
            choices=[job.metadata.name for job in jobs_in_namespace.items], ), ]
        job_name = inquirer.prompt(questions)['job']
    else:
        job_name = jobs_in_namespace.items[0].metadata.name

    # Get pods associated with the selected job
    job_pods = get_pods_for_jobs(job_name=job_name, namespace=namespace)

    if job_pods is None:
        click.echo(click.style(
            f"Your job failed to initialize. No containers could be started. Check configuration or view deployment logs",
            fg='red'))
        return

    if len(job_pods.items) == 0:
        click.echo(click.style(f"No active pods found for job {job_name}.", fg='yellow'))
        return
    elif len(job_pods.items) == 1:
        pod_name = job_pods.items[0].metadata.name
    else:
        click.echo("Multiple pods found for job. Please select a pod.")
        questions = [inquirer.List('pod', message="Please select a pod",
            choices=[pod.metadata.name for pod in job_pods.items], ), ]
        pod_name = inquirer.prompt(questions)['pod']

    # Stream logs from the selected pod
    start_streaming_pod(pod_name=pod_name, namespace=namespace, container_name=container_name)


def list_tensorkube_training_jobs(namespace: Optional[str] = None, all: bool = False, job_prefix: Optional[str] = None):
    """
    Lists all jobs and their statuses with optional prefix filtering

    Args:
        namespace: Specific namespace to list jobs from
        all: If True, lists jobs from all namespaces
        job_prefix: Optional prefix to filter job names
    """
    table = Table(title="Tensorkube Jobs")
    trees = []

    # Add columns for the main table
    table.add_column("Job Id", style="magenta", no_wrap=True)
    table.add_column("Status", style="green", no_wrap=False, overflow="fold")
    table.add_column("Start Time", no_wrap=False, overflow="fold")
    table.add_column("Completion Time", no_wrap=False, overflow="fold")
    table.add_column("Env", no_wrap=False, overflow="fold")

    # Get jobs
    jobs = list_jobs(namespace=namespace, all=all, job_name_prefix=job_prefix)
    if not jobs:
        click.echo(click.style("No jobs found.", fg='yellow'))
        return

    for job in jobs.items:
        job_name = job.metadata.name
        job_namespace = job.metadata.namespace

        # Get job status information
        status = job.status
        start_time = status.start_time.strftime("%Y-%m-%d %H:%M:%S") if status.start_time else "N/A"
        completion_time = status.completion_time.strftime("%Y-%m-%d %H:%M:%S") if status.completion_time else "Running"

        # Determine job status
        if status.succeeded:
            job_status = "Succeeded"
        elif status.failed:
            job_status = f"Failed ({status.failed} attempts)"
            completion_time = "N/A"
        elif status.active:
            job_status = "Active"
        else:
            job_status = "Pending"

        # Create detailed tree view
        tree = Tree(f"[bold][bright_magenta]{get_training_id_from_job_name(job_name)}")
        tree.add(f"[bold]Namespace:[/] {job_namespace}")
        tree.add(f"[bold]Status:[/] {job_status}")
        tree.add(f"[bold]Start Time:[/] {start_time}")
        tree.add(f"[bold]Completion Time:[/] {completion_time}")

        # Add additional status details if available
        if hasattr(status, 'conditions') and status.conditions:
            conditions_tree = tree.add("[bold]Conditions")
            for condition in status.conditions:
                condition_status = f"{condition.type}: {condition.status}"
                if condition.reason:
                    condition_status += f" ({condition.reason})"
                conditions_tree.add(condition_status)

        trees.append(tree)

        # Add row to main table
        table.add_row(get_training_id_from_job_name(job_name), job_status, start_time, completion_time, job_namespace)

    # Print both table and trees
    console = Console()
    console.print(table)
    console.print()  # Add blank line between table and trees
    for tree in trees:
        console.print(tree)


def get_tensorkube_training_job(job_prefix: str, namespace: str = "default"):
    """
    Get job details

    Args:
        job_prefix: Prefix of the job name
        namespace: Kubernetes namespace where the job exists
    """
    # Get all jobs in the namespace with the prefix
    jobs_in_namespace = list_jobs(namespace=namespace, job_name_prefix=job_prefix)
    if not jobs_in_namespace or len(jobs_in_namespace.items) == 0:
        click.echo(click.style(f"No jobs with prefix '{job_prefix}' found in environment {namespace}", fg='red'))
        return

    # TODO: ideally there should be a single job with the prefix
    job = jobs_in_namespace.items[0]
    status = job.status
    start_time = status.start_time.strftime("%Y-%m-%d %H:%M:%S") if status.start_time else "N/A"
    completion_time = status.completion_time.strftime("%Y-%m-%d %H:%M:%S") if status.completion_time else "Running"

    # Determine job status
    if status.succeeded:
        job_status = "Succeeded"
    elif status.failed:
        job_status = f"Failed ({status.failed} attempts)"
        completion_time = "N/A"
    elif status.active:
        job_status = "Active"
    else:
        job_status = "Pending"
    stats = ''
    if job_status == "Succeeded" or job_status == "Active":
        # Convert start_time to milliseconds
        start_time = int(status.start_time.timestamp())
        stats = get_training_stats(job.metadata.name, start_time, namespace)
    table = Table(show_header=False, show_lines=True)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    # Add rows to the table
    table.add_row("Status", job_status)
    table.add_row("Completion Time", completion_time)
    table.add_row("Info", str(stats))
    console = Console()
    console.print(table)


def delete_tensorkube_job_by_prefix(job_prefix: str, namespace: str = "default") -> bool:
    """
    Deletes a job matching the given prefix. If multiple jobs match, asks user to select one.

    Args:
        job_prefix: Prefix of the job name to delete
        namespace: Kubernetes namespace where the job exists

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    # Get all jobs in the namespace with the prefix
    jobs_in_namespace = list_jobs(namespace=namespace, job_name_prefix=job_prefix)
    if not jobs_in_namespace or len(jobs_in_namespace.items) == 0:
        click.echo(click.style(f"No jobs with prefix '{job_prefix}' found in environment {namespace}", fg='red'))
        return False

    # If multiple jobs found, ask user to select one
    if len(jobs_in_namespace.items) > 1:
        click.echo("Multiple jobs found. Please select a job to delete.")
        questions = [inquirer.List('job', message="Please select a job to delete",
            choices=[job.metadata.name for job in jobs_in_namespace.items], ), ]
        job_name = inquirer.prompt(questions)['job']
    else:
        job_name = jobs_in_namespace.items[0].metadata.name

    # Confirm deletion
    if click.confirm(click.style(f"Are you sure you want to delete job '{job_name}'?", fg='yellow')):
        return delete_job(job_name, namespace)
    else:
        click.echo("Job deletion cancelled.")
        return False


def display_keda_scaled_jobs(jobs):
    jobs = jobs['items']
    if not jobs:
        click.echo(f"No jobs found")
        return

    table = Table(title="Jobs")
    table.add_column("Name", style="magenta", no_wrap=True)
    table.add_column("Ready", style="green", no_wrap=False, overflow="fold")

    for job in jobs:
        table.add_row(job['metadata']['name'], job['status']['conditions'][0]['status'])

    console = Console()
    console.print(table)


def prettify_aws_user_keys(aws_access_key_id, aws_secret_access_key):
    table = Table(title="AWS User Keys")
    table.add_column("Key", style="magenta", no_wrap=True)
    table.add_column("Value", style="green", no_wrap=False, overflow="fold")
    table.add_row("Access Key ID", aws_access_key_id)
    table.add_row("Secret Access Key", aws_secret_access_key)

    console = Console()
    console.print(table)


def display_queued_jobs(keda_jobs: Dict, dynamodb_jobs: Dict):
    jobs = keda_jobs['items']
    if not jobs:
        click.echo(f"No queued jobs found")
        return
    table = Table(title="Queued Jobs", show_lines=True)
    table.add_column("Job Name", style="magenta", no_wrap=True)
    table.add_column("Ready", style="green", no_wrap=False, overflow="ellipsis")
    table.add_column("Job IDs", style="cyan", no_wrap=True)
    table.add_column("Status", style="green", no_wrap=False, overflow="fold")

    for job in jobs:
        job_name = job['metadata']['name']
        ready_status = job['status']['conditions'][0]['status']
        if dynamodb_jobs.get(job_name, []):
            job_ids = "\n".join([x['job_id'] for x in dynamodb_jobs[job_name]])
            job_statuses = "\n".join([x['status'] for x in dynamodb_jobs[job_name]])
        else:
            job_ids = "-"
            job_statuses = "-"
        table.add_row(job_name, ready_status, job_ids, job_statuses)

    console = Console()
    console.print(table)


def display_specific_queued_job(keda_job: Dict, dynamodb_jobs: List[Dict]):
    job_name = keda_job['metadata']['name']
    ready_status = keda_job['status']['conditions'][0]['status']

    table = Table(title=f"Queued Job: {job_name}")
    table.add_column("Job IDs", style="cyan", no_wrap=True)
    table.add_column("Status", style="green", no_wrap=False, overflow="ellipsis")

    if dynamodb_jobs:
        for job in dynamodb_jobs:
            table.add_row(job['job_id'], job['status'])
    else:
        table.add_row("-", "-")

    console = Console()
    console.print(table)
    console.print(f"Ready Status: {ready_status}")


def display_dns_records_table(domain: str, validation_records: dict):
    """
    Display DNS records in a Rich formatted table
    Args:
        domain: Domain name
        validation_records: Dictionary containing validation records
    """
    # Get ELB hostname
    elb_hostname = get_istio_ingress_gateway_hostname()
    if not elb_hostname:
        console = Console()
        console.print("[red]Error: Could not get Istio ingress gateway hostname[/red]")
        return

    table = Table(title="Required DNS Records")
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Value", style="magenta")

    # Add validation record
    if validation_records:
        v_record = validation_records['validation_record']
        table.add_row(v_record['type'], v_record['name'], v_record['value'])

    # Add routing record with actual ELB hostname
    table.add_row("CNAME", f"*.{domain}", elb_hostname)

    console = Console()
    console.print(table)
    console.print("\n[yellow]Please configure these records in your DNS provider.[/yellow]")


def display_efs_volumes(volumes: List[Dict]):
    """
    Display EFS volumes in a Rich formatted table
    Args:
        volumes: List of EFS volumes
    """
    table = Table(title="EFS Volumes")
    table.add_column("Name", style="green")
    table.add_column("Volume ID", style="magenta", no_wrap=True)
    table.add_column("Status", style="cyan")

    for volume in volumes:
        table.add_row(volume['Name'], volume['FileSystemId'], volume['LifeCycleState'])

    console = Console()
    console.print(table)
