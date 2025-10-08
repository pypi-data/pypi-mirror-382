import json
import os
import platform
import subprocess
from string import Template
from typing import List
import yaml
import click
import semver
from pkg_resources import resource_filename

from tensorkube.constants import CliColors, LOCKED_EKSCTL_VERSION
from tensorkube.constants import get_cluster_name
from tensorkube.services.aws_service import get_aws_account_id, get_karpenter_namespace, get_session_region
from tensorkube.services.error import CLIVersionError


# create base cluster using eksctl
def create_base_tensorkube_cluster_eksctl(cluster_name, vpc_public_subnets: List[str] = [], vpc_private_subnets: List[str]=[]):
    yaml_file_path = resource_filename('tensorkube', 'configurations/base_cluster.yaml')
    # variables
    region = get_session_region()
    variables = {"CLUSTER_NAME": cluster_name, "AWS_DEFAULT_REGION": region, "K8S_VERSION": "1.29",
                 "AWS_ACCOUNT_ID": get_aws_account_id(), "KARPENTER_NAMESPACE": get_karpenter_namespace(),
                 "AWS_PARTITION": "aws", }

    with open(yaml_file_path) as file:
        template = file.read()
    yaml_content = Template(template).substitute(variables)

    yaml_data = yaml.safe_load(yaml_content)
    
    # Dynamically construct the VPC section
    vpc_config = {"subnets": {"private": {}, "public": {}}}
    
    # Add private subnets
    for i, subnet_id in enumerate(vpc_private_subnets, start=1):
        vpc_config["subnets"]["private"][f"subnetprivate{i}"] = {"id": subnet_id}

    # Add public subnets
    for i, subnet_id in enumerate(vpc_public_subnets, start=1):
        vpc_config["subnets"]["public"][f"subnetpublic{i}"] = {"id": subnet_id}

    if len(vpc_public_subnets) > 1 and len(vpc_private_subnets) > 1:
        yaml_data["vpc"] = vpc_config

    temp_yaml_file_path = "/tmp/temp_cluster.yaml"
    with open(temp_yaml_file_path, 'w') as file:
        yaml.dump(yaml_data, file, default_flow_style=False)

    # Check if the cluster already exists
    try:
        subprocess.run(["eksctl", "get", "cluster", cluster_name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'Cluster {cluster_name} already exists.')
        os.remove(temp_yaml_file_path)
        return None
    except subprocess.CalledProcessError:
        pass  # Cluster does not exist, we can create it

        # Run the eksctl create cluster command
    command = ["eksctl", "create", "cluster", "-f", temp_yaml_file_path]
    subprocess.run(command, check=True)

    # Remove the temporary file
    os.remove(temp_yaml_file_path)


def delete_cluster():
    command = ["eksctl", "delete", "cluster", "--name", get_cluster_name()]
    subprocess.run(command)


def check_and_install_eksctl():
    """Check if eksctl is installed and if not isntall it."""
    try:
        version_cmd = subprocess.run(["eksctl", "version", "-o", "json"], check=True, stdout=subprocess.PIPE)
        version_dict = json.loads(version_cmd.stdout.decode("utf-8"))
        version = semver.VersionInfo.parse(version_dict["Version"])
        locked_eksctl_version = semver.VersionInfo.parse(LOCKED_EKSCTL_VERSION)
        # check if the eksctl version is above locked eksctl version
        print("eksctl is already installed.")
        if (version.major, version.minor) < (locked_eksctl_version.major, locked_eksctl_version.minor):
            text = f"eksctl version is {version}. Please upgrade eksctl to version above {LOCKED_EKSCTL_VERSION}."
            click.echo(click.style(text, bold=True, fg=CliColors.ERROR.value))
            raise CLIVersionError(text)
    except Exception as e:
        if isinstance(e, CLIVersionError):
            raise e
        click.echo(
            click.style("Eksctl not found. Proceeding with installation. Might require sudo password.", bold=True,
                        fg=CliColors.WARNING.value))
        # check if the operating system is mac and install eksctl
        if platform.system() == "Darwin" or platform.system() == "Linux":
            try:
                loc = f"https://github.com/eksctl-io/eksctl/releases/download/v{LOCKED_EKSCTL_VERSION}/eksctl_Darwin_amd64.tar.gz"
                download_command = ["curl", "--silent", "--location", loc, "-o", "/tmp/eksctl.tar.gz"]
                subprocess.run(" ".join(download_command), shell=True, check=True)
                # Extract the tar.gz file
                extract_command = ["tar", "xzf", "/tmp/eksctl.tar.gz", "-C", "/tmp"]
                subprocess.run(extract_command, check=True)
                # Move the binary to /usr/local/bin
                move_command = ["sudo", "mv", "/tmp/eksctl", "/usr/local/bin"]
                subprocess.run(move_command, check=True)
                subprocess.run(["eksctl", "version"])
            except Exception as e:
                print("Unable to install eksctl. Please install eksctl manually.")
                raise e
        else:
            print("eksctl is not installed. Please install eksctl manually.")
            raise e


def delete_nodegroup(nodegroup_name):
    # Construct the eksctl command to delete the nodegroup
    delete_command = f"eksctl delete nodegroup --name={nodegroup_name} --cluster={get_cluster_name()} --wait"

    # Execute the command
    print(f"Initiating deletion of nodegroup {nodegroup_name}...")
    subprocess.run(delete_command, shell=True, check=True)
    print(f"Nodegroup {nodegroup_name} deletion initiated. Please wait for the process to complete.")
