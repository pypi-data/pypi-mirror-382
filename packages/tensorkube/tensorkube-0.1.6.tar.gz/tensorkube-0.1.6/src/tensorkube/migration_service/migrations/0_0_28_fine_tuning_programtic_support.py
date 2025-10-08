from tensorkube.services.job_queue_service import create_cloud_resources_for_queued_job_support
from tensorkube.services.aws_service import get_credentials
from tensorkube.services.s3_service import create_s3_bucket, get_bucket_name
from tensorkube.services.k8s_service import create_aws_secret
from tensorkube.constants import get_cluster_name
from tensorkube.services.iam_service import attach_role_policy, get_aws_account_id
import click

def apply(test: bool = False):
    try:
        bucket_name = get_bucket_name(env_name='keda', type='train')
        create_s3_bucket(bucket_name)
        cluster_name = get_cluster_name()
        role_name = f"{cluster_name}-sqs-access-role"
        dyanmo_policy_name = f"{cluster_name}-dynamo-access-policy"
        attach_role_policy(get_aws_account_id(), dyanmo_policy_name, role_name)
        create_aws_secret(get_credentials(),"keda")
        click.echo("Successfully Created Cloud Resources for Queued Job Support")
    except Exception as e:
        raise e