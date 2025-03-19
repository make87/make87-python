import os
import threading
from typing import Optional

import zenoh


class _SessionManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._session: Optional[zenoh.Session] = None
        self._initialized: bool = False

    @classmethod
    def get_instance(cls):
        """Singleton pattern to ensure only one instance exists."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def initialize(self):
        """Initialize the session and topics."""
        with self._lock:
            if self._initialized:
                return  # Already initialized

            # Read configuration from environment variables
            if "COMMUNICATION_CONFIG" in os.environ:
                config = zenoh.Config.from_json5(os.environ["COMMUNICATION_CONFIG"])
            else:
                config = zenoh.Config()
            self._session = zenoh.open(config=config)
            self._initialized = True

    def get_session(self) -> zenoh.Session:
        """Get the session."""
        if not self._initialized:
            raise RuntimeError("SessionManager not initialized. Call initialize() first.")
        return self._session


def get_session() -> zenoh.Session:
    """Get the session.

    Returns:
        The session singleton.

    Raises:
        RuntimeError: If the session manager has not been initialized correctly. Call `make87.initialize()`.
    """
    return _SessionManager.get_instance().get_session()
