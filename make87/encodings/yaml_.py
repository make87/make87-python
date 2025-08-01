"""YAML encoder for serializing Python objects to YAML format.

This module provides a YAML-based encoder that converts Python objects
to UTF-8 encoded YAML bytes and vice versa, with support for custom
loaders and dumpers. Falls back to an import error if PyYAML is not installed.
"""

try:
    import yaml
    from typing import Optional, TypeVar

    from make87.encodings.base import Encoder

    T = TypeVar("T")

    class YamlEncoder(Encoder[T]):
        """YAML encoder for Python objects.

        This encoder converts Python objects to UTF-8 encoded YAML bytes
        and deserializes YAML bytes back to Python objects. It supports
        custom YAML loaders and dumpers for advanced use cases.

        Attributes:
            loader: YAML loader class used for deserialization
            dumper: YAML dumper class used for serialization
        """

        def __init__(self, *, loader: Optional[type] = None, dumper: Optional[type] = None) -> None:
            """Initialize the YAML encoder with optional custom loader and dumper.

            Args:
                loader: Custom YAML loader class for deserialization.
                    Defaults to yaml.SafeLoader for security.
                dumper: Custom YAML dumper class for serialization.
                    Defaults to yaml.SafeDumper for security.

            Example:

                >>> # Simple encoder with safe defaults
                >>> encoder = YamlEncoder()
                >>>
                >>> # With custom loader/dumper
                >>> encoder = YamlEncoder(
                ...     loader=yaml.FullLoader,
                ...     dumper=yaml.SafeDumper
                ... )
            """
            self.loader = loader or yaml.SafeLoader
            self.dumper = dumper or yaml.SafeDumper

        def encode(self, obj: T) -> bytes:
            """Serialize a Python object to UTF-8 encoded YAML bytes.

            Args:
                obj: The Python object to serialize

            Returns:
                UTF-8 encoded YAML bytes representation of the object

            Raises:
                ValueError: If YAML encoding fails due to unsupported object types
                    or other serialization errors

            Example:

                >>> encoder = YamlEncoder()
                >>> data = {"key": "value", "items": [1, 2, 3]}
                >>> encoded = encoder.encode(data)
                >>> print(encoded.decode('utf-8'))
                items:
                - 1
                - 2
                - 3
                key: value
            """
            try:
                return yaml.dump(obj, Dumper=self.dumper).encode("utf-8")
            except Exception as e:
                raise ValueError(f"YAML encoding failed: {e}")

        def decode(self, data: bytes) -> T:
            """Deserialize UTF-8 encoded YAML bytes to a Python object.

            Args:
                data: UTF-8 encoded YAML bytes to deserialize

            Returns:
                The deserialized Python object

            Raises:
                ValueError: If YAML decoding fails due to invalid YAML data
                    or encoding issues

            Example:

                >>> encoder = YamlEncoder()
                >>> yaml_data = b'key: value\\nitems:\\n- 1\\n- 2\\n- 3\\n'
                >>> decoded = encoder.decode(yaml_data)
                >>> print(decoded)
                {'key': 'value', 'items': [1, 2, 3]}
            """
            try:
                return yaml.load(data.decode("utf-8"), Loader=self.loader)
            except Exception as e:
                raise ValueError(f"YAML decoding failed: {e}")

except ImportError:

    def _raise_yaml_import_error(*args, **kwargs):
        """Raise ImportError when PyYAML dependencies are not installed.

        Raises:
            ImportError: Always raised with installation instructions
        """
        raise ImportError("Yaml support is not installed. " "Install with: pip install make87[yaml]")

    YamlEncoder = _raise_yaml_import_error
