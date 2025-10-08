import json


import click
from botocore.exceptions import ClientError
from pkg_resources import resource_filename

from tensorkube.constants import get_logging_service_account_name, get_cluster_name, get_cloudwatch_role_name, \
    get_cloudwatch_namespace
from tensorkube.services.aws_service import get_aws_account_id, get_logs_client, get_eks_client, get_iam_client
from tensorkube.services.eks_service import get_cluster_oidc_issuer_url, delete_eks_addon
from tensorkube.services.iam_service import delete_iam_role


def create_logging_role(account_no: str, role_name: str, oidc_issuer_url: str, namespace: str,
                        service_account_name: str):
    oidc_issuer = oidc_issuer_url[8:]
    trust_policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/base_policy.json')
    with open(trust_policy_file_path, 'r') as f:
        trust_policy = json.load(f)
    trust_policy['Statement'][0]['Principal']['Federated'] = 'arn:aws:iam::{}:oidc-provider/{}'.format(account_no,
                                                                                                       oidc_issuer)
    trust_policy['Statement'][0]['Condition']['StringEquals'] = {
        "{}:sub".format(oidc_issuer): "system:serviceaccount:{}:{}".format(namespace, service_account_name),
        "{}:aud".format(oidc_issuer): "sts.amazonaws.com"}
    iam_client = get_iam_client()
    try:
        # Check if the IAM role already exists
        iam_client.get_role(RoleName=role_name)
        print(f"IAM role {role_name} already exists. Skipping creation.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"IAM role {role_name} does not exist. Proceeding with creation.")
            response = iam_client.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy), )
            print(f"IAM role {role_name} created successfully.")
            return response
        else:
            print(f"An error occurred: {e}")
            raise e


def create_logging_role_with_policy(cluster_name, account_no, role_name,
                                    service_account_name=get_logging_service_account_name(),
                                    namespace=get_cloudwatch_namespace()):
    oidc_issuer_url = get_cluster_oidc_issuer_url(cluster_name)
    create_logging_role(account_no, role_name, oidc_issuer_url, namespace, service_account_name)
    iam_client = get_iam_client()
    response = iam_client.attach_role_policy(PolicyArn='arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess',
                                             RoleName=role_name, )
    response = iam_client.attach_role_policy(PolicyArn='arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy',
                                             RoleName=role_name, )
    return response


def create_cloudwatch_addon():
    # Execute the shell commands
    eks_client = get_eks_client()
    addon_name = 'amazon-cloudwatch-observability'
    cluster_name = get_cluster_name()
    service_account_role_arn = f'arn:aws:iam::{get_aws_account_id()}:role/{get_cloudwatch_role_name()}'
    try:
        # Check if the EFS addon already exists
        eks_client.describe_addon(clusterName=cluster_name, addonName=addon_name)
        click.echo(f"Addon {addon_name} already exists in cluster {cluster_name}. Skipping creation.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            click.echo(f"Addon {addon_name} does not exist in cluster {cluster_name}. Proceeding with creation.")
            response = eks_client.create_addon(addonName=addon_name, clusterName=cluster_name,
                                               serviceAccountRoleArn=service_account_role_arn, )
            click.echo(f"Addon {addon_name} created successfully in cluster {cluster_name}.")
            return response
        else:
            click.echo(f"An error occurred: {e}")
            raise e


def delete_cloudwatch_log_groups(cluster_name: str):
    # Initialize the CloudWatch Logs client
    logs_client = get_logs_client()

    # Define the log group prefixes to identify the log groups created by the add-on
    log_group_prefixes = [f'/aws/containerinsights/{cluster_name}/application',
                          f'/aws/containerinsights/{cluster_name}/dataplane',
                          f'/aws/containerinsights/{cluster_name}/host',
                          f'/aws/containerinsights/{cluster_name}/performance']

    # List and delete log groups
    for prefix in log_group_prefixes:
        try:
            paginator = logs_client.get_paginator('describe_log_groups')
            for page in paginator.paginate(logGroupNamePrefix=prefix):
                for log_group in page['logGroups']:
                    log_group_name = log_group['logGroupName']
                    try:
                        logs_client.delete_log_group(logGroupName=log_group_name)
                        print(f"Deleted log group: {log_group_name}")
                    except ClientError as e:
                        print(f"Failed to delete log group {log_group_name}: {e}")
        except ClientError as e:
            print(f"Failed to list log groups with prefix {prefix}: {e}")


def configure_cloudwatch():
    create_logging_role_with_policy(cluster_name=get_cluster_name(), account_no=get_aws_account_id(),
                                    role_name=get_cloudwatch_role_name(),
                                    service_account_name=get_logging_service_account_name())
    create_cloudwatch_addon()


def teardown_cloudwatch():
    delete_cloudwatch_log_groups(get_cluster_name())
    delete_eks_addon(cluster_name=get_cluster_name(), addon_name='amazon-cloudwatch-observability')
    delete_iam_role(get_cloudwatch_role_name())
