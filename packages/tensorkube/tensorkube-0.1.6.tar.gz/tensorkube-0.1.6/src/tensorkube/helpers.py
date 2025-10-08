import base64
import json
import os
import re
from typing import Optional

import click
import requests

from tensorkube.constants import NAMESPACE, SERVICE_ACCOUNT_NAME, get_base_login_url
from tensorkube.services.eks_service import get_cluster_oidc_issuer_url
from tensorkube.services.iam_service import create_s3_csi_driver_role, attach_role_policy


def is_valid_email(email:str) -> bool:
    if not email or not isinstance(email, str):
        return False
    if re.match(r"^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return True
    return False

def create_mountpoint_driver_role_with_policy(cluster_name, account_no, role_name, policy_name,
                                              service_account_name=SERVICE_ACCOUNT_NAME, namespace=NAMESPACE):
    oidc_issuer_url = get_cluster_oidc_issuer_url(cluster_name)
    create_s3_csi_driver_role(account_no, role_name, oidc_issuer_url, namespace, service_account_name)
    attach_role_policy(account_no, policy_name, role_name)


def get_base64_encoded_docker_config(username: str, password: str, email: str):
    auth = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")

    docker_config_dict = {"auths": {
        "https://index.docker.io/v1/": {"username": username, "password": password, "email": email, "auth": auth, }}}

    base64_encoded_docker_config = base64.b64encode(json.dumps(docker_config_dict).encode("utf-8")).decode("utf-8")
    return base64_encoded_docker_config


def sanitise_name(name: str):
    return name.replace("_", "-").replace(" ", "-").lower()


def sanitise_assumed_role_arn(arn: str):
    arn = arn.replace('assumed-role', 'role')
    last_slash_index = arn.rfind('/')
    if last_slash_index != -1:
        arn = arn[:last_slash_index]
    return arn


def track_event(event_name: str, event_properties: dict) -> bool:
    try:
        try:
            user_email, _ = verify_user()
        except Exception as e:
            user_email = None
        if not user_email:
            return False

        base_url = get_base_login_url()
        url = base_url + '/tensorkube/track/package-event/'

        body = {"id": user_email, "event": event_name, "properties": event_properties}
        x = requests.post(url, json=body)
        return True
    except Exception as e:
        click.echo(f"Error while tracking event: {e}")


def extract_workdir_from_dockerfile(dockerfile_path: str) -> Optional[str]:
    with open(dockerfile_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("WORKDIR"):
                return line.split(" ")[1].replace("\n", "")

    return None


def extract_command_from_dockerfile(dockerfile_path: str) -> Optional[str]:
    command = None
    with open(dockerfile_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("CMD") or line.startswith("ENTRYPOINT"):
                command = line.split(" ")[1:]

    if not command:
        return None

    command = " ".join(command)
    command = command.replace('[', "").replace(']', "").replace('"', '').replace(",", " ").replace("\n", "")
    return command


def verify_user(session_id: str = None, token: str = None, ) -> Optional[tuple[str, str|None]]:
    if not (token and session_id):
        token = os.getenv("TENSORKUBE_TOKEN", None)
        session_id = os.getenv("TENSORKUBE_SESSION_ID", None)
        if not (token and session_id):
            token_path = os.path.expanduser('~/.tensorkube/token')
            os.makedirs(os.path.dirname(token_path), exist_ok=True)

            if not os.path.exists(token_path):
                return None, None
            with open(token_path, "r") as f:
                token = f.readline().split("=")[1].replace("\n", "")
                session_id = f.readline().split("=")[1].replace("\n", "")
    if not (token and session_id):
        click.echo("Can't find tensorkube credentials.")
        return None, None

    base_url = get_base_login_url()
    response = requests.get(base_url + '/tensorkube/verify-package-user/',
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'session_id': session_id, 'token': token}))
    if response.status_code == 200:
        body = response.json()
        email = body.get('email', None)
        region = body.get('region', None)
        return email, region
    else:
        return None, None


def save_user_credentials(session_id: str, token: str):
    token_path = os.path.expanduser('~/.tensorkube/token')
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    with open(token_path, "w") as f:
        f.write("token=" + token + "\n")
        f.write("session_id=" + session_id + "\n")


def create_user_access_entry(principal_arn: str):
    base_url = get_base_login_url()
    url = base_url + '/tensorkube/permissions/create-access-entry-tensorkube-sync/'
    token = os.getenv("TENSORKUBE_TOKEN", None)
    session_id = os.getenv("TENSORKUBE_SESSION_ID", None)
    if not (token and session_id):
        token_path = os.path.expanduser('~/.tensorkube/token')
        os.makedirs(os.path.dirname(token_path), exist_ok=True)

        if not os.path.exists(token_path):
            return None
        with open(token_path, "r") as f:
            token = f.readline().split("=")[1].replace("\n", "")
            session_id = f.readline().split("=")[1].replace("\n", "")
    if not (token and session_id):
        click.echo("Can't find tensorkube credentials.")
        click.echo("Please run `tensorkube login` to login to the cluster.")
        return None
    response = requests.post(url=url, json={'arn': principal_arn, 'sessionId': session_id, 'token': token})
    return response.status_code == 200


def get_tensorkube_token_and_session_id():
    token = os.getenv("TENSORKUBE_TOKEN", None)
    session_id = os.getenv("TENSORKUBE_SESSION_ID", None)
    if not (token and session_id):
        token_file_path = os.path.expanduser('~/.tensorkube/token')
        if not os.path.exists(token_file_path):
            return None, None
        with open(token_file_path, "r") as f:
            token = f.readline().split("=")[1].replace("\n", "")
            session_id = f.readline().split("=")[1].replace("\n", "")
            return token, session_id
    return token, session_id


def get_user_cloud_account_id_and_org_id(token: str, session_id: str):
    if not token or not session_id:
        return None, None
    base_url = get_base_login_url()
    response = requests.get(base_url + '/tensorkube/user/get-user-info/',
                            headers={
                                'Content-Type': 'application/json',
                                'session-id': session_id,
                                'token': token},
                            )
    if response.status_code == 200:
        body = response.json()
        cloud_account_id = body.get("cloud_account_id", None)
        org_id = body.get("default_org_id", None)
        if not cloud_account_id or not org_id:
            return None, None
        return cloud_account_id, org_id
    else:
        return None, None
