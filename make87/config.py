import os
import re
from typing import Union, Dict, TypeVar, Callable, Any

from make87.models import ApplicationConfig

CONFIG_ENV_VAR = "MAKE87_CONFIG"

# Match pattern: {{ secret.XYZ }} with optional whitespace inside the braces
SECRET_PATTERN = re.compile(r"^\s*\{\{\s*secret\.([A-Za-z0-9_]+)\s*}}\s*$")


def _resolve_secrets(obj):
    # Recursively resolve secrets in dicts/lists
    if isinstance(obj, dict):
        return {k: _resolve_secrets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_secrets(item) for item in obj]
    elif isinstance(obj, str):
        match = SECRET_PATTERN.match(obj)
        if match:
            secret_name = match.group(1)
            secret_path = f"/run/secrets/{secret_name}.secret"
            try:
                with open(secret_path, "r") as f:
                    return f.read().strip()
            except Exception as e:
                raise RuntimeError(f"Failed to load secret '{secret_name}' from {secret_path}: {e}")
        return obj
    else:
        return obj


def load_config_from_env(var: str = CONFIG_ENV_VAR) -> ApplicationConfig:
    """
    Load and validate ApplicationConfig from a JSON environment variable.
    Raises RuntimeError if not present or invalid.
    """
    raw = os.environ.get(var)
    if not raw:
        raise RuntimeError(f"Required env var {var} missing!")
    config = ApplicationConfig.model_validate_json(raw)
    config.config = _resolve_secrets(config.config)
    return config


def load_config_from_json(json_data: Union[str, Dict]) -> ApplicationConfig:
    """
    Load and validate ApplicationConfig from a JSON string or dict.
    """
    if isinstance(json_data, str):
        config = ApplicationConfig.model_validate_json(json_data)
    elif isinstance(json_data, dict):
        config = ApplicationConfig.model_validate(json_data)
    else:
        raise TypeError("json_data must be a JSON string or dict.")
    config.config = _resolve_secrets(config.config)
    return config


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
