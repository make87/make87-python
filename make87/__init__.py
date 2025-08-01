"""Make87 Python SDK.

This package provides a comprehensive SDK for building applications on the Make87 platform.
It includes modules for configuration management, peripheral control, messaging interfaces,
data encoding/decoding, storage operations, and host system integration.

Modules:
    config: Configuration loading and management utilities
    peripherals: Hardware peripheral control and management
    models: Data models and type definitions
    encodings: Data serialization and encoding utilities
    interfaces: Messaging and communication interfaces
    storage: Blob storage operations and utilities
    host: Host system integration utilities
"""

import signal
import threading
import make87.config as config
import make87.peripherals as peripherals
import make87.models as models
import make87.encodings as encodings
import make87.interfaces as interfaces
import make87.storage as storage
import make87.host as host


__all__ = [
    "run_forever",
    "config",
    "peripherals",
    "models",
    "encodings",
    "interfaces",
    "storage",
    "host",
]


def run_forever() -> None:
    """Run the application forever until a termination signal is received.

    This function sets up signal handlers for SIGTERM and SIGINT (Ctrl+C) and blocks
    execution until one of these signals is received. This is typically used as the
    main loop for long-running Make87 applications.

    The function will gracefully handle:
        - SIGTERM: Termination signal (sent by process managers)
        - SIGINT: Interrupt signal (Ctrl+C from terminal)

    Note:
        This is a blocking function that will run indefinitely until a signal
        is received. Make sure to set up all your application components before
        calling this function.

    Example:

        >>> import make87
        >>> # Set up your application components here
        >>> make87.run_forever()  # Blocks until signal received
    """
    stop_event = threading.Event()

    def handle_stop(signum: int, frame) -> None:
        stop_event.set()

    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)  # Optional: Ctrl-C

    stop_event.wait()
