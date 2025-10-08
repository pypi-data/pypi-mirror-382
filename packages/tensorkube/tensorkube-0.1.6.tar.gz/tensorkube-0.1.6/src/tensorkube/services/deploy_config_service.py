import click
import yaml
import os
import re
from typing import List, Dict, Optional

from tensorkube.constants import CliColors
from tensorkube.services.volumes_service import SUPPORTED_VOLUME_TYPES, check_existing_volume_pv_and_pvc, \
    create_volume_k8s_resources, get_volume_cloud_resource


class Config(object):
    def __init__(self, config_file_path):
        self.__config = {}
        if config_file_path != None:
            file_path = os.path.abspath(config_file_path)  # Convert to absolute path
            if not os.path.isfile(file_path):
                raise Exception(f"Config.yaml file not found in path: {file_path}")
            with open(file_path, 'r') as config_file:
                self.__config = yaml.safe_load(config_file)

    def get(self, key):
        return self.__config.get(key, None)

    def set_if_not_exist(self, key, value):
        if key in self.__config:
            return self
        if isinstance(value, tuple):
            self.__config[key] = list(value)
        else:
            self.__config[key] = value
        return self
    
    def update(self, key, value):
        self.__config[key] = value
        return self

    def __str__(self) -> str:
        return str(self.__config)


def run_deployment_config_pre_flight_checks(config: Config) -> bool:
    return (run_volume_checks(volumes=config.get("volumes"), env=config.get("env"))
            and is_valid_project_name(config.get("name")))

def is_valid_mount_path(mount_path: Optional[str]):
    if not mount_path:
        return True
    pattern = r'^(\/[a-zA-Z0-9._-]+)+\/?$'
    return bool(re.match(pattern, mount_path))

def is_valid_project_name(project_name: Optional[str]):
    if not project_name:
        click.echo(click.style("Invalid project name. Project name cannot be empty.", fg=CliColors.ERROR.value))
        return False
    pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
    is_valid = bool(re.match(pattern, project_name))
    if not is_valid:
        click.echo(click.style(f"Invalid project name '{project_name}'. Project name must start with a lowercase letter, and can contain lowercase letters, numbers, and hyphens, and must end with a letter or number. No spaces or special characters allowed.", fg=CliColors.ERROR.value))
    return is_valid

def run_volume_checks(volumes: Optional[List[Dict]], env: Optional[str]) -> bool:
    if not volumes:
        return True

    for volume in volumes:
        volume_name = volume.get("name", None)
        volume_type = volume.get("type", None)
        volume_mount_path = volume.get("mount_path", None)

        if not volume_type or not volume_name:
            click.echo(click.style("Volume name and type are required", fg=CliColors.ERROR.value))
            return False

        if volume_type not in SUPPORTED_VOLUME_TYPES:
            click.echo(click.style(f"Volume type '{volume_type}' is not supported", fg=CliColors.ERROR.value))
            return False

        if not is_valid_mount_path(volume_mount_path):
            click.echo(click.style(f"Mount path '{volume_mount_path}' for volume '{volume_name}' is invalid. Refer to our docs for mount path guidelines: https://tensorfuse.io/docs/concepts/volumes", fg=CliColors.ERROR.value))
            return False

        click.echo(f"Checking volume '{volume_name}' of type '{volume_type}'")
        cloud_volume_resource = get_volume_cloud_resource(volume_name, volume_type)
        if not cloud_volume_resource:
            click.echo(click.style(f"Volume '{volume_name}' of type '{volume_type}' not found", fg=CliColors.ERROR.value))
            return False

        click.echo(f"Cloud resources for volume '{volume_name}' of type '{volume_type}' found")
        is_existing_volume_pv_and_pvc = check_existing_volume_pv_and_pvc(volume_name, volume_type, env)
        if not is_existing_volume_pv_and_pvc:
            try:

                click.echo(f"Not Found: Cluster resources for volume '{volume_name}' of type '{volume_type}'")
                click.echo(f"Creating cluster resources...")
                create_volume_k8s_resources(volume_name=volume_name, volume_type=volume_type,
                                            cloud_volume_resource=cloud_volume_resource , env=env)
            except Exception as e:
                click.echo(click.style(f"Error creating volume resources: {e}", fg=CliColors.ERROR.value))
                return False
        else:
            click.echo(f"Cluster resources for volume '{volume_name}' of type '{volume_type}' found")

    return True
