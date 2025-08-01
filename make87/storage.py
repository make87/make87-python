"""Blob storage operations and utilities for Make87 applications.

This module provides the BlobStorage class for interacting with S3-compatible
storage systems. It supports file operations, public URL generation, and
path management for both system and application-specific storage.
"""

import logging
from typing import Optional, Any

try:
    from s3path import S3Path, register_configuration_parameter
    import boto3

    from make87.config import load_config_from_env
    from make87.models import ApplicationConfig

    class BlobStorage:
        """S3-compatible blob storage client for Make87 applications.

        This class provides a high-level interface for interacting with S3-compatible
        storage systems. It handles authentication, path management, and file operations
        for both system-level and application-specific storage.

        Attributes:
            _config: The Make87 application configuration
            _resource: Cached boto3 S3 resource instance
        """

        def __init__(self, make87_config: Optional[ApplicationConfig] = None):
            """Initialize the BlobStorage client.

            Args:
                make87_config: Optional ApplicationConfig instance. If not provided,
                    configuration will be loaded from the environment.
            """
            if make87_config is None:
                make87_config = load_config_from_env()
            self._config = make87_config
            self._resource: Optional[Any] = None

        @property
        def resource(self):
            """Get or create the boto3 S3 resource instance.

            Returns:
                Configured boto3 S3 resource for the storage endpoint.
            """
            if self._resource is None:
                self._resource = boto3.resource(
                    "s3",
                    endpoint_url=self._config.storage.endpoint_url,
                    aws_access_key_id=self._config.storage.access_key,
                    aws_secret_access_key=self._config.storage.secret_key,
                )
            return self._resource

        def get_system_path(self) -> S3Path:
            """Get the S3Path for the system-level storage root.

            Returns:
                S3Path instance pointing to the system storage root.

            Note:
                This method registers the S3 resource configuration with s3path
                and includes a workaround for an s3path bug by also registering
                the bucket root.
            """
            path = S3Path(self._config.storage.url)
            register_configuration_parameter(path, resource=self.resource)
            # Also register the bucket root, workaround for s3path bug
            bucket_path = S3Path(path._flavour.sep, path.bucket)
            register_configuration_parameter(bucket_path, resource=self.resource)
            return path

        def get_application_path(self) -> S3Path:
            """Get the S3Path for application-specific storage.

            Returns:
                S3Path instance pointing to the current application's storage directory.
            """
            return self.get_system_path() / self._config.application_info.application_id

        def get_deployed_application_path(self) -> S3Path:
            """Get the S3Path for deployed application storage.

            Returns:
                S3Path instance pointing to the deployed application's storage directory.
            """
            return self.get_system_path() / self._config.application_info.deployed_application_id

        def _update_content_type(self, file_path: S3Path, new_content_type: str):
            """Update the content type of an S3 object.

            Args:
                file_path: S3Path pointing to the file to update
                new_content_type: The new content type to set

            Note:
                This is a private method that performs an in-place copy operation
                to update the object's metadata.
            """
            bucket_name, object_key = file_path.bucket, file_path.key
            s3_object = self.resource.Object(bucket_name, object_key)
            current_metadata = s3_object.metadata
            s3_object.copy_from(
                CopySource={"Bucket": bucket_name, "Key": object_key},
                Metadata=current_metadata,
                ContentType=new_content_type,
                MetadataDirective="REPLACE",
            )

        def generate_public_url(
            self, path: S3Path, expires_in: int = 604800, update_content_type: Optional[str] = None
        ) -> str:
            """Generate a public presigned URL for accessing a file.

            Args:
                path: S3Path pointing to the file to generate a URL for
                expires_in: URL expiration time in seconds. Defaults to 604800 (1 week).
                update_content_type: Optional content type to set before generating the URL

            Returns:
                Presigned URL string for accessing the file

            Raises:
                ValueError: If the path is not a file or URL generation fails

            Example:

                >>> storage = BlobStorage()
                >>> file_path = storage.get_application_path() / "data.json"
                >>> url = storage.generate_public_url(file_path, expires_in=3600)
                >>> print(f"File URL: {url}")
            """
            if not path.is_file():
                raise ValueError("Path must be a file.")
            if update_content_type:
                try:
                    self._update_content_type(path, update_content_type)
                except Exception:
                    logging.warning("Failed to update content type. Continuing without updating.")
            try:
                s3_client = self.resource.meta.client
                return s3_client.generate_presigned_url(
                    "get_object", Params={"Bucket": path.bucket, "Key": path.key}, ExpiresIn=expires_in
                )
            except Exception as e:
                logging.error("Could not generate public URL: %s", e)
                raise ValueError(
                    f"Could not generate public URL. Make sure you have the correct permissions. Original exception: {e}"
                )

except ImportError:

    def _raise_s3path_import_error(*args, **kwargs):
        """Raise ImportError when S3Path dependencies are not installed.

        Raises:
            ImportError: Always raised with installation instructions
        """
        raise ImportError("S3Path support is not installed. " "Install with: pip install make87[storage]")

    BlobStorage = _raise_s3path_import_error
