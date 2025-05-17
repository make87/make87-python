import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Any

from make87 import APPLICATION_ID, DEPLOYED_APPLICATION_ID, DEPLOYED_SYSTEM_ID

if TYPE_CHECKING:
    from s3path import S3Path

# Constants for environment variable names
ENV_STORAGE_ENDPOINT_URL = "MAKE87_STORAGE_ENDPOINT_URL"
ENV_STORAGE_ACCESS_KEY = "MAKE87_STORAGE_ACCESS_KEY"
ENV_STORAGE_SECRET_KEY = "MAKE87_STORAGE_SECRET_KEY"
ENV_STORAGE_PATH = "MAKE87_STORAGE_PATH"

_MAKE87_RESOURCE: Optional[Any] = None


def _setup_make87_resource() -> None:
    """Initializes the global S3 resource using environment variables."""
    global _MAKE87_RESOURCE
    import boto3

    endpoint_url = os.environ[ENV_STORAGE_ENDPOINT_URL]
    access_key = os.environ.get(ENV_STORAGE_ACCESS_KEY)
    secret_key = os.environ.get(ENV_STORAGE_SECRET_KEY)

    _MAKE87_RESOURCE = boto3.resource(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def get_make87_resource() -> Any:
    """Returns the initialized S3 resource, initializing it if necessary."""
    global _MAKE87_RESOURCE
    if _MAKE87_RESOURCE is None:
        try:
            _setup_make87_resource()
        except ImportError:
            raise ImportError("Please install make87[storage] to use the cloud storage functionality.")
    return _MAKE87_RESOURCE


def get_system_storage_path() -> Path:
    """Returns the path to the system storage directory."""
    path = Path("/tmp/make87") / DEPLOYED_SYSTEM_ID
    if ENV_STORAGE_PATH in os.environ:
        resource = get_make87_resource()
        from s3path import S3Path, register_configuration_parameter

        storage_url = os.environ[ENV_STORAGE_PATH]
        path = S3Path(storage_url)
        register_configuration_parameter(path, resource=resource)
        # workaround for issue in `s3path` where testing for the bucket existence without passing the configured credentials.
        # https://github.com/liormizr/s3path/blob/8780ddd42a9c98db2c2e9dd2dfaedf88286e0454/s3path/old_versions.py#L1145
        bucket_path = S3Path(path._flavour.sep, path.bucket)
        register_configuration_parameter(bucket_path, resource=resource)
    else:
        path.mkdir(parents=True, exist_ok=True)
    return path


def get_organization_storage_path() -> Path:
    """Returns the path to the organization storage directory."""
    return get_system_storage_path().parent


def get_application_storage_path() -> Path:
    """Returns the path to the application storage directory."""
    return get_system_storage_path() / APPLICATION_ID


def get_deployed_application_storage_path() -> Path:
    """Returns the path to the deployed application storage directory."""
    return get_system_storage_path() / DEPLOYED_APPLICATION_ID


def _update_s3_object_content_type(file_path: "S3Path", new_content_type: str) -> None:
    """Updates the content type of an S3 object."""
    resource = get_make87_resource()
    bucket_name, object_key = file_path.bucket, file_path.key
    s3_object = resource.Object(bucket_name, object_key)
    current_metadata = s3_object.metadata
    s3_object.copy_from(
        CopySource={"Bucket": bucket_name, "Key": object_key},
        Metadata=current_metadata,
        ContentType=new_content_type,
        MetadataDirective="REPLACE",
    )


def generate_public_url(path: Path, expires_in: int = 604800, update_content_type: Optional[str] = None) -> str:
    """Returns a public URL for a given path.

    :param path: The S3Path object representing the file. Raises TypeError if not an S3Path.
    :param expires_in: The number of seconds until the URL expires. Defaults to 604800 (7 days).
    :param update_content_type: The content type to set for the file. If None, the content type will not be updated.

    :raises ValueError: If the path is not a file or if the URL cannot be generated.
    :raises ImportError: If the required dependencies are not installed.

    :return: The public URL for the file.
    """
    from s3path import S3Path

    if not isinstance(path, S3Path):
        raise TypeError("Path must be an S3Path object.")

    if not path.is_file():
        raise ValueError("Path must be a file.")

    resource = get_make87_resource()

    if update_content_type is not None:
        try:
            _update_s3_object_content_type(path, update_content_type)
        except Exception:
            logging.warning("Failed to update content type. Continuing without updating.")

    try:
        s3_client = resource.meta.client
        return s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": path.bucket, "Key": path.key}, ExpiresIn=expires_in
        )
    except Exception as e:
        logging.error("Could not generate public URL: %s", e)
        raise ValueError(
            f"Could not generate public URL. Make sure you have the correct permissions. Original exception: {e}"
        )
