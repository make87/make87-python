import signal
import threading


__all__ = [
    "run_forever",
]


def run_forever():
    stop_event = threading.Event()

    def handle_stop(signum, frame):
        stop_event.set()

    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)  # Optional: Ctrl-C

    stop_event.wait()
