from typing import Optional, List
from tensorkube.constants import DEFAULT_NAMESPACE, get_cluster_name
from tensorkube.services.aws_service import get_aws_account_id, get_session_region
from tensorkube.services.nydus import get_nydus_image_url
from tensorkube.services.k8s_service import get_tensorkube_cluster_context_name, get_s3_claim_name, get_efs_claim_name
from pkg_resources import resource_filename
import yaml
import click
from kubernetes import config, utils
from tensorkube.services.iam_service import create_or_update_iam_role_with_service_account_cluster_access, attach_role_policy, delete_iam_role
from tensorkube.services.eks_service import get_cluster_oidc_issuer_url
from tensorkube.services.k8s_service import patch_service_account, create_service_account

    
def get_buildkit_command(sanitised_project_name: str, image_tag: str, image_url: Optional[str] =None,
                         upload_to_nfs: bool= False, convert_to_nydus_image: bool = False, secrets: List[str] = [],
                         relative_dockerfile_path: str = "Dockerfile"):
    region = get_session_region()
    aws_account_number =  get_aws_account_id()
    secrets_to_env_vars_command = ""
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
                        # Append to the env_vars string in the format --secret id=<filename>,src=<folder_path>/<filename>
                        env_vars="$env_vars --secret id=$filename,src=$folder_path/$filename"
                    fi
                done"""
    # Ensure dockerfile local is mounted and filename is relative to that root
    command = [ "/bin/sh", "-c",
        f"""
        apk add --no-cache curl unzip aws-cli docker
        aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {aws_account_number}.dkr.ecr.{region}.amazonaws.com
        {secrets_to_env_vars_command}
        buildctl-daemonless.sh build\
            --frontend dockerfile.v0\
            --local context=/data/build/{sanitised_project_name}\
            --local dockerfile=/data/build/{sanitised_project_name}\
            --opt filename={relative_dockerfile_path}\
            --output type=image,name={image_url},push=true \
            $env_vars
        """
    ]
    if convert_to_nydus_image:
        nydus_image_url = get_nydus_image_url(image_url=image_url)
        command = [ "/bin/sh", "-c",
            f"""
            apk add --no-cache curl unzip aws-cli docker
            aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {aws_account_number}.dkr.ecr.{region}.amazonaws.com
            {secrets_to_env_vars_command}
            time buildctl-daemonless.sh build\
                --frontend dockerfile.v0\
                --local context=/data/build/{sanitised_project_name}\
                --local dockerfile=/data/build/{sanitised_project_name}\
                --opt filename={relative_dockerfile_path}\
                --output type=image,name={nydus_image_url},push=true,compression=nydus,force-compression=true,oci-mediatypes=true \
                $env_vars
            """
        ]
        return command

    if upload_to_nfs:
        command =  ["/bin/sh", "-c", f"""
        mkdir -p /data/cache
        mkdir -p /test/tars/{sanitised_project_name} /mnt/efs/images/{sanitised_project_name}/{image_tag}/rootfs /test/tars/{sanitised_project_name} /test/images/{sanitised_project_name}/rootfs
        {secrets_to_env_vars_command}
        time buildctl-daemonless.sh build\
            --frontend dockerfile.v0\
            --local context=/data/build/{sanitised_project_name}\
            --local dockerfile=/data/build/{sanitised_project_name}\
            --opt filename={relative_dockerfile_path}\
            --output type=tar,dest=/test/tars/{sanitised_project_name}/{sanitised_project_name}-{image_tag}.tar \
            $env_vars
        if [ $? -ne 0 ]; then
            echo "buildctl-daemonless.sh command failed"
            exit 1
        fi
        echo "Extracting rootfs from tar file"
        time tar -xf /test/tars/{sanitised_project_name}/{sanitised_project_name}-{image_tag}.tar -C /test/images/{sanitised_project_name}/rootfs --checkpoint=1000 --checkpoint-action=echo="Extracted #%u: %T"
        if [ $? -ne 0 ]; then
            echo "extracting rootfs from tar file failed"
            exit 1
        fi
        echo "Extracted rootfs from tar file"
        echo "Uploading rootfs to NFS"
        cd /test/images/{sanitised_project_name}/rootfs
        find . -type d | split -l 5000 - batch_dir_
        find . -type f | split -l 5000 - batch_file_
        find . -type l | split -l 5000 - batch_link_

        total_batches=$(ls batch_* | wc -l)
        processed_batches=0
        total_time=0

        process_batches() {{
            local batch_type=$1
            for batch_file in batch_${{batch_type}}_*; do
                start_time=$(date +%s)
                
                if [ "$batch_type" == "dir" ]; then
                    cat $batch_file | parallel -j 15 mkdir -p /mnt/efs/images/{sanitised_project_name}/{image_tag}/rootfs/{{}}
                elif [ "$batch_type" == "file" ]; then
                    cat $batch_file | parallel -j 15 cp --parents {{}} /mnt/efs/images/{sanitised_project_name}/{image_tag}/rootfs/
                elif [ "$batch_type" == "link" ]; then
                    cat $batch_file | parallel -j 15 cp --parents -P {{}} /mnt/efs/images/{sanitised_project_name}/{image_tag}/rootfs/
                fi
                
                end_time=$(date +%s)
                batch_time=$((end_time - start_time))
                total_time=$((total_time + batch_time))
                processed_batches=$((processed_batches + 1))
                remaining_batches=$((total_batches - processed_batches))
                avg_time_per_batch=$((total_time / processed_batches))
                estimated_remaining_time=$((avg_time_per_batch * remaining_batches))
                
                echo "Processed batch $processed_batches/$total_batches. Remaining: $remaining_batches. Time for this batch: $batch_time seconds. Estimated remaining time: $estimated_remaining_time seconds."
                rm $batch_file
            done
        }}

        process_batches "dir"
        process_batches "file"
        process_batches "link"
        echo "Uploaded rootfs to NFS" """]
    return command


def apply_k8s_buildkit_config(sanitised_project_name: str, image_tag: str,
                              env_name: Optional[str] = None, context_name: Optional[str] = None,
                              image_url: Optional[str] = None, upload_to_nfs: bool = False,
                              convert_to_nydus_image: bool = False, secrets: List[str] = [],
                              relative_dockerfile_path: str = "Dockerfile"):
    if not context_name:
        context_name = get_tensorkube_cluster_context_name()
        if not context_name:
            return None
    k8s_api_client = config.new_client_from_config(context=context_name)

    buildkit_config_file_path = resource_filename('tensorkube', 'configurations/build_configs/buildkit.yaml')
    with open(buildkit_config_file_path) as f:
        buildkit_config = yaml.safe_load(f)

    buildkit_config['metadata']['name'] = 'buildkit-{}'.format(sanitised_project_name)
    buildkit_config['spec']['template']['spec']['containers'][0]['env'][0]['value'] = get_session_region()
    buildkit_config['spec']['ttlSecondsAfterFinished'] = 100
    

    # Include the namespace in the buildkit configuration
    # Replace 'default' with your default namespace if needed
    namespace_to_use = env_name if env_name else DEFAULT_NAMESPACE
    buildkit_config['metadata']['namespace'] = namespace_to_use
    
    # set service account name so that pod can access ECR   
    buildkit_config['spec']['template']['spec']['serviceAccountName'] = get_buildkit_service_account_name(namespace=namespace_to_use)

    # mount secrets as volume to the buildkit configuration
    buildkit_config["spec"]["template"]["spec"]["volumes"].append(
        {
            "name": "secrets",
            "projected": {
                "sources": [
                    {"secret": {"name": secret_name}} for secret_name in secrets
                ]
            },
        }
    )

    buildkit_config["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(
        {"name": "secrets", "mountPath": "/mnt/secrets", "readOnly": True}
    )
    
    
    # Modify volume claim names based on env_name
    for volume in buildkit_config['spec']['template']['spec']['volumes']:
        if volume['name'] == 'persistent-storage':
            volume['persistentVolumeClaim']['claimName'] = get_s3_claim_name(env_name=env_name)
        elif volume['name'] == 'efs-pvc':
            volume['persistentVolumeClaim']['claimName'] = get_efs_claim_name(env_name=env_name)

    buildkit_config['spec']['template']['spec']['containers'][0]['command'] = get_buildkit_command(
        sanitised_project_name, image_tag, image_url, upload_to_nfs, convert_to_nydus_image, secrets,
        relative_dockerfile_path=relative_dockerfile_path)

    utils.create_from_dict(k8s_api_client, buildkit_config)
    click.echo('Deployed a Buildkit image')


def configure_buildkit_irsa(env_name: Optional[str] = None):
    namespace = env_name if env_name else DEFAULT_NAMESPACE
    service_account_name = get_buildkit_service_account_name(namespace=namespace)
    create_service_account(service_account_name, namespace)
    role_name = get_buildkit_ecr_iam_role_name()
    role = create_or_update_iam_role_with_service_account_cluster_access(get_aws_account_id(),get_cluster_oidc_issuer_url(get_cluster_name()), role_name, service_account_name, namespace)
    role_arn = role["Role"]["Arn"]
    attach_role_policy("aws", "AmazonEC2ContainerRegistryPowerUser", role_name)
    patch_service_account(role_arn, service_account_name, namespace)

def get_buildkit_service_account_name(namespace: str):
    return f"{get_cluster_name()}-{namespace}-buildkit-sa"

def get_buildkit_ecr_iam_role_name():
    return f"{get_cluster_name()}-buildkit-ecr-role"


def delete_buildkit_irsa():
    role_name = get_buildkit_ecr_iam_role_name()
    delete_iam_role(role_name)
    click.echo(f"Deleted Buildkit IAM role '{role_name}'")