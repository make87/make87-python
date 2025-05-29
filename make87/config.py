import os
from typing import Union, Dict, TypeVar, Callable, Any

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


T = TypeVar("T")


def get_config_value(
    config: ApplicationConfig,
    name: str,
    default: T = None,
    default_factory: Callable[[], T] = None,
    converter: Callable[[Any], T] = None,
) -> T:
    """
    Get a configuration value by name with optional default and type conversion.
    """
    config_dict: Dict[str, Any] = config.config
    value = config_dict.get(name, None)
    if value is None:
        if default is not None:
            return default
        if default_factory is not None:
            return default_factory()
        raise KeyError(f"Configuration key '{name}' not found and no default provided.")
    else:
        if converter:
            return converter(value)
    return value
