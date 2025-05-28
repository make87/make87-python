
try:
    import yaml
    from typing import Optional, TypeVar

    from make87.encodings.base import Encoder

    T = TypeVar("T")


    class YamlEncoder(Encoder[T]):
        def __init__(self, *, loader: Optional[type] = None, dumper: Optional[type] = None) -> None:
            """
            loader: custom YAML loader class (e.g. yaml.SafeLoader)
            dumper: custom YAML dumper class (e.g. yaml.SafeDumper)
            """
            self.loader = loader or yaml.SafeLoader
            self.dumper = dumper or yaml.SafeDumper

        def encode(self, obj: T) -> bytes:
            """
            Serialize a Python object to UTF-8 encoded YAML bytes.
            """
            try:
                return yaml.dump(obj, Dumper=self.dumper).encode("utf-8")
            except Exception as e:
                raise ValueError(f"YAML encoding failed: {e}")

        def decode(self, data: bytes) -> T:
            """
            Deserialize UTF-8 encoded YAML bytes to a Python object.
            """
            try:
                return yaml.load(data.decode("utf-8"), Loader=self.loader)
            except Exception as e:
                raise ValueError(f"YAML decoding failed: {e}")
except ImportError:
    def _raise_yaml_import_error(*args, **kwargs):
        raise ImportError("Yaml support is not installed. " "Install with: pip install make87[yaml]")
    YamlEncoder = _raise_yaml_import_error
