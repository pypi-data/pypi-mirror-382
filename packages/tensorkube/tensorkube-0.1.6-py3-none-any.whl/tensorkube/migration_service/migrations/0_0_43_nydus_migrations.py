
from tensorkube.services.build import configure_buildkit_irsa
from tensorkube.services.environment_service import list_environments
from tensorkube.services.ecr_service import patch_lifecycle_all_tensorkube_ecr_repositories
from tensorkube.services.job_queue_service import deploy_job
from tensorkube.services.k8s_service import get_jobs_by_container_image
from tensorkube.services.knative_service import add_runtimeclass_knative_features, get_gpu_type_from_instance_family
from tensorkube.services.nydus import install_nydus
from tensorkube.services.train import AXOLOTL_IMAGE_SCALED_JOB


def apply(test: bool = False):
    try:
        install_nydus()
        add_runtimeclass_knative_features()
        patch_lifecycle_all_tensorkube_ecr_repositories()
        envs  = list_environments()
        for env in envs:
            configure_buildkit_irsa(env_name=env)
        # trying to migrate jobs
        env = 'keda'
        jobs = get_jobs_by_container_image(AXOLOTL_IMAGE_SCALED_JOB, namespace=env)
        for job in jobs:
            containers = job.get("spec", {}).get("jobTargetRef", {}).get("template", {}).get("spec", {}).get(
                "containers", [])
            node_selector = job.get("spec", {}).get("jobTargetRef", {}).get("template", {}).get("spec", {}).get(
                "nodeSelector", {})
            instance_family = node_selector.get("karpenter.k8s.aws/instance-family")
            gpu_type = get_gpu_type_from_instance_family(instance_family) if instance_family else None
            max_scale = job.get("spec", {}).get("maxReplicaCount")
            job_name = job["metadata"]["name"]

            # Extract secrets from volumes
            volumes = job.get("spec", {}).get("jobTargetRef", {}).get("template", {}).get("spec", {}).get("volumes", [])
            secrets = []
            for volume in volumes:
                if volume.get("name") == "secrets" and "projected" in volume:
                    for source in volume["projected"].get("sources", []):
                        if "secret" in source:
                            secrets.append(source["secret"]["name"])

            for container in containers:
                if container.get("image") == AXOLOTL_IMAGE_SCALED_JOB:
                    resources = container.get("resources", {})
                    gpus = resources.get("limits", {}).get("nvidia.com/gpu")
                    cpu = resources.get("requests", {}).get("cpu")
                    memory = resources.get("requests", {}).get("memory")

                    deploy_job(job_name=job_name, env=env, gpus=gpus, gpu_type=gpu_type, cpu=cpu, memory=memory,
                        max_scale=max_scale, image_tag=AXOLOTL_IMAGE_SCALED_JOB, secrets=secrets, job_type='axolotl',
                               update=True)
            print(f"Migrated the job {job_name} to the latest version")

    except Exception as e:
        raise e
