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


def run_forever():
    stop_event = threading.Event()

    def handle_stop(signum, frame):
        stop_event.set()

    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)  # Optional: Ctrl-C

    stop_event.wait()
