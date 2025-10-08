import click
import requests
import json

from tensorkube.constants import get_cluster_name, ADDON_NAME, get_mount_policy_name, get_mount_driver_role_name, \
    get_base_login_url
from tensorkube.helpers import get_tensorkube_token_and_session_id, get_user_cloud_account_id_and_org_id
from tensorkube.services.aws_service import get_aws_account_id
from tensorkube.services.build import delete_buildkit_irsa
from tensorkube.services.cloudformation_service import delete_cloudformation_stack, delete_launch_templates, \
    delete_tensorkube_base_stack
from tensorkube.services.eks_service import delete_eks_addon, delete_knative_core, delete_knative_crds, \
    delete_karpenter_from_cluster
from tensorkube.services.eksctl_service import delete_cluster
from tensorkube.services.environment_service import list_environments, delete_environment
from tensorkube.services.filesystem_service import cleanup_filesystem_resources
from tensorkube.services.iam_service import detach_role_policy, delete_role, delete_policy
from tensorkube.services.istio import remove_domain_server, uninstall_istio_from_cluster
from tensorkube.services.job_queue_service import teardown_job_queue_support
from tensorkube.services.knative_service import delete_knative_services, cleanup_knative_resources
from tensorkube.services.logging_service import teardown_cloudwatch
from tensorkube.services.nydus import delete_nydus
from tensorkube.services.s3_service import delete_s3_bucket, get_bucket_name



def cfn_teardown():
    delete_tensorkube_base_stack()


def legacy_teardown():
    click.echo("Deleting all job queue resources...")
    try:
        teardown_job_queue_support()
    except Exception as e:
        click.echo(f"Error while deleting job queue resources: {e}")

    # delete all services
    try:
        delete_knative_services()
    except Exception as e:
        click.echo("Error while deleting Knative services.")
    try:
        cleanup_filesystem_resources()
    except Exception as e:
        click.echo(f"Error while cleaning up filesystem resources: {e}")

    # EKS addon
    try:
        click.echo("Deleting EKS addon...")
        delete_eks_addon(get_cluster_name(), ADDON_NAME)
    except Exception as e:
        click.echo(f"Error while deleting EKS addon: {e}")

    # teardown cloudwatch
    try:
        teardown_cloudwatch()
    except Exception as e:
        click.echo(f"Error while tearing down Cloudwatch: {e}")

    click.echo("Deleting Enviroments...")
    try:
        environments = list_environments()
        for env in environments:
            click.echo(f"Deleting environment: {env}")
            delete_environment(env_name=env)
    except Exception as e:
        click.echo(f"Error while deleting environments: {e}")

    # Detach policy from role, delete role, delete policy
    click.echo("Deleting mountpoint driver role and policy...")
    click.echo("Detaching policy from role...")
    try:
        detach_role_policy(get_aws_account_id(), get_mount_driver_role_name(get_cluster_name()),
                           get_mount_policy_name(get_cluster_name()))
        click.echo("Deleting role...")
        delete_role(get_mount_driver_role_name(get_cluster_name()))
        click.echo("Deleting policy...")
        delete_policy(get_aws_account_id(), get_mount_policy_name(get_cluster_name()))
    except Exception as e:
        click.echo(f"Error while deleting role and policy: {e}")

    # delete s3 bucket
    click.echo("Deleting S3 bucket...")
    try:
        delete_s3_bucket(get_bucket_name())
    except Exception as e:
        click.echo(f"Error while deleting S3 bucket: {e}")

    click.echo("Deleting buildkit irsa...")
    try:
        delete_buildkit_irsa()
    except Exception as e:
        click.echo(f"Error while deleting buildkit irsa: {e}")

    click.echo("Uninstalling nydus helm charts...")
    try:
        delete_nydus()
    except Exception as e:
        click.echo(f"Error while uninstalling nydus resources: {e}")

    click.echo("Uninstalling domain server...")
    try:
        remove_domain_server()
    except Exception as e:
        click.echo(f"Error while uninstalling domain server: {e}")

    click.echo("Uninstalling Knative resources")
    try:
        cleanup_knative_resources()
    except Exception as e:
        click.echo(f"Error while cleaning up Knative resources: {e}")

    click.echo("Uninstalling and deleting Istio resources")
    try:
        uninstall_istio_from_cluster()
    except Exception as e:
        click.echo(f"Error while uninstalling Istio: {e}")
    click.echo("Uninstalling Knative core")
    try:
        delete_knative_core()
        click.echo("Uninstalling Knative CRDs")
        delete_knative_crds()
        click.echo("Successfully uninstalled Knative and Istio.")
    except Exception as e:
        click.echo(f"Error while uninstalling Knative: {e}")

    # remove karpenter
    click.echo("Uninstalling Karpenter...")
    try:
        delete_karpenter_from_cluster()
        click.echo("Successfully uninstalled Karpenter.")
    except Exception as e:
        click.echo(f"Error while uninstalling Karpenter: {e}")
    # delete cluster
    try:
        click.echo("Deleting cluster...")
        delete_cluster()
        click.echo("Successfully deleted cluster.")
    except Exception as e:
        click.echo(f"Error while deleting cluster.: {e}")
    try:
        # delete cloudformation stack
        click.echo("Deleting cloudformation stack...")
        delete_cloudformation_stack(get_cluster_name())
        click.echo("Successfully deleted cloudformation stack.")
    except Exception as e:
        click.echo(f"Error while deleting cloudformation stack: {e}")

    # delete launch templates
    click.echo("Deleting launch templates...")
    delete_launch_templates()


def start_remote_teardown():
    base_url = get_base_login_url()
    token, session_id = get_tensorkube_token_and_session_id()
    cloud_account_id, org_id = get_user_cloud_account_id_and_org_id(token=token, session_id=session_id)
    if not (token and session_id and cloud_account_id and org_id):
        print("Something went wrong. Please contact us to teardown successfully.")

    response = requests.post(base_url + '/tensorkube/teardown/start/',
                             headers={
                                 'Content-Type': 'application/json',
                                 'session-id': session_id,
                                 'token': token},
                             data=json.dumps({'orgId': org_id, 'cloudAccountId': cloud_account_id})
                             )
    if response.status_code == 200:
        print("Teardown started successfully.")
        return True
    else:
        print("Teardown failed. Please contact us to teardown successfully.")
        return False


