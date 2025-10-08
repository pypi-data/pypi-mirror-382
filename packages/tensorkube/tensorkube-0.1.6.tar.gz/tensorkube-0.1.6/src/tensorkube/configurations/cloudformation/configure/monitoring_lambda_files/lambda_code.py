import boto3
import os
import yaml
import time
import subprocess
from kubernetes import client, config
from typing import Dict
from enum import Enum
import json
import datetime

KUBECONFIG_FILE_PATH = '/tmp/kubeconfig'
# KUBECONFIG_FILE_PATH = '~/.kube/config'


def get_aws_caller_identity():
    return boto3.client('sts').get_caller_identity()


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
            "name": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}'
        }],
        "contexts": [{
            "context": {
                "cluster": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}',
                "user": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}'
            },
            "name": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}'
        }],
        "current-context": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}',
        "kind": "Config",
        "users": [{
            "name": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}',
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


def get_nodes(cluster_name: str):
    kubeconfig_file = os.path.expanduser(KUBECONFIG_FILE_PATH)
    config.load_kube_config(config_file=kubeconfig_file)

    # Load the existing kubeconfig
    v1 = client.CoreV1Api()
    try:
        print(f"Getting unhealthy nodes for cluster: {cluster_name}")
        nodes = v1.list_node()
        return nodes
    except Exception as e:
        print(f"Failed to get nodes: {e}")
        raise Exception(f"Failed to get nodes: {e}")


def is_unhealthy_node(node) -> bool:
    if node.status.conditions:
        for condition in node.status.conditions:
            # Check for 'Ready' condition and its status should not be 'True'. values are 'True', 'False', 'Unknown'
            if condition.type == 'Ready' and condition.status == 'Unknown':
                return True
    return False

def is_node_deleting(node) -> bool:
    if node.metadata.deletion_timestamp:
        return True
    return False


def get_unhealthy_nodes(cluster_name: str):
    kubeconfig_file = os.path.expanduser(KUBECONFIG_FILE_PATH)
    config.load_kube_config(config_file=kubeconfig_file)

    # Load the existing kubeconfig
    v1 = client.CoreV1Api()
    try:
        print(f"Getting unhealthy nodes for cluster: {cluster_name}")
        nodes = v1.list_node()
        unhealthy_nodes = []
        current_nodes = []
        for node in nodes.items:
            # about condition - https://kubernetes.io/docs/reference/node/node-status/#condition
            current_nodes.append(node.metadata.name)
            if node.status.conditions:
                for condition in node.status.conditions:
                    # Check for 'Ready' condition and its status should not be 'True'. values are 'True', 'False', 'Unknown'
                    if condition.type == 'Ready' and condition.status == 'Unknown':
                        print(f"Node {node.metadata.name} is unhealthy")
                        print(f"status: {condition.status}")
                        print(f"last heartbeat time: {condition.last_heartbeat_time}")
                        print(f"message: {condition.message}")
                        print(f"reason: {condition.reason}")
                        unhealthy_nodes.append(node.metadata.name)
        print(f"Unhealthy nodes: {unhealthy_nodes}")
        return unhealthy_nodes
    except Exception as e:
        print(f"Failed to get nodes: {e}")
        raise Exception(f"Failed to get nodes: {e}")


def delete_k8s_node(node_name: str, cluster_name: str):
    kubeconfig_file = os.path.expanduser(KUBECONFIG_FILE_PATH)
    config.load_kube_config(config_file=kubeconfig_file)

    # Load the existing kubeconfig
    v1 = client.CoreV1Api()
    try:
        print(f"Deleting node: {node_name}")
        node = v1.read_node(name=node_name)
        if node.metadata.finalizers:
            print(f"Removing finalizers from node: {node_name}")
            body = {"metadata": {"finalizers": []}}
            v1.patch_node(name=node_name, body=body)
        response = v1.delete_node(name=node_name, grace_period_seconds=0, propagation_policy='Foreground', pretty=True)
        print(f"Deletion Node Response: {response}")
        return True
    except Exception as e:
        print(f"Failed to delete node: {e}")
        return False


def delete_unhealthy_nodes_and_wait(cluster_name: str):
    while True:
        nodes = get_nodes(cluster_name)
        unhealthy_nodes = False
        for node in nodes.items:
            if is_unhealthy_node(node):
                unhealthy_nodes = True
                if not is_node_deleting(node):
                    print(f"Node {node.metadata.name} is unhealthy and not deleting, deleting it now")
                    delete_k8s_node(node.metadata.name, cluster_name)
                else:
                    print(f"Node {node.metadata.name} is unhealthy and deleting")
        if not unhealthy_nodes:
            print(f"All unhealthy nodes have been deleted")
            return
        else:
            print(f"Unhealthy nodes found, waiting for 60 seconds before checking again")
            time.sleep(60)


def handler(event, context):
    records = event['Records']
    record = records[0]

    sns_msg = record['Sns']
    message_str = sns_msg['Message']
    message = json.loads(message_str)

    account_id = message.get('AWSAccountId', None)
    if not account_id:
        raise ValueError("AWSAccountId not found in message")

    trigger = message.get('Trigger', None)
    node_name = None
    cluster_name = None
    region = None
    if trigger:
        dimensions = trigger.get('Dimensions', [])
        for dimension in dimensions:
            if dimension.get('name') == 'NodeName':
                node_name = dimension.get('value')
            if dimension.get('name') == 'ClusterName':
                cluster_name = dimension.get('value')

    region = boto3.session.Session().region_name
    print(f"Cluster: {cluster_name}")
    print(f"Region: {region}")
    if not cluster_name:
        raise ValueError("ClusterName not found in message")
    if not region:
        raise ValueError("Region is not found in message")

    print('Generating kubeconfig')
    generate_kubeconfig(cluster_name, region, account_id)
    os.environ['XDG_CONFIG_HOME'] = '/tmp/.config'
    os.environ['XDG_CACHE_HOME'] = '/tmp/.cache'
    os.environ['KUBECONFIG'] = KUBECONFIG_FILE_PATH
    print('Kubeconfig generated successfully')

    print('Getting unhealthy nodes')
    unhealthy_nodes = get_unhealthy_nodes(cluster_name)
    if not unhealthy_nodes:
        print('No unhealthy nodes found')
        return
    print(f"Unhealthy nodes: {unhealthy_nodes}")
    for node_name in unhealthy_nodes:
        deleted = delete_k8s_node(node_name, cluster_name)
        if deleted:
            print(f"Node {node_name} deleted successfully")
        else:
            print(f"Failed to delete node {node_name}")
            raise Exception(f"Failed to delete node {node_name}")
    print('Unhealthy nodes deleted successfully')
    # delete_unhealthy_nodes_and_wait(cluster_name)
