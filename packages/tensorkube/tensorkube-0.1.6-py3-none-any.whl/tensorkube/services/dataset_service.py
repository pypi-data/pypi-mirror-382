import os
from typing import Optional, List
import click
from tqdm import tqdm

from tensorkube.constants import DATASET_BUCKET_TYPE
from tensorkube.services.aws_service import get_s3_client
from tensorkube.services.s3_service import check_if_a_bucket_type_exists, create_s3_bucket, list_bucket_contents, \
    S3ObjectInfo, upload_file, delete_file_from_s3, get_bucket_name


def ensure_dataset_bucket_exists() -> str:
    if check_if_a_bucket_type_exists(type=DATASET_BUCKET_TYPE):
        return get_bucket_name(type=DATASET_BUCKET_TYPE)
    ## doesnt exist create new bucket
    bucket_name = get_bucket_name(type=DATASET_BUCKET_TYPE)
    ## create bucket
    create_s3_bucket(bucket_name)
    return bucket_name


def list_datasets()->Optional[List[S3ObjectInfo]]:
    if not check_if_a_bucket_type_exists(type=DATASET_BUCKET_TYPE):
        click.echo(click.style("No datasets have ever been created.", fg='yellow'))
        return None

    datasets = list_bucket_contents(bucket_name=get_bucket_name(type=DATASET_BUCKET_TYPE))
    return datasets

def check_if_dataset_exists(dataset_id: str) -> bool:
    existing_datasets = list_datasets()
    # The name/path of the file in S3
    object_name = f"{dataset_id}.jsonl"
    if existing_datasets:
        if any(d.key == object_name for d in existing_datasets):
            return True
    return False


def upload_tensorkube_dataset(dataset_id: str, file_path: str) -> bool:
    """
    Uploads a dataset file to S3 with progress bar

    Args:
        dataset_id: Unique identifier for the dataset
        file_path: Path to the local JSONL file

    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        # Ensure bucket exists
        bucket_name = ensure_dataset_bucket_exists()

        # The name/path of the file in S3
        object_name = f"{dataset_id}.jsonl"

        if check_if_dataset_exists(dataset_id):
            click.echo(click.style(f"Dataset with ID '{dataset_id}' already exists.", fg='red'))
            return False
        # Create s3 client
        s3_client = get_s3_client()
        # Get file size for progress bar
        file_size = os.path.getsize(file_path)

        # Create progress bar
        progress_bar = tqdm(
            total=file_size,
            unit='B',
            unit_scale=True,
            desc=f"Uploading {dataset_id}",
            leave=True
        )

        # Upload file
        upload_file(
            file_name=file_path,
            bucket_name=bucket_name,
            s3_key=object_name,  # This is the name/path in S3
            s3_client=s3_client,
            progress_bar=progress_bar
        )

        click.echo(click.style(f"Successfully uploaded dataset '{dataset_id}'", fg='green'))
        return True

    except Exception as e:
        print(f"Error uploading dataset: {e}")
        click.echo(click.style(f"Failed to upload dataset: {str(e)}", fg='red'))
        return False


def delete_tensorkube_dataset(dataset_id: str) -> bool:
    """
    Deletes a dataset from S3 using its ID

    Args:
        dataset_id: ID of the dataset to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        # Check if datasets bucket exists
        if not check_if_a_bucket_type_exists(type=DATASET_BUCKET_TYPE):
            click.echo(click.style("No datasets bucket exists.", fg='yellow'))
            return False

        bucket_name = get_bucket_name(type=DATASET_BUCKET_TYPE)
        object_name = f"{dataset_id}.jsonl"

        if not check_if_dataset_exists(dataset_id):
            click.echo(click.style(f"Dataset with ID '{dataset_id}' does not exists.", fg='red'))
            return False

        # Delete the dataset
        if delete_file_from_s3(bucket_name, object_name):
            click.echo(click.style(f"Successfully deleted dataset '{dataset_id}'", fg='green'))
            return True
        else:
            click.echo(click.style(f"Failed to delete dataset '{dataset_id}'", fg='red'))
            return False

    except Exception as e:
        print(f"Error deleting dataset: {e}")
        click.echo(click.style(f"Failed to delete dataset: {str(e)}", fg='red'))
        return False

