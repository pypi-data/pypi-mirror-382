from typing import Dict
import re

from tensorkube.services.filesystem_service import create_efs_volume_k8s_resources, get_efs_filesystem_by_name, \
    check_existing_efs_volume_k8s_resources

SUPPORTED_VOLUME_TYPES = ["efs"]

def volume_name_satisfies_regex(volume_name: str):
    pattern = r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$'
    return bool(re.match(pattern, volume_name))

def get_deployment_volume_name(volume_name: str, volume_type: str):
    return f"{volume_type}-{volume_name}"

def get_deployment_volume_mount_path(volume: Dict):
    if not volume.get("mount_path", None):
        return f"/mnt/{volume['type']}/{volume['name']}"
    return volume.get("mount_path")


def get_volume_cloud_resource(volume_name, volume_type):
    if volume_type == "efs":
        return get_efs_filesystem_by_name(volume_name)

    return None


def check_existing_volume_pv_and_pvc(volume_name, volume_type, env):
    if volume_type == "efs":
        return check_existing_efs_volume_k8s_resources(volume_name, env)
    return False

def create_volume_k8s_resources(volume_name, volume_type, cloud_volume_resource, env) -> bool:
    if volume_type == "efs":
        return create_efs_volume_k8s_resources(volume_name=volume_name, efs_id=cloud_volume_resource['FileSystemId'], env=env)
    else:
        raise Exception(f"Volume type '{volume_type}' is not supported")
