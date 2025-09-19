#!/usr/bin/env python3
"""
Integration test server for Rerun interface.

This script tests the server recording stream functionality by hosting
a Rerun server and logging some test data.
"""

import time

from make87.interfaces.rerun import RerunInterface


def main():
    print("Starting Rerun server integration test...", flush=True)

    # Create interface instance
    interface = RerunInterface("rerun_test")

    print("Creating server recording stream...", flush=True)
    _ = interface.get_server_recording_stream("rerun_server")

    print("Server recording stream created successfully", flush=True)
    print("Rerun server is now hosting on 0.0.0.0:9876", flush=True)
    print("Server is ready to accept client connections", flush=True)

    # Keep server running for clients to connect
    print("Server will run for 30 seconds to allow client connections...", flush=True)
    time.sleep(30)

    print("Server integration test completed successfully", flush=True)


if __name__ == "__main__":
    main()
