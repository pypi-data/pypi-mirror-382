import click

from tensorkube.constants import get_cluster_name, get_job_sidecar_iam_role_name
from tensorkube.services.aws_service import get_aws_account_id
from tensorkube.services.dynamodb_service import get_dynamodb_access_policy_name
from tensorkube.services.eks_service import get_cluster_oidc_issuer_url
from tensorkube.services.iam_service import attach_role_policy, \
    create_or_update_iam_role_with_service_account_cluster_access
from tensorkube.services.k8s_service import patch_service_account
from tensorkube.services.s3_access_service import get_s3_access_policy_name, update_s3_policy
from tensorkube.services.sqs_service import get_sqs_access_policy_name


def apply(test: bool = False):
    try:
        s3_access_policy_name = get_s3_access_policy_name()
        update_s3_policy(policy_name=s3_access_policy_name)
        dynamodb_access_policy_name = get_dynamodb_access_policy_name()
        sqs_access_policy_name = get_sqs_access_policy_name()
        role_name = get_job_sidecar_iam_role_name()
        job_queue_sidecar_sa_name = "job-queue-sidecar-keda-sa"
        role = create_or_update_iam_role_with_service_account_cluster_access(get_aws_account_id(),
                                                                             get_cluster_oidc_issuer_url(get_cluster_name()),
                                                                             role_name, job_queue_sidecar_sa_name,
                                                                             'keda')
        role_arn = role['Role']['Arn']
        attach_role_policy(account_no=get_aws_account_id(), policy_name=s3_access_policy_name, role_name=role_name)
        attach_role_policy(account_no=get_aws_account_id(), policy_name=dynamodb_access_policy_name, role_name=role_name)
        attach_role_policy(account_no=get_aws_account_id(), policy_name=sqs_access_policy_name, role_name=role_name)
        patch_service_account(role_arn, job_queue_sidecar_sa_name, "keda")
        click.echo("Successfully migrated to ISRA for fine-tuning s3 access")


    except Exception as e:
        raise e
