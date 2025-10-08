import time
import click
import boto3
from kubernetes import client

from tensorkube.constants import get_cluster_name, CliColors
from tensorkube.services.k8s_service import list_namespaced_k8s_deployments, scale_k8s_deployment_replicas, \
    describe_k8s_deployment, check_nodes_ready, add_k8s_nodegroup_affinity_to_deployment, get_nodes_with_label_selector, \
    delete_node_and_wait, get_deployment_for_pod, get_pods_on_node
from tensorkube.services.eks_service import upgrade_nodegroup_ami_version, scale_nodegroup_replicas, \
    wait_for_nodegroup_active

NODEGROUP_BASE_DEPLOYMENT_NAMESPACES = ["istio-system", "knative-serving", "keda", "kube-system"]

def upgrade_managed_nodegroup_ami_version():
    cluster_name = get_cluster_name()
    nodegroup_name = f"{get_cluster_name()}-tensorkube-nodegroup"

    latest_ami_release_version = get_latest_nodegroup_release_version(cluster_name=cluster_name, nodegroup_name=nodegroup_name)
    input_version = click.prompt(click.style(
        f"This action is irreversible and will upgrade the nodegroup AMI to release version '{latest_ami_release_version}'.\nPlease input the release version to confirm you want to proceed:",
        bold=True, fg=CliColors.ERROR.value))
    if input_version != latest_ami_release_version:
        raise click.ClickException(click.style("Input version does not match the latest AMI release version. Aborting upgrade.", fg=CliColors.ERROR.value, bold=True))
    print(click.style(f"Upgrading nodegroup AMI to release version '{latest_ami_release_version}'...", fg=CliColors.INFO.value, bold=True))

    scale_nodegroup_replicas(cluster_name=cluster_name, nodegroup_name=nodegroup_name, scale=5)
    wait_for_nodegroup_active(cluster_name=cluster_name, nodegroup_name=nodegroup_name)
    wait_for_nodegroup_nodes_to_be_ready(cluster_name=cluster_name, nodegroup_name=nodegroup_name)

    add_affinity_to_deployments()
    scale_nodegroup_deployments(scale_up=True)
    wait_for_nodegroup_deployments_to_be_ready()

    upgrade_nodegroup_ami_version(cluster_name=cluster_name, nodegroup_name=nodegroup_name)
    # upgrade_nodegroup_ami_version(cluster_name=cluster_name, nodegroup_name=nodegroup_name, version="1.32.7-20250807")
    wait_for_nodegroup_active(cluster_name=cluster_name, nodegroup_name=nodegroup_name)

    scale_nodegroup_deployments(scale_up=False)
    wait_for_nodegroup_deployments_to_be_ready()

    scale_nodegroup_replicas(cluster_name=cluster_name, nodegroup_name=nodegroup_name, scale=2)
    wait_for_nodegroup_active(cluster_name=cluster_name, nodegroup_name=nodegroup_name)
    delete_cordoned_nodegroup_nodes(cluster_name=cluster_name, nodegroup_name=nodegroup_name)



UPGRADE_NODEGROUP_SCALE_UP_COUNT = 5
KUBE_SYSTEM_DEPLOYMENTS_ORIGINAL_REPLICA_COUNT = 2
DEPLOYMENTS_ORIGINAL_REPLICA_COUNT = 2
def get_new_replica_count(scale_up: bool, namespace: str) -> int:
    if scale_up:
        return UPGRADE_NODEGROUP_SCALE_UP_COUNT
    else:
        if namespace == 'kube-system':
            return KUBE_SYSTEM_DEPLOYMENTS_ORIGINAL_REPLICA_COUNT
        else:
            return DEPLOYMENTS_ORIGINAL_REPLICA_COUNT


def scale_nodegroup_deployments(scale_up: bool):
    for ns in NODEGROUP_BASE_DEPLOYMENT_NAMESPACES:
        deployments = list_namespaced_k8s_deployments(namespace=ns)
        for deployment in deployments:
            scale_k8s_deployment_replicas(deployment_name=deployment.metadata.name, namespace=ns,
                                      new_scale=get_new_replica_count(scale_up=scale_up, namespace=ns))
            print(f"Scaled deployment {deployment.metadata.name} in namespace {ns} to {get_new_replica_count(scale_up=scale_up, namespace=ns)} replicas.")


def wait_for_deployment_to_be_ready(deployment: client.V1Deployment, timeout: int = 600):
    namespace = deployment.metadata.namespace
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for deployment {deployment.metadata.name} in namespace {namespace} to be ready.")
            break
        current_deployment = describe_k8s_deployment(deployment_name=deployment.metadata.name, namespace=namespace)
        desired_replicas = current_deployment.spec.replicas
        ready_replicas = current_deployment.status.ready_replicas if current_deployment.status.ready_replicas else 0
        if ready_replicas >= desired_replicas:
            print(
                f"Deployment {deployment.metadata.name} in namespace {namespace} is ready with {ready_replicas}/{desired_replicas} replicas.")
            break
        else:
            print(
                f"Waiting for deployment {deployment.metadata.name} in namespace {namespace} to be ready. Current status: {ready_replicas}/{desired_replicas} replicas.")
            time.sleep(10)  # Sleep for 10 seconds before checking again


def wait_for_nodegroup_deployments_to_be_ready(timeout: int = 600):
    for ns in NODEGROUP_BASE_DEPLOYMENT_NAMESPACES:
        deployments = list_namespaced_k8s_deployments(namespace=ns)
        for deployment in deployments:
            wait_for_deployment_to_be_ready(deployment=deployment, timeout=timeout)


def wait_for_nodegroup_nodes_to_be_ready(cluster_name: str, nodegroup_name: str):
    label_selector = f"alpha.eksctl.io/cluster-name={cluster_name},alpha.eksctl.io/nodegroup-name={nodegroup_name}"

    ready = False
    while not ready:
        ready, ready_nodes = check_nodes_ready(label_selector)
        if ready and len(ready_nodes) > 0:
            print(f"All nodes in nodegroup {nodegroup_name} are ready: {ready_nodes}")
        else:
            print(f"Waiting for nodes in nodegroup {nodegroup_name} to become ready...")
            time.sleep(10)  # Check every 10 seconds

    print(f"Nodegroup {nodegroup_name} is ready.")

# NOTE: this will cause a drift from the helm chart but we don't update the helm installation after configure
# so not implementing a more complex solution for now
def add_affinity_to_deployments():
    for namespace in NODEGROUP_BASE_DEPLOYMENT_NAMESPACES:
        deployments = list_namespaced_k8s_deployments(namespace=namespace)
        for deployment in deployments:
            print(f"Adding affinity to deployment {deployment.metadata.name} in namespace knative-serving")
            add_k8s_nodegroup_affinity_to_deployment(deployment_name=deployment.metadata.name, namespace=namespace,
                                                nodegroup_name=f"{get_cluster_name()}-tensorkube-nodegroup",
                                                cluster_name=get_cluster_name())


def delete_cordoned_nodegroup_nodes(cluster_name: str, nodegroup_name: str):
    click.echo(f"Deleting cordoned nodes in nodegroup {nodegroup_name}")

    label_selector = f"alpha.eksctl.io/cluster-name={cluster_name},alpha.eksctl.io/nodegroup-name={nodegroup_name}"

    nodes = get_nodes_with_label_selector(label_selector=label_selector)

    for node in nodes:
        if node.spec and node.spec.unschedulable:
            # get pods running on the node
            try:
                node_pods = get_pods_on_node(node_name=node.metadata.name)
            except client.ApiException as e:
                continue
            # get deployments for those pods
            # scale those deployments up by 1
            scaled_deployments = []
            for pod in node_pods:
                namespace, pod_deployment_name = get_deployment_for_pod(pod_name=pod.metadata.name, namespace=pod.metadata.namespace)
                if namespace not in NODEGROUP_BASE_DEPLOYMENT_NAMESPACES:
                    continue
                if pod_deployment_name:
                    pod_deployment = describe_k8s_deployment(deployment_name=pod_deployment_name, namespace=namespace)
                    click.echo(f"Found pod {pod.metadata.name} on node {node.metadata.name} belonging to deployment {pod_deployment.metadata.name}.")
                    click.echo(f"Scaling deployment by +1 to ensure availability during node deletion.")

                    scale_k8s_deployment_replicas(deployment_name=pod_deployment.metadata.name,
                                                  namespace=pod_deployment.metadata.namespace,
                                                  new_scale=pod_deployment.spec.replicas + 1)
                    scaled_deployments.append(pod_deployment)

                    wait_for_deployment_to_be_ready(deployment=pod_deployment)

            # delete node
            click.echo(f"Deleting node {node.metadata.name}")
            delete_node_and_wait(node_name=node.metadata.name)

            # scale deployments back down
            for deployment in scaled_deployments:
                click.echo(f"Scaling deployment {deployment.metadata.name} to original replica count.")
                scale_k8s_deployment_replicas(deployment_name=deployment.metadata.name,
                                              namespace=deployment.metadata.namespace,
                                              new_scale=get_new_replica_count(scale_up=False,
                                                                              namespace=deployment.metadata.namespace))
                wait_for_deployment_to_be_ready(deployment=deployment)


# AL2023 variants (managed nodegroups use these amiTypes)
# AL2023_MAP = {
#     "AL2023_x86_64_STANDARD": "/aws/service/eks/optimized-ami/{k8s}/amazon-linux-2023/x86_64/standard/recommended/release_version",
#     "AL2023_x86_64_NVIDIA":   "/aws/service/eks/optimized-ami/{k8s}/amazon-linux-2023/x86_64/nvidia/recommended/release_version",
#     "AL2023_ARM_64_STANDARD": "/aws/service/eks/optimized-ami/{k8s}/amazon-linux-2023/arm64/standard/recommended/release_version",
#     "AL2023_ARM_64_NVIDIA":   "/aws/service/eks/optimized-ami/{k8s}/amazon-linux-2023/arm64/nvidia/recommended/release_version",
# }
def _ssm_param_for_release_version(k8s_version: str, ami_type: str) -> str:
    if ami_type != "AL2023_x86_64_STANDARD":
        raise click.ClickException(f"Unsupported amiType for SSM release_version lookup: {ami_type}. Only AL2023_x86_64_STANDARD is supported.")
    return f"/aws/service/eks/optimized-ami/{k8s_version}/amazon-linux-2023/x86_64/standard/recommended/release_version"


def get_latest_nodegroup_release_version(cluster_name: str, nodegroup_name: str, region: str = None) -> str:
    session = boto3.Session(region_name=region) if region else boto3.Session()
    eks = session.client("eks")
    ssm = session.client("ssm")

    ng = eks.describe_nodegroup(clusterName=cluster_name, nodegroupName=nodegroup_name)["nodegroup"]
    k8s_version = ng["version"]
    ami_type = ng["amiType"]

    param_name = _ssm_param_for_release_version(k8s_version, ami_type)
    value = ssm.get_parameter(Name=param_name)["Parameter"]["Value"]
    return value
