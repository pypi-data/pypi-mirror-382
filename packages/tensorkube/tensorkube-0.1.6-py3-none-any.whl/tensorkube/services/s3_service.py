import concurrent.futures
import logging
import mimetypes
import os
import threading
from typing import Optional, NamedTuple, List
import uuid
import boto3
import click
import pathspec
from boto3.s3.transfer import TransferConfig
from tqdm import tqdm

from tensorkube.constants import REGION, get_cluster_name, DEFAULT_NAMESPACE
from tensorkube.services.utils import human_readable_date, human_readable_size
from tensorkube.services.aws_service import get_s3_client, get_s3_resource, get_session_region

class S3ObjectInfo(NamedTuple):
    key: str
    last_modified: str  # Human readable time
    size: str          # Human readable size
    raw_size: int      # Original size in bytes
    is_directory: bool
    content_type: str
    etag: str
    owner: str
    file_extension: str = ''


    @classmethod
    def from_response(cls, obj: dict, head_object: dict = None, is_directory: bool = False):
        """
        Creates an S3ObjectInfo instance from S3 response objects with human-readable formats
        """
        if is_directory:
            return cls(
                key=obj['Prefix'],
                last_modified="Directory",
                size="--",
                raw_size=0,
                is_directory=True,
                content_type="directory",
                etag="--",
                owner="--",
                file_extension=""
            )

        # Get file extension and mime type
        _, file_extension = os.path.splitext(obj['Key'])
        content_type = head_object.get('ContentType', 'application/octet-stream') if head_object else \
                      mimetypes.guess_type(obj['Key'])[0] or 'application/octet-stream'
        return cls(
            key=obj['Key'],
            last_modified=human_readable_date(obj['LastModified']),
            size=human_readable_size(obj['Size']),
            raw_size=obj['Size'],
            is_directory=False,
            content_type=content_type,
            etag=obj.get('ETag', '').strip('"'),
            owner=obj.get('Owner', {}).get('DisplayName', '--'),
            file_extension=file_extension.lower()
        )


# NOTE: bucket name must be universally unique
# NOTE: bucket name should not be guessable
def create_s3_bucket(bucket_name):
    try:
        s3_client = get_s3_client()
        region = get_session_region()
        if region is None or region == REGION:
            s3_client.create_bucket(Bucket=bucket_name)
            click.echo(f"Created bucket {bucket_name} in region {region}")
        else:
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location) #TODO: check if this works, can us-west-1 s3 client create a bucket in us-east-1?
    except Exception as e:
        click.echo(f"Error creating bucket {bucket_name} in region {region}: {e}")
        return False

    return True


def list_s3_buckets(region: Optional[str] = None):
    try:
        s3 = get_s3_client(region=region)
        response = s3.list_buckets()
        return response['Buckets']
    except Exception as e:
        click.echo(f"Error listing buckets: {e}")
        return []


# Set up logging for debugging
logging.basicConfig(level=logging.INFO)


def upload_file(file_name, bucket_name, s3_key, s3_client, progress_bar):
    def upload_progress(chunk):
        # logging.debug(f"Uploading chunk of {chunk} bytes for {file_name}")
        progress_bar.update(chunk)

    config = boto3.s3.transfer.TransferConfig(use_threads=False)
    try:
        s3_client.upload_file(file_name, bucket_name, s3_key, Callback=upload_progress,
                              Config=config)  # logging.info(f"Successfully uploaded {file_name} to {bucket_name}/{s3_key}")
    except Exception as e:
        logging.error(f"Error uploading {file_name}: {e}")
    finally:
        progress_bar.close()


def load_dockerignore(file_path):
    with open(file_path, 'r') as f:
        patterns = f.read().splitlines()
    return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, patterns)


def upload_files_in_parallel(bucket_name, folder_path, s3_path=''):
    s3_client = get_s3_client()
    files_to_upload = []

    dockerignore_filepath = os.path.join(folder_path, '.dockerignore')
    if os.path.exists(dockerignore_filepath):
        spec = load_dockerignore(dockerignore_filepath)
    else:
        spec = pathspec.PathSpec([])

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            local_file = os.path.join(root, file)
            if spec.match_file(local_file):
                continue
            files_to_upload.append(local_file)

    # logging.debug(f"Files to upload: {files_to_upload}")
    progress_bars = {}
    locks = {file: threading.Lock() for file in files_to_upload}

    def upload_with_progress(file_name):
        file_size = os.path.getsize(file_name)
        s3_key = s3_path + os.path.relpath(file_name, folder_path).replace(os.sep, '/')
        # logging.debug(f"Uploading {file_name} to {s3_key} in bucket {bucket_name}")
        with locks[file_name]:
            progress_bars[file_name] = tqdm(total=file_size, unit='B', unit_scale=True, desc=s3_key, leave=True)
        upload_file(file_name, bucket_name, s3_key, s3_client, progress_bars[file_name])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(upload_with_progress, file): file for file in files_to_upload}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in future for {futures[future]}: {e}")

    for progress_bar in progress_bars.values():
        progress_bar.close()


def empty_s3_bucket(bucket_name):
    try:
        s3 = get_s3_resource()
        bucket = s3.Bucket(bucket_name)
        bucket.objects.all().delete()
    except Exception as e:
        click.echo(f"Error emptying bucket {bucket_name}: {e}")
        return False

    return True


def empty_s3_folder(bucket_name, folder_name):
    try:
        s3 = get_s3_resource()
        bucket = s3.Bucket(bucket_name)
        bucket.objects.filter(Prefix=folder_name).delete()
    except Exception as e:
        click.echo(f"Error emptying folder {folder_name} in bucket {bucket_name}: {e}")
        return False

    return True


def delete_s3_bucket(bucket_name):
    try:
        click.echo(f"Emptying bucket {bucket_name}...")
        empty_s3_bucket(bucket_name)
        click.echo(f"Deleting bucket {bucket_name}...")
        s3 = get_s3_client()
        s3.delete_bucket(Bucket=bucket_name)
        click.echo(f"Deleted bucket {bucket_name}")
    except Exception as e:
        click.echo(f"Error deleting bucket {bucket_name}: {e}")
        return False

    return True

def check_if_a_bucket_type_exists(env_name: Optional[str] = None, type: str = "build"):
    buckets = list_s3_buckets()
    if env_name and env_name != DEFAULT_NAMESPACE:
        prefix = f'{get_cluster_name()}-{env_name}-{type}-bucket-'
    else:
        prefix = f'{get_cluster_name()}-{type}-bucket-'
    # checks if such a bucket already exists
    for bucket in buckets:
        if bucket['Name'].startswith(prefix):
            return True
    return False


def list_bucket_contents(bucket_name: str, prefix: str = '') -> List[S3ObjectInfo]:
    """
    Lists all objects in an S3 bucket with detailed, human-readable information.

    Args:
        bucket_name: Name of the S3 bucket
        prefix: Optional prefix to filter objects (like a directory path)

    Returns:
        List of S3ObjectInfo containing human-readable file/directory information
    """
    try:
        s3_client = get_s3_client()
        paginator = s3_client.get_paginator('list_objects_v2')
        objects = []

        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter='/'):
            # Handle directories (common prefixes)
            if 'CommonPrefixes' in page:
                for prefix_obj in page['CommonPrefixes']:
                    objects.append(S3ObjectInfo.from_response(prefix_obj, is_directory=True))

            # Handle files
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'] == prefix:
                        continue

                    try:
                        head_object = s3_client.head_object(Bucket=bucket_name, Key=obj['Key'])
                    except Exception as _:
                        head_object = None

                    objects.append(S3ObjectInfo.from_response(obj, head_object))

        return sorted(objects, key=lambda x: (x.is_directory, x.key.lower()))

    except Exception as e:
        logging.error(f"Error listing contents of bucket {bucket_name}: {e}")
        return []


def delete_file_from_s3(bucket_name: str, object_name: str) -> bool:
    """
    Deletes a single file from an S3 bucket

    Args:
        bucket_name: Name of the S3 bucket
        object_name: Name of the file to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        return True
    except Exception as e:
        logging.error(f"Error deleting file {object_name} from bucket {bucket_name}: {e}")
        return False


# TODO!: make function generic to get any config value
def get_bucket_name(env_name: Optional[str] = None, type: str = "build", cluster_region: Optional[str] = None):
    buckets = list_s3_buckets(region=cluster_region)
    if env_name and env_name != DEFAULT_NAMESPACE:
        prefix = f'{get_cluster_name()}-{env_name}-{type}-bucket-'
    else:
        prefix = f'{get_cluster_name()}-{type}-bucket-'
    # checks if such a bucket already exists
    for bucket in buckets:
        if bucket['Name'].startswith(prefix):
            return bucket['Name']
    else:
        bucket_name = f"{prefix}{str(uuid.uuid4())[:18]}"
        if len(bucket_name) > 63:
            raise ValueError("Environment name is too long. Please use a shorter name.")
        return bucket_name

def get_existing_bucket_name(env_name: Optional[str] = None, type: str = "build"):
    buckets = list_s3_buckets()
    if env_name and env_name != DEFAULT_NAMESPACE:
        prefix = f'{get_cluster_name()}-{env_name}-{type}-bucket-'
    else:
        prefix = f'{get_cluster_name()}-{type}-bucket-'
    # checks if such a bucket already exists
    for bucket in buckets:
        if bucket['Name'].startswith(prefix):
            return bucket['Name']

    return None