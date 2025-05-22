import os
from typing import Union, Dict

from make87.models import ApplicationConfig

CONFIG_ENV_VAR = "MAKE87_CONFIG"


def load_config_from_env(var: str = CONFIG_ENV_VAR) -> ApplicationConfig:
    """
    Load and validate ApplicationConfig from a JSON environment variable.
    Raises RuntimeError if not present or invalid.
    """
    raw = os.environ.get(var)
    if not raw:
        raise RuntimeError(f"Required env var {var} missing!")
    return ApplicationConfig.model_validate_json(raw)


def load_config_from_json(json_data: Union[str, Dict]) -> ApplicationConfig:
    """
    Load and validate ApplicationConfig from a JSON string or dict.
    """
    if isinstance(json_data, str):
        return ApplicationConfig.model_validate_json(json_data)
    elif isinstance(json_data, dict):
        return ApplicationConfig.model_validate(json_data)
    else:
        raise TypeError("json_data must be a JSON string or dict.")
