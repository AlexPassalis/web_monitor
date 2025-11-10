import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from functools import lru_cache
import logging
from config import S3_ENDPOINT_URL, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET_NAME, S3_REGION

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_s3_client() -> BaseClient:
    """Create and return a cached S3 client configured for MinIO or AWS S3."""

    client_config = {
        'aws_access_key_id': S3_ACCESS_KEY,
        'aws_secret_access_key': S3_SECRET_KEY,
        'region_name': S3_REGION,
    }

    if S3_ENDPOINT_URL:
        client_config['endpoint_url'] = S3_ENDPOINT_URL

    return boto3.client('s3', **client_config)


def ensure_bucket_exists() -> None:
    """Ensure the S3 bucket exists, create if it doesn't."""

    s3_client = get_s3_client()

    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            try:
                s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
                logger.info(f'Created bucket: {S3_BUCKET_NAME}')
            except ClientError as create_error:
                logger.error(f'Failed to create bucket: {create_error}')
                raise
        else:
            logger.error(f'Error checking bucket: {e}')
            raise


def upload_file(file_bytes: bytes, file_name: str, content_type: str = 'image/png') -> str:
    """Upload a file to S3 and return the object key."""

    s3_client = get_s3_client()

    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=file_bytes,
            ContentType=content_type,
        )
        logger.info(f'Uploaded file to S3: {file_name}')
        return file_name
    except ClientError as e:
        logger.error(f'Failed to upload file {file_name}: {e}')
        raise
