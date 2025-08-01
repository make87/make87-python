"""Configuration management utilities for Make87 applications.

This module provides functions for loading and managing application configuration
from environment variables and JSON data. It supports secret resolution from
Docker secrets and type-safe configuration access.
"""

import os
import re
from typing import Union, Dict, TypeVar, Callable, Any

from make87.models import ApplicationConfig

CONFIG_ENV_VAR = "MAKE87_CONFIG"

# Match pattern: {{ secret.XYZ }} with optional whitespace inside the braces
SECRET_PATTERN = re.compile(r"^\s*\{\{\s*secret\.([A-Za-z0-9_]+)\s*}}\s*$")


def _resolve_secrets(obj: Any) -> Any:
    """Recursively resolve secret placeholders in configuration objects.

    Args:
        obj: The configuration object to process (dict, list, str, or other)

    Returns:
        The configuration object with secret placeholders resolved

    Raises:
        RuntimeError: If a secret file cannot be read
    """
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
    """Load and validate ApplicationConfig from a JSON environment variable.

    Loads configuration from the specified environment variable, validates it
    against the ApplicationConfig schema, and resolves any secret placeholders.

    Args:
        var: Environment variable name to load configuration from.
            Defaults to "MAKE87_CONFIG".

    Returns:
        Validated and processed ApplicationConfig instance.

    Raises:
        RuntimeError: If the environment variable is missing or contains invalid JSON.

    Example:

        >>> import os
        >>> os.environ["MAKE87_CONFIG"] = '{"application_info": {...}, "config": {...}}'
        >>> config = load_config_from_env()
        >>> print(config.application_info.application_id)
    """
    raw = os.environ.get(var)
    if not raw:
        raise RuntimeError(f"Required env var {var} missing!")
    config = ApplicationConfig.model_validate_json(raw)
    config.config = _resolve_secrets(config.config)
    return config


def load_config_from_json(json_data: Union[str, Dict]) -> ApplicationConfig:
    """Load and validate ApplicationConfig from a JSON string or dictionary.

    Processes the provided JSON data, validates it against the ApplicationConfig
    schema, and resolves any secret placeholders.

    Args:
        json_data: JSON string or dictionary containing configuration data.

    Returns:
        Validated and processed ApplicationConfig instance.

    Raises:
        TypeError: If json_data is neither a string nor a dictionary.

    Example:

        >>> config_dict = {"application_info": {...}, "config": {...}}
        >>> config = load_config_from_json(config_dict)
        >>> config_json = '{"application_info": {...}, "config": {...}}'
        >>> config = load_config_from_json(config_json)
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
    """Get a configuration value by name with optional default and type conversion.

    Retrieves a configuration value from the application config with support
    for default values, factory functions, and type conversion.

    Args:
        config: The ApplicationConfig instance to retrieve values from.
        name: The configuration key name to look up.
        default: Default value to return if the key is not found.
        default_factory: Factory function to call if the key is not found
            and no default is provided.
        converter: Optional function to convert the retrieved value to the
            desired type.

    Returns:
        The configuration value, potentially converted to the desired type.

    Raises:
        KeyError: If the configuration key is not found and no default is provided.

    Example:

        >>> config = load_config_from_env()
        >>> port = get_config_value(config, "port", default=8080, converter=int)
        >>> debug = get_config_value(config, "debug", default=False, converter=bool)
        >>> timeout = get_config_value(config, "timeout", default_factory=lambda: 30.0)
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
