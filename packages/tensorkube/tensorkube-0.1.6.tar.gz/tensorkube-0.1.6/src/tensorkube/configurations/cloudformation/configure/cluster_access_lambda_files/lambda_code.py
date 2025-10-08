import boto3
import os
import yaml
import cfnresponse
import subprocess
from kubernetes import client, config
from typing import Dict, List
from enum import Enum
from time import sleep, time


KUBECONFIG_FILE_PATH = '/tmp/kubeconfig'

class Operation(Enum):
    UPDATE_AUTHMAP = 'update-authmap'
    HELMFILE_SYNC = 'helmfile-sync'
    PATCH_SERVICE_ACCOUNT = 'patch-service-account'
    SYNC_CLI_VERSION_TO_CLUSTER = 'sync-cli-version-to-cluster'
    CREATE_ENV = 'create-env'
    TEARDOWN_KSVCS_SCALEDJOBS = 'teardown-ksvcs-scaledjobs'


def get_aws_caller_identity():
    return boto3.client('sts').get_caller_identity()


def get_managed_node_group_name(cluster_name: str) -> str:
    return f"{cluster_name}-tensorkube-nodegroup"


def generate_kubeconfig(cluster_name: str, region: str, aws_account_id: str):
    eks_client = boto3.client('eks', region_name=region)

    cluster_info = eks_client.describe_cluster(name=cluster_name)['cluster']

    # Extract cluster details
    endpoint = cluster_info['endpoint']
    cluster_ca_certificate = cluster_info['certificateAuthority']['data']

    # Create a kubeconfig dictionary
    kubeconfig_data = {
        "apiVersion": "v1",
        "clusters": [{
            "cluster": {
                "server": endpoint,
                "certificate-authority-data": cluster_ca_certificate
            },
            "name": f'arn:aws:eks:us-east-1:{aws_account_id}:cluster/{cluster_name}'
        }],
        "contexts": [{
            "context": {
                "cluster": f'arn:aws:eks:us-east-1:{aws_account_id}:cluster/{cluster_name}',
                "user": f'arn:aws:eks:us-east-1:{aws_account_id}:cluster/{cluster_name}'
            },
            "name": f'arn:aws:eks:us-east-1:{aws_account_id}:cluster/{cluster_name}'
        }],
        "current-context": f'arn:aws:eks:us-east-1:{aws_account_id}:cluster/{cluster_name}',
        "kind": "Config",
        "users": [{
            "name": f'arn:aws:eks:us-east-1:{aws_account_id}:cluster/{cluster_name}',
            "user": {
                "exec": {
                    "apiVersion": "client.authentication.k8s.io/v1beta1",
                    "command": "aws",
                    "args": [
                        "eks",
                        "get-token",
                        "--cluster-name", cluster_name
                    ],
                    "env": [
                        {"name": "AWS_DEFAULT_REGION", "value": region}
                    ]
                }
            }
        }]
    }
    # kubeconfig_dir = os.path.expanduser('~/.kube')
    # kubeconfig_file = os.path.join(kubeconfig_dir, 'config')
    kubeconfig_dir = os.path.expanduser('/tmp')
    kubeconfig_file = os.path.join(kubeconfig_dir, 'kubeconfig')

    # Create the directory if it does not exist
    if not os.path.exists(kubeconfig_dir):
        os.makedirs(kubeconfig_dir, exist_ok=True)

    # Load existing kubeconfig or create a new one if it doesn't exist
    if os.path.exists(kubeconfig_file):
        with open(kubeconfig_file, 'r') as f:
            existing_config = yaml.safe_load(f) or {}
    else:
        existing_config = {'apiVersion': 'v1', 'kind': 'Config', 'clusters': [], 'contexts': [], 'users': []}

    # Merge new kubeconfig entry into existing config
    # Function to update or add an entry in the list
    def update_or_add_entry(existing_list, new_entry, key):
        for i, entry in enumerate(existing_list):
            if entry[key] == new_entry[key]:
                existing_list[i] = new_entry  # Update the existing entry
                return
        existing_list.append(new_entry)  # Add as a new entry if not found

    # Merge new kubeconfig entry into existing config
    update_or_add_entry(existing_config['clusters'], kubeconfig_data['clusters'][0], 'name')
    update_or_add_entry(existing_config['contexts'], kubeconfig_data['contexts'][0], 'name')
    update_or_add_entry(existing_config['users'], kubeconfig_data['users'][0], 'name')
    existing_config['current-context'] = kubeconfig_data['current-context']

    # Write back to the default kubeconfig file
    with open(kubeconfig_file, 'w') as f:
        yaml.dump(existing_config, f)

    os.chmod(kubeconfig_file, 0o700)


def get_cluster_info(cluster_name: str):
    eks = boto3.client('eks')
    cluster = eks.describe_cluster(name=cluster_name)['cluster']
    return {
        'endpoint': cluster['endpoint'],
        'ca': cluster['certificateAuthority']['data']
    }


def add_karpenter_role_to_aws_auth_config_map(role_arn: str):
    # Load the kubeconfig
    # kubeconfig_file = os.path.expanduser('~/.kube/config')
    kubeconfig_file = os.path.expanduser(KUBECONFIG_FILE_PATH)
    config.load_kube_config(config_file=kubeconfig_file)

    # Load the existing aws-auth config map
    v1 = client.CoreV1Api()
    aws_auth_config_map = v1.read_namespaced_config_map(name='aws-auth', namespace='kube-system')

    # Extract the existing roles
    roles = yaml.safe_load(aws_auth_config_map.data['mapRoles'])

    # Add the new role
    roles.append({
        "rolearn": role_arn,
        "username": "system:node:{{EC2PrivateDNSName}}",
        "groups": ["system:bootstrappers", "system:nodes"]
    })

    # Update the aws-auth config map
    aws_auth_config_map.data['mapRoles'] = yaml.dump(roles)
    v1.patch_namespaced_config_map(name='aws-auth', namespace='kube-system', body=aws_auth_config_map)


def get_availability_zones(region: str) -> List[str]:
    ec2_client = boto3.client('ec2', region_name=region)
    azs = ec2_client.describe_availability_zones(
        Filters=[{"Name": "region-name", "Values": [region]}, {"Name": "zone-type", "Values": ["availability-zone"]}],
        AllAvailabilityZones=False,
    )["AvailabilityZones"]

    zone_names = [az["ZoneName"] for az in azs if az["State"] == "available"]
    return zone_names


def update_values_yaml(parameters: Dict):
    cluster_name = parameters.get('ClusterName')
    sqs_access_role_arn = parameters.get('SQSAccessRoleArn')
    region = parameters.get('Region')
    bucket_name = parameters.get('DefaultEnvBuildBucketName')
    buildkit_isra_role_arn = parameters.get('BuildkitISRARoleArn')
    job_queue_sidecar_role_arn = parameters.get('JobQueueSidecarIAMRoleArn')
    tk_helm_charts_repo_id = parameters.get("ImageRegistryId")
    karpenter_config_topology_zone_values = get_availability_zones(region)


    if not (cluster_name and sqs_access_role_arn and region and bucket_name and buildkit_isra_role_arn and job_queue_sidecar_role_arn):
        raise Exception("ClusterName, SQSAccessRoleArn, Region, DefaultEnvBuildBucketName, JobQueueSidecarIAMRoleArn and BuildkitISRARoleArn are required parameters")

    with open("helm-charts/values.yaml", "r") as f:
        values = yaml.safe_load(f) or {}

    values['clusterName'] = cluster_name
    values['sqsAccessRoleArn'] = sqs_access_role_arn
    values['region'] = region
    values['envName'] = "default"
    values['defaultEnvBuildBucketName'] = bucket_name
    values['buildkitISRARoleArn'] = buildkit_isra_role_arn
    values['jobQueueISRARoleArn'] = job_queue_sidecar_role_arn
    values['managedNodeGroupName'] = get_managed_node_group_name(cluster_name)
    values['tkHelmChartsRepoId'] = tk_helm_charts_repo_id
    values['karpenterConfigTopologyZoneValues'] = karpenter_config_topology_zone_values

    with open("/tmp/values.yaml", "w") as f:
        yaml.dump(values, f)


def run_helmfile_sync(parameters: Dict):
    update_values_yaml(parameters=parameters)
    subprocess.run(["helmfile", "sync", "--file", "./helm-charts/helmfile.yaml"], check=True)


def run_helmfile_destroy(parameters: Dict):
    update_values_yaml(parameters=parameters)
    tries = 0
    while tries < 3:
        try:
            subprocess.run(["helmfile", "destroy", "--file", "./helm-charts/helmfile.yaml"], check=True)
            return True
        except Exception as e:
            tries += 1
            print(f"An error occurred: {e}")
            print("Retrying in 30 seconds...")
            sleep(30)

    print("Failed to destroy helm resources after 3 attempts.")
    return False


def patch_service_account(role_arn: str, service_account_name: str, namespace: str):
    kubeconfig_file = os.path.expanduser(KUBECONFIG_FILE_PATH)
    config.load_kube_config(config_file=kubeconfig_file)

    # Load the existing service account
    v1 = client.CoreV1Api()
    service_account = v1.read_namespaced_service_account(name=service_account_name, namespace=namespace)

    # Extract the existing annotations
    annotations = service_account.metadata.annotations or {}

    # Add the new annotation
    annotations['eks.amazonaws.com/role-arn'] = role_arn

    # Update the service account
    service_account.metadata.annotations = annotations
    v1.patch_namespaced_service_account(name=service_account_name, namespace=namespace, body=service_account)


def set_current_cli_version_to_cluster(current_version: str):
    kubeconfig_file = os.path.expanduser(KUBECONFIG_FILE_PATH)
    config.load_kube_config(config_file=kubeconfig_file)

    v1 = client.CoreV1Api()
    config_map = client.V1ConfigMap(
        metadata=client.V1ObjectMeta(name="tensorkube-migration", namespace="default"),
        data={"version": current_version}
    )
    try:
        v1.replace_namespaced_config_map("tensorkube-migration", "default", config_map)
    except client.exceptions.ApiException as e:
        if e.status == 404:
            v1.create_namespaced_config_map("default", config_map)
        else:
            raise e


def create_env(env_name: str, build_bucket_name: str, buildkit_isra_role_arn: str, region: str, cluster_name: str):
    try:
        subprocess.run(["helm", "install", f"{env_name}-env", "./helm-charts/tk-env", "--set", f"envName={env_name}",
                        "--set", f"bucketName={build_bucket_name}", "--set", f"region={region}",
                        "--set", f"clusterName={cluster_name}", "--set", f"buildkitISRARoleArn={buildkit_isra_role_arn}"
                        ], check=True)
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def delete_all_ksvcs() -> bool:
    kubeconfig_file = os.path.expanduser(KUBECONFIG_FILE_PATH)
    config.load_kube_config(config_file=kubeconfig_file)

    # Create the CustomObjectsApi
    custom_api = client.CustomObjectsApi()
    core_v1_api = client.CoreV1Api()

    # Group, version, and plural for Knative Services CRD
    group = "serving.knative.dev"
    version = "v1"
    plural = "services"

    namespaces = core_v1_api.list_namespace()
    for ns in namespaces.items:
        ns_name = ns.metadata.name

        try:
            # List all Knative Services in the current namespace
            knative_services = custom_api.list_namespaced_custom_object(
                group=group,
                version=version,
                namespace=ns_name,
                plural=plural
            )

            # Delete each Knative Service found
            for svc in knative_services.get("items", []):
                svc_name = svc["metadata"]["name"]
                print(f"Deleting Knative Service '{svc_name}' in namespace '{ns_name}'...")
                custom_api.delete_namespaced_custom_object(
                    group=group,
                    version=version,
                    namespace=ns_name,
                    plural=plural,
                    name=svc_name
                )

        except client.exceptions.ApiException as e:
            print(f"Error deleting ksvc in namespace '{ns_name}': {e}")
            return False
    return True


def delete_all_scaledjobs():
    kubeconfig_file = os.path.expanduser(KUBECONFIG_FILE_PATH)
    config.load_kube_config(config_file=kubeconfig_file)

    custom_api = client.CustomObjectsApi()
    group = "keda.sh"
    version = "v1alpha1"
    plural = "scaledjobs"
    namespace = "keda"

    try:
        scaled_jobs = custom_api.list_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural
        )

        # Delete each ScaledJob found
        for sj in scaled_jobs.get("items", []):
            sj_name = sj["metadata"]["name"]
            print(f"Deleting ScaledJob '{sj_name}' in namespace '{namespace}'...")
            custom_api.delete_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                name=sj_name
            )

    except client.exceptions.ApiException as e:
       return False
    return True


def wait_for_nodes_with_label_only(cluster_name: str, timeout_seconds: int = 840,
                                   poll_interval_seconds: int = 10) -> True:
    kubeconfig_file = os.path.expanduser(KUBECONFIG_FILE_PATH)
    config.load_kube_config(config_file=kubeconfig_file)

    v1 = client.CoreV1Api()

    # Label key and value we want to keep
    label_key = "alpha.eksctl.io/nodegroup-name"
    label_value = get_managed_node_group_name(cluster_name)

    start_time = time()

    while True:
        nodes = v1.list_node().items

        remaining_unlabeled = [
            node for node in nodes
            if node.metadata.labels.get(label_key, None) != label_value
        ]

        if not remaining_unlabeled:
            print("All nodes without the desired label have been removed.")
            return True

        elapsed = time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(
                f"Timed out after {timeout_seconds} seconds waiting for all other nodes to be deleted."
            )

        print(
            f"Still waiting for {len(remaining_unlabeled)} node(s) without label "
            f"'{label_key}={label_value}' to be deleted. Retrying in {poll_interval_seconds}s..."
        )
        sleep(poll_interval_seconds)


def delete_all_ksvcs_scaledjobs(parameters: Dict) -> bool:
    #TODO?: delete all build jobs?
    cluster_name = parameters.get('ClusterName')
    if not cluster_name:
        raise Exception("ClusterName is a required parameter")

    deleted_ksvcs = delete_all_ksvcs()
    if not deleted_ksvcs:
        return False

    deleted_scaledjobs = delete_all_scaledjobs()
    if not deleted_scaledjobs:
        return False

    try:
        wait_for_nodes_with_label_only(cluster_name=cluster_name)
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    return True


def perform_create_operation(operation: str, parameters: Dict) -> bool:
    if operation == Operation.UPDATE_AUTHMAP.value:
        karpenter_role_arn = parameters.get('KarpenterRoleArn')
        add_karpenter_role_to_aws_auth_config_map(karpenter_role_arn)
        return True
    elif operation == Operation.HELMFILE_SYNC.value:
        run_helmfile_sync(parameters)
        return True
    elif operation == Operation.PATCH_SERVICE_ACCOUNT.value:
        role_arn = parameters.get('RoleArn')
        service_account_name = parameters.get('ServiceAccountName')
        namespace = parameters.get('Namespace')
        if not role_arn or not service_account_name or not namespace:
            raise Exception("RoleArn, ServiceAccountName and Namespace are required parameters")
        patch_service_account(role_arn, service_account_name, namespace)
        return True
    elif operation == Operation.SYNC_CLI_VERSION_TO_CLUSTER.value:
        cli_version = parameters.get('CliVersion')
        if not cli_version:
            raise Exception("CliVersion is a required parameter")
        set_current_cli_version_to_cluster(cli_version)
        return True
    elif operation == Operation.CREATE_ENV.value:
        env_name = parameters.get('EnvName')
        build_bucket_name = parameters.get('BuildBucketName')
        buildkit_isra_role_arn = parameters.get('BuildkitISRARoleArn')
        region = parameters.get('Region')
        cluster_name = parameters.get('ClusterName')
        if not (env_name and build_bucket_name and buildkit_isra_role_arn and region and cluster_name):
            raise Exception("EnvName, BuildBucketName, BuildkitISRARoleArn, Region and ClusterName are required parameters")
        return create_env(env_name, build_bucket_name, buildkit_isra_role_arn, region, cluster_name)
    elif operation in [Operation.TEARDOWN_KSVCS_SCALEDJOBS.value]:
        return True
    else:
        return False


def perform_delete_operation(operation: str, parameters: Dict) -> bool:
    if operation == Operation.HELMFILE_SYNC.value:
        return run_helmfile_destroy(parameters)
    elif operation == Operation.TEARDOWN_KSVCS_SCALEDJOBS.value:
        return delete_all_ksvcs_scaledjobs(parameters)
    elif operation in [Operation.UPDATE_AUTHMAP.value, Operation.PATCH_SERVICE_ACCOUNT.value,
                       Operation.SYNC_CLI_VERSION_TO_CLUSTER.value, Operation.CREATE_ENV.value]:
        return True
    else:
        return False


def handler(event, context):
    cluster_name = event['ResourceProperties'].get('ClusterName')
    command = event['ResourceProperties'].get('Operation')
    parameters = event['ResourceProperties'].get('Parameters')
    region = event['ResourceProperties'].get('Region')
    aws_account_id = event['ResourceProperties'].get('AWSAccountId')

    print('Generating kubeconfig')
    generate_kubeconfig(cluster_name, region, aws_account_id)
    os.environ['XDG_CONFIG_HOME'] = '/tmp/.config'
    os.environ['XDG_CACHE_HOME'] = '/tmp/.cache'
    os.environ['KUBECONFIG'] = KUBECONFIG_FILE_PATH
    print('Kubeconfig generated successfully')
    print("testing v3")

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
