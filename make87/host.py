import logging

logger = logging.getLogger(__name__)

def host_is_updating() -> bool:
    """
    host_is_updating() -> bool

    Check if the host is currently updating.
    This is the case if the host system client or other applications are running an update.

    Returns:
        bool: True if the host is updating, False otherwise.
    """
    # check /run/signal/updating if it exists
    try:
        with open("/run/signal/updating", "r") as f:
            return True
    except FileNotFoundError:
        # File does not exist, host is not updating
        return False
    except Exception as e:
        logger.error(f"Error checking host update status: {e}")
    return False