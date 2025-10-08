from datetime import datetime
from typing import Optional, List
from kubernetes import config, utils
from pkg_resources import resource_filename
import yaml
import click

from tensorkube.constants import DEFAULT_NAMESPACE, GPU_DEPLOYMENT_MIN_MEMORY, CliColors, GPU_DEPLOYMENT_MIN_CPU, \
    PodStatus
from tensorkube.services.deploy import DEFAULT_ENTRYPOINT, DEFAULT_GITHUB_ACTIONS, DEFAULT_ENV
from tensorkube.services.k8s_service import get_tensorkube_cluster_context_name, get_pod_name_corresponing_to_job, \
    start_streaming_pod, find_and_delete_old_job
from tensorkube.services.knative_service import get_instance_family_from_gpu_type, apply_anti_affinity_for_gpus
from tensorkube.services.nodepool import get_gpu_nodepool
from tensorkube.services.nydus import get_nydus_runtime_class_name


DEFAULT_FOLLOW = False


def get_one_shot_job_name(sanitised_project_name: str) -> str:
    return f"{sanitised_project_name}-one-shot-job"


def deploy_one_shot_job(name: Optional[str], sanitised_project_name: str, image_url: str,
                        gpus: int, gpu_type: str, cpu: float = 100, memory: int = 200, env: Optional[str] = DEFAULT_ENV,
                        entrypoint: Optional[str] = DEFAULT_ENTRYPOINT, secrets: List[str] = None,
                        context_name: Optional[str] = None, follow: bool = DEFAULT_FOLLOW,
                        github_actions: bool = DEFAULT_GITHUB_ACTIONS) -> None:
    if secrets is None:
        secrets = []
    namespace = env if env else DEFAULT_NAMESPACE

    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Read the YAML file
    yaml_file_path = resource_filename('tensorkube', 'configurations/build_configs/one_shot_job.yaml')
    with open(yaml_file_path, 'r') as f:
        yaml_content = f.read()

    job_name = name if name else get_one_shot_job_name(sanitised_project_name)
    click.echo(f"Creating One-Shot Job `{job_name}` for project {sanitised_project_name} and {gpus} GPUs.")
    yaml_content = yaml_content.replace('${JOB_NAME}', job_name)
    yaml_content = yaml_content.replace('${GPUS}', str(gpus))

    # Load the YAML content
    yaml_dict = yaml.safe_load(yaml_content)

    yaml_dict['metadata']['namespace'] = namespace
    yaml_dict['spec']['template']['spec']['containers'][0]['image'] = image_url
    yaml_dict['spec']['template']['spec']['containers'][0]['env'][0]['value'] = "us-east-1"

    if secrets:
        yaml_dict['spec']['template']['spec']['containers'][0]['envFrom'] = [{
            'secretRef': {
                'name': secret_name
            }

        } for secret_name in secrets]

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
            yaml_dict['spec']['template']['spec']['nodeSelector'][
                'karpenter.k8s.aws/instance-family'] = get_instance_family_from_gpu_type(gpu_type)
        else:
            yaml_dict['spec']['template']['spec']['nodeSelector'] = {
                'karpenter.k8s.aws/instance-family': get_instance_family_from_gpu_type(gpu_type)}

        if yaml_dict['spec']['template']['spec']['containers'][0].get('volumeMounts', None):
            yaml_dict['spec']['template']['spec']['containers'][0]['volumeMounts'].append(
                {'name': 'dshm', 'mountPath': '/dev/shm'})
            yaml_dict['spec']['template']['spec']['volumes'].append(
                {'name': 'dshm', 'emptyDir': {'medium': 'Memory', 'sizeLimit': '10Gi'}})
        else:
            yaml_dict['spec']['template']['spec']['containers'][0]['volumeMounts'] = [{'name': 'dshm', 'mountPath': '/dev/shm'}]
            yaml_dict['spec']['template']['spec']['volumes'] = [{'name': 'dshm', 'emptyDir': {'medium': 'Memory', 'sizeLimit': '10Gi'}}]
    else:
        yaml_dict['spec']['template']['spec']['containers'][0]['resources']['requests'][
            'memory'] = f'{str(int(memory))}M'
        yaml_dict['spec']['template']['spec']['containers'][0]['resources']['requests']['cpu'] = f'{str(int(cpu))}m'
        apply_anti_affinity_for_gpus(yaml_dict)


    yaml_dict['spec']['template']['metadata'] = {
        'annotations': {'deploy_time': datetime.now().isoformat()}}

    if entrypoint:
        yaml_dict['spec']['template']['spec']['containers'][0]['command'] = [entrypoint]

    old_job_deleted = find_and_delete_old_job(job_name=job_name, namespace=namespace)
    if not old_job_deleted:
        click.echo("Another Job is already in progress. Please wait for it to complete.")
        if github_actions:
            raise Exception("Another Job is already in progress. Please wait for it to complete.")
        return

    utils.create_from_dict(k8s_api_client, yaml_dict)
    click.echo('Deployed your one shot job.')

    if follow:
        job_pod_name = get_pod_name_corresponing_to_job(job_name=job_name, namespace=namespace)
        if job_pod_name is None:
            click.echo("Job pod not found")
            return PodStatus.FAILED.value
        # TODO: stream multiple lines instead of one by one
        start_streaming_pod(pod_name=job_pod_name, namespace=namespace, status=PodStatus.SUCCEEDED)




