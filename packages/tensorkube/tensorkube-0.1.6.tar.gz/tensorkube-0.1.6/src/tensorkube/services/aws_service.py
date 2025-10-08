import os
import platform
import shutil
import subprocess
import uuid
from typing import Optional, List

import boto3
import botocore
import click
import semver

from tensorkube.constants import CliColors
from tensorkube.constants import get_cluster_name, DEFAULT_NAMESPACE, LOCKED_AWS_CLI_VERSION
from tensorkube.services.error import CLIVersionError
import configparser

TENSORFUSE_SESSION = 'tensorfuse'

def get_eks_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("eks")

def get_session_region():
    session  = get_boto3_session()
    return session.region_name

def get_cloudformation_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("cloudformation")


def get_ec2_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("ec2")


def get_iam_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("iam")

def get_sts_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("sts")

def get_s3_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("s3")

def get_s3_resource(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.resource("s3")

def get_ecr_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("ecr")

def get_efs_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("efs")


def get_aws_account_id(session_region: Optional[str] = None):
    sts = get_sts_client(region=session_region)
    identity = sts.get_caller_identity()
    return identity['Account']

def get_logs_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("logs")

def get_sqs_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("sqs")

def get_dynamodb_client(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.client("dynamodb")

def get_dynamodb_resource(region: Optional[str] = None):
    session = get_boto3_session(region_name=region)
    return session.resource("dynamodb")

def get_aws_user_arn() -> str:
    session = get_boto3_session()
    sts = session.client('sts')
    identity = sts.get_caller_identity()
    return identity['Arn']

def get_boto3_session(region_name: Optional[str] = None):
    default_session = boto3.Session(region_name=region_name)
    config_path = os.path.expanduser(
        os.environ.get("AWS_CONFIG_FILE", "~/.aws/config")
    )

    if not default_session.available_profiles and os.environ.get("AWS_DEFAULT_REGION") is None and region_name is None:
        raise click.ClickException("No AWS profiles found. Please configure your AWS profile using the command: `aws configure sso`")
        
    if TENSORFUSE_SESSION in default_session.available_profiles:
        if not os.path.isfile(config_path):
            text =  f"AWS config file not found at {config_path}; using default session"
            click.echo(click.style(text, bold=True, fg=CliColors.WARNING.value))
            return default_session

        # load and parse
        cfg = configparser.ConfigParser()
        try:
            cfg.read(config_path)
        except Exception as e:
            text = f"Failed to read AWS config file ({e}); using default session"
            click.echo(click.style(text, bold=True, fg=CliColors.WARNING.value))
            return default_session

        profile_section = f"profile {TENSORFUSE_SESSION}"
        try:
            region = cfg.get(profile_section, "region")
            if region_name is not None:
                region = region_name
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            text = f"Profile or region not found in config ({e}); using default session"
            click.echo(click.style(text, bold=True, fg=CliColors.WARNING.value))
            return default_session

        # if we got a region, build a session with it
        if region:
            return boto3.Session(profile_name=TENSORFUSE_SESSION, region_name=region)
    return default_session

def get_session_profile_name(session_region: Optional[str] = None):
    session = get_boto3_session(region_name=session_region)
    return session.profile_name

def get_principal_arn_from_identity_center_arn(arn: str) -> str:
    arn_parts = arn.split(':')
    account_no = arn_parts[4]
    role_name = arn_parts[5].split('/')[1]
    principal_arn = f"arn:aws:iam::{account_no}:role/aws-reserved/sso.amazonaws.com/{role_name}"
    return principal_arn


def get_aws_user_principal_arn() -> str:
    sts = get_sts_client()
    identity = sts.get_caller_identity()
    if 'assumed-role' in identity['Arn']:
        return get_principal_arn_from_identity_center_arn(identity['Arn'])
    return identity['Arn']


def get_karpenter_namespace():
    return "kube-system"


def get_karpenter_version():
    return "0.37.0"


def get_credentials():
    session =  get_boto3_session()
    return session.get_credentials().get_frozen_credentials()


def are_credentials_valid(credentials):
    session = get_boto3_session()
    sts = session.client('sts', aws_access_key_id=credentials.access_key, aws_secret_access_key=credentials.secret_key,
                       aws_session_token=credentials.token)
    try:
        sts.get_caller_identity()
        return True
    except botocore.exceptions.ClientError as e:
        return False



def check_and_install_aws_cli():
    """Check if aws cli is installed and if not install it."""
    try:
        result = subprocess.run(["aws", "--version"], capture_output=True, text=True, check=True)

        # The version is in the format: "aws-cli/2.13.4 Python/3.9.6 Linux/x86_64"
        version_output = result.stdout.strip()
        # Extract the AWS CLI version using string manipulation
        aws_version = semver.VersionInfo.parse(version_output.split(" ")[0].split("/")[1])
        locked_cli_version = semver.VersionInfo.parse(LOCKED_AWS_CLI_VERSION)
        if (aws_version.major, aws_version.minor) < (locked_cli_version.major, locked_cli_version.minor):
            text = f"AWS CLI version is {aws_version}. Please upgrade AWS CLI to version above {LOCKED_AWS_CLI_VERSION}."
            click.echo(click.style(text, bold=True, fg=CliColors.ERROR.value))
            raise CLIVersionError(text)
    except Exception as e:
        if isinstance(e, CLIVersionError):
            raise e
        click.echo(
            click.style("aws-cli not found. Proceeding with installation. Might require sudo password.", bold=True,
                        fg=CliColors.WARNING.value))
        try:
            system = platform.system().lower()
            architecture = platform.machine()
            print(f"Detected operating system: {system.capitalize()}")
            print(f"Detected architecture: {architecture}")
            url = ""
            file_name = ""
            # Define the download URL and file name based on the OS
            if system == "linux":
                url = f"https://awscli.amazonaws.com/awscli-exe-linux-{architecture}-{LOCKED_AWS_CLI_VERSION}.zip"
                file_name = f"awscliv2-{LOCKED_AWS_CLI_VERSION}.zip"
            elif system == "darwin":
                url = f"https://awscli.amazonaws.com/AWSCLIV2-{LOCKED_AWS_CLI_VERSION}.pkg"
                file_name = f"AWSCLIV2-{LOCKED_AWS_CLI_VERSION}.pkg"
            else:
                print("Unsupported operating system. Please install AWS CLI manually.")
                raise Exception("Unsupported operating system.")
            # Download the installer
            print(f"Downloading AWS CLI installer from {url}...")
            subprocess.run(["curl", "-fsSL", url, "-o", file_name], check=True)
            print("AWS CLI installer downloaded successfully.")
            if system == "linux":
                # Unzip the installer
                print("Unzipping the AWS CLI installer...")
                subprocess.run(["unzip", "-o", file_name], check=True)
                print("AWS CLI installer unzipped successfully.")

                # Install the AWS CLI
                print("Installing AWS CLI...")
                subprocess.run(["sudo", "./aws/install"], check=True)
                print("AWS CLI installed successfully.")

            elif system == "darwin":
                # Use the macOS installer
                print("Installing AWS CLI using macOS package...")
                subprocess.run(["sudo", "installer", "-pkg", file_name, "-target", "/"], check=True)
                print("AWS CLI installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during installation: {e}")
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
            if os.path.exists("aws"):
                shutil.rmtree("aws")
            print("Clean-up completed.")

# https://github.com/eksctl-io/eksctl/blob/f4d4076ee22c9026a11a70434b802a7e0f61bd46/pkg/az/az.go#L24
# taken from eksctl source code
zoneIDsToAvoid = {
    "us-east-1": ["use1-az3"],
    "us-west-1": ["usw1-az2"],
    "ca-central-1": ["cac1-az3"],
    "cn-north-1": ["cnn1-az4"],
}


def get_eks_control_plane_available_zones_for_region():
    ec2 = get_ec2_client()
    region = get_session_region()
    response = ec2.describe_availability_zones()
    return [zone['ZoneName'] for zone in response['AvailabilityZones'] if zone['ZoneId'] not in zoneIDsToAvoid.get(region, []) and zone['ZoneType'] == "availability-zone"]


def get_availability_zones(region: str) -> List[str]:
    ec2_client = boto3.client('ec2', region_name=region)
    azs = ec2_client.describe_availability_zones(
        Filters=[{"Name": "region-name", "Values": [region]}, {"Name": "zone-type", "Values": ["availability-zone"]}],
        AllAvailabilityZones=False,
    )["AvailabilityZones"]

    zone_names = [az["ZoneName"] for az in azs if az["State"] == "available"]
    return zone_names
