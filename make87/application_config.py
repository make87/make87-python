import json
import os
from typing import Any, Callable, Dict, Optional, TypeVar, Union

T = TypeVar("T")


class ApplicationConfig(Dict[str, Union[str, int, float, bool]]):
    instance = None

    def __init__(self, *args, **kwargs):
        json_config = os.environ.get("APPLICATION_CONFIG", "{}")
        config = json.loads(json_config)
        super().__init__(config)

    @classmethod
    def resolve(cls) -> "ApplicationConfig":
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


def smart_cast(value: str) -> Union[str, int, float, bool]:
    """Attempt to convert string values into int, float, or bool if possible."""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        if "." in value:
            return float(value)  # Convert to float if it contains a decimal point
        return int(value)  # Convert to int if it's a whole number
    except ValueError:
        return value  # Return as string if conversion fails


def get_config_value(
    key: str,
    default: Optional[T] = None,
    decode: Optional[Callable[[Any], T]] = None
) -> Optional[T]:
    value = ApplicationConfig.resolve().get(key, default)

    if value is None:
        return None  # Explicitly return None if key does not exist and no default is provided

    if decode:
        return decode(value)  # Apply custom decode function

    if default is not None:
        # Convert value to match default type
        if isinstance(default, (int, float, bool)) and isinstance(value, str):
            try:
                return type(default)(value)
            except ValueError:
                return default
        return value  # Return as is if default exists but is not a convertible type

    if isinstance(value, str):
        return smart_cast(value)  # Infer type if no default is provided

    return value  # Return raw value if it's already the correct type