import click
import importlib.metadata
from typing import Optional, List, Dict

from tensorkube.configurations.cloudformation.configure.cluster_access_lambda_files.lambda_code import \
    get_managed_node_group_name
from tensorkube.constants import get_cluster_name, get_template_bucket_name, DEFAULT_NAMESPACE, \
    get_mount_policy_name, get_mount_driver_role_name, ADDON_NAME, get_cfn_base_stack_name, get_templates_version, \
    AWS_ACCESS_LAMBDA_FUNCTION_IMAGE_VERSION, EKS_ACCESS_LAMBDA_FUNCTION_IMAGE_VERSION, get_image_registry_id, \
    MONITORING_LAMBDA_FUNCTION_IMAGE_VERSION, get_tag_for_repeated_alarm_notification, \
    REPEATED_NOTIFICATION_PERIOD_SECONDS, ALARM_EVALUATION_PERIODS
from tensorkube.helpers import create_mountpoint_driver_role_with_policy
from tensorkube.migration_service.migration_manager.migration_service import set_current_cli_version_to_cluster
from tensorkube.services.aws_service import get_eks_control_plane_available_zones_for_region, \
    get_aws_account_id, get_credentials, get_session_region, get_cloudformation_client
from tensorkube.services.build import get_buildkit_service_account_name, configure_buildkit_irsa
from tensorkube.services.cloudformation_service import is_existing_tk_macro, create_cloudformation_stack, \
    stream_stack_events, cloudformation, update_generic_cloudformation_stack, get_stack_parameter_value, \
    get_stack_status_from_stack_name, CfnStackStatus
from tensorkube.services.eks_service import install_karpenter, apply_knative_crds, apply_knative_core, \
    apply_nvidia_plugin, create_eks_addon
from tensorkube.services.eksctl_service import create_base_tensorkube_cluster_eksctl
from tensorkube.services.filesystem_service import configure_efs
from tensorkube.services.iam_service import create_mountpoint_iam_policy
from tensorkube.services.istio import check_and_install_istioctl, install_istio_on_cluster, install_net_istio
from tensorkube.services.job_queue_service import create_cloud_resources_for_queued_job_support, \
    create_sa_role_rb_for_job_sidecar
from tensorkube.services.k8s_service import create_aws_secret, create_build_pv_and_pvc
from tensorkube.services.karpenter_service import apply_karpenter_configuration
from tensorkube.services.knative_service import enable_knative_selectors_pv_pvc_capabilities
from tensorkube.services.local_service import check_and_install_cli_tools
from tensorkube.services.logging_service import configure_cloudwatch
from tensorkube.services.nydus import get_nydus_snapshoter_namespace, get_nydus_snapshoter_service_account_name, \
    install_nydus
from tensorkube.services.s3_access_service import create_s3_access_to_pods
from tensorkube.services.s3_service import create_s3_bucket, get_bucket_name


def cfn_configure(test: bool, user_alert_email: str = None):
    click.echo("Configuring with cloudformation...")
    cluster_name = get_cluster_name()
    stack_name = get_cfn_base_stack_name()
    create_macro = True

    template_bucket_name = get_template_bucket_name(test)

    if test:
        click.echo("Test run. Checking if Macro exists...")
        create_macro = not is_existing_tk_macro()
        click.echo("Check complete")
        user_alert_email = "divyanshu@tensorfuse.io"

    zones = get_eks_control_plane_available_zones_for_region()
    parameters = [{"ParameterKey": "ClusterName", 'ParameterValue': cluster_name},
                  {"ParameterKey": "CliVersion", 'ParameterValue': importlib.metadata.version("tensorkube")},
                  {"ParameterKey": "KedaTrainBucketName",
                   'ParameterValue': get_bucket_name(env_name='keda', type="train")},
                  {"ParameterKey": "DefaultEnv", 'ParameterValue': DEFAULT_NAMESPACE},
                  {"ParameterKey": "DefaultEnvBuildBucketName", 'ParameterValue': get_bucket_name()},
                  {"ParameterKey": "DefaultEnvBuildkitISRAServiceAccountName",
                   "ParameterValue": get_buildkit_service_account_name(namespace=DEFAULT_NAMESPACE)},
                  {"ParameterKey": "NydusNamespace", 'ParameterValue': get_nydus_snapshoter_namespace()},
                  {"ParameterKey": "NydusServiceAccountName",
                   'ParameterValue': get_nydus_snapshoter_service_account_name()},
                  {"ParameterKey": "CreateMacro", 'ParameterValue': str(create_macro)},
                  {"ParameterKey": "TemplateBucketName", "ParameterValue": template_bucket_name},
                  {"ParameterKey": "TemplatesVersion", "ParameterValue": get_templates_version()},
                  {"ParameterKey": "AWSAccessLambdaFunctionImageVersion", "ParameterValue": AWS_ACCESS_LAMBDA_FUNCTION_IMAGE_VERSION},
                  {"ParameterKey": "EksAccessLambdaFunctionImageVersion", "ParameterValue": EKS_ACCESS_LAMBDA_FUNCTION_IMAGE_VERSION},
                  {"ParameterKey": "MonitoringLambdaFunctionImageVersion", "ParameterValue": MONITORING_LAMBDA_FUNCTION_IMAGE_VERSION},
                  {"ParameterKey": "ImageRegistryId", "ParameterValue": get_image_registry_id(test)},
                  {"ParameterKey": "UserAlertEmail", "ParameterValue": user_alert_email},
                  {"ParameterKey": "EvaluationPeriods", "ParameterValue": ALARM_EVALUATION_PERIODS},
                  {"ParameterKey": "RepeatedNotificationPeriod", "ParameterValue": REPEATED_NOTIFICATION_PERIOD_SECONDS},
                  {"ParameterKey": "TagForRepeatedNotification", "ParameterValue": get_tag_for_repeated_alarm_notification()},
                  {"ParameterKey": "KedaBuildBucketName", "ParameterValue": get_bucket_name(env_name='keda')},
                  {"ParameterKey": "KedaBuildkitISRAServiceAccountName",
                   "ParameterValue": get_buildkit_service_account_name(namespace='keda')},
                   {"ParameterKey": "Region","ParameterValue": get_session_region()},
                  {"ParameterKey": "ManagedNodeGroupName", "ParameterValue": get_managed_node_group_name(get_cluster_name())},
                  ]
    for zone in zones:
        parameters.append({"ParameterKey": ("zone"+zone[-1]).upper(), 'ParameterValue': "true"})

    capabilities = ["CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"]
    creation_queued, in_created_state = create_cloudformation_stack(
        template_file_path="configurations/cloudformation/configure/tensorkube-base-stack.yaml",
        stack_name=stack_name,
        parameters=parameters,
        capabilities=capabilities)
    if creation_queued:
        stream_stack_events(stack_name)


def legacy_configure(vpc_public_subnets: str, vpc_private_subnets: str):
    if not check_and_install_cli_tools():
        return False
    # TODO!: add helm annotations

    # create cloudformation stack
    cloudformation()

    # create eks cluster
    vpc_public_subnets_list = vpc_public_subnets.split(",") if vpc_public_subnets else []
    vpc_private_subnets_list = vpc_private_subnets.split(",") if vpc_private_subnets else []
    create_base_tensorkube_cluster_eksctl(cluster_name=get_cluster_name(), vpc_public_subnets=vpc_public_subnets_list,
                                          vpc_private_subnets=vpc_private_subnets_list)
    # install karpenter
    install_karpenter()
    # # apply karpenter configuration
    apply_karpenter_configuration()
    configure_cloudwatch()
    #
    # install istio networking plane
    check_and_install_istioctl()
    install_istio_on_cluster()

    # install knative crds
    apply_knative_crds()
    # install knative core
    apply_knative_core()

    # install nvidia plugin
    apply_nvidia_plugin()
    #
    # install net istio
    install_net_istio()

    # create s3 bucket for build
    bucket_name = get_bucket_name()
    create_s3_bucket(bucket_name)

    # create mountpoint policy to mount bucket to eks cluster
    create_mountpoint_iam_policy(get_mount_policy_name(get_cluster_name()), bucket_name)

    # create s3 csi driver role and attach mountpoint policy to it
    create_mountpoint_driver_role_with_policy(cluster_name=get_cluster_name(), account_no=get_aws_account_id(),
                                              role_name=get_mount_driver_role_name(get_cluster_name()),
                                              policy_name=get_mount_policy_name(get_cluster_name()))

    # create eks addon to mount s3 bucket to eks cluster
    create_eks_addon(get_cluster_name(), ADDON_NAME, get_aws_account_id(),
                     get_mount_driver_role_name(get_cluster_name()))

    # create aws credentials cluster secret
    # TODO!: figure out how to update credentials in case of token expiry
    create_aws_secret(get_credentials())

    # create pv and pvc claims for build
    create_build_pv_and_pvc(bucket_name)

    # update knative to use pod labels
    enable_knative_selectors_pv_pvc_capabilities()

    # enable Network files system for the cluster
    click.echo("Configuring EFS for the cluster...")
    configure_efs()

    create_s3_access_to_pods()

    # install keda, create related resources
    create_cloud_resources_for_queued_job_support()
    create_sa_role_rb_for_job_sidecar()

    # configure buildkit irsa, so that pods can access ecr
    configure_buildkit_irsa()

    install_nydus()

    # set current cli version to the cluster
    set_current_cli_version_to_cluster()

    return True


def get_configured_user_alert_email():
    email = get_stack_parameter_value(get_cfn_base_stack_name(), "UserAlertEmail")
    return email

def get_parameter_value(parameter_key: str, updated_parameters: dict, test: bool = False) -> Optional[str]:
    if parameter_key == "ClusterName":
        cluster_name = get_cluster_name()
        return updated_parameters.get("ClusterName", cluster_name)
    elif parameter_key == "CliVersion":
        return updated_parameters.get("CliVersion", importlib.metadata.version("tensorkube"))
    elif parameter_key == "KedaTrainBucketName":
        return updated_parameters.get("KedaTrainBucketName", get_bucket_name(env_name='keda', type="train"))
    elif parameter_key == "DefaultEnv":
        return updated_parameters.get("DefaultEnv", DEFAULT_NAMESPACE)
    elif parameter_key == "DefaultEnvBuildBucketName":
        return updated_parameters.get("DefaultEnvBuildBucketName", get_bucket_name())
    elif parameter_key == "DefaultEnvBuildkitISRAServiceAccountName":
        return updated_parameters.get("DefaultEnvBuildkitISRAServiceAccountName",
                                               get_buildkit_service_account_name(namespace=DEFAULT_NAMESPACE))
    elif parameter_key == "NydusNamespace":
        return updated_parameters.get("NydusNamespace", get_nydus_snapshoter_namespace())
    elif parameter_key == "NydusServiceAccountName":
        return updated_parameters.get("NydusServiceAccountName", get_nydus_snapshoter_service_account_name())
    elif parameter_key == "CreateMacro":
        create_macro = True
        if test:
            click.echo("Test run. Checking if Macro exists...")
            create_macro = not is_existing_tk_macro()
            click.echo("Check complete")
        return str(create_macro)
    elif parameter_key == "TemplateBucketName":
        template_bucket_name = get_template_bucket_name(test)
        return updated_parameters.get("TemplateBucketName", template_bucket_name)
    elif parameter_key == "TemplatesVersion":
        return updated_parameters.get("TemplatesVersion", get_templates_version())
    elif parameter_key == "AWSAccessLambdaFunctionImageVersion":
        return updated_parameters.get("AWSAccessLambdaFunctionImageVersion",
                                               AWS_ACCESS_LAMBDA_FUNCTION_IMAGE_VERSION)
    elif parameter_key == "EksAccessLambdaFunctionImageVersion":
        return updated_parameters.get("EksAccessLambdaFunctionImageVersion",
                                               EKS_ACCESS_LAMBDA_FUNCTION_IMAGE_VERSION)
    elif parameter_key == "ImageRegistryId":
        return updated_parameters.get("ImageRegistryId", get_image_registry_id(test))
    elif parameter_key == "MonitoringLambdaFunctionImageVersion":
        return updated_parameters.get("MonitoringLambdaFunctionImageVersion",
                                      MONITORING_LAMBDA_FUNCTION_IMAGE_VERSION)
    elif parameter_key == "UserAlertEmail":
        email = updated_parameters.get("UserAlertEmail", get_configured_user_alert_email())
        if not email:
            raise click.ClickException("User Alert Email is not set")
        return email
    elif parameter_key == "EvaluationPeriods":
        return updated_parameters.get("EvaluationPeriods", ALARM_EVALUATION_PERIODS)
    elif parameter_key == "RepeatedNotificationPeriod":
        return updated_parameters.get("RepeatedNotificationPeriod", REPEATED_NOTIFICATION_PERIOD_SECONDS)
    elif parameter_key == "TagForRepeatedNotification":
        return updated_parameters.get("TagForRepeatedNotification", get_tag_for_repeated_alarm_notification())
    elif parameter_key == "KedaBuildBucketName":
        return updated_parameters.get("KedaBuildBucketName", get_bucket_name(env_name='keda'))
    elif parameter_key == "KedaBuildkitISRAServiceAccountName":
        return updated_parameters.get("KedaBuildkitISRAServiceAccountName",
                                               get_buildkit_service_account_name(namespace='keda'))
    elif parameter_key == "ManagedNodeGroupName":
        return updated_parameters.get("ManagedNodeGroupName", get_managed_node_group_name(cluster_name=get_cluster_name()))
    elif parameter_key == "Region":
        return get_session_region()
    elif parameter_key in ["ZONEA", "ZONEB", "ZONEC", "ZONED", "ZONEE", "ZONEF"]:
        return None
    else:
        raise Exception(f"Unknown parameter key : {parameter_key}")



def generate_cfn_parameters_dict_list(template_url: str, updated_parameters: dict, test: bool = False) -> List[Dict]:
    cfn_client = get_cloudformation_client()

    # Get parameters defined in the template
    response = cfn_client.get_template_summary(TemplateURL=template_url)
    parameters = response.get('Parameters', [])

    # Build Parameters list for stack operations
    parameter_list = []
    for param in parameters:
        key = param['ParameterKey']
        value = get_parameter_value(key, updated_parameters, test)
        if value is not None:
            parameter_list.append({
                'ParameterKey': key,
                'ParameterValue': value
            })

    return parameter_list

def update_cfn_configure_stack(updated_parameters, test=False):
    click.echo("Updating base cloudformation stack...")
    stack_name = get_cfn_base_stack_name()

    template_bucket_name = get_template_bucket_name(test)
    templates_version = updated_parameters.get("TemplatesVersion", get_templates_version())
    base_stack_url = f"https://{template_bucket_name}.s3.us-east-1.amazonaws.com/{templates_version}/tensorkube-base-stack.yaml"

    zones = get_eks_control_plane_available_zones_for_region()
    parameters = generate_cfn_parameters_dict_list(base_stack_url, updated_parameters, test)
    for zone in zones:
        parameters.append({"ParameterKey": ("zone" + zone[-1]).upper(), 'ParameterValue': "true"})

    capabilities = ["CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"]
    update_generic_cloudformation_stack(stack_name=stack_name, parameters=parameters, capabilities=capabilities,
                                        template_url = f"https://{template_bucket_name}.s3.us-east-1.amazonaws.com/{templates_version}/tensorkube-base-stack.yaml")
    stack_status = get_stack_status_from_stack_name(stack_name)
    if stack_status == CfnStackStatus.UPDATE_COMPLETE:
        click.echo(click.style("Successfully updated base stack", bold=True, fg="green"))
    else:
        click.echo(click.style(f"Failed to update base stack. Current status: {stack_status}", bold=True, fg="red"))
        raise click.ClickException(f"Failed to update base stack. Current status: {stack_status}")
