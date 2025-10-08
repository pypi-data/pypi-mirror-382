from enum import Enum
from typing import Optional
import os
REGION = 'us-east-1'
NAMESPACE = 'kube-system'
DEFAULT_NAMESPACE = 'default'
SERVICE_ACCOUNT_NAME = 's3-csi-driver-sa'
ADDON_NAME = "aws-mountpoint-s3-csi-driver"
KNATIVE_SERVING_NAMESPACE = 'knative-serving'
CONFIG_FEATURES = 'config-features'
BUILD_TOOL = 'buildkit'
DATASET_BUCKET_TYPE = 'datasets'

DEFAULT_CAPABILITIES = ['CAPABILITY_NAMED_IAM']
TENSORKUBE_MACRO_NAME = "TensorkubePyPlate"

KEDA_NAMESPACE = 'keda'
KEDA_SERVICE_ACCOUNT_NAME = 'keda-operator'
KEDA_IAM_ROLE_NAME = 'keda-iam-role'

CREATED_BY_TAG = 'CreatedBy'
CLUSTER_NAME_TAG = 'ClusterName'
TENSORFUSE_STRING = 'tensorfuse'


TENSORFUSE_NAMESPACES = ['amazon-cloudwatch', 'kube-system', 'istio-system', 'knative-serving', 'kube-node-lease',
                         'kube-public', 'kube-system', 'nydus-snapshotter' ]

LOCKED_AWS_CLI_VERSION = "2.22.8"
LOCKED_EKSCTL_VERSION = "0.194.0"
LOCKED_KUBECTL_VERSION = "1.31.3"
LOCKED_HELM_VERSION = "3.16.3"
LOCKED_ISTIO_VERSION = "1.24.0"


NODEPOOL = 'nodepool'
EC2NODECLASS = 'ec2nodeclass'
GPU_NODEPOOL_VERSION = 'gpu-v1'

AWS_ACCESS_LAMBDA_FUNCTION_IMAGE_VERSION = 'v1.0.2'
EKS_ACCESS_LAMBDA_FUNCTION_IMAGE_VERSION = 'v1.0.5'
MONITORING_LAMBDA_FUNCTION_IMAGE_VERSION = 'v1.0.0'

GPU_DEPLOYMENT_MIN_CPU = 2000
GPU_DEPLOYMENT_MIN_MEMORY = 8000

REPEATED_NOTIFICATION_PERIOD_SECONDS = "900"
ALARM_EVALUATION_PERIODS = "45"

def get_cluster_name():
    return "tensorkube"

def get_cfn_base_stack_name():
    return f"{get_cluster_name()}-base-stack"

def get_template_bucket_name(test: bool):
    if test:
        return "tensorkube-cfn-staging-70w939rx1f"
    return "tensorkube-cfn-templates-bwgkphrtz5pdbv"


def get_image_registry_id(test):
    if test:
        return "s6z9f6e5"
    return "q0m5o9l2"


def get_templates_version():
    return "v0.0.9"


def get_mount_policy_name(cluster_name: str, env: Optional[str] = None) -> str:
    if env:
        return f'{cluster_name}-mountpoint-policy-env-{env}'
    return f'{cluster_name}-mountpoint-policy'


def get_mount_driver_role_name(cluster_name):
    return f'{cluster_name}-mountpoint-driver-role'


class Events(Enum):
    LOGGED_IN = 'logged-in'

    COMMAND_RUN = 'command-run'
    CONFIGURED_REGION = 'configured-region'
    CONFIGURE_START = 'configure-start'
    CONFIGURE_END = 'configure-end'
    CONFIGURE_ERROR = 'configure-error'

    TEARDOWN_START = 'teardown-start'
    TEARDOWN_END = 'teardown-end'

    DEPLOY_START = 'deploy-start'
    DEPLOY_END = 'deploy-end'
    DEPLOY_ERROR = 'deploy-error'

    DEVCONTAINER = 'devcontainer'
    DEVCONTAINER_START = 'devcontainer-start'
    DEVCONTAINER_STOP = 'devcontainer-stop'
    DEVCONTAINER_LIST = 'devcontainer-list'
    DEVCONTAINER_DELETE = 'devcontainer-delete'
    DEVCONTAINER_ERROR = 'devcontainer-error'

    JOB_DEPLOY_START = 'job-deploy-start'
    JOB_DEPLOY_END = 'job-deploy-end'
    JOB_DEPLOY_ERROR = 'job-deploy-error'

    TEST_START = 'test-start'
    TEST_END = 'test-end'


class PodStatus(Enum):
    PENDING = 'Pending'
    RUNNING = 'Running'
    SUCCEEDED = 'Succeeded'
    FAILED = 'Failed'
    UNKNOWN = 'Unknown'


class CliColors(Enum):
    ERROR = 'red'
    SUCCESS = 'green'
    WARNING = 'yellow'
    INFO = 'blue'
    DEFAULT = 'white'

class TeardownType(Enum):
    LEGACY = 'legacy'
    CFN = 'cfn'
    UNKNOWN = 'unknown'

class ProbeType(Enum):
    LIVENESS = 'liveness'
    READINESS = 'readiness'
    STARTUP = 'startup'

def get_efs_service_account_name() -> str:
    return f'{get_cluster_name()}-efs-csi-controller-sa'


def get_efs_role_name() -> str:
    return f'AmazonEKS_EFS_CSI_DriverRole_{get_cluster_name()}'


def get_logging_service_account_name() -> str:
    return f'cloudwatch-agent'


def get_cloudwatch_role_name() -> str:
    return f'cloudwatch-agent-role_{get_cluster_name()}'


def get_cloudwatch_namespace() -> str:
    return 'amazon-cloudwatch'


def get_job_sidecar_iam_role_name() -> str:
    return f'{get_cluster_name()}-job-sidecar-iam-role'


def get_efs_security_group_name(env: Optional[str] = None) -> str:
    if env:
        return f'eks-efs-sg-{get_cluster_name()}-env-{env}'
    return f'eks-efs-sg-{get_cluster_name()}'

def get_base_login_url():
    return os.getenv("TENSORKUBE_BASE_LOGIN_URL", "https://backend.tensorfuse.io")

def get_tag_for_repeated_alarm_notification() -> str:
    return "TensorkubeRepeatedAlarm:true"

def get_base_frontend_url():
    return "https://app.tensorfuse.io"