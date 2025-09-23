#!/usr/bin/env python3
"""
Multi-server integration test for Rerun interface - Server 3.

This script hosts a Rerun server on port 9878 for multi-client testing.
"""

import time
import rerun as rr

from make87.interfaces.rerun import RerunInterface


def main():
    print("Starting Rerun multi-server 3 integration test...", flush=True)

    # Create interface instance
    interface = RerunInterface("rerun_test")

    print("Creating server 3 recording stream...", flush=True)
    recording = interface.get_server_recording_stream("rerun_server_3")

    print("Server 3 recording stream created successfully", flush=True)
    print("Rerun server 3 is now hosting on 0.0.0.0:9876", flush=True)
    print("Server 3 is ready to accept client connections", flush=True)

    # Log some initial data to the server
    recording.log(
        "server_3/status", rr.TextLog("Server 3 is running and ready for connections", level=rr.TextLogLevel.INFO)
    )

    # Log some identifying data
    recording.log(
        "server_3/points",
        rr.Points3D(
            positions=[[0.0, 0.0, 3.0], [0.1, 0.1, 3.1]],
            colors=[[0, 0, 255], [50, 50, 200]],
        ),
    )

    # Keep server running for clients to connect
    print("Server 3 will run for 60 seconds to allow client connections...", flush=True)
    time.sleep(60)

    print("Server 3 integration test completed successfully", flush=True)


if __name__ == "__main__":
    main()
