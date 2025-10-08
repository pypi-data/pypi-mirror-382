import os
import subprocess
import time
import json
from threading import Thread, Event
from typing import List, Optional, Dict, Any
from copy import deepcopy

import boto3
import click
import yaml
from kubernetes import client, config, utils, watch, dynamic
from kubernetes.client import ApiTypeError, ApiException
from pkg_resources import resource_filename

from tensorkube.constants import NAMESPACE, PodStatus, BUILD_TOOL, DEFAULT_NAMESPACE, TENSORFUSE_NAMESPACES, \
    get_cluster_name, CliColors
from tensorkube.services.aws_service import get_aws_account_id, get_eks_client, get_session_region, get_session_profile_name
import os

def get_s3_pv_name(env_name: Optional[str] = None):
    if env_name and env_name != DEFAULT_NAMESPACE:
        return f"s3-pv-env-{env_name}"
    return "s3-pv"


def get_s3_claim_name(env_name: Optional[str] = None):
    if env_name and env_name != DEFAULT_NAMESPACE:
        return f"s3-claim-env-{env_name}"
    return "s3-claim"


def get_efs_claim_name(env_name: Optional[str] = None):
    if env_name and env_name != DEFAULT_NAMESPACE:
        return f"efs-pvc-env-{env_name}"
    return "efs-pvc"


def create_namespace(namespace_name, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    namespace = client.V1Namespace()
    namespace.metadata = client.V1ObjectMeta(name=namespace_name)
    v1 = client.CoreV1Api(k8s_api_client)
    v1.create_namespace(body=namespace)


def create_docker_registry_secret(secret_name: str, namespace: str, base64_encoded_dockerconfigjson: str,
                                  context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)

    secret = client.V1Secret()
    secret.api_version = "v1"
    secret.kind = "Secret"
    secret.metadata = client.V1ObjectMeta(name=secret_name, namespace=namespace)
    secret.type = "kubernetes.io/dockerconfigjson"
    secret.data = {".dockerconfigjson": base64_encoded_dockerconfigjson}

    v1.create_namespaced_secret(namespace=namespace, body=secret)


def create_aws_secret(credentials, namespace: str = DEFAULT_NAMESPACE, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    secret_name = "aws-secret"

    secret = client.V1Secret()
    secret.metadata = client.V1ObjectMeta(name=secret_name)
    secret.string_data = {"AWS_ACCESS_KEY_ID": credentials.access_key, "AWS_SECRET_ACCESS_KEY": credentials.secret_key,
                          "AWS_SESSION_TOKEN": credentials.token}

    try:
        # Check if the secret already exists
        existing_secret = v1.read_namespaced_secret(name=secret_name, namespace=namespace)
        # If the secret exists, update it
        v1.replace_namespaced_secret(name=secret_name, namespace=namespace, body=secret)
        print(f"Secret {secret_name} updated successfully in namespace {namespace}.")
    except ApiException as e:
        if e.status == 404:
            # Secret does not exist, create it
            v1.create_namespaced_secret(namespace=namespace, body=secret)
            print(f"Secret {secret_name} created successfully in namespace {namespace}.")
        else:
            print(f"An error occurred: {e}")
            raise e


def delete_aws_secret(namespace: str = DEFAULT_NAMESPACE, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    try:
        v1.read_namespaced_secret(name="aws-secret", namespace=namespace)
    except client.ApiException as e:
        if e.status == 404:
            return
        else:
            raise
    v1.delete_namespaced_secret(name="aws-secret", namespace=namespace)


def create_build_pv_and_pvc(bucket_name: str, env: Optional[str] = None,
                            context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    pv_config_file_path = resource_filename('tensorkube', 'configurations/build_configs/pv.yaml')
    pvc_config_file_path = resource_filename('tensorkube', 'configurations/build_configs/pvc.yaml')
    with open(pv_config_file_path) as f:
        pv = yaml.safe_load(f)
    with open(pvc_config_file_path) as f:
        pvc = yaml.safe_load(f)

    env_namespace = env if env else DEFAULT_NAMESPACE

    pv['spec']['mountOptions'] = ["allow-delete", "region {}".format(get_session_region())]
    pv['spec']['csi']['volumeAttributes']['bucketName'] = bucket_name
    pv['metadata']['namespace'] = env_namespace
    pv['metadata']['name'] = get_s3_pv_name(env_name=env)

    pvc['metadata']['namespace'] = env_namespace
    pvc['metadata']['name'] = get_s3_claim_name(env_name=env)
    pvc['spec']['volumeName'] = get_s3_pv_name(env_name=env)

    v1 = client.CoreV1Api(k8s_api_client)

    pv_name = pv['metadata']['name']
    pvc_name = pvc['metadata']['name']

    try:
        # Check if the PV already exists
        v1.read_persistent_volume(name=pv_name)
        click.echo(f"PersistentVolume {pv_name} already exists. Skipping creation.")
    except ApiException as e:
        if e.status == 404:
            utils.create_from_dict(k8s_api_client, pv)
            click.echo(f"PersistentVolume {pv_name} created successfully.")
        else:
            click.echo(f"An error occurred while checking PersistentVolume: {e}")
            raise e

    try:
        # Check if the PVC already exists
        v1.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=env_namespace)
        click.echo(f"PersistentVolumeClaim {pvc_name} already exists in namespace {env_namespace}. Skipping creation.")
    except ApiException as e:
        if e.status == 404:
            # PVC does not exist, proceed to create
            utils.create_from_dict(k8s_api_client, pvc)
            click.echo(f"PersistentVolumeClaim {pvc_name} created successfully in namespace {env_namespace}.")
        else:
            click.echo(f"An error occurred while checking PersistentVolumeClaim: {e}")
            raise e


def apply_image_cleanup_job(sanitised_project_name: str, image_tags: List[str], env: Optional[str] = None,
                            context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    cleanup_config_file_path = resource_filename('tensorkube', 'configurations/build_configs/efs_cleanup_pod.yaml')
    with open(cleanup_config_file_path) as f:
        cleanup_config = yaml.safe_load(f)
    cleanup_config['metadata']['name'] = 'cleanup-{}'.format(sanitised_project_name)
    namespace_to_use = env if env else DEFAULT_NAMESPACE  # Replace 'default' with your default namespace if needed
    cleanup_config['metadata']['namespace'] = namespace_to_use

    for volume in cleanup_config['spec']['template']['spec']['volumes']:
        if volume['name'] == 'efs-pvc':
            volume['persistentVolumeClaim']['claimName'] = get_efs_claim_name(env_name=env)

    cleanup_config['spec']['template']['spec']['containers'][0]['command'] = ["/bin/sh", "-c",
                                                                              f"""cd /mnt/efs/images/{sanitised_project_name}
        echo 'Deleting all images except' {", ".join(image_tags)}
        find . -mindepth 1 -maxdepth 1 -type d ! -name {" ! -name ".join(image_tags)} -exec rm -rf {{}} +
        echo 'Deletion completed' """]

    utils.create_from_dict(k8s_api_client, cleanup_config)
    click.echo('Deployed a delete config job')


def get_build_job_pod_name(sanitised_project_name: str, namespace: str = NAMESPACE, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    pods = v1.list_namespaced_pod(namespace=namespace)
    for pod in pods.items:
        if pod.metadata.name.startswith("{}-{}".format(BUILD_TOOL, sanitised_project_name)):
            return pod.metadata.name
    return None


def check_pod_status(pod_name, namespace, context_name: Optional[str] = None):
    # Load kube config
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Create a Kubernetes API client
    v1 = client.CoreV1Api(k8s_api_client)

    # Get the status of the pod
    pod_status = v1.read_namespaced_pod_status(name=pod_name, namespace=namespace)

    # Return the status of the pod
    return pod_status.status.phase


def find_and_delete_old_job(job_name: str, namespace: str = DEFAULT_NAMESPACE, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    job_pod_name = get_pod_name_corresponing_to_job(job_name, namespace)
    if job_pod_name:
        click.echo("Terminating pod {} corresponding to job {}".format(job_pod_name, job_name))
        v1.delete_namespaced_pod(name=job_pod_name, namespace=namespace)

    v1 = client.BatchV1Api(k8s_api_client)
    jobs = v1.list_namespaced_job(namespace=namespace)
    for job in jobs.items:
        if job.metadata.name == job_name:
            v1.delete_namespaced_job(name=job.metadata.name, namespace=namespace)
            return True

    return True


def delete_all_jobs_in_namespace(namespace: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.BatchV1Api(k8s_api_client)
    jobs = v1.list_namespaced_job(namespace=namespace)
    for job in jobs.items:
        v1.delete_namespaced_job(name=job.metadata.name, namespace=namespace)
        print(f"Job {job.metadata.name} deletion initiated.")

        # Wait for the job to be deleted
        while True:
            try:
                v1.read_namespaced_job(name=job.metadata.name, namespace=namespace)
                time.sleep(1)  # Wait for 1 second before checking again
            except ApiException as e:
                if e.status == 404:
                    print(f"Job {job.metadata.name} deleted successfully.")
                    break
                else:
                    print(f"Error while waiting for deletion of job {job.metadata.name}: {e}")
                    raise e
    return True


def start_streaming_pod(pod_name, namespace, status=None, container_name=None, retry_number: int = 0,
                        max_retries: int = 4, context_name: Optional[str] = None, stop_event: Optional[Event] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    # Create a stream to the pod
    # Initialize the Watch class
    watch_client = watch.Watch()
    # Stream events until the pod is ready
    print(f"Streaming events for pod {pod_name} in namespace {namespace}")
    try:
        events_streamed_upto_index = 0

        while True:
            if stop_event and stop_event.is_set():
                print("Event streaming stopped.")
                return
            pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            events = v1.list_namespaced_event(namespace=namespace, field_selector=f'involvedObject.name={pod_name}')
            for event in events.items[events_streamed_upto_index:]:
                print("Event: %s %s" % (event.type, event.message))
            events_streamed_upto_index = len(events.items)
            if pod.status.phase != 'Pending':
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print("Log streaming stopped by user")
        return

    print(f"Streaming logs for pod {pod_name} in namespace {namespace}")

    try:
        last_log_printed = None
        while True:
            if stop_event and stop_event.is_set():
                print("Stop event received, stopping log streaming.")
                return
            try:
                logs = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, container=container_name,
                                                  since_seconds=5)
            except UnicodeDecodeError:
                print(f'Got invalid characters in log. trying to process.')
                # If automatic decoding fails, fetch raw bytes and decode with error replacement.
                response = v1.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    container=container_name,
                    since_seconds=5,
                    _preload_content=False
                )
                logs = response.data.decode('utf-8', errors='replace')
            logs_by_line = logs.split('\n')
            logs_by_line = logs_by_line[:len(logs_by_line) - 1]
            if logs_by_line:
                if not last_log_printed:
                    for log in logs_by_line:
                        print(log)
                else:
                    found_last_printed_log = False
                    for log in logs_by_line:
                        if found_last_printed_log:
                            print(log)
                            continue
                        if log == last_log_printed:
                            found_last_printed_log = True
                            continue
                        continue
                    if not found_last_printed_log:
                        for log in logs_by_line:
                            print(log)
                last_log_printed = logs_by_line[-1]

            pod = v1.read_namespaced_pod_status(name=pod_name, namespace=namespace)
            if pod.status.phase == PodStatus.FAILED.value:
                print(f"Pod {pod_name} in namespace {namespace} failed.")
                return
            if status:
                if status.value == pod.status.phase:
                    print(f"Pod {pod_name} has reached {status.value} state")
                    return
            time.sleep(1)
    except client.ApiException as e:
        if e.status == 404:
            print(f"Pod {pod_name} not found in namespace {namespace}")
        else:
            raise
    except KeyboardInterrupt:
        print("Log streaming stopped by user")
        return
    except ApiTypeError as e:
        print(f"An error occurred while streaming logs for pod {pod_name} in namespace {namespace}")
        print(e)
        return
    except Exception as e:
        print(f"An unexpected error occurred for pod {pod_name} in namespace {namespace}")
        print(e)
        raise


def get_pod_status_from_job(job_name: str, namespace: str = DEFAULT_NAMESPACE, context_name: str = None) -> Optional[
    str]:
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.BatchV1Api(k8s_api_client)
    try:
        job = v1.read_namespaced_job(name=job_name, namespace=namespace)
        if job.status.failed == 1:
            return PodStatus.FAILED.value
        if job.status.succeeded == 1:
            return PodStatus.SUCCEEDED.value
        return None
    except ApiException as e:
        if e.status == 404:
            print(f"Job {job_name} not found in namespace {namespace}")
            return PodStatus.FAILED.value
        else:
            raise e

def set_stop_event_post_ksvc_ready(service_name, namespace, stop_event, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None

    k8s_api_client = config.new_client_from_config(context=context_name)
    custom_api = client.CustomObjectsApi(k8s_api_client)
    v1 = client.CoreV1Api(k8s_api_client)
    revision_name = None

    group = "serving.knative.dev"
    version = "v1"
    plural = "services"

    max_wait_seconds = 1200  # maximum time to wait (adjust as needed)
    start_time = time.time()

    while not stop_event.is_set():
        try:
            ksvc = custom_api.get_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
                name=service_name
            )
            if ksvc['status']['latestCreatedRevisionName']:
                revision_name = ksvc['status']['latestCreatedRevisionName']
            conditions = ksvc.get("status", {}).get("conditions", [])
            for condition in conditions:
                if condition.get("type") == "Ready" and condition.get("status") == "True":
                    print(f"Service {service_name} is ready.")
                    stop_event.set()
                    return
        except client.ApiException as e:
            if e.status == 404:
                print(f"Service {service_name} not found in namespace {namespace}")
            else:
                raise

        # fallback to service name if no latest ready revision name is found
        if not revision_name:
            revision_name = service_name
            pods = v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f'serving.knative.dev/service={service_name}'
            )
        else:
        # Check pods for CrashLoopBackOff status
            pods = v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f'serving.knative.dev/revision={revision_name}'
            )
            
        for pod in pods.items:
            for cs in pod.status.container_statuses or []:
                waiting_state = cs.state.waiting
                if waiting_state and waiting_state.reason == "CrashLoopBackOff":
                    click.echo(click.style(f"Pod {pod.metadata.name} is in CrashLoopBackOff state.", fg='red', bold=True))
                    stop_event.set()
                    return
        # Check if we've exceeded the maximum wait time
        if (time.time() - start_time) > max_wait_seconds:
            click.echo(click.style(f"Service {service_name} did not become ready within {max_wait_seconds} seconds. Exiting.", fg='red', bold=True))
            stop_event.set()
            return
        time.sleep(5)

def start_streaming_service(service_name, namespace, context_name: Optional[str] = None):
    # Load kube config
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Create a Kubernetes API client
    v1 = client.CoreV1Api(k8s_api_client)

    # Stream the service status
    try:
        pod_name = None
        while pod_name is None:
            pods = v1.list_namespaced_pod(namespace, label_selector=f'serving.knative.dev/service={service_name}')
            if pods.items:
                sorted_pods = sorted(pods.items, key=lambda x: x.metadata.name, reverse=True)
                pod_name = sorted_pods[0].metadata.name
                print(f"Found pod {pod_name} for service {service_name}.")
            else:
                time.sleep(5)

        # Create an Event to signal the log streaming thread when the service is ready.
        stop_event = Event()
        # Start streaming the logs from the pod
        streaming_thread = Thread(target=start_streaming_pod,
                        args=(pod_name, namespace, None, 'user-container'),
                        kwargs={'stop_event': stop_event, 'context_name': context_name})
        streaming_thread.start()
        set_stop_event_post_ksvc_ready(
            service_name=service_name,
            namespace=namespace,
            stop_event=stop_event,
            context_name=context_name
        )
        streaming_thread.join()  # Ensure the streaming thread is properly joined.
    except client.ApiException as e:
        if e.status == 404:
            print(f"Service {service_name} not found in namespace {namespace}")
        else:
            raise
    except KeyboardInterrupt:
        print("Service status streaming stopped by user")
        return
    except Exception as e:
        print("An unexpected error occurred for service status streaming")
        raise


def check_nodes_ready(label_selector):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    ready_nodes = []
    nodes = v1.list_node(label_selector=label_selector).items
    for node in nodes:
        for condition in node.status.conditions:
            if condition.type == "Ready" and condition.status == "True":
                ready_nodes.append(node.metadata.name)
    return len(ready_nodes) == len(nodes), ready_nodes


def evict_pods_from_node(node_name, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    core_api = client.CoreV1Api(k8s_api_client)
    pods = core_api.list_pod_for_all_namespaces(field_selector=f'spec.nodeName={node_name}').items
    for pod in pods:
        if pod.metadata.owner_references and any(owner.kind == "DaemonSet" for owner in pod.metadata.owner_references):
            continue
        eviction = client.V1Eviction(
            metadata=client.V1ObjectMeta(name=pod.metadata.name, namespace=pod.metadata.namespace))
        retry_attempts = 0
        max_retries = 5
        backoff_delay = 1  # Start with 1 second delay
        while retry_attempts < max_retries:
            try:
                core_api.create_namespaced_pod_eviction(name=pod.metadata.name, namespace=pod.metadata.namespace,
                                                        body=eviction)
                print(f"Evicting pod {pod.metadata.name} from node {node_name}.")
                break  # Eviction successful, break out of the retry loop
            except ApiException as e:
                if e.status == 429:  # Too Many Requests
                    print(
                        f"Rate limit exceeded when evicting pod {pod.metadata.name}: {e}. Retrying in {backoff_delay} seconds...")
                    time.sleep(backoff_delay)
                    backoff_delay *= 2  # Exponential backoff
                    retry_attempts += 1
                else:
                    print(f"Exception when evicting pod {pod.metadata.name}: {e}")
                    break  # Break on any other exception
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break
        if retry_attempts == max_retries:
            print(f"Failed to evict pod {pod.metadata.name} after {max_retries} attempts.")


def drain_and_delete_node(node_name, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    core_api = client.CoreV1Api(k8s_api_client)
    # Cordon the node
    body = {"spec": {"unschedulable": True}}
    core_api.patch_node(node_name, body)
    click.echo(f"Cordoned node {node_name}")

    # Evict all pods from the node
    evict_pods_from_node(node_name)
    click.echo(f"All pods evicted from node {node_name}")

    # delete the node
    core_api.delete_node(node_name)


def get_nodes_not_using_bottlerocket(ec2_node_class_label, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)

    # List all nodes
    nodes = v1.list_node().items

    filtered_nodes = []
    for node in nodes:
        labels = node.metadata.labels
        os_image = node.status.node_info.os_image

        # Check if the node belongs to the specified EC2NodeClass
        if labels.get('karpenter.sh/nodepool') == ec2_node_class_label:
            # Check if the node is using Bottlerocket AMI
            if 'bottlerocket' not in os_image.lower():
                filtered_nodes.append(node.metadata.name)

    return filtered_nodes


def delete_pv_using_name(pv_name: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)

    timeout = 60  # Timeout in seconds
    start_time = time.time()

    try:
        v1.delete_persistent_volume(name=pv_name)
        while time.time() - start_time < timeout:
            try:
                v1.read_persistent_volume(name=pv_name)
                print(f"Waiting for PV {pv_name} to be deleted...")
                time.sleep(5)  # Wait for 5 seconds before checking again
            except ApiException as e:
                if e.status == 404:
                    print(f"PersistentVolume {pv_name} successfully deleted.")
                    return
                else:
                    raise
        print(f"Timeout reached while waiting for PV {pv_name} to be deleted.")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            print(f"PersistentVolume {pv_name} not found")
        else:
            raise e


def delete_pvc_using_name_and_namespace(pvc_name: str, namespace: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    timeout = 60  # Timeout in seconds
    start_time = time.time()
    try:
        v1.delete_namespaced_persistent_volume_claim(name=pvc_name, namespace=namespace)
        while time.time() - start_time < timeout:
            try:
                v1.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=namespace)
                print(f"Waiting for PVC {pvc_name} to be deleted...")
                time.sleep(5)  # Wait for 5 seconds before checking again
            except ApiException as e:
                if e.status == 404:
                    print(f"PersistentVolumeClaim {pvc_name} successfully deleted from namespace {namespace}.")
                    return
                else:
                    raise
        print(f"Timeout reached while waiting for PVC {pvc_name} to be deleted.")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            print(f"PersistentVolumeClaim {pvc_name} not found in namespace {namespace}")
        else:
            raise e


def check_pvc_exists_by_name(claim_name, namespace, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Create an instance of the CoreV1Api
    v1 = client.CoreV1Api(k8s_api_client)

    try:
        # Attempt to read the specified PVC in the given namespace
        v1.read_namespaced_persistent_volume_claim(name=claim_name, namespace=namespace)
        return True  # PVC exists
    except ApiException as e:
        if e.status == 404:
            return False  # PVC does not exist
        else:
            print(f"An error occurred: {e}")
            raise e


def get_image_tags_to_retain(sanitised_project_name: str, service_name: str, namespace: str,
                             context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    k8s_client = client.CustomObjectsApi(k8s_api_client)
    click.echo(f"Cleaning up old image tags for project {sanitised_project_name}, service {service_name}.")
    group = "serving.knative.dev"
    version = "v1"
    plural = "revisions"

    # List all revisions for the service
    # Define the label selector string based on the service name
    label_selector = f"serving.knative.dev/service={service_name}"

    # Use the label selector in the list_namespaced_custom_object call to directly filter revisions
    service_revisions = \
        k8s_client.list_namespaced_custom_object(group, version, namespace, plural, label_selector=label_selector)[
            'items']

    # Sort all revisions by configurationGeneration in descending order
    all_revisions_sorted = sorted(service_revisions, key=lambda x: int(
        x['metadata']['labels']['serving.knative.dev/configurationGeneration']), reverse=True)

    # Identify all "Ready" revisions
    ready_revisions = [rev for rev in all_revisions_sorted if any(
        cond['type'] == 'Ready' and cond['status'] == 'True' for cond in rev['status']['conditions'])]

    # Find the index of the latest "Ready" revision
    if ready_revisions:
        latest_ready_revision = ready_revisions[0]
        latest_ready_index = all_revisions_sorted.index(latest_ready_revision)
    else:
        latest_ready_index = -1

    # Determine active revisions
    active_revisions = ready_revisions[:3]  # Last three "Ready" revisions
    if latest_ready_index != -1:
        active_revisions += all_revisions_sorted[:latest_ready_index]  # Any newer revisions

    # Find the index for slicing stale revisions
    if len(ready_revisions) >= 3:
        third_last_ready_index = all_revisions_sorted.index(ready_revisions[2])
    elif len(ready_revisions) == 2:
        third_last_ready_index = all_revisions_sorted.index(ready_revisions[1])
    else:
        third_last_ready_index = latest_ready_index

    # Determine stale revisions, ensuring last three "Ready" revisions are not included
    stale_revisions = all_revisions_sorted[third_last_ready_index + 1:] if third_last_ready_index != -1 else []
    retained_revisions = all_revisions_sorted[
                         :third_last_ready_index + 1] if third_last_ready_index != -1 else all_revisions_sorted

    image_tags_to_retain = []
    image_tags_to_delete = []
    for rev in retained_revisions:
        # check if this exists yaml_dict['spec']['template']['metadata']['annotations']['image_tag'] = image_tag
        if rev['metadata']['annotations'] and 'image_tag' in rev['metadata']['annotations']:
            image_tags_to_retain.append(rev['metadata']['annotations']['image_tag'])
            click.echo(f'Retaining revision {rev["metadata"]["name"]}')
        else:
            print(f'No image tag found for revision {rev["metadata"]["name"]}')

    for rev in stale_revisions:
        # check if this exists yaml_dict['spec']['template']['metadata']['annotations']['image_tag'] = image_tag
        if rev['metadata']['annotations'] and 'image_tag' in rev['metadata']['annotations']:
            image_tags_to_delete.append(rev['metadata']['annotations']['image_tag'])
            click.echo(f'Queuing revision {rev["metadata"]["name"]} for deletion')
        else:
            print(f'No image tag found for revision {rev["metadata"]["name"]}')
        try:
            # Delete the revision
            k8s_client.delete_namespaced_custom_object(group=group, version=version, namespace=namespace, plural=plural,
                                                       name=rev['metadata']['name'], body=client.V1DeleteOptions()
                                                       # You can customize this if needed
                                                       )
        except client.exceptions.ApiException as e:
            print(f"Failed to delete revision {rev['metadata']['name']}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while deleting revision {rev['metadata']['name']}: {e}")
    return image_tags_to_retain



def get_pod_name_corresponing_to_job(job_name: str, namespace: str = DEFAULT_NAMESPACE,
                                     context_name: Optional[str] = None, max_retries=5) -> Optional[str]:
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    for attempt in range(max_retries):
        pods = v1.list_namespaced_pod(namespace=namespace)
        for pod in pods.items:
            if not pod.metadata.owner_references:
                continue
            for owner in pod.metadata.owner_references:
                if owner.name == job_name:
                    return pod.metadata.name
        backoff_delay = 2 ** attempt
        time.sleep(backoff_delay)
    return None


def create_new_namespace(env_name: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    namespace = client.V1Namespace()
    namespace.metadata = client.V1ObjectMeta(name=env_name)
    v1 = client.CoreV1Api(k8s_api_client)
    v1.create_namespace(body=namespace)
    click.echo(f"Namespace {env_name} created successfully.")


def delete_namespace(env_name: str, context_name: Optional[str] = None):
    if env_name == DEFAULT_NAMESPACE or env_name in TENSORFUSE_NAMESPACES:
        click.echo(f"Cannot delete namespace {env_name}")
        return
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    v1.delete_namespace(name=env_name)
    click.echo(f"Namespace {env_name} deleted successfully.")


def list_all_namespaces(context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    namespaces = v1.list_namespace().items
    return [namespace.metadata.name for namespace in namespaces]


def ssh_into_pod(pod_name: str, namespace: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None

    command = ["kubectl", "--context", f"{context_name}", "exec", "-it", pod_name, "-n", namespace, "-c",
               "user-container", "--", "sh"]
    subprocess.run(command)


def ssh_into_pod_with_podman(pod_name: str, namespace: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    command = ["kubectl", "--context", f"{context_name}", "exec", "-it", pod_name, "-n", namespace, "-c",
               "user-container", "--", "sh", "-c", "podman exec -it $(podman ps -q) /bin/bash"]
    subprocess.run(command)


def get_tensorkube_cluster_context_name() -> Optional[str]:
    # Get the list of all contexts and the current context
    contexts, current_context = config.list_kube_config_contexts()

    tensorkube_contexts = [context['name'] for context in contexts if (
            f"cluster/{get_cluster_name()}" in context['name'] or f"@{get_cluster_name()}" in context['name'])]
    if len(tensorkube_contexts) == 1:
        return tensorkube_contexts[0]
    elif len(tensorkube_contexts) > 1:
        valid_context = remove_invalid_contexts(tensorkube_contexts)
        return valid_context
    else:
        click.echo(click.style(f"No context found for {get_cluster_name()} cluster.", fg="red"))
        click.echo(
            f"If you have already created a {get_cluster_name()} cluster and have access to it, please run the command")
        click.echo(click.style("tensorkube sync", fg="cyan"))
        click.echo("Otherwise, please create a new cluster using the command")
        click.echo(click.style("tensorkube configure", fg="cyan"))
        return None


def remove_invalid_contexts(tensorkube_contexts: List[str]) -> Optional[str]:
    for context in tensorkube_contexts:
        try:
            command = ["kubectl", "--context", f"{context}", "get", "pods"]
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            command = ["kubectl", "config", "delete-context", context]
            subprocess.run(command)
            tensorkube_contexts.remove(context)

    if len(tensorkube_contexts) == 1:
        return tensorkube_contexts[0]
    elif len(tensorkube_contexts) > 1:
        return tensorkube_contexts[0]
    return None


def create_secret(name: str, namespace: str, data: Dict[str, str], force: bool = False,
                  context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            raise Exception("No context found for the cluster. Please configure Tensorfuse properly.")
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)

    secret = client.V1Secret()
    secret.metadata = client.V1ObjectMeta(name=name, namespace=namespace)
    secret.string_data = data

    try:
        # Check if the secret already exists
        v1.read_namespaced_secret(name, namespace)
        if force:
            # If the secret exists and force is True, update the secret
            v1.replace_namespaced_secret(name, namespace, body=secret)
            click.echo(click.style("Updated already existing secret ", fg=CliColors.SUCCESS.value) + click.style(name,
                                                                                                                 bold=True,
                                                                                                                 fg=CliColors.SUCCESS.value) + click.style(
                " in namespace ", fg=CliColors.SUCCESS.value) + click.style(namespace, bold=True,
                                                                            fg=CliColors.SUCCESS.value))
        else:
            click.echo(click.style("Secret ", fg=CliColors.WARNING.value) + click.style(name, bold=True,
                                                                                        fg=CliColors.WARNING.value) + click.style(
                " already exists in namespace ", fg=CliColors.WARNING.value) + click.style(namespace, bold=True,
                                                                                           fg=CliColors.WARNING.value) + click.style(
                ". Use --force to update the secret.", fg=CliColors.WARNING.value))
    except ApiException as e:
        if e.status == 404:
            # If the secret does not exist, create it
            try:
                v1.create_namespaced_secret(namespace=namespace, body=secret)
                click.echo(click.style("Secret ", fg=CliColors.SUCCESS.value) + click.style(name, bold=True,
                                                                                            fg=CliColors.SUCCESS.value) + click.style(
                    " created successfully.", fg=CliColors.SUCCESS.value))
            except ApiException as e:
                click.echo(click.style("An error occurred while creating the secret", fg=CliColors.ERROR.value))
                click.echo(click.style(f"Error: {e}", fg=CliColors.ERROR.value))
        else:
            raise e


def list_secrets(namespace: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return []
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    secrets = v1.list_namespaced_secret(namespace).items
    if not secrets:
        return []
    return secrets


def delete_secret(name: str, namespace: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    try:
        v1.delete_namespaced_secret(name, namespace)
        click.echo(click.style("Secret ", fg=CliColors.SUCCESS.value) + click.style(name, bold=True,
                                                                                    fg=CliColors.SUCCESS.value) + click.style(
            " deleted successfully.", fg=CliColors.SUCCESS.value))
    except ApiException as e:
        if e.status == 404:
            click.echo(click.style("Secret ", fg=CliColors.WARNING.value) + click.style(name, bold=True,
                                                                                        fg=CliColors.WARNING.value) + click.style(
                " not found in namespace ", fg=CliColors.WARNING.value) + click.style(namespace, bold=True,
                                                                                      fg=CliColors.WARNING.value))
        else:
            raise e


def create_configmap(name: str, namespace: str, data: Dict[str, str], force: bool = False,
                     context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            raise Exception("No context found for the cluster. Please configure Tensorfuse properly.")
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    configmap = client.V1ConfigMap()
    configmap.metadata = client.V1ObjectMeta(name=name, namespace=namespace)
    configmap.data = {"config": yaml.dump(data)}
    try:
        # Check if the configmap already exists
        v1.read_namespaced_config_map(name, namespace)
        if force:
            # If the configmap exists and force is True, update the configmap
            v1.replace_namespaced_config_map(name, namespace, body=configmap)
    except ApiException as e:
        if e.status == 404:
            # If the configmap does not exist, create it
            try:
                v1.create_namespaced_config_map(namespace=namespace, body=configmap)
            except ApiException as e:
                raise e
        else:
            raise e


def get_pods_for_jobs(job_name: str, namespace: str = "default"):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    api = client.CoreV1Api(k8s_api_client)
    try:
        return api.list_namespaced_pod(namespace=namespace, label_selector=f"job-name={job_name}")
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")
        return None


def list_jobs(namespace: Optional[str] = None, all: bool = False, job_name_prefix: Optional[str] = None):
    """
    Lists Kubernetes jobs in a namespace or across all namespaces with optional job name prefix filtering

    Args:
        namespace: Specific namespace to list jobs from
        all: If True, lists jobs from all namespaces
        context_name: Kubernetes context name to use
        job_name_prefix: Optional prefix to filter job names

    Returns:
        Dict containing list of jobs or None if context not found
    """
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None

    api_client = config.new_client_from_config(context=context_name)
    batch_v1 = client.BatchV1Api(api_client)

    try:
        if all:
            job_list = batch_v1.list_job_for_all_namespaces()
        else:
            namespace = namespace if namespace else DEFAULT_NAMESPACE
            job_list = batch_v1.list_namespaced_job(namespace=namespace)

        # Filter jobs by prefix if specified
        if job_name_prefix:
            filtered_items = [job for job in job_list.items if job.metadata.name.startswith(job_name_prefix)]
            job_list.items = filtered_items

        return job_list
    except ApiException as e:
        print(f"Exception when calling BatchV1Api: {e}")
        return None


def delete_job(job_name: str, namespace: str = "default") -> bool:
    """
    Stops and deletes a Kubernetes job and its associated pods

    Args:
        job_name: Name of the job to delete
        namespace: Kubernetes namespace where the job exists

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        # Get API clients
        api_client = config.new_client_from_config(context=get_tensorkube_cluster_context_name())
        batch_v1 = client.BatchV1Api(api_client)
        core_v1 = client.CoreV1Api(api_client)

        # First check if job exists
        try:
            batch_v1.read_namespaced_job(name=job_name, namespace=namespace)
        except ApiException as e:
            if e.status == 404:
                click.echo(click.style(f"Job {job_name} not found in namespace {namespace}", fg='red'))
                return False
            raise e

        # Delete associated pods first
        try:
            pods = core_v1.list_namespaced_pod(namespace=namespace, label_selector=f"job-name={job_name}")
            for pod in pods.items:
                core_v1.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)
        except ApiException as e:
            print(f"Error deleting pods for job {job_name}: {e}")

        # Delete the job
        try:
            batch_v1.delete_namespaced_job(name=job_name, namespace=namespace,
                body=client.V1DeleteOptions(propagation_policy='Foreground', grace_period_seconds=0))
            click.echo(click.style(f"Successfully deleted job {job_name}", fg='green'))
            return True
        except ApiException as e:
            click.echo(click.style(f"Error deleting job {job_name}: {e}", fg='red'))
            return False

    except Exception as e:
        print(f"Error in delete_job: {e}")
        click.echo(click.style(f"Failed to delete job: {str(e)}", fg='red'))
        return False


def list_keda_scaled_jobs():
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None

    api_client = config.new_client_from_config(context=context_name)
    k8s_client = client.CustomObjectsApi(api_client)

    try:
        keda_scaled_jobs = k8s_client.list_namespaced_custom_object(group="keda.sh", version="v1alpha1",
            plural="scaledjobs", namespace="keda")
        return keda_scaled_jobs
    except ApiException as e:
        print(f"Exception when calling CustomObjectsApi: {e}")
        return None


def list_trigger_authentications():
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None

    api_client = config.new_client_from_config(context=context_name)
    k8s_client = client.CustomObjectsApi(api_client)

    try:
        trigger_authentications = k8s_client.list_namespaced_custom_object(group="keda.sh", version="v1alpha1",
            plural="triggerauthentications", namespace="keda")
        return trigger_authentications
    except ApiException as e:
        print(f"Exception when calling CustomObjectsApi: {e}")
        return None


def delete_trigger_authentication(trigger_auth_name: str):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None

    api_client = config.new_client_from_config(context=context_name)
    k8s_client = client.CustomObjectsApi(api_client)

    try:
        k8s_client.delete_namespaced_custom_object(group="keda.sh", version="v1alpha1", plural="triggerauthentications",
            namespace="keda", name=trigger_auth_name)
    except ApiException as e:
        print(f"Exception when calling CustomObjectsApi: {e}")
        return None


def add_user_to_aws_auth_group(user_name, group_name):
    v1 = client.CoreV1Api()
    # details of the aws-auth ConfigMap
    namespace = "kube-system"
    configmap_name = "aws-auth"

    configmap = v1.read_namespaced_config_map(configmap_name, namespace)
    map_users = yaml.safe_load(configmap.data.get("mapUsers", "[]"))
    # Append the new user to the mapUsers list
    new_user = {"userarn": f"arn:aws:iam::{get_aws_account_id()}:user/{user_name}", "username": user_name,
        "groups": [group_name]}

    map_users.append(new_user)
    # Update the mapUsers back into the ConfigMap data
    configmap.data["mapUsers"] = yaml.dump(map_users)

    # Update the ConfigMap with the new user
    v1.replace_namespaced_config_map(name=configmap_name, namespace=namespace, body=configmap)


def add_user_to_k8s(user_name):
    config.load_kube_config()
    rbac_api = client.RbacAuthorizationV1Api()
    cluster_role_name = f"{get_cluster_name()}-{user_name}-job-cluster-role"
    cluster_role = client.V1ClusterRole(metadata=client.V1ObjectMeta(name=cluster_role_name), rules=[
        client.V1PolicyRule(api_groups=["keda.sh"], resources=["scaledjobs"],
            verbs=["create", "get", "list", "delete"])])
    try:
        rbac_api.create_cluster_role(body=cluster_role)
    except ApiException as e:
        if e.status == 409:
            print(f"ClusterRole {cluster_role_name} already exists.")
        else:
            raise
    print(f"ClusterRole {cluster_role_name} created successfully.")
    group_name = f"{get_cluster_name()}-{user_name}-job-access"
    cluster_role_binding_name = f"{get_cluster_name()}-{user_name}-job-cluster-role-binding"
    # Define ClusterRoleBinding to bind the role to a user
    cluster_role_binding = client.V1ClusterRoleBinding(metadata=client.V1ObjectMeta(name=cluster_role_binding_name),
        role_ref=client.V1RoleRef(api_group="rbac.authorization.k8s.io", kind="ClusterRole", name=cluster_role_name),
        subjects=[client.RbacV1Subject(kind="Group", name=group_name, )])
    try:
        rbac_api.create_cluster_role_binding(body=cluster_role_binding)
    except ApiException as e:
        if e.status == 409:
            print(f"ClusterRoleBinding {cluster_role_binding_name} already exists.")
        else:
            raise
    print(f"ClusterRoleBinding {cluster_role_binding_name} created successfully.")
    add_user_to_aws_auth_group(user_name, group_name)
    return


def generate_kubeconfig(cluster_region: Optional[str] = None):
    eks_client = get_eks_client(region=cluster_region)
    

    cluster_name = get_cluster_name()
    # Retrieve cluster information
    cluster_info = eks_client.describe_cluster(name=get_cluster_name())['cluster']

    # Extract cluster details
    endpoint = cluster_info['endpoint']
    cluster_ca_certificate = cluster_info['certificateAuthority']['data']
    if not cluster_region:
        region = get_session_region()
    else:
        region = cluster_region
    profile = get_session_profile_name(session_region=region)
    aws_account_id = get_aws_account_id(session_region=region)

    # Create a kubeconfig dictionary
    kubeconfig_data = {
        "apiVersion": "v1",
        "clusters": [{
            "cluster": {
                "server": endpoint,
                "certificate-authority-data": cluster_ca_certificate
            },
            "name": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}'
        }],
        "contexts": [{
            "context": {
                "cluster": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}',
                "user": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}'
            },
            "name": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}'
        }],
        "current-context": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}',
        "kind": "Config",
        "users": [{
            "name": f'arn:aws:eks:{region}:{aws_account_id}:cluster/{cluster_name}',
            "user": {
                "exec": {
                    "apiVersion": "client.authentication.k8s.io/v1beta1",
                    "command": "aws",
                    "args": ["eks", "get-token", "--cluster-name", cluster_name]
                            if not profile or profile == "default"
                            else ["eks", "get-token", "--profile", profile, "--cluster-name", cluster_name],
                    "env": [
                        {"name": "AWS_DEFAULT_REGION", "value": region}, #TODO: is this env needed ?
                    ]
                }
            }
        }]
    }
    kubeconfig_dir = os.path.expanduser('~/.kube')
    kubeconfig_file = os.path.join(kubeconfig_dir, 'config')

    # Create the directory if it does not exist
    if not os.path.exists(kubeconfig_dir):
        os.makedirs(kubeconfig_dir, exist_ok=True)

    # Load existing kubeconfig or create a new one if it doesn't exist
    if os.path.exists(kubeconfig_file):
        with open(kubeconfig_file, 'r') as f:
            existing_config = yaml.safe_load(f) or {}
    else:
        existing_config = {'apiVersion': 'v1', 'kind': 'Config', 'clusters': [], 'contexts': [], 'users': []}

    # Merge new kubeconfig entry into existing config
    # Function to update or add an entry in the list
    def update_or_add_entry(existing_list, new_entry, key):
        for i, entry in enumerate(existing_list):
            if entry[key] == new_entry[key]:
                existing_list[i] = new_entry  # Update the existing entry
                return
        existing_list.append(new_entry)  # Add as a new entry if not found

    # Merge new kubeconfig entry into existing config
    update_or_add_entry(existing_config['clusters'], kubeconfig_data['clusters'][0], 'name')
    update_or_add_entry(existing_config['contexts'], kubeconfig_data['contexts'][0], 'name')
    update_or_add_entry(existing_config['users'], kubeconfig_data['users'][0], 'name')
    existing_config['current-context'] = kubeconfig_data['current-context']

    # Write back to the default kubeconfig file
    with open(kubeconfig_file, 'w') as f:
        yaml.dump(existing_config, f)


def create_service_account(name: str, namespace: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            raise Exception("No context found for the cluster. Please configure Tensorfuse properly.")

    k8s_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_client)
    service_account = client.V1ServiceAccount()
    service_account.metadata = client.V1ObjectMeta(name=name)
    try:
        v1.create_namespaced_service_account(namespace=namespace, body=service_account)
    except ApiException as e:
        if e.status == 409:
            print(f"ServiceAccount '{name}' already exists in namespace '{namespace}'.")
        else:
            print(f"Failed to create ServiceAccount '{name}': {e}")
            raise e

def create_service_account_with_role_arn(name: str, namespace: str, role_arn: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            raise Exception("No context found for the cluster. Please configure Tensorfuse properly.")

    k8s_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_client)

    # Check if the ServiceAccount already exists
    try:
        v1.read_namespaced_service_account(name=name, namespace=namespace)
        print(f"ServiceAccount '{name}' already exists in namespace '{namespace}'.")
    except ApiException as e:
        if e.status == 404:
            # ServiceAccount does not exist; create it
            service_account = client.V1ServiceAccount(
                metadata=client.V1ObjectMeta(name=name, annotations={"eks.amazonaws.com/role-arn": role_arn},
                    namespace=namespace), )
            try:
                v1.create_namespaced_service_account(namespace=namespace, body=service_account)
                print(f"ServiceAccount '{name}' created in namespace '{namespace}'.")
            except ApiException as create_error:
                print(f"Failed to create ServiceAccount '{name}': {create_error}")
                raise create_error
        else:
            print(f"Failed to check ServiceAccount existence: {e}")
            raise e


def create_k8s_role(role_name: str, namespace: str, rules: List[Dict[str, Any]], context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            raise Exception("No context found for the cluster. Please configure Tensorfuse properly.")

    k8s_client = config.new_client_from_config(context=context_name)
    rbac_api = client.RbacAuthorizationV1Api(k8s_client)
    role = client.V1Role()
    role.metadata = client.V1ObjectMeta(name=role_name)
    role.rules = rules
    try:
        rbac_api.create_namespaced_role(namespace=namespace, body=role)
    except ApiException as e:
        if e.status == 409:
            print(f"Role '{role_name}' already exists in namespace '{namespace}'.")
        else:
            print(f"Failed to create Role '{role_name}': {e}")
            raise e


def create_role_binding(rb_name: str, rb_namespace: str, role_name: str, sa_name: str, sa_namespace: str,
                        context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            raise Exception("No context found for the cluster. Please configure Tensorfuse properly.")

    k8s_api_client = config.new_client_from_config(context=context_name)
    rbac_api = client.RbacAuthorizationV1Api(k8s_api_client)
    role_binding = client.V1RoleBinding(
        role_ref=client.V1RoleRef(api_group="rbac.authorization.k8s.io", kind="Role", name=role_name),
        subjects=[client.RbacV1Subject(kind="ServiceAccount", name=sa_name, namespace=sa_namespace)])
    role_binding.metadata = client.V1ObjectMeta(name=rb_name)
    try:
        rbac_api.create_namespaced_role_binding(namespace=rb_namespace, body=role_binding)
    except ApiException as e:
        if e.status == 409:
            print(f"RoleBinding '{rb_name}' already exists in namespace '{rb_namespace}'.")
        else:
            print(f"Failed to create RoleBinding '{rb_name}': {e}")
            raise e


def is_existing_scaled_job(job_name: str, namespace: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            raise Exception("No context found for the cluster. Please configure Tensorfuse properly.")
    k8s_api_client = config.new_client_from_config(context=context_name)
    k8s_client = client.CustomObjectsApi(k8s_api_client)
    try:
        job = k8s_client.get_namespaced_custom_object(group="keda.sh", version="v1alpha1", plural="scaledjobs",
            name=job_name, namespace=namespace)
        return True, job
    except ApiException as e:
        if e.status == 404:
            return False, None
        raise e


def apply_domain_claim(domain: str, namespace: str):
    k8s_api_client = config.new_client_from_config(context=get_tensorkube_cluster_context_name())
    k8s_client = client.CustomObjectsApi(k8s_api_client)

    config_yaml_path = resource_filename('tensorkube', 'configurations/build_configs/domain_claim_base_config.yaml')

    with open(config_yaml_path, 'r') as f:
        config_yaml = yaml.safe_load(f)

    config_yaml['metadata']['name'] = domain
    config_yaml['spec']['namespace'] = namespace

    group = 'networking.internal.knative.dev'
    version = 'v1alpha1'
    plural = 'clusterdomainclaims'

    try:
        # Use cluster-scoped methods instead of namespaced ones
        existing_claim = k8s_client.get_cluster_custom_object(group=group, version=version, plural=plural, name=domain)
        resource_version = existing_claim['metadata']['resourceVersion']
        config_yaml['metadata']['resourceVersion'] = resource_version
        k8s_client.patch_cluster_custom_object(group=group, version=version, plural=plural, name=domain,
            body=config_yaml)
        click.echo(f"Updated ClusterDomainClaim for domain {domain}")
    except ApiException as e:
        if e.status == 404:
            k8s_client.create_cluster_custom_object(group=group, version=version, plural=plural, body=config_yaml)
            click.echo(f"Created ClusterDomainClaim for domain {domain}")
        else:
            raise e


def patch_service_account(role_arn, service_account_name, namespace):
    # Load the Kubernetes configuration
    config.load_kube_config()

    # Create the Kubernetes API client
    v1 = client.CoreV1Api()

    # Define the patch for the ServiceAccount
    patch_body = {"metadata": {"annotations": {"eks.amazonaws.com/role-arn": role_arn}}}

    try:
        # Patch the existing ServiceAccount
        response = v1.patch_namespaced_service_account(name=service_account_name, namespace=namespace, body=patch_body)
        print(f"ServiceAccount '{service_account_name}' in namespace '{namespace}' patched successfully with role ARN.")
    except client.exceptions.ApiException as e:
        print(f"Failed to patch ServiceAccount: {e.reason}")


def get_jobs_by_container_image(image: str, namespace: str = "keda") -> list:
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise Exception("Unable to get cluster context")
    k8s_api_client = config.new_client_from_config(context=context_name)
    k8s_client = client.CustomObjectsApi(k8s_api_client)

    try:
        scaled_jobs = k8s_client.list_namespaced_custom_object(group="keda.sh", version="v1alpha1", plural="scaledjobs",
            namespace=namespace)
        matching_jobs = []
        for job in scaled_jobs.get("items", []):
            containers = job.get("spec", {}).get("jobTargetRef", {}).get("template", {}).get("spec", {}).get(
                "containers", [])
            if any(container.get("image") == image for container in containers):
                matching_jobs.append(job)
        return matching_jobs

    except ApiException as e:
        if e.status == 404:
            return []
        raise e


def add_helm_annotations_and_labels(resource_api_version: str, resource_type: str, resource_name: str,
                                    release_name: str, release_namespace: str,
                                    resource_namespace: Optional[str] = DEFAULT_NAMESPACE,):


    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise Exception("Unable to get cluster context")
    k8s_api_client = config.new_client_from_config(context=context_name)
    dyn_client = dynamic.DynamicClient(k8s_api_client)

    # Locate the resource dynamically
    resource = dyn_client.resources.get(api_version=resource_api_version, kind=resource_type)

    # Fetch the existing object
    try:
        obj = resource.get(name=resource_name, namespace=resource_namespace) if resource_namespace else resource.get(name=resource_name)
    except ApiException as e:
        raise RuntimeError(f"Failed to fetch resource: {e}")

    # Prepare annotations and labels
    annotations = dict(obj.metadata.annotations) or {}
    labels = dict(obj.metadata.labels or {})


    annotations["meta.helm.sh/release-name"] = release_name
    annotations["meta.helm.sh/release-namespace"] = release_namespace
    labels["app.kubernetes.io/managed-by"] = "Helm"

    patch_body = {
        "metadata": {
            "annotations": annotations,
            "labels": labels
        }
    }

    # Patch the resource
    try:
        if resource_namespace:
            resource.patch(name=resource_name, namespace=resource_namespace, body=patch_body)
        else:
            resource.patch(name=resource_name, body=patch_body)
        print(f"✅ {resource_type}/{resource_name} annotated and labeled for Helm.")
    except ApiException as e:
        raise RuntimeError(f"Failed to patch resource: {e}")


def get_helm_release_version(release_name: str, namespace: str):
    try:
        result = subprocess.run(
            ["helm", "get", "metadata", release_name, "-n", namespace, "-o", "json"],
            check=True,
            stdout=subprocess.PIPE
        )
        details = json.loads(result.stdout)
        version = details.get("version", None)
        if not version:
            raise RuntimeError(f"Could not find version for release {release_name} in namespace {namespace}")
        return version

    except subprocess.CalledProcessError as e:
        print("Error running helm list:", e)
        return None


def get_unhealthy_nodes(cluster_name: str):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise Exception("Unable to get cluster context")
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Load the existing kubeconfig
    v1 = client.CoreV1Api(k8s_api_client)
    try:
        print(f"Getting unhealthy nodes for cluster: {cluster_name}")
        nodes = v1.list_node()
        unhealthy_nodes = []
        current_nodes = []
        for node in nodes.items:
            # about condition - https://kubernetes.io/docs/reference/node/node-status/#condition
            current_nodes.append(node.metadata.name)
            if node.status.conditions:
                for condition in node.status.conditions:
                    # Check for 'Ready' condition and its status should not be 'True'. values are 'True', 'False', 'Unknown'
                    # you should also check for the last heartbeat time to determine if the node is unhealthy
                    if condition.type == 'Ready' and condition.status != 'True':
                        # Check if the last heartbeat time is older than a certain threshold (e.g., 5 minutes)
                        print(f"Node {node.metadata.name} is unhealthy")
                        print(f"status: {condition.status}")
                        print(f"last heartbeat time: {condition.last_heartbeat_time}")
                        print(f"message: {condition.message}")
                        print(f"reason: {condition.reason}")
                        unhealthy_nodes.append(node.metadata.name)
        print(f"Current nodes: {current_nodes}")
        print(f"Unhealthy nodes: {unhealthy_nodes}")
        return unhealthy_nodes
    except Exception as e:
        print(f"Failed to get nodes: {e}")
        raise Exception(f"Failed to get nodes: {e}")

def list_namespaced_k8s_deployments(namespace: str, context_name: Optional[str] = None):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise Exception("Unable to get cluster context")
    k8s_api_client = config.new_client_from_config(context=context_name)

    apps_api = client.AppsV1Api(k8s_api_client)
    try:
        deployments = apps_api.list_namespaced_deployment(namespace=namespace).items
        return deployments
    except ApiException as e:
        print(f"Exception when listing namespaced deployments: {e}")
        return []

def describe_k8s_deployment(deployment_name: str, namespace: str, context_name: Optional[str] = None):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise Exception("Unable to get cluster context")
    k8s_api_client = config.new_client_from_config(context=context_name)

    apps_api = client.AppsV1Api(k8s_api_client)
    try:
        deployment = apps_api.read_namespaced_deployment(deployment_name, namespace)
        return deployment
    except ApiException as e:
        print(f"Exception when reading namespaced deployment: {e}")
        return None

def scale_k8s_deployment_replicas(deployment_name: str, namespace: str, new_scale: int, context_name: Optional[str] = None):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise Exception("Unable to get cluster context")
    k8s_api_client = config.new_client_from_config(context=context_name)

    apps_api = client.AppsV1Api(k8s_api_client)
    try:
        deployments = apps_api.patch_namespaced_deployment_scale(deployment_name, namespace,
                                                                 {"spec": {"replicas": new_scale}})
        return deployments
    except ApiException as e:
        print(f"Exception when patching_namespaced_deployment: {e}")
        return []


def get_nodes_with_label_selector(label_selector):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)
    nodes = v1.list_node(label_selector=label_selector).items
    return nodes


def delete_node_and_wait(node_name: str, context_name: Optional[str] = None, timeout: int = 600):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    v1 = client.CoreV1Api(k8s_api_client)

    try:
        v1.delete_node(name=node_name)
    except ApiException as e:
        if e.status == 404:
            print(f"Node {node_name} not found; assuming already deleted.")
            return
        else:
            raise e

    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            raise Exception("Timeout waiting for node deletion.")
        try:
            v1.read_node(name=node_name)
            print(f"Waiting for node {node_name} to be deleted...")
            time.sleep(10)
        except ApiException as e:
            if e.status == 404:
                print(f"Node {node_name} successfully deleted.")
                break
            else:
                print(f"Error while checking node status: {e}")
                break


# Helper to test if a term already exists (simple deep-compare of matchExpressions)
def term_exists(term, existing_terms):
    for t in existing_terms:
        if t.get("matchExpressions", []) == term.get("matchExpressions", []):
            return True
    return False

def add_k8s_nodegroup_affinity_to_deployment(deployment_name: str, namespace: str, nodegroup_name: str,
                                             cluster_name: str):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise Exception("Unable to get cluster context")
    k8s_api_client = config.new_client_from_config(context=context_name)

    apps_api = client.AppsV1Api(k8s_api_client)
    dep = apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    deployment_dict = k8s_api_client.sanitize_for_serialization(dep)

    desired_required_terms = [
        {
            "matchExpressions": [
                {
                    "key": "alpha.eksctl.io/nodegroup-name",
                    "operator": "In",
                    "values": [nodegroup_name],
                }
            ]
        },
    ]

    # Current affinity (as dict) or empty structure
    current_affinity = deployment_dict.get("spec", {}).get("template", {}).get("spec", {}).get("affinity", {})
    current_node_affinity = current_affinity.get("nodeAffinity", {})
    current_required = current_node_affinity.get("requiredDuringSchedulingIgnoredDuringExecution", {})
    current_terms = current_required.get("nodeSelectorTerms", [])

    if current_required and "nodeSelectorTerms" in current_required:
        current_terms = current_required["nodeSelectorTerms"] or []

    merged_terms = list(current_terms)
    for term in desired_required_terms:
        if not term_exists(term, merged_terms):
            merged_terms.append({"matchExpressions": term["matchExpressions"]})

    # If nothing to change, exit
    if merged_terms == current_terms and current_terms:
        print(f"[affinity] {namespace}/{deployment_name}: nodeAffinity already present; no patch needed.")
        return

    patch = {
        "spec": {
            "template": {
                "spec": {
                    "affinity": {
                        "nodeAffinity": {
                            "requiredDuringSchedulingIgnoredDuringExecution": {
                                "nodeSelectorTerms": merged_terms
                            }
                        }
                    }
                },
            }
        }
    }

    apps_api.patch_namespaced_deployment(
        name=deployment_name,
        namespace=namespace,
        body=patch,
    )

    print(f"[affinity] Added/updated nodeAffinity on {namespace}/{deployment_name} for nodegroup '{nodegroup_name}'.")


def get_pods_on_node(node_name: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    core_api = client.CoreV1Api(k8s_api_client)
    return core_api.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node_name}").items


def get_deployment_for_pod(pod_name: str, namespace: str, context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None, None
    k8s_api_client = config.new_client_from_config(context=context_name)

    apps_api = client.AppsV1Api(k8s_api_client)
    core_api = client.CoreV1Api(k8s_api_client)

    try:
        pod = core_api.read_namespaced_pod(name=pod_name, namespace=namespace)

        owners = pod.metadata.owner_references or []
        rs_owner = next((o for o in owners if o.kind == "ReplicaSet" and o.controller), None)
        if not rs_owner:
            return None, None

        rs = apps_api.read_namespaced_replica_set(name=rs_owner.name, namespace=pod.metadata.namespace)

        dep_owner = next((o for o in (rs.metadata.owner_references or []) if o.kind == "Deployment" and o.controller),
                         None)
        if not dep_owner:
            return None, None
        return pod.metadata.namespace, dep_owner.name
    except ApiException:
        return None, None
