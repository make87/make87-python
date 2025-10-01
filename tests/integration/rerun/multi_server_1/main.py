#!/usr/bin/env python3
"""
Multi-server integration test for Rerun interface - Server 1.

This script hosts a Rerun server on port 9876 for multi-client testing.
"""

import time
import rerun as rr

from make87.interfaces.rerun import RerunInterface


def main():
    print("Starting Rerun multi-server 1 integration test...", flush=True)

    # Create interface instance
    interface = RerunInterface("rerun_test")

    print("Creating server 1 recording stream...", flush=True)
    recording = interface.get_server_recording_stream("rerun_server_1")

    print("Server 1 recording stream created successfully", flush=True)
    print("Rerun server 1 is now hosting on 0.0.0.0:9876", flush=True)
    print("Server 1 is ready to accept client connections", flush=True)

    # Log some initial data to the server
    recording.log(
        "server_1/status", rr.TextLog("Server 1 is running and ready for connections", level=rr.TextLogLevel.INFO)
    )

    # Log some identifying data
    recording.log(
        "server_1/points",
        rr.Points3D(
            positions=[[1.0, 0.0, 0.0], [1.1, 0.1, 0.1]],
            colors=[[255, 0, 0], [200, 50, 50]],
        ),
    )

    # Keep server running for clients to connect
    print("Server 1 will run for 60 seconds to allow client connections...", flush=True)
    time.sleep(60)

    print("Server 1 integration test completed successfully", flush=True)


if __name__ == "__main__":
    main()
