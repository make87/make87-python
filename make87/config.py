import os

from make87.models.application_env_config import ApplicationEnvConfig

CONFIG_ENV_VAR = "MAKE87_CONFIG"


def _load_config() -> ApplicationEnvConfig:
    raw = os.environ.get(CONFIG_ENV_VAR)
    if not raw:
        raise RuntimeError(f"Required env var {CONFIG_ENV_VAR} missing!")
    return ApplicationEnvConfig.model_validate_json(raw)


def get_config() -> ApplicationEnvConfig:
    global _config
    if _config is None:
        _config = _load_config()
    return _config


_config = get_config()

IS_IN_RELEASE_MODE = _config.is_in_release_mode
DEPLOYED_APPLICATION_ID = _config.deployed_application_id
DEPLOYED_APPLICATION_NAME = _config.deployed_application_name
DEPLOYED_SYSTEM_ID = _config.system_id
APPLICATION_ID = _config.application_id
APPLICATION_NAME = _config.application_name
STORAGE_URL = _config.storage_url
STORAGE_ENDPOINT_URL = _config.storage_endpoint_url
STORAGE_ACCESS_KEY = _config.storage_access_key
STORAGE_SECRET_KEY = _config.storage_secret_key
