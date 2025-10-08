import click
import json
from pkg_resources import resource_filename
from tensorkube.constants import get_cluster_name
from tensorkube.services.aws_service import get_ecr_client


def get_or_create_ecr_repository(sanitised_project_name:str):
    ecr = get_ecr_client()
    repository_name = f"{get_cluster_name()}-{sanitised_project_name}"
    ecr_repo_lifecycle_policy = None
    try:
        #TODO! verify if this works. deletion takes upto 24 hours.
        ecr_repo_lifecycle_policy_config_file_path = resource_filename('tensorkube', 
                                                                       'configurations/aws_configs/ecr_repo_lifecycle_policy.json')
        with open(ecr_repo_lifecycle_policy_config_file_path, 'r') as f:
            ecr_repo_lifecycle_policy = json.dumps(json.load(f))
    except Exception as e:
        click.echo(f"Failed to read ECR repository lifecycle policy config file. Error: {e}")
        return None    
    try:
        response = ecr.create_repository(
            repositoryName=repository_name
        )
        ecr.put_lifecycle_policy(
            repositoryName=repository_name,
            lifecyclePolicyText=ecr_repo_lifecycle_policy
        )
        return response['repository']['repositoryUri']
    except ecr.exceptions.RepositoryAlreadyExistsException:
        click.echo(f"Repository '{repository_name}' already exists.")
        response = ecr.describe_repositories(repositoryNames=[repository_name])
        return response['repositories'][0]['repositoryUri']

def list_all_repositories():
    #TODO! pagination
    #NOTE: right now only 100 repositories are returned.
    ecr = get_ecr_client()
    response = ecr.describe_repositories()
    return response['repositories']


def delete_ecr_repository(repository_name:str):
    ecr = get_ecr_client()
    response = ecr.delete_repository(
        repositoryName=repository_name,
        force=True
    )
    return response


def delete_all_tensorkube_ecr_repositories():
    repositories = list_all_repositories()
    for repo in repositories:
        if get_cluster_name() in repo['repositoryName']:
            # TODO: check using tags or implement a more robust way to identify the repository
            if ("aws-access-lambda" in repo['repositoryName']
                    or "eks-access-lambda" in repo['repositoryName']
                    or 'monitoring-lambda' in repo['repositoryName']):
                click.echo(f"Skipping deletion of repository '{repo['repositoryName']}' as it is a system repository. "
                           f"It will be deleted automatically when the cluster is deleted.")
                continue

            click.echo(f"Deleting repository '{repo['repositoryName']}'...")
            delete_ecr_repository(repo['repositoryName'])

def patch_lifecycle_all_tensorkube_ecr_repositories():
    ecr_repo_lifecycle_policy = None
    ecr = get_ecr_client()
    try:
        ecr_repo_lifecycle_policy_config_file_path = resource_filename('tensorkube', 
                                                                    'configurations/aws_configs/ecr_repo_lifecycle_policy.json')
        with open(ecr_repo_lifecycle_policy_config_file_path, 'r') as f:
            ecr_repo_lifecycle_policy = json.dumps(json.load(f))
    except Exception as e:
        click.echo(f"Failed to read ECR repository lifecycle policy config file. Error: {e}")
        return None    
    repositories = list_all_repositories()
    for repo in repositories:
        if get_cluster_name() in repo['repositoryName']:
            click.echo(f"Patching lifecycle policy for repository '{repo['repositoryName']}'...")
            ecr.put_lifecycle_policy(
                repositoryName=repo['repositoryName'],
                lifecyclePolicyText=ecr_repo_lifecycle_policy
            )
            click.echo(f"Lifecycle policy patched for repository '{repo['repositoryName']}'.")