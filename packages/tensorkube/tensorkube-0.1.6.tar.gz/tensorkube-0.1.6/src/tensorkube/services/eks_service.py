import subprocess
import time
from typing import Optional, List
import boto3
import click
from botocore.exceptions import ClientError
from kubernetes import config, client
from kubernetes.client import ApiException

from tensorkube.configurations.configuration_urls import KNATIVE_CRD_URL, KNATIVE_CORE_URL
from tensorkube.constants import get_cluster_name
from tensorkube.services.aws_service import get_eks_client, get_karpenter_version, get_karpenter_namespace, get_eks_client, get_ec2_client, get_session_region, get_session_profile_name
from tensorkube.services.k8s_service import get_tensorkube_cluster_context_name


def get_current_clusters():
    """Get all the clusters in the current AWS account."""
    eks_client = get_eks_client()
    response = eks_client.list_clusters()
    if response.get("clusters"):
        return response.get("clusters")
    return []


def get_pods_using_namespace(namespace, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    pods = v1.list_namespaced_pod(namespace=namespace)
    return pods


def describe_cluster(cluster_name):
    eks_client = get_eks_client()
    response = eks_client.describe_cluster(name=cluster_name)
    return response


def get_eks_cluster_vpc_config(cluster_name):
    eks_client = get_eks_client()
    response = eks_client.describe_cluster(name=cluster_name)
    vpc_config = response['cluster']['resourcesVpcConfig']
    return vpc_config


def get_vpc_cidr(vpc_id):
    ec2_client = get_ec2_client()
    response = ec2_client.describe_vpcs(VpcIds=[vpc_id])
    cidr_range = response['Vpcs'][0]['CidrBlock']
    print(f"VPC CIDR Range: {cidr_range}")
    return cidr_range


def get_security_group_id_by_name(group_name):
    ec2_client = get_ec2_client()
    response = ec2_client.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [group_name]}])
    security_groups = response.get('SecurityGroups', [])
    if not security_groups:
        print(f"No security group found with name {group_name}")
        return None
    return security_groups[0]['GroupId']


def install_karpenter():
    # Install/upgrade karpenter
    install_command = ["helm", "upgrade", "--install", "karpenter", "oci://public.ecr.aws/karpenter/karpenter",
                       "--version", get_karpenter_version(), "--namespace", get_karpenter_namespace(),
                       "--create-namespace", "--set", f"settings.clusterName={get_cluster_name()}", "--set",
                       f"settings.interruptionQueue={get_cluster_name()}", "--set",
                       "controller.resources.requests.cpu=1", "--set", "controller.resources.requests.memory=1Gi",
                       "--set", "controller.resources.limits.cpu=1", "--set", "controller.resources.limits.memory=1Gi",
                       "--wait"]

    install_karpenter_with_command(install_command)


def install_karpenter_with_command(install_command: List[str]):
    # Logout from helm registry
    logout_command = ["helm", "registry", "logout", "public.ecr.aws"]
    try:
        subprocess.run(logout_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        pass

    try:
        subprocess.run(install_command, check=True)
    except Exception as e:
        print(f"Error while installing karpenter: {e}")
        # now try running by logging into ecr
        # TODO: check if the login command is correct. Giving error rn. maybe it is never run
        region = get_session_region()
        login_command = ["aws", "ecr-public", "get-login-password", "--region", region, "|", "helm", "registry", "login",
                         "--username", "AWS", "--password-stdin", "public.ecr.aws"]
        try:
            subprocess.run(login_command, check=True)
            subprocess.run(install_command, check=True)
        except Exception as e:
            print(f"Error while installing karpenter: {e}")
            raise e


def delete_karpenter_from_cluster():
    # helm uninstall karpenter --namespace "${KARPENTER_NAMESPACE}"
    command = ["helm", "uninstall", "karpenter", "--namespace", get_karpenter_namespace()]
    subprocess.run(command, check=True)


def install_keda(sqs_access_role_arn:str):

    helm_repo_add_command = ["helm", "repo", "add", "kedacore", "https://kedacore.github.io/charts"]
    try:
        subprocess.run(helm_repo_add_command, check=True)
    except Exception as e:
        print(f"Error while adding helm repo: {e}")
        return False

    helm_repo_update_command = ["helm", "repo", "update"]
    try:
        subprocess.run(helm_repo_update_command, check=True)
    except Exception as e:
        print(f"Error while updating helm repo: {e}")
        return False

    install_command = ["helm", "upgrade", "--install", "keda", "kedacore/keda", "--namespace", "keda", "--create-namespace",
                       "--set", "podIdentity.aws.irsa.enabled=true",
                       "--set", f"podIdentity.aws.irsa.roleArn={sqs_access_role_arn}"]

    try:
        subprocess.run(install_command, check=True)
        return True
    except Exception as e:
        print(f"Error while installing keda: {e}")
        return False


def delete_keda_from_cluster():
    # helm uninstall keda -n keda
    command = ["helm", "uninstall", "keda", "-n", "keda"]
    subprocess.run(command, check=True)


def update_eks_kubeconfig(region: Optional[str] = None, profile: Optional[str] = None):
    if not region:
        region = get_session_region()
    if not profile:
        profile = get_session_profile_name()
    
    # for IAM users, we don't need to pass the profile
    if profile == "default":
        command = ["aws", "eks", "update-kubeconfig", "--name", get_cluster_name(), "--region", region]
    else:
        command = ["aws", "eks", "update-kubeconfig", "--name", get_cluster_name(), "--region", region, "--profile", profile]
    subprocess.run(command, check=True)


def apply_nvidia_plugin(context_name: Optional[str] = None):
    # Initialize the Kubernetes client
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    apps_v1 = client.AppsV1Api(k8s_api_client)

    namespace = "kube-system"
    daemonset_name = "nvidia-device-plugin-daemonset"

    try:
        # Check if the DaemonSet already exists
        apps_v1.read_namespaced_daemon_set(name=daemonset_name, namespace=namespace)
        print(f"DaemonSet {daemonset_name} already exists in namespace {namespace}. Skipping creation.")
    except ApiException as e:
        if e.status == 404:
            print(f"DaemonSet {daemonset_name} not found in namespace {namespace}. Proceeding with creation.")
            # Apply the NVIDIA device plugin DaemonSet using kubectl
            command = ["kubectl", "--context", f"{context_name}", "create", "-f",
                       "https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.9.0/nvidia-device-plugin.yml"]
            subprocess.run(command, check=True)
            print("NVIDIA device plugin applied successfully.")
        else:
            print(f"An error occurred: {e}")
            raise e


def apply_yaml_from_url(url, error_context, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    command = ["kubectl", "--context", f"{context_name}", "apply", "-f", url]
    subprocess.run(command, check=True)
    click.echo(f"Successfully {error_context}.")


def delete_resources_from_url(url, error_context, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    command = ["kubectl", "--context", f"{context_name}", "delete", "-f", url]
    try:
        subprocess.run(command, check=True)
    except Exception as e:
        print(f"Error while {error_context}: {e}")


def apply_knative_crds():
    apply_yaml_from_url(KNATIVE_CRD_URL, "installing Knative CRDs")


def delete_knative_crds():
    delete_resources_from_url(KNATIVE_CRD_URL, "deleting Knative CRDs")


def apply_knative_core():
    apply_yaml_from_url(KNATIVE_CORE_URL, "installing Knative core")


def delete_knative_core():
    delete_resources_from_url(KNATIVE_CORE_URL, "deleting Knative core")


def get_cluster_oidc_issuer_url(cluster_name):
    client = get_eks_client()
    response = client.describe_cluster(name=cluster_name)
    return response['cluster']['identity']['oidc']['issuer']


def create_eks_addon(cluster_name, addon_name, account_no, mountpoint_driver_role_name):
    client = get_eks_client()
    try:
        # Check if the addon already exists
        client.describe_addon(clusterName=cluster_name, addonName=addon_name)
        click.echo(f"EKS addon {addon_name} already exists in cluster {cluster_name}. Skipping creation.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            click.echo(f"EKS addon {addon_name} does not exist in cluster {cluster_name}. Proceeding with creation.")
            response = client.create_addon(addonName=addon_name, clusterName=cluster_name,
                serviceAccountRoleArn=f'arn:aws:iam::{account_no}:role/{mountpoint_driver_role_name}', )
            click.echo(f"EKS addon {addon_name} created successfully.")
            return response
        else:
            print(f"An error occurred: {e}")
            raise e


def delete_eks_addon(cluster_name: str, addon_name:str):
    client = get_eks_client()
    try:
        # Attempt to delete the addon
        client.delete_addon(clusterName=cluster_name, addonName=addon_name)
        click.echo(f"Deletion of EKS addon {addon_name} initiated.")

        # Poll for deletion status
        max_attempts = 30
        attempts = 0
        sleep_time = 10  # seconds
        while attempts < max_attempts:
            try:
                client.describe_addon(clusterName=cluster_name, addonName=addon_name)
                time.sleep(sleep_time)
                attempts += 1
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    click.echo(f"EKS addon {addon_name} deleted successfully.")
                    break
                else:
                    click.echo(f"An error occurred while checking deletion status: {e}")
                    raise e
        else:
            click.echo(f"Timeout reached while waiting for the deletion of EKS addon {addon_name}.")
    except ClientError as e:
        click.echo(f"An error occurred while deleting EKS addon {addon_name}: {e}")
        raise e


def get_nodegroup_status(cluster_name, nodegroup_name):
    # Create an EKS client
    eks_client = get_eks_client()

    # Describe the nodegroup
    response = eks_client.describe_nodegroup(clusterName=cluster_name, nodegroupName=nodegroup_name)

    # Extract the status
    status = response['nodegroup']['status']

    return status

# TODO: send region for IAM users
def is_existing_access_entry(principal_arn: str):
    eks_client = get_eks_client()
    cluster_name = get_cluster_name()
    response = eks_client.list_access_entries(clusterName=cluster_name)
    for entry in response.get('accessEntries', []):
        if entry == principal_arn:
            return True
    return False


def give_eks_cluster_access(principal_arn: str):
    eks_client = get_eks_client()
    cluster_name = get_cluster_name()
    policy_arn = 'arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy'

    access_entry_exists = is_existing_access_entry(principal_arn)

    if not access_entry_exists:
        try:
            create_access_entry_response = eks_client.create_access_entry(
                clusterName=cluster_name,
                principalArn=principal_arn,
            )
            print("Access entry created successfully")
        except Exception as e:
            print("Error creating access entry:", e)
    else:
        print("Access entry already exists. Skipping creation.")

    access_entry_exists = is_existing_access_entry(principal_arn)
    if not access_entry_exists:
        print("Access entry creation failed.")
        return

    try:
        associate_access_policy_response = eks_client.associate_access_policy(
            clusterName=cluster_name,
            principalArn=principal_arn,
            accessScope={'type': 'cluster'},
            policyArn=policy_arn
        )
        print("Access policy associated successfully")
    except Exception as e:
        print("Error associating access policy:", e)


def upgrade_nodegroup_ami_version(cluster_name: str, nodegroup_name: str, version: Optional[str] = None):
    eks_client = get_eks_client()
    try:
        if version:
            response = eks_client.update_nodegroup_version(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                releaseVersion=version,
                force=True
            )
        else:
            response = eks_client.update_nodegroup_version(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name,
                force=True
            )
        print(f"Upgrade initiated for nodegroup {nodegroup_name} in cluster {cluster_name}.")
        return response
    except Exception as e:
        print(f"Error upgrading nodegroup {nodegroup_name} in cluster {cluster_name}: {e}")
        raise e

def scale_nodegroup_replicas(cluster_name: str, nodegroup_name: str, scale: int):
    eks_client = get_eks_client()

    try:
        response = eks_client.update_nodegroup_config(
            clusterName=cluster_name,
            nodegroupName=nodegroup_name,
            scalingConfig={
                'desiredSize': scale
            }
        )
        print(f"Scaling initiated for nodegroup {nodegroup_name} in cluster {cluster_name} to {scale} nodes.")
        return response
    except Exception as e:
        print(f"Error scaling nodegroup {nodegroup_name} in cluster {cluster_name}: {e}")
        raise e

def wait_for_nodegroup_active(cluster_name: str, nodegroup_name: str, timeout: int = 1800, poll_interval: int = 30):
    eks_client = get_eks_client()
    start_time = time.time()

    while True:
        try:
            response = eks_client.describe_nodegroup(clusterName=cluster_name, nodegroupName=nodegroup_name)
            status = response['nodegroup']['status']
            if status == 'ACTIVE':
                print(f"Nodegroup {nodegroup_name} is now ACTIVE.")
                return
            else:
                elapsed_time = time.time() - start_time
                if elapsed_time >= timeout:
                    raise TimeoutError(f"Timeout waiting for nodegroup {nodegroup_name} to become ACTIVE.")
                print(f"Current status of nodegroup {nodegroup_name}: {status}. Waiting...")
                time.sleep(poll_interval)
        except Exception as e:
            print(f"Error checking status of nodegroup {nodegroup_name}: {e}")
            raise e
