import logging
from typing import Optional, Any

try:
    from s3path import S3Path, register_configuration_parameter
    import boto3

    from make87.config import load_config_from_env
    from make87.models import ApplicationConfig


    class BlobStorage:
        def __init__(self, make87_config: Optional[ApplicationConfig] = None):
            if make87_config is None:
                make87_config = load_config_from_env()
            self._config = make87_config
            self._resource: Optional[Any] = None

        @property
        def resource(self):
            if self._resource is None:
                self._resource = boto3.resource(
                    "s3",
                    endpoint_url=self._config.storage.endpoint_url,
                    aws_access_key_id=self._config.storage.access_key,
                    aws_secret_access_key=self._config.storage.secret_key,
                )
            return self._resource

        def get_system_path(self) -> S3Path:
            path = S3Path(self._config.storage.url)
            register_configuration_parameter(path, resource=self.resource)
            # Also register the bucket root, workaround for s3path bug
            bucket_path = S3Path(path._flavour.sep, path.bucket)
            register_configuration_parameter(bucket_path, resource=self.resource)
            return path

        def get_application_path(self) -> S3Path:
            return self.get_system_path() / self._config.application_info.application_id

        def get_deployed_application_path(self) -> S3Path:
            return self.get_system_path() / self._config.application_info.deployed_application_id

        def _update_content_type(self, file_path: S3Path, new_content_type: str):
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
        raise ImportError(
            "S3Path support is not installed. "
            "Install with: pip install make87[storage]"
        )

    BlobStorage = _raise_s3path_import_error