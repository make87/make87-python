"""Protocol Buffers encoder with version compatibility.

This module provides a Protocol Buffers-based encoder that automatically
detects the installed protobuf version and imports the appropriate
implementation. Supports protobuf versions 4, 5, and 6.
"""

import importlib
from packaging.version import Version


def _get_protobuf_major_version() -> int:
    """Get the major version of the installed protobuf library.

    Returns:
        The major version number of the installed protobuf library

    Raises:
        ImportError: If protobuf is not installed
    """
    try:
        import google.protobuf
    except ImportError as e:
        raise ImportError("Protobuf support is not installed. " "Install with: pip install make87[protobuf]") from e

    version = getattr(google.protobuf, "__version__", None)
    if version is None:
        try:
            from importlib.metadata import version as pkg_version
        except ImportError:
            from importlib_metadata import version as pkg_version  # type: ignore
        version = pkg_version("protobuf")
    return Version(version).major


try:
    _major = _get_protobuf_major_version()

    if _major == 4:
        module = importlib.import_module(".pb4", __package__)
    elif _major == 5:
        module = importlib.import_module(".pb5", __package__)
    elif _major == 6:
        module = importlib.import_module(".pb6", __package__)
    else:
        raise ImportError(f"Unsupported protobuf major version: {_major}")

    ProtobufEncoder = module.ProtobufEncoder
except ImportError:
    # Only expose the error at import/use time
    def _raise_protobuf_import_error(*args, **kwargs):
        """Raise ImportError when protobuf dependencies are not installed.

        Raises:
            ImportError: Always raised with installation instructions
        """
        raise ImportError("Protobuf support is not installed. " "Install with: pip install make87[protobuf]")

    ProtobufEncoder = _raise_protobuf_import_error
