from typing import Optional

from tensorkube.services.aws_service import get_sqs_client
from tensorkube.constants import get_cluster_name
def get_sqs_access_policy_name():
    return f"{get_cluster_name()}-sqs-access-policy"


def create_sqs_queue(queue_name: str, cluster_region: Optional[str] = None) -> str:
    sqs = get_sqs_client(region=cluster_region)
    response = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            'DelaySeconds': '0',
            'MessageRetentionPeriod': '86400',  # Retain messages for 1 day
            'VisibilityTimeout': '43200' # Make messages invisible for 12 hrs
        }
    )
    queue_url = response['QueueUrl']
    return queue_url


def delete_sqs_queue(queue_name: str) -> None:
    sqs = get_sqs_client()
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    sqs.delete_queue(QueueUrl=queue_url)
    print(f"Queue {queue_name} deleted successfully.")

def queue_message(queue_url: str, message_body: str, cluster_region: Optional[str] = None) -> None:
    sqs = get_sqs_client(region=cluster_region)
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )
    print(f"Message sent to queue")
