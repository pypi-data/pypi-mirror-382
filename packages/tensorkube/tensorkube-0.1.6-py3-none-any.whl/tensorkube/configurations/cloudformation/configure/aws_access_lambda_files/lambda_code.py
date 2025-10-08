import boto3
import botocore.exceptions
import os
import json
import cfnresponse
from typing import Dict
from enum import Enum


class Operation(Enum):
    UPDATE_BUILDKIT_ISRA_ROLE = 'update-buildkit-isra-role'
    EMPTY_S3_BUCKET = 'empty-s3-bucket'
    DELETE_KARPENTER_NODE_ROLE_AND_INSTANCE_PROFILE = 'delete-karpenter-node-role-and-instance-profile'
    DELETE_ECR_REPO_IMAGES = 'delete-ecr-repo-images'
    TEARDOWN_ALL_VOLUMES = 'teardown-all-volumes'


def get_aws_caller_identity():
    return boto3.client('sts').get_caller_identity()

def get_cluster_info(cluster_name: str):
    eks = boto3.client('eks')
    cluster = eks.describe_cluster(name=cluster_name)['cluster']
    return {
        'endpoint': cluster['endpoint'],
        'ca': cluster['certificateAuthority']['data']
    }


def empty_s3_bucket(bucket_name: str):
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    objects_deleted = 0
    for page in paginator.paginate(Bucket=bucket_name):
        if 'Contents' in page:
            for obj in page['Contents']:
                s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
                objects_deleted += 1
    print(f"Deleted {objects_deleted} objects from bucket {bucket_name}")
    return True


def update_buildkit_isra_role_trust_policy(cluster_name: str, oidc_provider_url: str, aws_account_id: str,
                                           service_account_name: str, namespace: str):
    iam = boto3.client('iam')
    role_name = f"{cluster_name}-buildkit-ecr-role"
    response = iam.get_role(RoleName=role_name)

    oidc_issuer = oidc_provider_url.split('//')[1]

    current_trust_policy = response['Role']['AssumeRolePolicyDocument']
    current_sub_values = current_trust_policy['Statement'][0]['Condition']['StringEquals'].get(
        "{}:sub".format(oidc_issuer), None)
    if isinstance(current_sub_values, str):
        current_sub_values = [current_sub_values]
    new_service_account = "system:serviceaccount:{}:{}".format(namespace, service_account_name)
    if new_service_account not in current_sub_values:
        current_sub_values.append(new_service_account)
        trust_policy = current_trust_policy
        trust_policy['Statement'][0]['Condition']['StringEquals']["{}:sub".format(oidc_issuer)] = current_sub_values

        # Update the trust policy with the new service account
        iam.update_assume_role_policy(RoleName=role_name, PolicyDocument=json.dumps(trust_policy))
        print(f"IAM role {role_name} trust policy updated successfully.")
    else:
        print(f"Service account {new_service_account} already exists in the IAM role trust policy.")
    return True


def delete_role_and_attached_policies(iam, role_name, cluster_name):
    # List all attached policies
    attached_policies = iam.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']

    # Detach each policy
    for policy in attached_policies:
        iam.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
        if cluster_name in policy['PolicyName']:
            # Delete the policy
            iam.delete_policy(PolicyArn=policy['PolicyArn'])

    # Delete the role
    iam.delete_role(RoleName=role_name)

def delete_karpenter_node_role_and_instance_profile(cluster_name: str):
    iam = boto3.client('iam')
    role_name = f'KarpenterNodeRole-{cluster_name}'

    # List all instance profiles
    instance_profiles = iam.list_instance_profiles()['InstanceProfiles']

    # For each instance profile
    for profile in instance_profiles:
        # Check if the role is associated with the instance profile
        for role in profile['Roles']:
            if role['RoleName'] == role_name:
                # Remove the role from the instance profile
                iam.remove_role_from_instance_profile(InstanceProfileName=profile['InstanceProfileName'],
                    RoleName=role_name)

                # Delete the instance profile
                iam.delete_instance_profile(InstanceProfileName=profile['InstanceProfileName'])

    # Delete the role
    delete_role_and_attached_policies(iam, role_name, cluster_name)
    return True


def delete_ecr_repo_images(repository_name: str):
    ecr = boto3.client('ecr')
    try:
        ecr.describe_repositories(repositoryNames=[repository_name])
    except ecr.exceptions.RepositoryNotFoundException:
        print(f"Repository {repository_name} does not exist.")
        return True

    print(f"Fetching images from ECR for repository: {repository_name}...")
    images = ecr.list_images(repositoryName=repository_name)['imageIds']
    if images:
        print(f"{len(images)} Images found. Deleting images...")
        ecr.batch_delete_image(repositoryName=repository_name, imageIds=images)
    else:
        print("No images found in the repository.")
    return True


def delete_cloudformation_stack(stack_name: str, wait: bool = False):
    cloudformation_client = boto3.client('cloudformation')
    try:
        cloudformation_client.describe_stacks(StackName=stack_name)
    except botocore.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print(f'Stack {stack_name} does not exist.')
            return True
        else:
            raise

    print(f"Deleting stack: {stack_name}")
    response = cloudformation_client.delete_stack(StackName=stack_name)
    if wait:
        waiter = cloudformation_client.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stack_name, WaiterConfig={'MaxAttempts': 30})
    return response


def delete_all_cluster_efs_volumes(cluster_name: str) -> bool:
    efs_client = boto3.client('efs')
    response = efs_client.describe_file_systems()
    file_systems = response['FileSystems']
    deleted_stacks = []
    try:
        for fs in file_systems:
            tags = efs_client.describe_tags(FileSystemId=fs['FileSystemId'])['Tags']
            created_by = next((tag['Value'] for tag in tags if tag['Key'] == 'CreatedBy'), None)
            efs_cluster_name = next((tag['Value'] for tag in tags if tag['Key'] == 'ClusterName'), None)
            if created_by != 'Tensorfuse' or efs_cluster_name != cluster_name:
                continue

            name = next((tag['Value'] for tag in tags if tag['Key'] == 'Name'), None)

            efs_vol_stack_name = f"{cluster_name}-efs-volume-{name}"
            print(f"Deleting volume: {name}")
            delete_cloudformation_stack(efs_vol_stack_name, wait=False)
            deleted_stacks.append(efs_vol_stack_name)

        cloudformation_client = boto3.client('cloudformation')
        waiter = cloudformation_client.get_waiter('stack_delete_complete')
        for stack in deleted_stacks:
            print(f"Waiting for stack '{stack}' to delete...")
            waiter.wait(StackName=stack, WaiterConfig={'MaxAttempts': 30})
            print("Stack deleted.")
    except Exception as e:
        print(f"Error deleting EFS volumes: {str(e)}")
        return False

    return True


def delete_all_volumes(cluster_name: str):
    print("Deleting EFS Volumes...")
    delete_all_cluster_efs_volumes(cluster_name)
    print("Deleting EFS Volume Support...")
    delete_cloudformation_stack(f"{cluster_name}-volume-support-efs", wait=True)
    return True


def perform_create_operation(operation: str, parameters: Dict) -> bool:
    if operation == Operation.UPDATE_BUILDKIT_ISRA_ROLE.value:
        service_account_name = parameters.get('ServiceAccountName')
        namespace = parameters.get('Namespace')
        cluster_name = parameters.get('ClusterName')
        oidc_provider_url = parameters.get('OIDCProviderUrl')
        aws_account_id = parameters.get('AWSAccountId')
        if not (service_account_name and namespace and cluster_name and oidc_provider_url and aws_account_id):
            raise Exception("RoleArn, ServiceAccountName and Namespace are required parameters")
        update_buildkit_isra_role_trust_policy(cluster_name, oidc_provider_url, aws_account_id, service_account_name, namespace)
        return True
    elif operation in [Operation.EMPTY_S3_BUCKET.value, Operation.DELETE_KARPENTER_NODE_ROLE_AND_INSTANCE_PROFILE.value,
                       Operation.DELETE_ECR_REPO_IMAGES.value, Operation.TEARDOWN_ALL_VOLUMES.value]:
        return True
    else:
        return False


def perform_delete_operation(operation: str, parameters: Dict) -> bool:
    if operation == Operation.EMPTY_S3_BUCKET.value:
        bucket_name = parameters.get('BucketName')
        if not bucket_name:
            raise Exception("BucketName is a required parameter")
        empty_s3_bucket(bucket_name)
        return True
    elif operation == Operation.DELETE_KARPENTER_NODE_ROLE_AND_INSTANCE_PROFILE.value:
        cluster_name = parameters.get('ClusterName')
        if not cluster_name:
            raise Exception("ClusterName is a required parameter")
        delete_karpenter_node_role_and_instance_profile(cluster_name)
        return True
    elif operation == Operation.DELETE_ECR_REPO_IMAGES.value:
        repository_name = parameters.get('RepositoryName')
        if not repository_name:
            raise Exception("RepositoryName is a required parameter")
        delete_ecr_repo_images(repository_name)
        return True
    elif operation == Operation.TEARDOWN_ALL_VOLUMES.value:
        cluster_name = parameters.get('ClusterName')
        if not cluster_name:
            raise Exception("ClusterName is a required parameter")
        return delete_all_volumes(cluster_name)
    elif operation in [Operation.UPDATE_BUILDKIT_ISRA_ROLE.value]:
        return True
    else:
        return False

def handler(event, context):
    command = event['ResourceProperties'].get('Operation')
    parameters = event['ResourceProperties'].get('Parameters')

    os.environ['XDG_CONFIG_HOME'] = '/tmp/.config'
    os.environ['XDG_CACHE_HOME'] = '/tmp/.cache'

    if event['RequestType'] == 'Create':
        try:
            success = perform_create_operation(command, parameters)

            if success:
                cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Event': 'Create', 'Reason': 'Operation successful'})
            else:
                cfnresponse.send(event, context, cfnresponse.FAILED, {'Event': 'Create', 'Reason': 'Invalid operation or parameters'})
        except Exception as e:
            cfnresponse.send(event, context, cfnresponse.FAILED, {'Event': 'Create', 'Reason': str(e)})
    elif event['RequestType'] == 'Update':
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Event': 'Update', 'Reason': 'No action needed'})
    elif event['RequestType'] == 'Delete':
        try:
            success = perform_delete_operation(command, parameters)

            if success:
                cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Event': 'Delete', 'Reason': 'Operation successful'})
            else:
                cfnresponse.send(event, context, cfnresponse.FAILED, {'Event': 'Delete', 'Reason': 'Invalid operation or parameters'})
        except Exception as e:
            cfnresponse.send(event, context, cfnresponse.FAILED, {'Event': 'Delete', 'Reason': str(e)})
    else:
        cfnresponse.send(event, context, cfnresponse.FAILED, {'Reason': 'Invalid request type'})
