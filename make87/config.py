import os
from typing import Union, Dict

from make87.models.application_env_config import ApplicationEnvConfig

CONFIG_ENV_VAR = "MAKE87_CONFIG"


def load_config_from_env(var: str = CONFIG_ENV_VAR) -> ApplicationEnvConfig:
    """
    Load and validate ApplicationEnvConfig from a JSON environment variable.
    Raises RuntimeError if not present or invalid.
    """
    raw = os.environ.get(var)
    if not raw:
        raise RuntimeError(f"Required env var {var} missing!")
    return ApplicationEnvConfig.model_validate_json(raw)


def load_config_from_json(json_data: Union[str, Dict]) -> ApplicationEnvConfig:
    """
    Load and validate ApplicationEnvConfig from a JSON string or dict.
    """
    if isinstance(json_data, str):
        return ApplicationEnvConfig.model_validate_json(json_data)
    elif isinstance(json_data, dict):
        return ApplicationEnvConfig.model_validate(json_data)
    else:
        raise TypeError("json_data must be a JSON string or dict.")
