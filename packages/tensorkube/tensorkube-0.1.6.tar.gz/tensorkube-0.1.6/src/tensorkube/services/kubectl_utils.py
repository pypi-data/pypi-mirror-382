import json
import os
import platform
import shutil
import subprocess

import click
import semver

from tensorkube.constants import CliColors, LOCKED_KUBECTL_VERSION, LOCKED_HELM_VERSION
from tensorkube.services.error import CLIVersionError


def check_and_install_kubectl():
    """Check if kubectl is installed and install it if it's not."""
    try:
        output = subprocess.run(["kubectl", "version", "--client", "-o", "json"], check=True, stdout=subprocess.PIPE)
        version_dict = json.loads(output.stdout.decode("utf-8"))
        version = semver.VersionInfo.parse(version_dict["clientVersion"]["gitVersion"].lstrip("v"))
        locked_kubectl_version = semver.VersionInfo.parse(LOCKED_KUBECTL_VERSION)
        print("kubectl is already installed.")
        if (version.major, version.minor) < (locked_kubectl_version.major, locked_kubectl_version.minor):
            text = f"kubectl version is {version}. Please upgrade kubectl to version above {LOCKED_KUBECTL_VERSION}."
            click.echo(click.style(text, bold=True, fg=CliColors.ERROR.value))
            raise CLIVersionError(text)
    except Exception as e:
        if isinstance(e, CLIVersionError):
            raise e
        click.echo(
            click.style("kubectl not found. Proceeding with installation. Might require sudo password.", bold=True,
                        fg=CliColors.WARNING.value))
        if platform.system() == "Darwin" or platform.system() == "Linux":
            try:
                system_name = platform.system().lower()
                architecture = "arm64" if 'arm' in platform.machine() else "amd64"
                install_kubectl(system_name, architecture)
            except subprocess.CalledProcessError as e:
                print("Unable to install kubectl. Please install kubectl manually.")
                raise e
        else:
            print("Unsupported operating system. Please install kubectl manually.")
            raise Exception('Unsupported operating system.')

        # Verify kubectl installation
        try:
            subprocess.run("kubectl version --client", shell=True, check=True)
            print("kubectl installed successfully.")
        except subprocess.CalledProcessError as e:
            print("kubectl installation failed. Please install kubectl manually.")
            raise e


def check_and_install_helm():
    """Check if helm is installed and install it if it's not."""
    try:
        output = subprocess.run(["helm", "version", "--template={{.Version}}"], check=True, stdout=subprocess.PIPE)
        version = semver.VersionInfo.parse(output.stdout.decode("utf-8").strip().lstrip("v"))
        locked_helm_version = semver.VersionInfo.parse(LOCKED_HELM_VERSION)
        print("Helm is already installed.")
        if (version.major, version.minor) < (locked_helm_version.major, locked_helm_version.minor):
            text = f"Helm version is {version}. Please upgrade Helm to version above {LOCKED_HELM_VERSION}."
            click.echo(click.style(text, bold=True, fg=CliColors.ERROR.value))
            raise CLIVersionError(text)
    except Exception as e:
        if isinstance(e, CLIVersionError):
            raise e
        click.echo(click.style("Helm not found. Proceeding with installation. Might require sudo password.", bold=True,
                               fg=CliColors.WARNING.value))
        if platform.system() == "Darwin" or platform.system() == "Linux":
            try:
                system_name = platform.system().lower()
                architecture = "arm64" if 'arm' in platform.machine() else "amd64"
                install_helm_using_downloader(system_name=system_name, architecture=architecture)
            except Exception as e:
                click.echo(f"Error while installing helm: {e}. Please install helm manually", err=True)
                raise e
        else:
            print("Unsupported operating system. Please install helm manually.")
            raise Exception('Unsupported operating system.')

        # Verify helm installation
        try:
            subprocess.run(["helm", "version"], check=True)
            print("Helm installed successfully.")
        except subprocess.CalledProcessError as e:
            print("Helm installation failed. Please install helm manually.")
            raise e


def install_helm_using_downloader(system_name, architecture):
    try:
        # Download Helm installer script
        click.echo("Downloading Helm installer script...")

        # Install Helm by downloading specific version
        click.echo(f"Downloading Helm {LOCKED_HELM_VERSION} for {system_name}-{architecture} architecture...")

        download_url = f"https://get.helm.sh/helm-v{LOCKED_HELM_VERSION}-{system_name}-{architecture}.tar.gz"
        tarball_name = f"helm-{LOCKED_HELM_VERSION}-{system_name}-{architecture}.tar.gz"
        subprocess.run(f"curl -fsSL {download_url} -o {tarball_name}", shell=True, check=True)

        click.echo("Helm tarball downloaded successfully.")

        # Extract the tarball
        click.echo("Extracting Helm tarball...")
        subprocess.run(f"tar -zxvf {tarball_name}", shell=True, check=True)

        # Move the helm binary to /usr/local/bin
        click.echo("Moving Helm binary to /usr/local/bin...")
        subprocess.run(f"sudo mv {system_name}-{architecture}/helm /usr/local/bin/", shell=True, check=True)

        # Clean up the downloaded tarball and extracted files
        click.echo("Cleaning up downloaded files...")
        os.remove(tarball_name)
        shutil.rmtree(f"{system_name}-{architecture}")
        subprocess.run(f"rm -rf helm-{LOCKED_HELM_VERSION}-{system_name}-{architecture}", shell=True, check=True)

    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred: {e}", err=True)
        raise e
    except OSError as e:
        click.echo(f"Error deleting the installer script: {e}", err=True)


def install_kubectl(system, architecture):
    valid_architectures = {"amd64", "arm64"}
    if architecture not in valid_architectures:
        click.echo(f"Invalid architecture: {architecture}. Valid options are: {valid_architectures}", err=True)
        return

    try:
        # Download kubectl binary for the specified architecture
        click.echo(f"Downloading kubectl binary for {architecture} architecture...")
        cmd = f"curl -LO https://dl.k8s.io/release/v{LOCKED_KUBECTL_VERSION}/bin/{system}/{architecture}/kubectl"
        subprocess.run(
            cmd,
            shell=True, check=True)
        click.echo(f"kubectl binary for {architecture} downloaded successfully.")

        # Make the binary executable
        subprocess.run("chmod +x kubectl", shell=True, check=True)

        # Move it to /usr/local/bin
        subprocess.run("sudo mv kubectl /usr/local/bin/", shell=True, check=True)

        click.echo(f"kubectl for {architecture} installed successfully.")

    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred: {e}", err=True)
