"""Host system integration utilities for Make87 applications.

This module provides functions for interacting with the host system and
checking system status, such as whether the host is currently updating.
"""

import logging

logger = logging.getLogger(__name__)


def host_is_updating() -> bool:
    """Check if the host is currently updating.

    This function checks if the host system client or other applications are
    running an update by looking for the presence of the update signal file.

    Returns:
        True if the host is updating, False otherwise.

    Note:
        This function checks for the existence of `/run/signal/updating` file.
        If the file exists, it indicates that an update is in progress.

    Example:

        >>> import make87.host
        >>> if make87.host.host_is_updating():
        ...     print("Host is updating, waiting...")
        ... else:
        ...     print("Host is ready")
    """
    # check /run/signal/updating if it exists
    try:
        with open("/run/signal/updating", "r"):
            return True
    except FileNotFoundError:
        # File does not exist, host is not updating
        return False
    except Exception as e:
        logger.error(f"Error checking host update status: {e}")
    return False
