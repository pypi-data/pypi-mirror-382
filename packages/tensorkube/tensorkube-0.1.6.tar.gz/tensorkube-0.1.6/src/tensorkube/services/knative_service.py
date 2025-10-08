import subprocess
import time
from datetime import datetime
from typing import Optional, List, Dict

import click
import yaml
from kubernetes import config, client
from kubernetes.client import ApiException

from tensorkube.constants import KNATIVE_SERVING_NAMESPACE, CONFIG_FEATURES, TENSORFUSE_NAMESPACES, DEFAULT_NAMESPACE, \
    GPU_DEPLOYMENT_MIN_MEMORY, GPU_DEPLOYMENT_MIN_CPU, CliColors, ProbeType
from tensorkube.services.filesystem_service import get_efs_vol_pvc_name
from tensorkube.services.k8s_service import get_efs_claim_name, get_tensorkube_cluster_context_name
from tensorkube.services.nydus import get_nydus_runtime_class_name
from tensorkube.services.nodepool import get_gpu_nodepool
from tensorkube.services.volumes_service import get_deployment_volume_name, get_deployment_volume_mount_path


def get_instance_family_from_gpu_type(gpu_type):
    gpu_type = gpu_type.lower()
    if gpu_type == 'v100':
        return 'p3'
    elif gpu_type == 'a10g':
        return 'g5'
    elif gpu_type == 't4':
        return 'g4dn'
    elif gpu_type == 't4g':
        return 'g5g'
    elif gpu_type == 'l4':
        return 'g6'
    elif gpu_type == 'l40s':
        return 'g6e'
    elif gpu_type == 'a100':
        return 'p4d'
    elif gpu_type == 'h100':
        return 'p5'
    else:
        raise ValueError(f"Unsupported GPU type: {gpu_type}")

def get_gpu_type_from_instance_family(instance_family):
    if instance_family == 'p3':
        return 'v100'
    elif instance_family == 'g5':
        return 'a10g'
    elif instance_family == 'g4dn':
        return 't4'
    elif instance_family == 'g5g':
        return 't4g'
    elif instance_family == 'g6':
        return 'l4'
    elif instance_family == 'g6e':
        return 'l40s'
    elif instance_family == 'p4d':
        return 'a100'
    elif instance_family == 'p5':
        return 'h100'
    else:
        raise ValueError(f"Unsupported instance family: {instance_family}")


def get_supported_gpu_families():
    return ['p3', 'g5', 'g4dn', 'g5g', 'g6', 'g6e']


def apply_anti_affinity_for_gpus(yaml_dict):
    # this function assumes that already there are anti affinity terms
    existing_terms = \
    yaml_dict['spec']['template']['spec']['affinity']['nodeAffinity']['requiredDuringSchedulingIgnoredDuringExecution'][
        'nodeSelectorTerms']
    for term in existing_terms:
        for expression in term.get('matchExpressions', []):
            if expression['key'] == 'karpenter.k8s.aws/instance-family' and expression['operator'] == 'NotIn':
                expression['values'] = list(set(expression['values'] + get_supported_gpu_families()))
    return yaml_dict


def update_or_apply_istio_gateway(gateway_name: str, gateway_namespace: str,
                                  gateway_yaml_dict: Dict):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise ValueError("Could not get the cluster context name")

    k8s_api_client = config.new_client_from_config(context=context_name)
    k8s_client = client.CustomObjectsApi(k8s_api_client)

    # Define Istio Gateway API parameters
    group = "networking.istio.io"
    version = "v1"
    plural = "gateways"

    try:
        # Check if Gateway exists
        existing_gateway = k8s_client.get_namespaced_custom_object(
            group=group,
            version=version,
            namespace=gateway_namespace,
            plural=plural,
            name=gateway_name
        )

        # Update existing Gateway
        resource_version = existing_gateway['metadata']['resourceVersion']
        gateway_yaml_dict['metadata']['resourceVersion'] = resource_version
        click.echo(f'Resource version is {resource_version}')

        k8s_client.patch_namespaced_custom_object(
            group=group,
            version=version,
            namespace=gateway_namespace,
            plural=plural,
            name=gateway_name,
            body=gateway_yaml_dict
        )
        click.echo(f"Updated Gateway {gateway_name}")

    except ApiException as e:
        if e.status == 404:
            # Create new Gateway if it doesn't exist
            k8s_client.create_namespaced_custom_object(
                group=group,
                version=version,
                namespace=gateway_namespace,
                plural=plural,
                body=gateway_yaml_dict
            )
            click.echo(f"Created Gateway {gateway_name}")
        else:
            click.echo(f"Error applying Gateway: {e}")
            raise e

def get_tls_gateway_name(domain: str):
    sanitised = domain.replace('.','-')
    return f'{sanitised}-tls-gateway'

def apply_tls_gateway(service_name: str, domain: str, yaml_file_path: str,
                              gateway_namespace: str):
    gateway_name = get_tls_gateway_name(domain=domain)
    with open(yaml_file_path, 'r') as f:
        yaml_content = f.read()
        yaml_dict = yaml.safe_load(yaml_content)
    click.echo(f"Applying Virtual service {gateway_name} for project {service_name}.")
    yaml_dict['metadata']['name'] = gateway_name
    yaml_dict['metadata']['namespace'] = gateway_namespace
    yaml_dict['spec']['servers'][0]['hosts'] = [domain]
    yaml_dict['spec']['servers'][1]['hosts'] = [domain]
    update_or_apply_istio_gateway(
        gateway_name=gateway_name,
        gateway_namespace=gateway_namespace,
        gateway_yaml_dict=yaml_dict
    )


def update_or_apply_virtual_service(virtual_service_name: str, virtual_service_namespace: str,
        virtual_service_yaml_dict: Dict,

):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise ValueError("Could not get the cluster context name")
    k8s_api_client = config.new_client_from_config(context=context_name)
    # Create a Kubernetes API client
    k8s_client = client.CustomObjectsApi(k8s_api_client)
    # define the group version and plural for the virtual service
    group = "networking.istio.io"
    version = "v1"
    plural = "virtualservices"

    # Check if the VirtualService already exists
    try:
        existing_service = k8s_client.get_namespaced_custom_object(group=group, version=version,
                                                                   namespace=virtual_service_namespace, plural=plural,
                                                                   name=virtual_service_name)
        resource_version = existing_service['metadata']['resourceVersion']
        # Add the resource_version to the yaml dict
        virtual_service_yaml_dict['metadata']['resourceVersion'] = resource_version
        click.echo(f'Resource version is {resource_version}')
        k8s_client.patch_namespaced_custom_object(group=group, version=version, namespace=virtual_service_namespace,
                                                  plural=plural, name=virtual_service_name,
                                                  body=virtual_service_yaml_dict)
        click.echo(f"Updated VirtualService {virtual_service_name}.")
    except ApiException as e:
        if e.status == 404:
            k8s_client.create_namespaced_custom_object(group=group, version=version,
                                                       namespace=virtual_service_namespace, plural=plural,
                                                       body=virtual_service_yaml_dict)
            click.echo(f"Created VirtualService {virtual_service_name}")
        else:
            click.echo(f"Error applying VirtualService: {e}")
            raise e

def get_subpath_virtual_service_name(service_name:str):
    return f'{service_name}-subpath-ingress'

def apply_virtual_service_for_routing(service_name: str, yaml_file_path: str, sanitised_project_name: str,
                                      env: Optional[str] = None):
    virtual_service_namespace = env if env else DEFAULT_NAMESPACE
    virtual_service_name = get_subpath_virtual_service_name(service_name)

    with open(yaml_file_path, 'r') as f:
        yaml_content = f.read()
        yaml_dict = yaml.safe_load(yaml_content)

    click.echo(f"Applying Virtual service {service_name} for project {sanitised_project_name}.")
    yaml_dict['metadata']['name'] = virtual_service_name
    yaml_dict['metadata']['namespace'] = virtual_service_namespace
    yaml_dict['spec']['hosts'][0] = get_istio_ingress_gateway_hostname()
    yaml_dict['spec']['http'][0]['match'][0]['uri']['prefix'] = f"/svc/{virtual_service_namespace}/{service_name}/"
    yaml_dict['spec']['http'][0]['route'][0]['destination'][
        'host'] = 'knative-local-gateway.istio-system.svc.cluster.local'
    yaml_dict['spec']['http'][0]['route'][0]['headers']['request']['set'][
        'Host'] = f'{service_name}.{virtual_service_namespace}.svc.cluster.local'
    update_or_apply_virtual_service(virtual_service_name=virtual_service_name,
        virtual_service_namespace=virtual_service_namespace, virtual_service_yaml_dict=yaml_dict)


def apply_tls_virtual_service(service_name: str, domain: str, yaml_file_path: str, gateway_name: str,
                              namespace: str) -> bool:
    """
    Apply TLS VirtualService for HTTP to HTTPS redirection
    Args:
        service_name: Name of the service
        domain: Domain name for the service
        yaml_file_path: Path to the TLS virtual service YAML template
        namespace: Kubernetes namespace
        context_name: Kubernetes context name
    Returns:
        bool: True if successful, False otherwise
    """

    virtual_service_name = f'{domain}-tls-ingress'

    # Load and modify YAML
    with open(yaml_file_path, 'r') as f:
        yaml_dict = yaml.safe_load(f.read())

    # Update YAML with service specific values
    yaml_dict['metadata']['name'] = virtual_service_name
    yaml_dict['metadata']['namespace'] = namespace
    yaml_dict['spec']['hosts'][0] = domain
    yaml_dict['spec']['gateways'][0] = f'{namespace}/{gateway_name}'
    yaml_dict['spec']['http'][0]['route'][0]['destination']['host'] = f'{service_name}.{namespace}.svc.cluster.local'
    yaml_dict['spec']['http'][0]['match'][0]['authority']['prefix'] = domain
    yaml_dict['spec']['http'][0]['rewrite']['authority'] = f'{service_name}.{namespace}.svc.cluster.local'

    update_or_apply_virtual_service(virtual_service_name=virtual_service_name, virtual_service_namespace=namespace,
        virtual_service_yaml_dict=yaml_dict)



def set_probe(knative_yaml_dict: Dict, probe_type: ProbeType, probe_dict: Dict) -> Dict:
    http_get = probe_dict.get('httpGet', None)
    initial_delay_seconds = probe_dict.get('initialDelaySeconds', None)
    period_seconds = probe_dict.get('periodSeconds', None)
    timeout_seconds = probe_dict.get('timeoutSeconds', None)
    failure_threshold = probe_dict.get('failureThreshold', None)
    success_threshold = probe_dict.get('successThreshold', None)
    termination_grace_period_seconds = probe_dict.get('terminationGracePeriodSeconds', None)

    if probe_type == ProbeType.LIVENESS:
        knative_yaml_dict['spec']['template']['spec']['containers'][0][f'{probe_type.value}Probe'] = {}

    if http_get:
        knative_yaml_dict['spec']['template']['spec']['containers'][0][f'{probe_type.value}Probe']['httpGet'] = http_get
    if initial_delay_seconds:
        knative_yaml_dict['spec']['template']['spec']['containers'][0][f'{probe_type.value}Probe']['initialDelaySeconds'] = initial_delay_seconds
    if period_seconds:
        knative_yaml_dict['spec']['template']['spec']['containers'][0][f'{probe_type.value}Probe']['periodSeconds'] = period_seconds
    if timeout_seconds:
        knative_yaml_dict['spec']['template']['spec']['containers'][0][f'{probe_type.value}Probe']['timeoutSeconds'] = timeout_seconds
    if failure_threshold:
        knative_yaml_dict['spec']['template']['spec']['containers'][0][f'{probe_type.value}Probe']['failureThreshold'] = failure_threshold
    if success_threshold:
        knative_yaml_dict['spec']['template']['spec']['containers'][0][f'{probe_type.value}Probe']['successThreshold'] = success_threshold
    if termination_grace_period_seconds:
        knative_yaml_dict['spec']['template']['spec']['containers'][0][f'{probe_type.value}Probe']['terminationGracePeriodSeconds'] = termination_grace_period_seconds

    return knative_yaml_dict


def apply_knative_service(service_name: str, yaml_file_path: str, sanitised_project_name: str,
                          image_tag: str, workdir: str, command: str, gpus: int, gpu_type: str, port: int,
                          domain: Optional[str], env: Optional[str] = None, cpu: float = 100,
                          memory: int = 200, min_scale: int = 0, max_scale: int = 3,
                          context_name: Optional[str] = None, secrets: List[str] = [],
                          enable_efs: bool = False, concurrency: int = 100, readiness: Optional[Dict] = None,
                          startup_probe: Optional[Dict] = None, liveness_probe: Optional[Dict] = None,
                          volumes: Optional[List[Dict]] = None, last_pod_retention_period: str = None,
                          scale_down_delay: str = None):

    # Load kube config
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Read the YAML file
    with open(yaml_file_path, 'r') as f:
        yaml_content = f.read()

    click.echo(f"Applying Knative service {service_name} for project {sanitised_project_name} and {gpus} GPUs.")
    yaml_content = yaml_content.replace('${SERVICE_NAME}', service_name)
    yaml_content = yaml_content.replace('${GPUS}', str(gpus))

    # Load the YAML content    
    yaml_dict = yaml.safe_load(yaml_content)

    if enable_efs:
        for volume in yaml_dict['spec']['template']['spec']['volumes']:
            if volume['name'] == 'efs-storage':
                volume['persistentVolumeClaim']['claimName'] = get_efs_claim_name(env_name=env)
    else:
        # Remove the EFS volume
        yaml_dict['spec']['template']['spec']['volumes'] = [volume for volume in yaml_dict['spec']['template']['spec']['volumes'] if volume['name'] != 'efs-storage']
        # Remove the volume mount
        yaml_dict['spec']['template']['spec']['containers'][0]['volumeMounts'] = [volume for volume in yaml_dict['spec']['template']['spec']['containers'][0]['volumeMounts'] if volume['name'] != 'efs-storage']
    
    if secrets:
        if enable_efs:
            # podman is ran as a process inside the container so env needs to be read from files and exposed as env vars to podman
            yaml_dict['spec']['template']['spec']['volumes'].append({
                'name': 'secrets',
                'projected': {
                    'sources': [{
                        'secret': {
                            'name': secret_name
                        }
                    } for secret_name in secrets]
                }
            })

            yaml_dict['spec']['template']['spec']['containers'][0]['volumeMounts'].append({
                'name': 'secrets',
                'mountPath': '/mnt/secrets',
                'readOnly': True
            })
        else:
            yaml_dict['spec']['template']['spec']['containers'][0]['envFrom'] = [{
                'secretRef': {
                    'name': secret_name
                }
            
            } for secret_name in secrets]

    if enable_efs:
        if gpus > 0:
            yaml_dict['spec']['template']['spec']['containers'][0]['image'] = "tensorfuse/podman-nvidia:v1"
            config_nvidia_ctk_commands = """sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
                nvidia-ctk cdi list
                """
            podman_gpu_tags = "--gpus all --env NVIDIA_VISIBLE_DEVICES=all --env NVIDIA_DRIVER_CAPABILITIES=compute,utility"
        else:
            config_nvidia_ctk_commands = ""
            yaml_dict['spec']['template']['spec']['containers'][0]['image'] = "quay.io/podman/stable"
            podman_gpu_tags = ""

        if workdir:
            final_command = f"cd {workdir} && {command}"
        else:
            final_command = command

        if secrets:
            secrets_to_env_vars_command = """\
                folder_path="/mnt/secrets"

                # Initialize an empty string to hold the environment variables
                env_vars=""

                # Loop through each file in the folder
                for file in "$folder_path"/*; do
                    if [[ -f $file ]]; then
                        # Get the filename without the path
                        filename=$(basename "$file")
                        
                        # Get the contents of the file
                        contents=$(<"$file")
                        
                        # Escape the contents to handle any special characters or spaces
                        escaped_contents=$(printf '%q' "$contents")

                        # Append to the env_vars string in the format --env filename=contents
                        env_vars="$env_vars --env $filename=$escaped_contents"
                    fi
                done"""
        else:
            secrets_to_env_vars_command = "env_vars=''"

        yaml_dict['spec']['template']['spec']['containers'][0]['command'] = ["/bin/sh", "-c",
                                                                            f"""{config_nvidia_ctk_commands}
        {secrets_to_env_vars_command}
                sed -i 's|mount_program = "/usr/bin/fuse-overlayfs"|mount_program = ""|' /etc/containers/storage.conf
                sudo podman run --name mycontainer $env_vars {podman_gpu_tags} --network=host \
                --rootfs /mnt/efs/images/{sanitised_project_name}/{image_tag}/rootfs:O sh -c "{final_command}" """]
    else:
        # if efs is disabled then we dont need podman.
        del yaml_dict['spec']['template']['spec']['containers'][0]['command']
        yaml_dict['spec']['template']['spec']['containers'][0]['image'] = image_tag
        del yaml_dict['spec']['template']['spec']['containers'][0]['securityContext']
        if gpus > 0:
            yaml_dict['spec']['template']['spec']['runtimeClassName'] = get_nydus_runtime_class_name()
            if 'nodeSelector' in yaml_dict['spec']['template']['spec']:
                yaml_dict['spec']['template']['spec']['nodeSelector']['karpenter.sh/nodepool'] = get_gpu_nodepool()
            else:
                yaml_dict['spec']['template']['spec']['nodeSelector'] = {'karpenter.sh/nodepool': get_gpu_nodepool()}


    if gpus > 0:
        # by default gpu pods usually use all of available memory and cpu
        # so I am here defining some limits above which the cpu and memory parameters will be used
        if memory >= GPU_DEPLOYMENT_MIN_MEMORY:
            yaml_dict['spec']['template']['spec']['containers'][0]['resources']['requests'][
                'memory'] = f'{str(int(memory))}M'
        else:
            click.echo(click.style(
                f"Memory is not specified or is less than the minimum required for GPU deployment. Setting to minimum: {GPU_DEPLOYMENT_MIN_MEMORY}M.",
                fg=CliColors.WARNING.value))
            yaml_dict['spec']['template']['spec']['containers'][0]['resources']['requests'][
                'memory'] = f'{str(GPU_DEPLOYMENT_MIN_MEMORY)}M'
        if cpu >= GPU_DEPLOYMENT_MIN_CPU:
            yaml_dict['spec']['template']['spec']['containers'][0]['resources']['requests'][
                'cpu'] = f'{str(int(cpu))}m'
        else:
            click.echo(click.style(
                f"CPU is not specified or is less than the minimum required for GPU deployment. Setting to minimum: {GPU_DEPLOYMENT_MIN_CPU}m.",
                fg=CliColors.WARNING.value))
            yaml_dict['spec']['template']['spec']['containers'][0]['resources']['requests'][
                'cpu'] = f'{str(GPU_DEPLOYMENT_MIN_CPU)}m'

        if 'nodeSelector' in yaml_dict['spec']['template']['spec']:
            yaml_dict['spec']['template']['spec']['nodeSelector']['karpenter.k8s.aws/instance-family'] = get_instance_family_from_gpu_type(gpu_type)
        else:
            yaml_dict['spec']['template']['spec']['nodeSelector'] = {'karpenter.k8s.aws/instance-family': get_instance_family_from_gpu_type(gpu_type)}
            
        
        yaml_dict['spec']['template']['metadata']['annotations'][
            'autoscaling.knative.dev/scale-to-zero-pod-retention-period'] = last_pod_retention_period if last_pod_retention_period else '10m'
        yaml_dict['spec']['template']['metadata']['annotations']['autoscaling.knative.dev/scale-down-delay'] = scale_down_delay if scale_down_delay else '10m'
        yaml_dict['spec']['template']['spec']['containers'][0]['volumeMounts'].append(
            {'name': 'dshm', 'mountPath': '/dev/shm'})
        yaml_dict['spec']['template']['spec']['volumes'].append(
            {'name': 'dshm', 'emptyDir': {'medium': 'Memory', 'sizeLimit': '10Gi'}})
    else:
        yaml_dict['spec']['template']['spec']['containers'][0]['resources']['requests'][
            'memory'] = f'{str(int(memory))}M'
        yaml_dict['spec']['template']['spec']['containers'][0]['resources']['requests']['cpu'] = f'{str(int(cpu))}m'
        apply_anti_affinity_for_gpus(yaml_dict)
    if gpus > 2:
        yaml_dict['spec']['template']['metadata']['annotations'][
            'autoscaling.knative.dev/scale-to-zero-pod-retention-period'] = last_pod_retention_period if last_pod_retention_period else '20m'
        yaml_dict['spec']['template']['metadata']['annotations']['autoscaling.knative.dev/scale-down-delay'] = scale_down_delay if scale_down_delay else '20m'
    # apply min scale and max scale arguements
    yaml_dict['spec']['template']['metadata']['annotations']['autoscaling.knative.dev/min-scale'] = str(min_scale)
    yaml_dict['spec']['template']['metadata']['annotations']['autoscaling.knative.dev/max-scale'] = str(max_scale)
    yaml_dict['spec']['template']['metadata']['annotations']['autoscaling.knative.dev/target'] = str(concurrency)

    yaml_dict['spec']['template']['metadata']['annotations']['image_tag'] = image_tag
    yaml_dict['spec']['template']['metadata']['annotations']['deploy_time'] = datetime.now().isoformat()

    if readiness:
        yaml_dict = set_probe(yaml_dict, ProbeType.READINESS, readiness)

    if startup_probe:
        yaml_dict = set_probe(yaml_dict, ProbeType.STARTUP, startup_probe)
    else:
        if readiness:
            yaml_dict = set_probe(yaml_dict, ProbeType.STARTUP, readiness)

    if liveness_probe:
        yaml_dict = set_probe(yaml_dict, ProbeType.LIVENESS, liveness_probe)
    
    # set container port
    yaml_dict['spec']['template']['spec']['containers'][0]['ports'] = [{'containerPort': port}]
    if readiness is None:
        if 'httpGet' in yaml_dict['spec']['template']['spec']['containers'][0]['readinessProbe']:
            yaml_dict['spec']['template']['spec']['containers'][0]['readinessProbe']['httpGet']['port'] = port

    if (startup_probe is None) and (readiness is None):
        if 'httpGet' in yaml_dict['spec']['template']['spec']['containers'][0]['startupProbe']:
            yaml_dict['spec']['template']['spec']['containers'][0]['startupProbe']['httpGet']['port'] = port

    if volumes:
        for volume in volumes:
            volume_details = {
                "name" : get_deployment_volume_name(volume['name'], volume['type']),
                "persistentVolumeClaim":{
                    "claimName": get_efs_vol_pvc_name(volume['name'], namespace=env)
                }
            }
            volume_mount = {
                "name": get_deployment_volume_name(volume['name'], volume['type']),
                "mountPath": get_deployment_volume_mount_path(volume)
            }

            yaml_dict['spec']['template']['spec']['volumes'].append(volume_details)
            yaml_dict['spec']['template']['spec']['containers'][0]['volumeMounts'].append(volume_mount)

    # enable http redirects if domain is available
    # if domain:
    #     if 'annotations' not in yaml_dict['metadata']:
    #         yaml_dict['metadata']['annotations'] = {}
    #     yaml_dict['metadata']['annotations']['networking.knative.dev/http-protocol'] = 'redirected'

    # Create a Kubernetes API client
    k8s_client = client.CustomObjectsApi(k8s_api_client)

    # Apply the configuration
    group = "serving.knative.dev"
    version = "v1"
    namespace = env if env else DEFAULT_NAMESPACE
    plural = "services"

    # check if the custom object exists if yes then update else create
    try:
        existing_service = k8s_client.get_namespaced_custom_object(group, version, namespace, plural, service_name)
        resource_version = existing_service['metadata']['resourceVersion']
        # add the resource_version to the yaml dict
        yaml_dict['metadata']['resourceVersion'] = resource_version
        click.echo(f'Resource version is {resource_version}')
        # Remove immutable fields
        if 'metadata' in yaml_dict:
            if 'annotations' in yaml_dict['metadata']:
                if 'serving.knative.dev/creator' in yaml_dict['metadata']['annotations']:
                    del yaml_dict['metadata']['annotations']['serving.knative.dev/creator']
            if 'annotations' in yaml_dict['metadata']:
                if 'serving.knative.dev/lastModifier' in yaml_dict['metadata']['annotations']:
                    del yaml_dict['metadata']['annotations']['serving.knative.dev/lastModifier']
        k8s_client.patch_namespaced_custom_object(group, version, namespace, plural, service_name, yaml_dict)
        click.echo(f"Updated Knative service {service_name}.")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            k8s_client.create_namespaced_custom_object(group, version, namespace, plural, yaml_dict)
            click.echo(f"Created Knative service {service_name}.")
        else:
            click.echo(f"Error applying Knative service: {e}")
            raise e


def enable_knative_selectors_pv_pvc_capabilities(namespace=KNATIVE_SERVING_NAMESPACE,
                                                 context_name: Optional[str] = None):
    """
    Enable the nodeSelector feature in the config-features ConfigMap.

    Args:
        namespace (str): The namespace where the ConfigMap is located. Defaults to 'knative-serving'.
    """
    # Load the kubeconfig
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Create an instance of the API class
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
        config_map.data["kubernetes.podspec-runtimeclassname"] = "enabled"

        # Update the ConfigMap
        v1.patch_namespaced_config_map(name=CONFIG_FEATURES, namespace=namespace, body=config_map)
        print(
            f"Successfully enabled node selector, affinity, pv-claim, pv-write and add-capabilities features in {CONFIG_FEATURES} ConfigMap.")
    except client.exceptions.ApiException as e:
        print(f"Exception when updating ConfigMap: {e}")
        raise

def add_runtimeclass_knative_features(namespace=KNATIVE_SERVING_NAMESPACE,
                                                 context_name: Optional[str] = None):
    # Load the kubeconfig
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Create an instance of the API class
    v1 = client.CoreV1Api(k8s_api_client)

    try:
        # Get the existing config-features ConfigMap
        config_map = v1.read_namespaced_config_map(name=CONFIG_FEATURES, namespace=namespace)

        # Update the ConfigMap data
        if config_map.data is None:
            config_map.data = {}
        config_map.data["kubernetes.podspec-runtimeclassname"] = "enabled"

        # Update the ConfigMap
        v1.patch_namespaced_config_map(name=CONFIG_FEATURES, namespace=namespace, body=config_map)
        print(
            f"Successfully enabled pod runtime feature in {CONFIG_FEATURES} ConfigMap.")
    except client.exceptions.ApiException as e:
        print(f"Exception when updating ConfigMap: {e}")
        raise







def list_deployed_services(env_name: Optional[str] = None, all: bool = False, context_name: Optional[str] = None):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None
    api_client = config.new_client_from_config(context=context_name)
    api = client.CustomObjectsApi(api_client)
    if all:
        ksvc_list = api.list_cluster_custom_object(group="serving.knative.dev", version="v1", plural="services", )
    else:
        namespace = env_name if env_name else DEFAULT_NAMESPACE
        ksvc_list = api.list_namespaced_custom_object(group="serving.knative.dev", version="v1", plural="services",
                                                      namespace=namespace, )

    return ksvc_list


def get_knative_service(service_name: str, namespace: str = "default", context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    api = client.CustomObjectsApi(k8s_api_client)
    try:
        ksvc = api.get_namespaced_custom_object(group="serving.knative.dev", version="v1", plural="services",
                                                name=service_name, namespace=namespace, )
        return ksvc
    except ApiException as e:
        if e.status == 404:
            return None
        else:
            raise e


def delete_knative_service_by_name(service_name: str, namespace: str = "default", context_name: Optional[str] = None,
                           wait: bool = False, timeout: int = 600) -> bool:
    """
    Delete a Knative service and optionally wait for completion.

    Args:
        service_name: Name of the Knative service
        namespace: Kubernetes namespace
        context_name: Kubernetes context name
        wait: Whether to wait for deletion to complete
        timeout: Maximum time to wait in seconds

    Returns:
        bool: True if deletion successful, False if service not found
    """
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return False

    k8s_api_client = config.new_client_from_config(context=context_name)
    api = client.CustomObjectsApi(k8s_api_client)

    try:
        # Delete the Knative service
        api.delete_namespaced_custom_object(
            group="serving.knative.dev",
            version="v1",
            plural="services",
            name=service_name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Background",
                grace_period_seconds=0
            )
        )

        if wait:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    api.get_namespaced_custom_object(
                        group="serving.knative.dev",
                        version="v1",
                        plural="services",
                        name=service_name,
                        namespace=namespace
                    )
                    time.sleep(2)
                except ApiException as e:
                    if e.status == 404:
                        return True
                    raise e
            raise TimeoutError(f"Timeout waiting for service {service_name} deletion")

        return True

    except ApiException as e:
        if e.status == 404:
            return False
        raise e


def get_ready_condition(service):
    ready_condition = [condition for condition in service['status']['conditions'] if condition['type'] == 'Ready']
    if ready_condition:
        return ready_condition[0]
    return None


def get_latest_running_revision(service_name: str, namespace: str = "default"):
    service = get_knative_service(service_name, namespace)
    if service is None:
        return None
    latest_revision_name = service['status'].get('latestReadyRevisionName', None)
    return latest_revision_name


def get_pods_for_service(service_name: str, namespace: str = "default"):
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    api = client.CoreV1Api(k8s_api_client)
    latest_revision = get_latest_running_revision(service_name, namespace)
    if latest_revision is None:
        return None
    pods = api.list_namespaced_pod(namespace=namespace,
                                   label_selector=f"serving.knative.dev/service={service_name},serving.knative.dev/revision={latest_revision}")
    return pods


def delete_knative_services(context_name: Optional[str] = None):
    # kubectl delete ksvc --all -n <your-namespace>
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    command = ["kubectl", "--context", f"{context_name}", "delete", "ksvc", "--all", "-n", "default"]
    subprocess.run(command, check=True)  # TODO maybe wait for pods to scale down before returning


def cleanup_knative_resources(context_name: Optional[str] = None):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    try:
        # kubectl delete gateway --all -n istio-system
        command = ["kubectl", "--context", f"{context_name}", "delete", "gateway", "--all", "-n", "istio-system"]
        subprocess.run(command, check=True)
        #  kubectl delete gateway --all -n knative-serving
        command = ["kubectl", "--context", f"{context_name}", "delete", "gateway", "--all", "-n", "knative-serving"]
        subprocess.run(command, check=True)
    except Exception as e:
        click.echo(f"Error while cleaning up Istio gateways: {e}")


def list_ksvc_in_namespace(namespace: str, context_name: Optional[str] = None):
    # Load the Kubernetes configuration
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Create an instance of the CustomObjectsApi
    api_instance = client.CustomObjectsApi(k8s_api_client)

    # Define the group, version, and plural for the Knative service
    group = 'serving.knative.dev'
    version = 'v1'
    plural = 'services'

    try:
        # List all Knative services in the specified namespace
        services = api_instance.list_namespaced_custom_object(group=group, version=version, namespace=namespace,
                                                              plural=plural)
        return services
    except ApiException as e:
        print(f"Failed to list Knative services in namespace {namespace}: {e}")
        raise e


def delete_ksvc_from_namespace(service_name: str, namespace: str, context_name: Optional[str] = None):
    # Load the Kubernetes configuration
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Create an instance of the CustomObjectsApi
    api_instance = client.CustomObjectsApi(k8s_api_client)

    # Define the group, version, and plural for the Knative service
    group = 'serving.knative.dev'
    version = 'v1'
    plural = 'services'

    try:
        # Delete the Knative service
        api_instance.delete_namespaced_custom_object(group=group, version=version, namespace=namespace, plural=plural,
                                                     name=service_name, body=client.V1DeleteOptions())
        print(f"Knative service {service_name} deletion initiated.")
        # Wait for the service to be deleted
        while True:
            try:
                api_instance.get_namespaced_custom_object(group, version, namespace, plural, service_name)
                time.sleep(1)  # Wait for 1 second before checking again
            except ApiException as e:
                if e.status == 404:
                    print(f"Knative service {service_name} deleted successfully.")
                    break
                else:
                    print(f"Error while waiting for deletion of Knative service {service_name}: {e}")
                    raise e
        print(f"Knative service {service_name} deleted successfully.")
    except ApiException as e:
        print(f"Failed to delete Knative service {service_name}: {e}")


def delete_all_ksvc_from_namespace(namespace: str):
    if namespace in TENSORFUSE_NAMESPACES:
        click.echo(f"Namespace {namespace} is a system namespace. Skipping deletion of Knative services.")
        return False
    services = list_ksvc_in_namespace(namespace)
    for service in services['items']:
        service_name = service['metadata']['name']
        delete_ksvc_from_namespace(service_name, namespace)


def get_istio_ingress_gateway_hostname():
    # Load the Kubernetes configuration

    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None
    api_client = config.new_client_from_config(context=context_name)

    # Create an instance of the API class
    api_instance = client.CoreV1Api(api_client)

    try:
        # Get the list of services in the istio-system namespace
        services = api_instance.list_namespaced_service(namespace='istio-system')

        # Find the Istio ingress gateway service
        ingress_gateway = next((svc for svc in services.items if svc.metadata.name.startswith('istio-ingressgateway')),
                               None)

        if ingress_gateway and ingress_gateway.status.load_balancer.ingress:
            # Return the hostname or IP of the load balancer
            return ingress_gateway.status.load_balancer.ingress[0].hostname or \
                ingress_gateway.status.load_balancer.ingress[0].ip
        else:
            print("Istio ingress gateway not found or does not have a load balancer.")
            return None
    except client.exceptions.ApiException as e:
        print(f"Exception when calling CoreV1Api->list_namespaced_service: {e}")
        return None

def delete_virtual_service(virtual_service_name: str, namespace: str):
    """
    Deletes the specified VirtualService.
    """
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return None
    k8s_api_client = config.new_client_from_config(context=context_name)
    api = client.CustomObjectsApi(k8s_api_client)

    group = "networking.istio.io"
    version = "v1"
    plural = "virtualservices"

    try:
        api.delete_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=virtual_service_name,
            body=client.V1DeleteOptions()
        )
        click.echo(f"VirtualService {virtual_service_name} deletion initiated.")
    except ApiException as e:
        if e.status == 404:
            click.echo(f"VirtualService {virtual_service_name} not found.")
        else:
            click.echo(f"Failed to delete VirtualService {virtual_service_name}: {e}")


def check_existing_virtual_service(virtual_service_name: str, namespace: str) -> bool:
    """
    Checks if a VirtualService with the given name exists in the specified namespace.
    Returns True if it exists, otherwise False.
    """
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        return False
    k8s_api_client = config.new_client_from_config(context=context_name)
    api = client.CustomObjectsApi(k8s_api_client)

    group = "networking.istio.io"
    version = "v1"
    plural = "virtualservices"

    try:
        # Attempt to get the specified VirtualService
        api.get_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=virtual_service_name
        )
        print(f"VirtualService {virtual_service_name} exists in namespace {namespace}.")
        return True
    except ApiException as e:
        if e.status == 404:
            print(f"VirtualService {virtual_service_name} does not exist in namespace {namespace}.")
            return False
        else:
            print(f"Error checking VirtualService {virtual_service_name}: {e}")
            return False