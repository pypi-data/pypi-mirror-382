import json
from kubernetes import config, client
import click
import subprocess
from packaging.version import Version
from pkg_resources import resource_filename
from tensorkube.constants import get_cluster_name, CliColors, get_image_registry_id
from tensorkube.services.aws_service import get_karpenter_namespace, get_aws_account_id, get_session_region, \
    get_availability_zones
from tensorkube.services.k8s_service import add_helm_annotations_and_labels, get_helm_release_version, \
    get_unhealthy_nodes, get_tensorkube_cluster_context_name
from tensorkube.services.configure_service import update_cfn_configure_stack
from tensorkube.services.iam_service import create_iam_policy, attach_role_policy, detach_role_policy, delete_policy
from tensorkube.services.eks_service import install_karpenter_with_command


def add_do_not_disrupt_annotation_to_keda_pods():
    context_name = get_tensorkube_cluster_context_name()
    if not context_name:
        raise Exception("Unable to get cluster context")
    k8s_api_client = config.new_client_from_config(context=context_name)

    # Load the existing kubeconfig
    v1 = client.CoreV1Api(k8s_api_client)
    namespace = "keda"

    # List all pods in the keda namespace
    pods = v1.list_namespaced_pod(namespace=namespace)

    for pod in pods.items:
        # Check if the pod is in Pending or Running state
        if pod.status.phase in ["Pending", "Running"]:
            if ("keda-admission-webhooks" in pod.metadata.name
                or "keda-operator" in pod.metadata.name
                    or "keda-operator-metrics-apiserver" in pod.metadata.name):
                continue
            annotations = pod.metadata.annotations or {}
            annotations["karpenter.sh/do-not-disrupt"] = "true"

            # Patch the pod with the updated annotations
            body = {
                "metadata": {
                    "annotations": annotations
                }
            }
            v1.patch_namespaced_pod(name=pod.metadata.name, namespace=namespace, body=body)
            print(f"Added do-not-disrupt annotation to pod: {pod.metadata.name}")


def apply(test: bool = False):
    try:
        cluster_name = get_cluster_name()
        region = get_session_region()
        unhealthy_nodes = get_unhealthy_nodes(cluster_name=cluster_name)
        if unhealthy_nodes:
            click.echo(click.style("Nodes in Not Ready state found. If these are unhealthy, please manually delete them and rerun the migration."
                                   "Please contact support if you are unsure or need any other help.", fg=CliColors.ERROR.value))
            raise Exception("NotReady nodes found. If these are unhealthy, please manually delete them and rerun the migration. Please contact support if you are unsure or need any other help.")

        account_id = get_aws_account_id()
        karpenter_version = "0.37.7"
        karpenter_namespace = get_karpenter_namespace()
        karpenter_iam_role_arn = f"arn:aws:iam::{account_id}:role/{cluster_name}-karpenter"

        click.echo("Adding Helm labels and annotations to Karpenter CRDs")

        add_helm_annotations_and_labels(resource_api_version="apiextensions.k8s.io/v1",
                                        resource_type="CustomResourceDefinition",
                                        resource_name="ec2nodeclasses.karpenter.k8s.aws", release_name="karpenter-crd",
                                        release_namespace="kube-system", resource_namespace=None)
        add_helm_annotations_and_labels(resource_api_version="apiextensions.k8s.io/v1",
                                        resource_type="CustomResourceDefinition",
                                        resource_name="nodeclaims.karpenter.sh", release_name="karpenter-crd",
                                        release_namespace="kube-system", resource_namespace=None)
        add_helm_annotations_and_labels(resource_api_version="apiextensions.k8s.io/v1",
                                        resource_type="CustomResourceDefinition",
                                        resource_name="nodepools.karpenter.sh", release_name="karpenter-crd",
                                        release_namespace="kube-system", resource_namespace=None)



        installed_karpenter_version = get_helm_release_version("karpenter", "kube-system")
        installed_karpenter_crd_version = get_helm_release_version("karpenter-crd", "kube-system")

        if Version(installed_karpenter_version) < Version(karpenter_version):
            click.echo(f"Upgrading Karpenter to version {karpenter_version}")
            install_command = ["helm", "upgrade", "--install", "karpenter", "oci://public.ecr.aws/karpenter/karpenter",
                 f"--version", karpenter_version, "--namespace", f"{karpenter_namespace}", "--create-namespace",
                 "--set", f'serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn={karpenter_iam_role_arn}',
                 "--set", f"settings.clusterName={cluster_name}",
                 "--set", f"settings.interruptionQueue={cluster_name}",
                 "--set", "controller.resources.requests.cpu=1",
                 "--set", "controller.resources.requests.memory=1Gi",
                 "--set", "controller.resources.limits.cpu= 1",
                 "--set", "controller.resources.limits.memory=1Gi",
                 "--set", "webhook.enabled=true",
                 "--set", "webhook.port=8443",
                  "--wait"]

            install_karpenter_with_command(install_command)
            click.echo("Upgrade Complete")
        else:
            click.echo(f"Karpenter version is already >= {karpenter_version}")

        if not installed_karpenter_crd_version or Version(installed_karpenter_crd_version) < Version(karpenter_version):
            click.echo(f"Upgrading Karpenter CRDs to version {karpenter_version}")
            install_karpenter_crd_command = ["helm", "upgrade", "--install", "karpenter-crd", "oci://public.ecr.aws/karpenter/karpenter-crd",
                  f"--version", karpenter_version, "--namespace", f"{karpenter_namespace}", "--create-namespace",
                  "--set", "webhook.enabled=true",
                  "--set", "webhook.serviceName='karpenter'",
                  "--set", "webhook.port=8443",
                  "--wait"]
            install_karpenter_with_command(install_karpenter_crd_command)
            click.echo("Upgrade Complete")
        else:
            click.echo(f"Karpenter CRDs version is already >= {karpenter_version}")

        karpenter_version_v1_0 = "1.0.9"
        file_path = "configurations/aws_configs/karpenter_controller_policy_v1.json"
        with open(resource_filename("tensorkube", file_path), "r") as f:
            policy_document = f.read()
        updated_policy_document = policy_document.replace("${AWS::Partition}", "aws")\
            .replace("${AWS::Region}", region)\
            .replace("${AWS::AccountId}", account_id)\
            .replace("${ClusterName}", cluster_name)\
            .replace("${KarpenterInterruptionQueue.Arn}", f"arn:aws:sqs:{region}:{account_id}:{cluster_name}")\
            .replace("${KarpenterNodeRole.Arn}", f"arn:aws:iam::{account_id}:role/KarpenterNodeRole-{cluster_name}")


        role_name = f"{cluster_name}-karpenter"
        policy_name = f"KarpenterControllerPolicy-{cluster_name}-v1"

        click.echo("Creating temporary IAM policy for karpenter")
        create_iam_policy(policy_name=policy_name, policy_document=json.loads(updated_policy_document))
        click.echo("Attatching temp IAM policy to role")
        attach_role_policy(account_no=account_id, policy_name=policy_name, role_name=role_name)
        click.echo("Temporary IAM polilcy created and attached to role")


        installed_karpenter_version = get_helm_release_version("karpenter", "kube-system")
        installed_karpenter_crd_version = get_helm_release_version("karpenter-crd", "kube-system")

        if Version(installed_karpenter_crd_version) < Version(karpenter_version_v1_0):
            click.echo(f"Upgrading karpenter CRDs to version {karpenter_version_v1_0}")
            install_karpenter_crd_command = ["helm", "upgrade", "--install", "karpenter-crd", "oci://public.ecr.aws/karpenter/karpenter-crd",
                 "--version", f"{karpenter_version_v1_0}", "--namespace", f"{karpenter_namespace}", "--create-namespace",
                 "--set", "webhook.enabled=true",
                 "--set", 'webhook.serviceName="karpenter"',
                 "--set", "webhook.port=8443"]
            install_karpenter_with_command(install_karpenter_crd_command)
            click.echo("Upgrade Complete")
        else:
            click.echo(f"Karpenter CRDs version is already >= {karpenter_version_v1_0}")

        if Version(installed_karpenter_version) < Version(karpenter_version_v1_0):
            click.echo(f"Upgrading karpenter to version {karpenter_version_v1_0}")
            install_karpenter_command = ["helm", "upgrade", "--install", "karpenter", "oci://public.ecr.aws/karpenter/karpenter",
                 "--version", f"{karpenter_version_v1_0}", "--namespace", f"{karpenter_namespace}", "--create-namespace",
                 "--set", f'serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn={karpenter_iam_role_arn}',
                 "--set", f'settings.clusterName={cluster_name}',
                 "--set", f"settings.interruptionQueue={cluster_name}",
                 "--set", "controller.resources.requests.cpu=1",
                 "--set", "controller.resources.requests.memory=1Gi",
                 "--set", "controller.resources.limits.cpu= 1",
                 "--set", "controller.resources.limits.memory=1Gi",
                 "--wait"]
            install_karpenter_with_command(install_karpenter_command)
            click.echo("Upgrade Complete")
        else:
            click.echo(f"Karpenter version is already >= {karpenter_version_v1_0}")

        updated_params = {
            "TemplatesVersion": "v0.0.6",
            "AWSAccessLambdaFunctionImageVersion": "v1.0.2",
            "CliVersion": "0.0.89",
            "EksAccessLambdaFunctionImageVersion": "v1.0.4"
        }
        click.echo("Updating CloudFormation templates")
        update_cfn_configure_stack(updated_parameters=updated_params, test=test)
        click.echo("CloudFormation templates updated")


        click.echo("Detatching and deleting temporary IAM policy")
        detach_role_policy(account_no=account_id, role_name=role_name, policy_name=policy_name)
        delete_policy(account_no=account_id, policy_name=policy_name)
        click.echo("Temporary IAM policy deleted")

        click.echo("Setting job pods to do-not-disrupt")
        add_do_not_disrupt_annotation_to_keda_pods()

        click.echo("Uprading karpenter Nodepools and Nodeclasses to v1")
        release_name = "karpenter-configuration"
        chart_version = "0.1.3"
        update_karpenter_config_command = ["helm", "upgrade", "--install", release_name,
                        f"oci://public.ecr.aws/{get_image_registry_id(test)}/tensorfuse/helm-charts/tk-karpenter-config",
                        "--version", chart_version,
                        "--set", f"clusterName={get_cluster_name()}"]
        availability_zones = get_availability_zones(region=region)
        for (i, az) in enumerate(availability_zones):
            update_karpenter_config_command.append("--set")
            update_karpenter_config_command.append(f"karpenterTopologyZoneValues[{i}]={az}")
        subprocess.run(update_karpenter_config_command,check=True)
        click.echo("Upgrade complete")

        installed_karpenter_version = get_helm_release_version("karpenter", "kube-system")
        installed_karpenter_crd_version = get_helm_release_version("karpenter-crd", "kube-system")
        installed_karpenter_config_version = get_helm_release_version("karpenter-configuration", "default")


        if Version(installed_karpenter_config_version) < Version("0.1.1"):
            raise Exception(f"Karpenter Nodeclasses and Nodepools not up to date")
        karpenter_version_v1_4 = "1.4.0"

        if Version(installed_karpenter_crd_version) < Version(karpenter_version_v1_4):
            click.echo(f"Upgrading karpenter CRDs to version {karpenter_version_v1_4}")
            install_karpenter_crd_command = ["helm", "upgrade", "--install", "karpenter-crd", "oci://public.ecr.aws/karpenter/karpenter-crd",
                 "--version", f"{karpenter_version_v1_4}", "--namespace", f"{karpenter_namespace}", "--create-namespace",
                 "--set", "webhook.enabled=true",
                 "--set", 'webhook.serviceName="karpenter"',
                 "--set", "webhook.port=8443"
                 "--wait"]
            install_karpenter_with_command(install_karpenter_crd_command)
            click.echo("Upgrade complete")
        else:
            click.echo(f"Karpenter CRDs version is already >= {karpenter_version_v1_4}")

        if Version(installed_karpenter_version) < Version(karpenter_version_v1_4):
            click.echo(f"Upgrading karpenter to version {karpenter_version_v1_4}")
            install_karpenter_command = ["helm", "upgrade", "--install", "karpenter", "oci://public.ecr.aws/karpenter/karpenter",
                 "--version", f"{karpenter_version_v1_4}", "--namespace", f"{karpenter_namespace}", "--create-namespace",
                 "--set", f'serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn={karpenter_iam_role_arn}',
                 "--set", f'settings.clusterName={cluster_name}',
                 "--set", f"settings.interruptionQueue={cluster_name}",
                 "--set", "controller.resources.requests.cpu=1",
                 "--set", "controller.resources.requests.memory=1Gi",
                 "--set", "controller.resources.limits.cpu= 1",
                 "--set", "controller.resources.limits.memory=1Gi",
                 "--set", "settings.featureGates.nodeRepair=true",
                 "--wait"]
            install_karpenter_with_command(install_karpenter_command)
            click.echo("Upgrade complete")
        else:
            click.echo(f"Karpenter version is already >= {karpenter_version_v1_4}")

        click.echo("Karpenter upgrade complete")

    except Exception as e:
        click.echo(click.style(f"Failed to upgrade karpenter: {e}", bold=True, fg="red"))
        raise e