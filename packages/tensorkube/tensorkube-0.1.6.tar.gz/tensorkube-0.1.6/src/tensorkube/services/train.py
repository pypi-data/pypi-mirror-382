import json
import logging
import time
from typing import Optional, List
import click
import yaml
from kubernetes import config, utils
from kubernetes.client.rest import ApiException
from pkg_resources import resource_filename

from tensorkube.constants import DEFAULT_NAMESPACE, get_cluster_name, DATASET_BUCKET_TYPE
from tensorkube.helpers import sanitise_name
from tensorkube.services.aws_service import get_logs_client
from tensorkube.services.deploy import DEFAULT_CPU, DEFAULT_MEMORY
from tensorkube.services.job_queue_service import deploy_job, queue_job, is_existing_queued_job
from tensorkube.services.k8s_service import get_tensorkube_cluster_context_name, create_configmap, generate_kubeconfig
from tensorkube.services.knative_service import get_instance_family_from_gpu_type
from tensorkube.services.s3_access_service import get_s3_service_account_name
from tensorkube.services.s3_service import create_s3_bucket, get_bucket_name

# disable botocore info logs
logging.getLogger('botocore').setLevel(logging.CRITICAL)

AXOLOTL_IMAGE_TRAIN_JOB = "gane5h/build_tool:axo"
AXOLOTL_IMAGE_SCALED_JOB = "tensorfuse/axolotl-train:v0.0.10"


def get_training_stats(job_name: str, start_time: int, namespace: str = "default"):
    log_group = f"/aws/containerinsights/{get_cluster_name()}/application"
    log_stream_prefix = job_name
    client = get_logs_client()
    # Define the log query pattern to search for
    log_pattern = 'loss'
    end_time = int(time.time())
    try:
        # Start the query
        response = client.start_query(logGroupName=log_group, startTime=start_time, endTime=end_time,
            queryString=f"fields @timestamp, @message | filter @message like /'{log_pattern}'/ and @logStream like /{log_stream_prefix}/ | sort @timestamp desc | limit 1")
        query_id = response["queryId"]

        while True:
            # Poll for the query results
            time.sleep(1)
            results = client.get_query_results(queryId=query_id)

            # Check if query is complete
            if results["status"] in ["Complete", "Failed", "Cancelled", "Timeout", "Unknown"]:
                break
        msg = ""
        if results["status"] == "Complete" and results["results"]:
            # Extract the relevant log from the results
            for result in results["results"]:
                message = result[1]["value"]
                message_dict = json.loads(message)
                msg = message_dict["log"]
                return msg
    except client.exceptions.ResourceNotFoundException as e:
        print(f"Resource not found: {e}")  # TODO: use good logger
    except Exception as e:
        print(f"An error occurred: {e}")  # TODO: use good logger
    return msg


def apply_training_job(job_name: str, namespace: str, yaml_file_path: str, gpus: int, gpu_type: str,
                       context_name: Optional[str] = None, secrets: List[str] = [], image_url: Optional[str] = None,
                       bucket: Optional[str] = None):
    # Load kube config
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Read the YAML file
    with open(yaml_file_path, 'r') as f:
        yaml_content = f.read()

    image_tag = image_url.split(':')[-1]
    click.echo(f"Creating job {job_name} with {gpus} GPUs.")
    yaml_content = yaml_content.replace('${JOB_NAME}', job_name)
    yaml_content = yaml_content.replace('${GPUS}', str(gpus))
    yaml_content = yaml_content.replace('${IMAGE_URL}', image_url)
    yaml_content = yaml_content.replace('${IMAGE_TAG}', image_tag)
    yaml_content = yaml_content.replace('${NAMESPACE}', namespace)
    yaml_content = yaml_content.replace('${AXOLOTL_CONFIGMAP_NAME}', f"{job_name}-config")

    # Load the YAML content    
    yaml_dict = yaml.safe_load(yaml_content)
    yaml_dict['spec']['template']['spec']['serviceAccountName'] = get_s3_service_account_name(namespace)
    if bucket:
        yaml_dict['spec']['template']['spec']['containers'][0]['env'].append(
            {'name': 'LORA_ADAPTER_BUCKET', 'value': bucket  # TODO: should we take region as well?
             })
    yaml_dict['spec']['template']['spec']['containers'][0]['env'].append({'name': 'JOB_NAME', 'value': job_name})

    if secrets:
        yaml_dict['spec']['template']['spec']['volumes'].append({'name': 'secrets', 'projected': {
            'sources': [{'secret': {'name': secret_name}} for secret_name in secrets]}})

        yaml_dict['spec']['template']['spec']['containers'][0]['volumeMounts'].append(
            {'name': 'secrets', 'mountPath': '/mnt/secrets', 'readOnly': True})

    yaml_dict['spec']['template']['spec']['nodeSelector'] = {
        'karpenter.k8s.aws/instance-family': get_instance_family_from_gpu_type(gpu_type), }

    # Create the job
    utils.create_from_dict(k8s_api_client, yaml_dict)
    click.echo(f"Job {job_name} created successfully.")


def get_job_prefix_from_job_id(job_id: str) -> str:
    job_name = sanitise_name(job_id)
    job_name = f"ax-{job_name}"
    return job_name


def get_training_id_from_job_name(job_name: str) -> str:
    return job_name.split('ax-')[1]


def validate_training_config(config: dict):
    if 'base_model' not in config:
        raise Exception("base_model is required")
    if 'datasets' not in config:
        raise Exception("datasets is required")
    return


def get_dataset_path(dataset_name: str, cluster_region: Optional[str] = None) -> str:
    bucket_name = get_bucket_name(type=DATASET_BUCKET_TYPE, cluster_region=cluster_region)
    return f"s3://{bucket_name}/{dataset_name}.jsonl"


def get_axolotl_base_config(gpus: int) -> dict:
    fileName = resource_filename('tensorkube', 'configurations/axolotl_configs/single_gpu.yaml')
    if gpus > 1:
        fileName = resource_filename('tensorkube', 'configurations/axolotl_configs/multi_gpu.yaml')
    with open(fileName, 'r') as f:
        yaml_dict = yaml.safe_load(f)
    return yaml_dict


# todo: currently supporting one dataset inside datasets
def convert_dataset_to_s3_path(datasets: dict, cluster_region: Optional[str] = None) -> str:
    if len(datasets) != 1:
        raise Exception("Only one dataset is supported")
    dataset = datasets[0]
    if 'id' in dataset:
        dataset['path'] = get_dataset_path(dataset['id'], cluster_region=cluster_region)
        return dataset['path']

    return dataset['path']


def axolotl_train(env: str, secrets: list, gpus: int, gpu_type: str, job_id: str, config_path: str):
    if config_path is None:
        raise Exception("config_path is required")
    if job_id is None:
        raise Exception("job_id is required")

    bucket_name = get_bucket_name(env_name=env, type='train')
    create_s3_bucket(bucket_name)
    yaml_dict = None
    with open(config_path, 'r') as f:  # user config path
        yaml_dict = yaml.safe_load(f)
    if yaml_dict is None or len(yaml_dict) == 0:
        raise Exception("Invalid yaml data")
    # validate the config
    validate_training_config(yaml_dict)
    # merge with base config
    base_yaml_dict = get_axolotl_base_config(gpus)
    yaml_dict = {**base_yaml_dict, **yaml_dict}
    # convert dataset to s3 path
    s3_path = convert_dataset_to_s3_path(yaml_dict['datasets'])
    namespace = DEFAULT_NAMESPACE if not env else env
    job_name = f'{get_job_prefix_from_job_id(job_id)}'
    try:
        config_name = f"{job_name}-config"
        create_configmap(config_name, namespace=namespace, data=yaml_dict, context_name=None, force=True)
    except Exception as e:
        raise Exception("Failed to create the configmap")

    yaml_file_path = resource_filename('tensorkube', 'configurations/build_configs/axolotl-train.yaml')

    try:
        apply_training_job(job_name, namespace, yaml_file_path, gpus, gpu_type, secrets=secrets,
                           image_url=AXOLOTL_IMAGE_TRAIN_JOB, bucket=bucket_name)
    except Exception as e:
        raise Exception("Failed to create the training job")
    return


# from hugging face model path
supported_base_models = ['meta-llama/Llama-3.1-70B-Instruct', 'meta-llama/Llama-3.1-8B-Instruct', 'google/gemma-3-27b-it']


def get_dataset_config_for_base_model(base_model: str, s3_path: str) -> dict:
    if base_model not in supported_base_models:
        raise Exception(f"Invalid base model {base_model}")
    base_config = get_axolotl_base_config_by_model(base_model)
    base_config['datasets'][0]['path'] = s3_path
    return base_config['datasets']


def get_config_from_paramaters(base_model: str, dataset: str, epochs: int, micro_batch_size: int, learning_rate: float,
                               lora_r: int,base_config: dict,wandb_entity=Optional[str], wandb_project=Optional[str],
                               wandb_name=Optional[str], val_set_size=Optional[float], hf_org_id: Optional[str] = None,
                               cluster_region: Optional[str] = None) -> dict:
    if micro_batch_size is None:
        micro_batch_size = base_config['micro_batch_size']
    if learning_rate is None:
        learning_rate = base_config['learning_rate']
    if lora_r is None:
        lora_r = base_config['lora_r']
    datasets_config = []
    if "s3://" in dataset:
        datasets_config = [{"path": dataset}]
    else:
        datasets_config = [{"id": dataset}]
    if val_set_size is None:
        val_set_size = base_config['val_set_size']
        evals_per_epoch = base_config['evals_per_epoch']
    else:
        evals_per_epoch = 1
    if wandb_entity is None or wandb_project is None:
        wandb_entity = base_config['wandb_entity']
        wandb_project = base_config['wandb_project']
    config = {"base_model": base_model, "datasets": datasets_config, "num_epochs": epochs,
        "micro_batch_size": micro_batch_size, "learning_rate": learning_rate, "lora_r": lora_r,
              "evals_per_epoch": evals_per_epoch,
              "val_set_size": val_set_size,
              "wandb_entity": wandb_entity, "wandb_project": wandb_project, "wandb_name": wandb_name, "hf_org_id": hf_org_id}
    s3_path = convert_dataset_to_s3_path(config['datasets'], cluster_region=cluster_region)
    config['datasets'] = get_dataset_config_for_base_model(base_model, s3_path)
    return config


def get_axolotl_base_config_by_model(base_model: str) -> dict:
    if base_model not in supported_base_models:
        raise Exception(f"Invalid base model {base_model}")
    filename = ''
    if base_model == 'meta-llama/Llama-3.1-70B-Instruct':
        fileName = resource_filename('tensorkube', 'configurations/axolotl_configs/llama-3.1-70B-Instruct.yaml')
    elif base_model == 'meta-llama/Llama-3.1-8B-Instruct':
        fileName = resource_filename('tensorkube', 'configurations/axolotl_configs/llama-3.1-8B-Instruct.yaml')
    elif base_model == 'google/gemma-3-27b-it':
        fileName = resource_filename('tensorkube', f'configurations/axolotl_configs/gemma-3-27b-it.yaml')
    else:
        raise Exception(f"Invalid base model {base_model}")
    with open(fileName, 'r') as f:
        yaml_dict = yaml.safe_load(f)
    return yaml_dict


def create_fine_tuning_job(job_name: str, job_id: str, gpus: int, gpu_type: str, max_scale: int, base_model: str,
                           dataset: str, epochs: int, cpu: float = DEFAULT_CPU, memory: float = DEFAULT_MEMORY,
                           secrets: List[str] = [], micro_batch_size: Optional[int] = None,
                           learning_rate: Optional[float] = None, lora_r: Optional[int] = None,
                           val_set_size: Optional[float] = None, cluster_region: Optional[str] = None,
                           wandb_entity: Optional[str] = None, hf_org_id: Optional[str] = None, store_weights_as_bf16: bool= False, **kwargs) -> None:
    # create the job definition
    env = 'keda'
    # validate the base model
    if base_model not in supported_base_models:
        raise Exception(f"Invalid base model {base_model}")
    try:
        generate_kubeconfig(cluster_region=cluster_region)
    except Exception as e:
        raise Exception(f"Failed to generate kubeconfig, {e}")
    try:
        exist, _ = is_existing_queued_job(job_name=job_name)
        if not exist:
            deploy_job(job_name=job_name, env=env, gpus=gpus, gpu_type=gpu_type, cpu=cpu, memory=memory,
                       max_scale=max_scale, image_tag=AXOLOTL_IMAGE_SCALED_JOB, secrets=secrets, job_type='axolotl',
                       cluster_region=cluster_region)
    except ApiException as e:
        if e.status == 409:
            click.echo(f"Job {job_name} already exists.")
        else:
            raise Exception(f"Failed to deploy job: {e}")
    base_yaml_dict = get_axolotl_base_config_by_model(base_model=base_model)
    config = get_config_from_paramaters(base_model=base_model, dataset=dataset, epochs=epochs,
                                        micro_batch_size=micro_batch_size, learning_rate=learning_rate, lora_r=lora_r,
                                        wandb_entity=wandb_entity, wandb_project=job_name,
                                        val_set_size=val_set_size,
                                        wandb_name=job_id,
                                        base_config=base_yaml_dict,
                                        hf_org_id=hf_org_id,
                                        cluster_region=cluster_region)
    config['store_weights_as_bf16'] = store_weights_as_bf16
    yaml_dict = {**base_yaml_dict, **config}
    yaml_dict = {**yaml_dict, **kwargs}
    payload = json.dumps(yaml_dict)
    queue_job(job_name, job_id, payload, cluster_region=cluster_region)
    return
