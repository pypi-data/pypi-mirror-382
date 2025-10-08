from typing import Optional
import json
import click

from pkg_resources import resource_filename
from tensorkube.constants import DEFAULT_NAMESPACE
from tensorkube.services.iam_service import create_iam_role_with_service_account_cluster_access, create_iam_policy, \
    attach_role_policy, delete_iam_role, delete_policy, detach_role_policy, update_iam_policy
from tensorkube.services.eks_service import get_cluster_name, get_cluster_oidc_issuer_url
from tensorkube.services.k8s_service import create_service_account_with_role_arn
from tensorkube.services.aws_service import get_aws_account_id

def create_s3_access_to_pods(env_name: Optional[str] = None):
    cluster_name = get_cluster_name()
    oidc_issuer_url = get_cluster_oidc_issuer_url(cluster_name)
    namespace = env_name if env_name else DEFAULT_NAMESPACE
    role_name = get_s3_access_role_name(env_name=env_name)
    service_account_name = get_s3_service_account_name(env_name=env_name)

    create_iam_role_with_service_account_cluster_access(get_aws_account_id(), oidc_issuer_url, role_name, service_account_name,
                                                        namespace)
    policy_name = get_s3_access_policy_name()
    create_s3_access_policy(policy_name)
    attach_role_policy(get_aws_account_id(), policy_name=policy_name, role_name=role_name)
    role_arn = f"arn:aws:iam::{get_aws_account_id()}:role/{role_name}"
    create_service_account_with_role_arn(name=service_account_name, namespace=namespace, role_arn=role_arn)

def create_s3_access_policy(policy_name: str):
    policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/s3_access_policy.json')
    with open(policy_file_path, 'r') as f:
        policy = json.load(f)
    for statement in policy['Statement']:
        statement['Resource'] = [r.replace('BUCKET', f"{get_cluster_name()}-*/*") for r in statement['Resource']]
    return create_iam_policy(policy_name, policy)

def update_s3_policy(policy_name):
    policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/s3_access_policy.json')
    with open(policy_file_path, 'r') as f:
        policy = json.load(f)
    for statement in policy['Statement']:
        statement['Resource'] = [r.replace('BUCKET', f"{get_cluster_name()}-*") for r in statement['Resource']]
    return update_iam_policy(get_aws_account_id(), policy_name, policy)

def get_s3_access_role_name(env_name: Optional[str] = None):
    namespace = env_name if env_name else DEFAULT_NAMESPACE
    return f"{get_cluster_name()}-{namespace}-s3-bucket-access"

def get_s3_service_account_name(env_name: Optional[str] = None):
    namespace = env_name if env_name else DEFAULT_NAMESPACE
    return f"{get_cluster_name()}-{namespace}-pod-s3-bucket-access-sa"

def get_s3_access_policy_name(env_name: Optional[str] = None):
    namespace = env_name if env_name else DEFAULT_NAMESPACE
    return f"{get_cluster_name()}-{namespace}-s3-bucket-access-policy"


def delete_s3_access_to_pods(env_name: Optional[str] = None):
    role_name = get_s3_access_role_name(env_name=env_name)
    policy_name = get_s3_access_policy_name(env_name=env_name)
    try:
        detach_role_policy(get_aws_account_id(), policy_name=policy_name, role_name=role_name)
    except Exception as e:
        click.echo(f"An error occurred while detaching policy from role: {e}")
    try:
        delete_iam_role(role_name)
    except Exception as e:
        click.echo(f"An error occurred while deleting role: {e}")
    try:
        delete_policy(account_no=get_aws_account_id(), policy_name=policy_name)
    except Exception as e:
        click.echo(f"An error occurred while deleting policy: {e}")