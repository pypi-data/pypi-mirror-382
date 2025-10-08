import subprocess
from pkg_resources import resource_filename
from tensorkube.services.k8s_service import patch_service_account
from tensorkube.constants import get_cluster_name
from tensorkube.services.aws_service import get_aws_account_id
from tensorkube.constants import NODEPOOL, EC2NODECLASS
from tensorkube.services.eks_service import get_cluster_oidc_issuer_url
from tensorkube.services.iam_service import create_iam_role_with_service_account_cluster_access, attach_role_policy, delete_iam_role
from tensorkube.services.karpenter_service import apply_ec2nodeclass, apply_nodepools
from tensorkube.services.nodepool import get_gpu_nodepool, get_gpu_ec2nodeclass, get_config_file, gpu_nodepool_version


def install_nydus():
    apply_ec2nodeclass(get_config_file(EC2NODECLASS, gpu_nodepool_version()), get_gpu_ec2nodeclass())
    apply_nodepools(get_config_file(NODEPOOL, gpu_nodepool_version()), get_gpu_nodepool())  
    install_nydus_snapshotter_helm(get_gpu_nodepool())
    create_nydus_ecr_service_account()
    
    
def delete_nydus():
    uninstall_nydus_snapshotter_helm()
    delete_iam_role(get_nydus_ecr_iam_role_name())


def install_nydus_snapshotter_helm(nodepool_name: str):
    namespace = 'nydus-snapshotter'
    nydus_snapshotter_chart_version = "0.0.10"
    try:
        subprocess.run(["helm", "upgrade", "--install", "nydus-snapshotter",
                        "oci://public.ecr.aws/q0m5o9l2/tensorfuse/helm-charts/nydus-snapshotter", "--version",
                        nydus_snapshotter_chart_version, "--create-namespace", "--namespace", namespace,
                        "--set", f"nodeSelector.nodepool={nodepool_name}"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install nydus snapshotter helm chart in namespace '{namespace}': {e}")

def uninstall_nydus_snapshotter_helm():
    try:
        subprocess.run(["helm", "uninstall", "nydus-snapshotter", "--namespace", "nydus-snapshotter"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to uninstall nydus snapshotter helm chart in namespace 'nydus-snapshotter': {e}")

def get_nydus_runtime_class_name():
    return "runc-nydus"

def get_nydus_ecr_iam_role_name():
    return f"{get_cluster_name()}-nydus-ecr-role"

def get_nydus_snapshoter_name():
    return "nydus-snapshotter"

def get_nydus_snapshoter_namespace():
    return get_nydus_snapshoter_name()

def get_nydus_snapshoter_service_account_name():
    return f"{get_nydus_snapshoter_name()}-sa"

def create_nydus_ecr_service_account():
    namespace = get_nydus_snapshoter_namespace()
    service_account_name = get_nydus_snapshoter_service_account_name()
    role_name = get_nydus_ecr_iam_role_name()
    role = create_iam_role_with_service_account_cluster_access(get_aws_account_id(),get_cluster_oidc_issuer_url(get_cluster_name()), role_name, service_account_name, namespace)
    role_arn = role["Role"]["Arn"]
    attach_role_policy("aws", "AmazonEC2ContainerRegistryReadOnly", role_name)
    patch_service_account(role_arn, service_account_name, namespace)




def get_nydus_image_url(image_url: str):
    return f'{image_url}-nydus'
