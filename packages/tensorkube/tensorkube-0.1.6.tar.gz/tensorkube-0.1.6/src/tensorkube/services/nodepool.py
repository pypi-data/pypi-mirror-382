from tensorkube.constants import NODEPOOL, EC2NODECLASS, GPU_NODEPOOL_VERSION

def gpu_nodepool_version():
    return GPU_NODEPOOL_VERSION

def get_gpu_nodepool():
    return f"{gpu_nodepool_version()}-nodepool"

def get_gpu_ec2nodeclass():
    return f"{gpu_nodepool_version()}-ec2nodeclass"

def get_config_file(type: str, name: str):
    if type != NODEPOOL and type != EC2NODECLASS:
        return None
    if name == 'default':
        return f"karpenter_{type}.yaml"
    name = name.replace("-", "_")
    return f"karpenter_{name}_{type}.yaml"


