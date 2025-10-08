import enum
import time
from typing import List, Dict
from typing import Tuple, Optional

import botocore.exceptions
import click
from pkg_resources import resource_filename

from tensorkube.constants import DEFAULT_CAPABILITIES, TENSORKUBE_MACRO_NAME, get_cfn_base_stack_name, TeardownType
from tensorkube.services.aws_service import get_cloudformation_client, get_ec2_client, get_iam_client, \
    get_aws_account_id
from tensorkube.constants import get_cluster_name, TENSORFUSE_STRING, CREATED_BY_TAG, CLUSTER_NAME_TAG
from tensorkube.services.iam_service import delete_policy


class CfnStackStatus(enum.Enum):
    CREATE_IN_PROGRESS = 'CREATE_IN_PROGRESS'
    CREATE_COMPLETE = 'CREATE_COMPLETE'
    CREATE_FAILED = 'CREATE_FAILED'
    ROLLBACK_IN_PROGRESS = 'ROLLBACK_IN_PROGRESS'
    ROLLBACK_COMPLETE = 'ROLLBACK_COMPLETE'
    ROLLBACK_FAILED = 'ROLLBACK_FAILED'
    UPDATE_IN_PROGRESS = 'UPDATE_IN_PROGRESS'
    UPDATE_COMPLETE = 'UPDATE_COMPLETE'
    UPDATE_FAILED = 'UPDATE_FAILED'
    DELETE_IN_PROGRESS = 'DELETE_IN_PROGRESS'
    DELETE_COMPLETE = 'DELETE_COMPLETE'
    DELETE_FAILED = 'DELETE_FAILED'
    UPDATE_ROLLBACK_IN_PROGRESS = 'UPDATE_ROLLBACK_IN_PROGRESS'
    UPDATE_ROLLBACK_COMPLETE = 'UPDATE_ROLLBACK_COMPLETE'
    UPDATE_ROLLBACK_FAILED = 'UPDATE_ROLLBACK_FAILED'
    REVIEW_IN_PROGRESS = 'REVIEW_IN_PROGRESS'


def get_stack_status_from_stack_name(stack_name: str) -> CfnStackStatus:
    """
    Get the status of a CloudFormation stack.

    Args:
        stack_name (str): Name of the CloudFormation stack

    Returns:
        CfnStackStatus: Enum representing the stack status

    Raises:
        ClientError: If there's an AWS API error other than stack not existing
    """
    cloudformation_client = get_cloudformation_client()
    try:
        response = cloudformation_client.describe_stacks(StackName=stack_name)
        status = response['Stacks'][0]['StackStatus']
        return CfnStackStatus(status)
    except Exception as e:
        if 'does not exist' in str(e):
            return None
        raise


def create_cloudformation_stack(template_file_path: str, stack_name: str, parameters: Optional[List[Dict]] = None,
                                capabilities: List[str] = DEFAULT_CAPABILITIES)-> Tuple[bool, bool]:
    cloudformation_client = get_cloudformation_client()
    file_name = resource_filename('tensorkube', template_file_path)

    try:
        stack = cloudformation_client.describe_stacks(StackName=stack_name)
        if stack['Stacks'][0]['StackStatus'] == 'CREATE_COMPLETE':
            click.echo(f"Stack {stack_name} already exists. Skipping stack creation")
            creation_queued = False
            in_created_state = True
            return creation_queued, in_created_state
        elif stack['Stacks'][0]['StackStatus'] == 'CREATE_IN_PROGRESS':
            click.echo(f"Stack {stack_name} already exists and is in creation state. Please wait for "
                       f"creation to complete.")
            creation_queued = True
            in_created_state = False
            return creation_queued, in_created_state
        elif stack['Stacks'][0]['StackStatus'] == 'ROLLBACK_COMPLETE':
            click.echo(f"Stack {stack_name} already exists but is in rollback state. Please delete the stack "
                       f"and recreate it.")
            creation_queued = False
            in_created_state = False
            return creation_queued, in_created_state
        elif stack['Stacks'][0]['StackStatus'] == 'DELETE_COMPLETE':
            # use the configurations/cloudformation/karpenter_cloudformation.yaml in the library
            with open(file_name) as file:
                template = file.read()
            response = cloudformation_client.create_stack(StackName=stack_name, TemplateBody=template, Parameters=parameters,
                                                          Capabilities=capabilities)
            creation_queued = True
            in_created_state = False
            return creation_queued, in_created_state
        else:
            click.echo(f"Stack {stack_name} already exists but not in created state. Either wait for "
                       f"creation to complete or delete stack to recreate it.")
            creation_queued = False
            in_created_state = False
            return creation_queued, in_created_state
    except botocore.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            # use the configurations/cloudformation/karpenter_cloudformation.yaml in the library
            with open(file_name) as file:
                template = file.read()
            response = cloudformation_client.create_stack(StackName=stack_name, TemplateBody=template, Parameters=parameters,
                                                          Capabilities=capabilities)
            creation_queued = True
            in_created_state = False
            return creation_queued, in_created_state
        else:
            click.echo(e)
            raise Exception('Unable to create cloudformation cluster')


def delete_role_and_attached_policies(iam, role_name):
    # List all attached policies
    attached_policies = iam.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']

    # Detach each policy
    for policy in attached_policies:
        iam.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
        if get_cluster_name() in policy['PolicyName']:
            # Delete the policy
            delete_policy(account_no=get_aws_account_id(), policy_name=policy['PolicyName'])

    # Delete the role
    iam.delete_role(RoleName=role_name)


def delete_cloudformation_stack(stack_name):
    cloudformation_client = get_cloudformation_client()

    try:
        cloudformation_client.describe_stacks(StackName=stack_name)
    except botocore.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print(f'Stack {stack_name} does not exist.')
            return
        else:
            raise
    iam = get_iam_client()

    role_name = f'KarpenterNodeRole-{get_cluster_name()}'

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
    delete_role_and_attached_policies(iam, role_name)

    response = cloudformation_client.delete_stack(StackName=stack_name)
    # Create a waiter to wait for the stack to be deleted
    waiter = cloudformation_client.get_waiter('stack_delete_complete')

    # Start streaming the stack events in a separate thread
    stream_stack_events(stack_name)

    # Wait for the stack to be deleted
    waiter.wait(StackName=stack_name, WaiterConfig={'MaxAttempts': 30})
    return response



def delete_tensorkube_base_stack():
    cloudformation_client = get_cloudformation_client()
    stack_name = get_cfn_base_stack_name()

    try:
        cloudformation_client.describe_stacks(StackName=stack_name)
    except botocore.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print(f'Stack {stack_name} does not exist.')
            return
        else:
            raise

    response = cloudformation_client.delete_stack(StackName=stack_name)
    # Create a waiter to wait for the stack to be deleted
    waiter = cloudformation_client.get_waiter('stack_delete_complete')

    # Start streaming the stack events in a separate thread
    stream_stack_events(stack_name)

    # Wait for the stack to be deleted
    waiter.wait(StackName=stack_name, WaiterConfig={'MaxAttempts': 30})
    return response


def delete_launch_templates():
    ec2_client = get_ec2_client()
    cluster_name = get_cluster_name()
    # Describe the launch templates
    response = ec2_client.describe_launch_templates(
        Filters=[{'Name': 'tag:karpenter.k8s.aws/cluster', 'Values': [cluster_name]}])
    launch_template_names = [lt['LaunchTemplateName'] for lt in response['LaunchTemplates']]

    # Delete each launch template
    for name in launch_template_names:
        ec2_client.delete_launch_template(LaunchTemplateName=name)


def stream_stack_events(stack_name):
    seen_events = set()
    cf_client = get_cloudformation_client()
    while True:
        try:
            events = cf_client.describe_stack_events(StackName=stack_name)['StackEvents']
            for event in reversed(events):
                event_id = event['EventId']
                if event_id not in seen_events:
                    seen_events.add(event_id)
                    click.echo(
                        f"{event['Timestamp']} {event['ResourceStatus']} {event['ResourceType']} {event['LogicalResourceId']} {event.get('ResourceStatusReason', '')}")
            # Check if stack creation is complete
            stack_status = cf_client.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
            if stack_status.endswith('_COMPLETE') or stack_status.endswith('_FAILED'):
                break
            time.sleep(5)
        except Exception as e:
            if stack_name in str(e) and 'does not exist' in str(e):
                break


def cloudformation():
    """Create a cloudformation stack."""
    click.echo("Creating cloudformation stack...")
    # create_cloudformation_stack()
    stack_name = get_cluster_name()
    parameters = [{"ParameterKey": "ClusterName", 'ParameterValue': get_cluster_name()}]
    creation_queued, in_created_state = create_cloudformation_stack(
        template_file_path="configurations/cloudformation/karpenter_cloudformation.yaml", stack_name=stack_name,
        parameters=parameters)
    if creation_queued:
        stream_stack_events(stack_name)
    click.echo("Cloudformation stack created.")


def deploy_generic_cloudformation_stack(stack_name: str, template_body: str, parameters: list,
                                capabilities=None,
                                should_wait: bool = True,
                                enable_termination_protection: bool = False) -> bool:
    """
    Base function to deploy any CloudFormation stack using boto3 waiters
    This method also checks if the stack already exists.
    It only creates a stack if it doesnt exist
    """
    if capabilities is None:
        capabilities = ['CAPABILITY_IAM']
    cloudformation_client = get_cloudformation_client()

    tags = [
        {'Key': CREATED_BY_TAG, 'Value': TENSORFUSE_STRING},
        {'Key': CLUSTER_NAME_TAG, 'Value': get_cluster_name()}
    ]

    try:
        # Check if stack exists
        try:
            stack = cloudformation_client.describe_stacks(StackName=stack_name)
            current_stack = stack['Stacks'][0]
            current_status = current_stack['StackStatus']
            click.echo(f'Stack status: {current_status}')

            if current_status == CfnStackStatus.CREATE_COMPLETE.value:
                click.echo(f"Stack {stack_name} already exists. Skipping stack creation.")
                return True
            elif current_status in [CfnStackStatus.CREATE_IN_PROGRESS.value,
                                    CfnStackStatus.UPDATE_IN_PROGRESS.value]:
                if should_wait:
                    waiter = cloudformation_client.get_waiter('stack_create_complete')
                    waiter.wait(StackName=stack_name)
                return True
            elif current_status in [CfnStackStatus.ROLLBACK_COMPLETE.value, CfnStackStatus.DELETE_COMPLETE.value]:
                click.echo(click.style(
                    f"Error: Stack {stack_name} has status {current_status}. Please check the CloudFormation console for details.",
                    fg='red'))
                return False
            else:
                click.echo(click.style(
                    f"Unhandled stack status {current_status}. Please take necessary actions.",
                    fg='yellow'))
                return False

        except cloudformation_client.exceptions.ClientError as e:
            if 'does not exist' in str(e):
                # Create new stack
                response = cloudformation_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=parameters,
                    Capabilities=capabilities,
                    EnableTerminationProtection=enable_termination_protection,
                    Tags=tags
                )
                click.echo(f"Stack {stack_name} creation initiated.")

                # Wait for stack creation
                if should_wait:
                    waiter = cloudformation_client.get_waiter('stack_create_complete')
                    waiter.wait(StackName=stack_name)
                time.sleep(3)
                # Get final stack details
                final_stack = cloudformation_client.describe_stacks(
                    StackName=stack_name
                )['Stacks'][0]

                return True
            raise
    except Exception as e:
        return False

def get_validation_records_from_events(stack_name: str) -> Optional[dict]:
    """Get DNS validation records from stack events during creation"""
    cloudformation_client = get_cloudformation_client()
    try:
        events = cloudformation_client.describe_stack_events(StackName=stack_name)['StackEvents']
        # check if the stack is in CREATE_IN_PROGRESS state
        stack_status = cloudformation_client.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
        if stack_status == CfnStackStatus.CREATE_COMPLETE.value:
            click.echo(
                click.style(
                    "Certificate already validated. No need to create a validation record. Only redirection record needed.","green"
                )
            )
            return {}
        for event in events:
            if (event['ResourceType'] == 'AWS::CertificateManager::Certificate' and
                    event['ResourceStatus'] == 'CREATE_IN_PROGRESS' and
                    'Content of DNS Record is:' in event.get('ResourceStatusReason', '')):

                # Extract DNS record details from ResourceStatusReason
                record_info = event['ResourceStatusReason'].split('Content of DNS Record is: ')[1]
                # Remove curly braces and split by comma
                record_parts = record_info.strip('{}').split(',')

                validation_record = {}
                for part in record_parts:
                    key, value = part.split(':', 1)
                    validation_record[key.strip()] = value.strip(' .')

                return {
                    'validation_record': {
                        'name': validation_record['Name'],
                        'value': validation_record['Value'],
                        'type': validation_record['Type']
                    }
                }
    except Exception as e:
        click.echo(click.style(f"Error getting validation records: {str(e)}", fg='red'))
        return None
    return None


def get_validation_records_with_wait(stack_name: str, timeout: int = 300, poll_interval: int = 10) -> Optional[dict]:
    """
    Wait until DNS validation records are available in CloudFormation stack events.

    :param stack_name: Name of the CloudFormation stack
    :param timeout: Maximum duration to wait for records (in seconds)
    :param poll_interval: Time to wait between checks (in seconds)
    :return: Validation records if available, None otherwise
    """
    start_time = time.time()

    while (time.time() - start_time) < timeout:
        records = get_validation_records_from_events(stack_name)
        if records is not None:
            return records
        time.sleep(poll_interval)

    click.echo(click.style("Timeout reached while waiting for DNS validation records.", fg='red'))
    return None


def is_existing_tk_macro(macro_name: str = TENSORKUBE_MACRO_NAME) -> bool:
    cloudformation_client = get_cloudformation_client()
    paginator = cloudformation_client.get_paginator('list_stack_resources')

    # Iterate through all stacks
    stacks = cloudformation_client.list_stacks(StackStatusFilter=['CREATE_COMPLETE'])['StackSummaries']
    for stack in stacks:
        stack_name = stack['StackName']
        pages = paginator.paginate(StackName=stack_name)
        for page in pages:
            for resource in page['StackResourceSummaries']:
                if (resource['ResourceType'] == 'AWS::CloudFormation::Macro'
                        and resource['PhysicalResourceId'] == macro_name):
                    print(resource)
                    print(f"Macro '{macro_name}' exists in stack '{stack_name}'.")
                    return True

    print(f"Macro '{macro_name}' does not exist.")
    return False


def determine_teardown_type():
    cloudformation_client = get_cloudformation_client()
    paginator = cloudformation_client.get_paginator('list_stacks')
    stack_status_filter = [
        'CREATE_IN_PROGRESS', 'CREATE_COMPLETE', 'ROLLBACK_IN_PROGRESS', 'ROLLBACK_COMPLETE',
        'DELETE_IN_PROGRESS', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_IN_PROGRESS',
        'UPDATE_ROLLBACK_COMPLETE'
    ]

    for page in paginator.paginate(StackStatusFilter=stack_status_filter):
        click.echo("Identifying stack type...")

        stacks = page['StackSummaries']

        for stack in stacks:
            if stack['StackName'] == get_cluster_name():
                return TeardownType.LEGACY

            if stack['StackName'] == get_cfn_base_stack_name():
                return TeardownType.CFN


    return TeardownType.UNKNOWN


def get_cfn_stack_export_values(export_names: List[str]) -> Dict[str, str]:
    cloudformation_client = get_cloudformation_client()
    paginator = cloudformation_client.get_paginator('list_exports')
    export_values = {}

    for page in paginator.paginate():
        for export in page['Exports']:
            if export['Name'] in export_names:
                export_values[export['Name']] = export['Value']

    return export_values


def delete_generic_cfn_stack(stack_name: str):
    cloudformation_client = get_cloudformation_client()
    try:
        cloudformation_client.describe_stacks(StackName=stack_name)
    except botocore.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            click.echo(f'Stack {stack_name} does not exist.')
            return
        else:
            raise

    response = cloudformation_client.delete_stack(StackName=stack_name)
    # Create a waiter to wait for the stack to be deleted
    waiter = cloudformation_client.get_waiter('stack_delete_complete')

    stream_stack_events(stack_name)

    # Wait for the stack to be deleted
    waiter.wait(StackName=stack_name, WaiterConfig={'MaxAttempts': 30})
    return response


def update_generic_cloudformation_stack(stack_name: str, template_url: str, parameters: List[Dict[str, str]],
                                        capabilities: List[str] = DEFAULT_CAPABILITIES):
    cloudformation_client = get_cloudformation_client()

    response = cloudformation_client.update_stack(StackName=stack_name, TemplateURL=template_url, Parameters=parameters,
                                                  Capabilities=capabilities)

    stream_stack_events(stack_name)
    return response


def get_stack_parameter_value(stack_name: str, parameter_key: str) -> Optional[str]:
    cloudformation_client = get_cloudformation_client()

    try:
        response = cloudformation_client.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        for param in stack.get('Parameters', []):
            if param['ParameterKey'] == parameter_key:
                return param['ParameterValue']
        print(f"Parameter '{parameter_key}' not found in stack '{stack_name}'.")
    except cloudformation_client.exceptions.ClientError as e:
        print(f"Error retrieving stack: {e}")

    return None
