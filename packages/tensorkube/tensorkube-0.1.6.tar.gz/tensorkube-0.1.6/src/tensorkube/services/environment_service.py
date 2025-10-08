import click

from tensorkube.constants import TENSORFUSE_NAMESPACES, DEFAULT_NAMESPACE, get_cluster_name, \
    get_efs_security_group_name, get_mount_policy_name, get_mount_driver_role_name
from tensorkube.services.aws_service import get_aws_account_id
from tensorkube.services.filesystem_service import configure_efs_for_the_cluster, apply_efs_pv, apply_efs_pvc, \
    get_efs_pvc_name, get_efs_pv_name, delete_efs_filesystem, get_efs_name, delete_security_group
from tensorkube.services.iam_service import create_mountpoint_iam_policy, attach_role_policy, detach_role_policy, \
    delete_policy
from tensorkube.services.k8s_service import create_new_namespace, list_all_namespaces, delete_namespace, \
    create_build_pv_and_pvc, delete_pvc_using_name_and_namespace, get_s3_claim_name, delete_pv_using_name, \
    get_s3_pv_name, delete_all_jobs_in_namespace, delete_aws_secret
from tensorkube.services.knative_service import delete_all_ksvc_from_namespace
from tensorkube.services.s3_service import create_s3_bucket, delete_s3_bucket, get_bucket_name
from tensorkube.services.s3_access_service import delete_s3_access_to_pods
from tensorkube.services.build import configure_buildkit_irsa


def create_new_environment(env_name: str):
    # create a new namespace for the environment
    # create an s3 bucket for the environment
    # Create NFS mounts for the environment
    if env_name is None:
        click.echo("Please provide a valid environment name")
        return
    if env_name in list_environments():
        click.echo("Environment already exists. Skipping creation")
        return
    if env_name in TENSORFUSE_NAMESPACES or env_name == DEFAULT_NAMESPACE:
        click.echo("Cannot create a system namespace")
        return
    # Create S3 Bucket
    bucket_name = get_bucket_name(env_name=env_name)
    cluster_name = get_cluster_name()
    create_s3_bucket(bucket_name)

    create_new_namespace(env_name=env_name)
    
    policy_name = get_mount_policy_name(cluster_name=cluster_name, env=env_name)
    create_mountpoint_iam_policy(policy_name=policy_name, bucket_name=bucket_name)
    attach_role_policy(account_no=get_aws_account_id(), policy_name=policy_name,
                       role_name=get_mount_driver_role_name(cluster_name=cluster_name))
    # Create PV and PVC for s3
    create_build_pv_and_pvc(bucket_name, env=env_name)
    # configure efs for the environment
    configure_efs_for_the_cluster(env=env_name)
    apply_efs_pv(env=env_name)
    apply_efs_pvc(env=env_name)
    configure_buildkit_irsa(env_name=env_name)


def delete_environment(env_name: str, is_teardown = False):
    # delete the namespace for the environment
    # delete the s3 bucket for the environment
    # delete the NFS mounts for the environment
    if env_name is None:
        click.echo("Please provide a valid environment name to delete")
        return
    if env_name in TENSORFUSE_NAMESPACES:
        click.echo("Cannot delete a system namespace")
        return
    if env_name == DEFAULT_NAMESPACE and (not is_teardown):
        click.echo("Cannot delete a system namespace")
        return
    if env_name not in list_environments():
        click.echo("Environment does not exist. Skipping deletion")
        return
    # delete all ksvcs in the namespace
    delete_all_ksvc_from_namespace(namespace=env_name)
    delete_all_jobs_in_namespace(namespace=env_name)
    # delete all s3 configuration
    bucket_name = get_bucket_name(env_name=env_name)
    cluster_name = get_cluster_name()
    policy_name = get_mount_policy_name(cluster_name=cluster_name, env=env_name)
    try:
        detach_role_policy(account_no=get_aws_account_id(), policy_name=policy_name,
                           role_name=get_mount_driver_role_name(cluster_name=cluster_name))
    except Exception as e:
        click.echo(f"An error occurred while detaching policy from role: {e}")

    try:
        delete_policy(get_aws_account_id(), policy_name)
    except Exception as e:
        click.echo(f"An error occurred while deleting policy: {e}")
    delete_pvc_using_name_and_namespace(pvc_name=get_s3_claim_name(env_name=env_name), namespace=env_name)
    delete_pv_using_name(pv_name=get_s3_pv_name(env_name=env_name))
    delete_s3_bucket(bucket_name=bucket_name)
    train_bucket_name = get_bucket_name(env_name=env_name, type='train')
    delete_s3_bucket(bucket_name=train_bucket_name)
    delete_aws_secret(env_name)
    delete_s3_access_to_pods(env_name)
    # delete efs
    delete_pvc_using_name_and_namespace(pvc_name=get_efs_pvc_name(env=env_name), namespace=env_name)
    delete_pv_using_name(pv_name=get_efs_pv_name(env=env_name))
    delete_efs_filesystem(get_efs_name(cluster_name=get_cluster_name(), env=env_name))
    delete_security_group(get_efs_security_group_name(env=env_name))
    # delete the namespace
    delete_namespace(env_name)


def list_environments():
    namespaces = list_all_namespaces()
    environments = []
    for namespace in namespaces:
        if namespace not in TENSORFUSE_NAMESPACES:
            environments.append(namespace)
    return environments


def check_environment_exists(env_name: str) -> bool:
    return env_name in list_environments()
