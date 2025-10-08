from tensorkube.constants import get_cluster_name
from tensorkube.services.aws_service import get_dynamodb_resource

def get_dynamodb_table_name():
    return f"{get_cluster_name()}-job-status"

def get_dynamodb_access_policy_name():
    return f"{get_cluster_name()}-dynamo-access-policy"

def get_user_dynamodb_access_policy_name(user: str):
    return f"{get_cluster_name()}-{user}-dynamodb-access-policy"


def get_all_job_statuses(limit: int = 3):
    dynamodb = get_dynamodb_resource()
    table_name = get_dynamodb_table_name()
    table = dynamodb.Table(table_name)

    all_jobs = {}
    last_evaluated_key = None

    try:
        while True:
            if last_evaluated_key:
                response = table.scan(ExclusiveStartKey=last_evaluated_key)
            else:
                response = table.scan()

            # Extract job_name, job_id, and status for each item
            for item in response.get('Items', []):
                job_name = item.get('job_name')
                if job_name not in all_jobs:
                    all_jobs[job_name] = []

                all_jobs[job_name].append({
                    'job_name': job_name,
                    'job_id': item.get('job_id'),
                    'status': item.get('status'),
                })

            last_evaluated_key = response.get('LastEvaluatedKey')

            if not last_evaluated_key:
                break

        latest_jobs = {}
        for job_name, jobs in all_jobs.items():
            latest_jobs[job_name] = sorted(jobs, key=lambda x: x['job_id'], reverse=True)[:limit]
            if len(all_jobs[job_name]) > limit:
                latest_jobs[job_name].append({
                    'job_name': job_name,
                    'job_id': '...',
                    'status': '...',
                })

        return latest_jobs

    except Exception as e:
        print(f"Error fetching job statuses: {e}")
        return []


def get_job_statuses(job_name: str):
    dynamodb = get_dynamodb_resource()
    table_name = get_dynamodb_table_name()
    table = dynamodb.Table(table_name)

    response = table.query(
        KeyConditionExpression='job_name = :job_name',
        ExpressionAttributeValues={
            ':job_name': job_name,
        }
    )

    return response.get('Items', [])
