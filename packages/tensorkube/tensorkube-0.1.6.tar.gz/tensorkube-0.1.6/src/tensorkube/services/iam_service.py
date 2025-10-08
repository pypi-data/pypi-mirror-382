import json
import boto3
import click

from botocore.exceptions import ClientError
from pkg_resources import resource_filename
from typing import Dict

from tensorkube.constants import get_cluster_name, CliColors
from tensorkube.services.aws_service import get_aws_account_id, get_iam_client, get_sts_client, get_session_region


def create_iam_policy(policy_name: str, policy_document: Dict):
    iam = get_iam_client()
    sts = get_sts_client()
    try:
        # Check if the IAM policy already exists
        account_id = sts.get_caller_identity()['Account']
        policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
        response = iam.get_policy(PolicyArn=policy_arn)
        print(f"IAM policy {policy_name} already exists. Skipping creation.")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"IAM policy {policy_name} does not exist. Proceeding with creation.")
            response = iam.create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy_document), )
            print(f"IAM policy {policy_name} created successfully.")
            return response
        else:
            print(f"An error occurred: {e}")
            raise e


def create_mountpoint_iam_policy(policy_name, bucket_name):
    policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/mountpoint_policy.json')
    with open(policy_file_path, 'r') as f:
        policy = json.load(f)
    for statement in policy['Statement']:
        statement['Resource'] = [r.replace('USER_BUCKET', bucket_name) for r in statement['Resource']]

    return create_iam_policy(policy_name, policy)


def create_sqs_access_policy(policy_name):
    policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/sqs_access_policy.json')
    region = get_session_region()
    with open(policy_file_path, 'r') as f:
        policy = json.load(f)
    for statement in policy['Statement']:
        statement['Resource'] = f"arn:aws:sqs:{region}:{get_aws_account_id()}:{get_cluster_name()}-*"
    return create_iam_policy(policy_name, policy)

def create_dynamo_access_policy(policy_name):
    policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/dynamo_access_policy.json')
    region = get_session_region()
    with open(policy_file_path, 'r') as f:
        policy = json.load(f)
    for statement in policy['Statement']:
        resource = statement['Resource']
        resource = resource.replace('REGION', region)
        resource = resource.replace('ACCOUNT_NO', get_aws_account_id())
        resource = resource.replace('TABLE_NAME', f"{get_cluster_name()}-*")
        statement['Resource'] = resource
    return create_iam_policy(policy_name, policy)



def create_iam_role_with_service_account_cluster_access(account_no: str, oidc_issuer_url: str, role_name: str,
                                                        service_account_name: str, namespace: str):
    oidc_issuer = oidc_issuer_url[8:]
    trust_policy_file_path = resource_filename('tensorkube',
                                               'configurations/aws_configs/iam_role_cluster_access_trust_policy.json')
    with open(trust_policy_file_path, 'r') as f:
        trust_policy = json.load(f)
    trust_policy['Statement'][0]['Principal']['Federated'] = 'arn:aws:iam::{}:oidc-provider/{}'.format(account_no,
                                                                                                       oidc_issuer)
    trust_policy['Statement'][0]['Condition']['StringEquals'] = {
        "{}:sub".format(oidc_issuer): "system:serviceaccount:{}:{}".format(namespace, service_account_name),
        "{}:aud".format(oidc_issuer): "sts.amazonaws.com"}

    iam = get_iam_client()

    try:
        # Check if the IAM role already exists
        response = iam.get_role(RoleName=role_name)
        print(f"IAM role {role_name} already exists. Skipping creation.")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"IAM role {role_name} does not exist. Proceeding with creation.")
            response = iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy), )
            print(f"IAM role {role_name} created successfully.")
            return response
        else:
            print(f"An error occurred: {e}")
            raise e



def create_or_update_iam_role_with_service_account_cluster_access(account_no: str, oidc_issuer_url: str, role_name: str,
                                                        service_account_name: str, namespace: str):
    oidc_issuer = oidc_issuer_url[8:]
    trust_policy_file_path = resource_filename('tensorkube',
                                               'configurations/aws_configs/iam_role_cluster_access_trust_policy.json')
    with open(trust_policy_file_path, 'r') as f:
        trust_policy = json.load(f)
    trust_policy['Statement'][0]['Principal']['Federated'] = 'arn:aws:iam::{}:oidc-provider/{}'.format(account_no,
                                                                                                       oidc_issuer)
    trust_policy['Statement'][0]['Condition']['StringEquals'] = {
        "{}:sub".format(oidc_issuer): "system:serviceaccount:{}:{}".format(namespace, service_account_name),
        "{}:aud".format(oidc_issuer): "sts.amazonaws.com"
    }

    iam = get_iam_client()

    try:
        # Check if the IAM role already exists
        response = iam.get_role(RoleName=role_name)
        print(f"IAM role {role_name} already exists. Updating trust policy.")

        # Get the current trust policy
        current_trust_policy = response['Role']['AssumeRolePolicyDocument']
        current_sub_values = current_trust_policy['Statement'][0]['Condition']['StringEquals'].get("{}:sub".format(oidc_issuer), [])
        # If it's a string, convert it into a list for consistency
        if isinstance(current_sub_values, str):
            current_sub_values = [current_sub_values]

        new_service_account = "system:serviceaccount:{}:{}".format(namespace, service_account_name)

       # If the service account is not already present in the list, append it
        if new_service_account not in current_sub_values:
            current_sub_values.append(new_service_account)
            trust_policy['Statement'][0]['Condition']['StringEquals']["{}:sub".format(oidc_issuer)] = current_sub_values

            # Update the trust policy with the new service account
            iam.update_assume_role_policy(RoleName=role_name, PolicyDocument=json.dumps(trust_policy))
            print(f"IAM role {role_name} trust policy updated successfully.")
        else:
            print(f"Service account {service_account_name} is already included in the trust policy. No update needed.")
        return response

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"IAM role {role_name} does not exist. Proceeding with creation.")
            response = iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy), )
            print(f"IAM role {role_name} created successfully.")
            return response
        else:
            print(f"An error occurred: {e}")
            raise e


def create_s3_csi_driver_role(account_no: str, role_name: str, oidc_issuer_url: str, namespace: str,
                              service_account_name: str):
    create_iam_role_with_service_account_cluster_access(account_no, oidc_issuer_url, role_name, service_account_name,
                                                        namespace)


def create_sqs_access_role(account_no: str, oidc_issuer_url: str, role_name: str, namespace: str,
                           service_account_name: str):
    return create_iam_role_with_service_account_cluster_access(account_no, oidc_issuer_url, role_name, service_account_name,
                                                        namespace)


def attach_role_policy(account_no, policy_name, role_name):
    client = get_iam_client()
    response = client.attach_role_policy(PolicyArn='arn:aws:iam::{}:policy/{}'.format(account_no, policy_name),
                                         RoleName=role_name, )
    return response


def detach_role_policy(account_no, role_name, policy_name):
    client = get_iam_client()
    response = client.detach_role_policy(PolicyArn='arn:aws:iam::{}:policy/{}'.format(account_no, policy_name),
                                         RoleName=role_name, )
    return response


def delete_role(role_name):
    client = get_iam_client()
    response = client.delete_role(RoleName=role_name)
    return response


def delete_policy(account_no, policy_name):
    client = get_iam_client()
    policy_arn = f'arn:aws:iam::{account_no}:policy/{policy_name}'
    #delete all policy versions
    policy = client.get_policy(PolicyArn=policy_arn)
    default_version = policy['Policy']['DefaultVersionId']
    # retrieve all policy versions
    versions = client.list_policy_versions(PolicyArn=policy_arn)
    for version in versions['Versions']:
        if version['VersionId'] != default_version:
            client.delete_policy_version(PolicyArn=policy_arn, VersionId=version['VersionId'])
    response = client.delete_policy(PolicyArn=policy_arn)
    return response


def update_iam_policy(account_no, policy_name, policy_document):
    client = get_iam_client()
    response = client.create_policy_version(PolicyArn='arn:aws:iam::{}:policy/{}'.format(account_no, policy_name),
                                           PolicyDocument=json.dumps(policy_document), SetAsDefault=True)
    return response


def delete_iam_role(role_name):
    iam_client = get_iam_client()
    attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']

    # Detach policies
    for policy in attached_policies:
        iam_client.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
        print(f"Detached policy {policy['PolicyArn']} from role {role_name}")

    # Delete the role
    iam_client.delete_role(RoleName=role_name)
    print(f"IAM Role {role_name} deleted")


def get_role_name_for_prefix(prefix: str):
    iam = get_iam_client()
    roles = []
    response = iam.list_roles()
    
    # Collect all roles, handling pagination
    while True:
        roles.extend(response['Roles'])
        if response.get('IsTruncated'):  # If there are more roles
            response = iam.list_roles(Marker=response['Marker'])
        else:
            break
    
    for role in roles:
        if role['RoleName'].startswith(prefix):
            return role['RoleName']
    return None

def create_iam_user(user_name):
    iam = get_iam_client()
    try:
        response = iam.create_user(UserName=user_name)
        print(f"IAM User '{user_name}' created successfully.")
        return response['User']
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"IAM User '{user_name}' already exists.")
        return iam.get_user(UserName=user_name)['User']

def create_eks_access_policy(policy_name):
    policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/eks_access_policy.json')
    region = get_session_region()
    with open(policy_file_path, 'r') as f:
        policy = json.load(f)
    statements= []
    for statement in policy['Statement']:
        resource = statement['Resource'] 
        resource = resource.replace('CLUSTER_NAME', get_cluster_name())
        resource =resource.replace('REGION', region)
        resource = resource.replace('ACCOUNT_NO', get_aws_account_id())
        statement['Resource'] = resource
        statements.append(statement)
    policy['Statement'] = statements
    return create_iam_policy(policy_name, policy)


def create_user_sqs_access_policy(policy_name):
    policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/user_sqs_access_policy.json')
    region = get_session_region()
    with open(policy_file_path, 'r') as f:
        policy = json.load(f)
    for statement in policy['Statement']:
        statement['Resource'] = f"arn:aws:sqs:{region}:{get_aws_account_id()}:{get_cluster_name()}-*"
    return create_iam_policy(policy_name, policy)

def create_user_s3_access_policy(policy_name):
    policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/user_s3_access_policy.json')
    with open(policy_file_path, 'r') as f:
        policy = json.load(f)
    return create_iam_policy(policy_name, policy)

def create_user_dynamo_access_policy(policy_name):
    policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/user_dynamo_access_policy.json')
    region = get_session_region()
    with open(policy_file_path, 'r') as f:
        policy = json.load(f)
    for statement in policy['Statement']:
        statement['Resource'] = f"arn:aws:dynamodb:{region}:{get_aws_account_id()}:table/{get_cluster_name()}-*"
    return create_iam_policy(policy_name, policy)



def attach_policy_to_user(policy_arn, user_name):
    iam = get_iam_client()
    iam.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)
    print(f"Policy '{policy_arn}' attached to user '{user_name}'.")


def create_access_key(user_name):
    iam = get_iam_client()
    response = iam.create_access_key(UserName=user_name)
    access_key = response['AccessKey']
    return access_key['AccessKeyId'], access_key['SecretAccessKey']


def get_policy_source_arn():
    sts = boto3.client('sts')
    caller_arn = sts.get_caller_identity()['Arn']
    if caller_arn.endswith(':root'):
        return caller_arn
    elif ":user/" in caller_arn:
        return caller_arn
    elif ":assumed-role/" in caller_arn:
        role_name = caller_arn.split('/')[1]
        account_id = caller_arn.split(':')[4]
        return f"arn:aws:iam::{account_id}:role/{role_name}"
    else:
        return None


def has_simulate_principal_policy_permissions(policy_source_arn: str) -> bool:
    iam_client = boto3.client('iam')
    try:
        test_action = ['iam:SimulatePrincipalPolicy']
        test_resource = ['*']
        iam_client.simulate_principal_policy(
            PolicySourceArn=policy_source_arn,
            ActionNames=test_action,
            ResourceArns=test_resource
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            click.echo(click.style("You do NOT have permissions to call 'iam:SimulatePrincipalPolicy' on Resource '*'.", fg=CliColors.ERROR.value))
            click.echo(click.style("Tensorkube uses the 'iam:SimulatePrincipalPolicy' to check for all other permissions required for running the configure command. You can refer to our docs for the full list of permissions we check for, here: https://tensorfuse.io/docs/reference/permissions/configure_permissions", fg=CliColors.WARNING.value))
            click.echo(click.style("Please request the necessary IAM permissions before running this check.", fg=CliColors.ERROR.value))
            return False
        else:
            raise


def has_configure_permissions() -> bool:
    click.echo("Checking if you have the necessary AWS permissions to run the configure command...")

    policy_source_arn = get_policy_source_arn()
    if not policy_source_arn:
        raise Exception("Could not determine the policy source ARN.")

    elif  policy_source_arn.endswith(':root'):
        click.echo(click.style("You are running this as the root user.", fg=CliColors.WARNING.value))
        click.echo(click.style("Skipping 'SimulatePrincipalPolicy' check for root ARN as it is not possible to run this check for the root user.", fg=CliColors.WARNING.value))
        click.echo(click.style("Please ensure no AWS Organizations Service Control Policies limit your root account.", fg=CliColors.WARNING.value))
        click.echo(click.style("You can refer to our docs for the full list of permissions we check for, here: https://tensorfuse.io/docs/reference/permissions/configure_permissions", fg=CliColors.WARNING.value))
        return True


    click.echo(f"Running tests for: {policy_source_arn}")
    if not has_simulate_principal_policy_permissions(policy_source_arn):
        return False


    policy_file_path = resource_filename('tensorkube', 'permissions/configure_permissions.json')
    with open(policy_file_path, 'r') as f:
        policy_doc = json.load(f)

    statements = policy_doc.get("Statement", [])
    if not isinstance(statements, list):
        # Some policies have Statement as dict if there's only one.
        statements = [statements]

    iam_client = boto3.client('iam')
    account_no = get_aws_account_id()
    all_allowed = True
    for idx, statement in enumerate(statements):
        actions = statement.get("Action", [])
        resources = statement.get("Resource", [])

        if isinstance(actions, str):
            actions = [actions]
        if isinstance(resources, str):
            resources = [resources]
        resources = [resource.replace('<ACCOUNT_NO>', account_no) for resource in resources]

        try:
            response = iam_client.simulate_principal_policy(
                PolicySourceArn=policy_source_arn,
                ActionNames=actions,
                ResourceArns=resources
            )
        except ClientError as e:
            print(f"Error simulating statement: {e}")
            continue

        eval_results = response.get('EvaluationResults', [])
        for result in eval_results:
            action_name = result.get('EvalActionName')
            resource_name = result.get('EvalResourceName')
            decision = result.get('EvalDecision')
            if decision != 'allowed':
                click.echo(click.style(f"Permissions Missing. Action: {action_name}, Resource: {resource_name} => Decision: {decision}", fg=CliColors.ERROR.value))
                all_allowed = False

    return all_allowed
