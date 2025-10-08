import subprocess
import tempfile
import time
from importlib import resources
from typing import Optional

from kubernetes import config, client

from tensorkube.constants import get_cluster_name, NAMESPACE, DEFAULT_NAMESPACE, KNATIVE_SERVING_NAMESPACE, \
    CONFIG_FEATURES, ADDON_NAME, get_mount_driver_role_name
from tensorkube.services.aws_service import get_aws_account_id
from tensorkube.services.eks_service import install_karpenter, delete_eks_addon, create_eks_addon
from tensorkube.services.eksctl_service import delete_nodegroup
from tensorkube.services.filesystem_service import configure_efs, cleanup_filesystem_resources
from tensorkube.services.k8s_service import check_nodes_ready, evict_pods_from_node, get_nodes_not_using_bottlerocket, \
    drain_and_delete_node, delete_pv_using_name, delete_pvc_using_name_and_namespace, create_build_pv_and_pvc, \
    check_pvc_exists_by_name, get_tensorkube_cluster_context_name
from tensorkube.services.karpenter_service import update_ec2_node_class_ami
from tensorkube.services.logging_service import configure_cloudwatch
from tensorkube.services.s3_service import get_bucket_name


def create_and_wait_for_nodegroup(test: bool = False):
    cluster_name = get_cluster_name()
    nodegroup_name = f"{cluster_name}-ng-bottlerocket"
    # Access the YAML file using importlib.resources
    package_dir = resources.files('tensorkube')
    yaml_file_path = package_dir / 'configurations' / 'bottlerocket_nodegroup.yaml'

    # Read the YAML file content
    with open(yaml_file_path, 'r') as file:
        filedata = file.read()

    # Replace ${CLUSTER_NAME} in the YAML content
    filedata = filedata.replace('${CLUSTER_NAME}', cluster_name)

    # Step 2: Create a temporary file and write the modified content to it
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write(filedata)
        temp_file_path = temp_file.name

    # Step 3: Create the nodegroup using eksctl with the temporary file
    create_command = f"eksctl create nodegroup --config-file={temp_file_path}"
    subprocess.run(create_command, shell=True, check=True)
    print(f"Nodegroup {nodegroup_name} creation initiated.")

    # New Step: Wait for the nodegroup to become ready using Kubernetes client
    label_selector = f"eks.amazonaws.com/nodegroup={nodegroup_name}"
    ready = False
    while not ready:
        ready, ready_nodes = check_nodes_ready(label_selector)
        if ready and len(ready_nodes) > 0:
            print(f"All nodes in nodegroup {nodegroup_name} are ready: {ready_nodes}")
        else:
            print(f"Waiting for nodes in nodegroup {nodegroup_name} to become ready...")
            time.sleep(60)  # Check every 60 seconds

    print(f"Nodegroup {nodegroup_name} is ready.")


def wait_for_deployments_to_be_ready(apps_api, namespaces):
    for ns in namespaces:
        deployments = apps_api.list_namespaced_deployment(ns).items
        for deployment in deployments:
            desired_replicas = deployment.spec.replicas
            while True:
                current_deployment = apps_api.read_namespaced_deployment(deployment.metadata.name, ns)
                ready_replicas = current_deployment.status.ready_replicas if current_deployment.status.ready_replicas else 0
                if ready_replicas >= desired_replicas:
                    print(
                        f"Deployment {deployment.metadata.name} in namespace {ns} is ready with {ready_replicas}/{desired_replicas} replicas.")
                    break
                else:
                    print(
                        f"Waiting for deployment {deployment.metadata.name} in namespace {ns} to be ready. Current status: {ready_replicas}/{desired_replicas} replicas.")
                    time.sleep(10)  # Sleep for 10 seconds before checking again


def enable_knative_pv_pvc_capabilities(namespace=KNATIVE_SERVING_NAMESPACE, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)

    try:
        # Get the existing config-features ConfigMap
        config_map = v1.read_namespaced_config_map(name=CONFIG_FEATURES, namespace=namespace)

        # Update the ConfigMap data
        if config_map.data is None:
            config_map.data = {}
            config_map.data['kubernetes.podspec-nodeselector'] = 'enabled'
            config_map.data['kubernetes.podspec-affinity'] = 'enabled'

        config_map.data["kubernetes.podspec-persistent-volume-claim"] = "enabled"
        config_map.data["kubernetes.podspec-persistent-volume-write"] = "enabled"
        config_map.data["kubernetes.containerspec-addcapabilities"] = "enabled"
        config_map.data["kubernetes.podspec-security-context"] = "enabled"

        # Update the ConfigMap
        v1.patch_namespaced_config_map(name=CONFIG_FEATURES, namespace=namespace, body=config_map)
        print(
            f"Successfully enabled node selector, affinity, pv-claim, pv-write and add-capabilities features in {CONFIG_FEATURES} ConfigMap.")
    except client.exceptions.ApiException as e:
        print(f"Exception when updating ConfigMap: {e}")
        raise


def apply():
    # check if the clusername-ng managed nodegroup exists in the cluster
    # if it does then first cordon all the nodes belonging to the clustername-ng managed nodegroup
    # create the new nodegroup with clustername-ng-bottlerocket and wait for it to get ready
    # scale the deployments from istio-system and knative-serving namespaces to 5 so that they move to new nodes despite the pdbs
    # drain the old nodes by ignoring the daemonsets
    # scale down the deployments back from istio-system and knative-serving namespaces to 1
    # check if all the pods across all the namespaces are ready
    # delete the old nodegroup and wait for it to finish
    # update the cluster cli version to this migration's version
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise Exception("No Kubernetes context found. Please ensure that you have a valid kubeconfig file and try again.")
    k8s_api_client = config.new_client_from_config(context=context_name)  # Load kubeconfig file
    
    core_api = client.CoreV1Api(k8s_api_client)
    apps_api = client.AppsV1Api(k8s_api_client)

    # Step 1 & 2: Check and cordon nodes
    old_nodegroup_name = f'{get_cluster_name()}-ng'
    new_nodegroup_name = f'{get_cluster_name()}-ng-bottlerocket'
    nodegroup_label = 'eks.amazonaws.com/nodegroup'

    # Cordon all nodes in the existing nodegroup
    nodes = core_api.list_node().items

    for node in nodes:
        # Check if the node is part of the target node group by examining its labels
        # if node.metadata.labels.get(nodegroup_label) == old_nodegroup_name:
        #     # Cordon the node by setting it to unschedulable
        core_api.patch_node(node.metadata.name, {"spec": {"unschedulable": True}})
        print(f"Cordoned node {node.metadata.name}")

    # Step 3: Create new nodegroup
    create_and_wait_for_nodegroup()
    print(f"Nodegroup {new_nodegroup_name} created")

    # now for the karpenter configuration
    update_ec2_node_class_ami("default", "Bottlerocket")

    # Step 4: Scale deployments
    namespaces = ["istio-system", "knative-serving"]
    for ns in namespaces:
        deployments = apps_api.list_namespaced_deployment(ns).items
        for deployment in deployments:
            replicas = 5 if ns == "knative-serving" else 2
            apps_api.patch_namespaced_deployment_scale(deployment.metadata.name, ns, {"spec": {"replicas": 5}})
            print(f"Scaled up deployment {deployment.metadata.name} in namespace {ns}")

    wait_for_deployments_to_be_ready(apps_api, namespaces)

    configure_cloudwatch()

    # move karpenter to new nodegroup
    install_karpenter()

    # Step 6: Drain old nodes (use kubectl drain or equivalent in Python)
    for node in nodes:
        # Check if the node is part of the target node group by examining its labels
        if node.metadata.labels.get(nodegroup_label) == old_nodegroup_name:
            # Evict all the pods scheduled there
            evict_pods_from_node(node.metadata.name)
            print(f"Evicted all pods from {node.metadata.name}")

    # Step 7: Scale down deployments
    for ns in namespaces:
        deployments = apps_api.list_namespaced_deployment(ns).items
        for deployment in deployments:
            apps_api.patch_namespaced_deployment_scale(deployment.metadata.name, ns, {"spec": {"replicas": 1}})
            print(f"Scaled down deployment {deployment.metadata.name} in namespace {ns}")

    nodes_without_bottlerocket = get_nodes_not_using_bottlerocket("default")
    for node in nodes_without_bottlerocket:
        drain_and_delete_node(node)

    delete_nodegroup(old_nodegroup_name)

    # Update Knative ConfigMap to enable PV and PVC capabilities, and add capabilities to containers
    enable_knative_pv_pvc_capabilities()

    # delete the s3-pvc in kube-system namespace and then delete s3-pv
    delete_pvc_using_name_and_namespace("s3-claim", NAMESPACE)
    delete_pv_using_name("s3-pv")
    delete_eks_addon(get_cluster_name(), ADDON_NAME)
    # recreate the s3-pv and s3-pvc
    bucket_name = get_bucket_name()
    create_eks_addon(get_cluster_name(), ADDON_NAME, get_aws_account_id(),
                     get_mount_driver_role_name(get_cluster_name()))
    create_build_pv_and_pvc(bucket_name)

    # now check if efs-claim exists
    if check_pvc_exists_by_name(claim_name='efs-pvc', namespace='default'):
        cleanup_filesystem_resources()
    configure_efs()
