#!/usr/bin/env python3
"""
Integration test server for Rerun interface.

This script tests the server recording stream functionality by hosting
a Rerun server and logging some test data.
"""

import time
import sys

from make87.interfaces.rerun import RerunInterface


def main():
    """Main server test function."""
    try:
        # Import rerun here to check if it's available
        import rerun as rr

        print("Starting Rerun server integration test...", flush=True)

        # Create interface instance
        interface = RerunInterface("rerun_test")

        print("Creating server recording stream...", flush=True)
        recording = interface.get_server_recording_stream("rerun_server")

        print("Server recording stream created successfully", flush=True)
        print("Rerun server is now hosting on 0.0.0.0:9876", flush=True)

        # Set the global recording stream
        rr.set_global_data_recording(recording)

        # Log some test data
        print("Logging test data...")

        # Log points
        rr.log(
            "integration_test/server_points",
            rr.Points3D(
                positions=[[0.0, 0.0, 0.0], [3.0, 3.0, 3.0], [6.0, 6.0, 6.0]],
                colors=[[255, 255, 0], [255, 0, 255], [0, 255, 255]],
            ),
        )

        # Log text
        rr.log(
            "integration_test/server_status",
            rr.TextLog("Integration test server is running", level=rr.TextLogLevel.INFO),
        )

        # Log some time series data
        for i in range(20):
            rr.set_time("step", sequence=i)
            rr.log("integration_test/server_scalars", rr.Scalars([float(i * 2)]))
            time.sleep(0.1)

        print("Test data logged successfully", flush=True)
        print("Server will continue running for 5 seconds...", flush=True)
        time.sleep(5)

        print("Server integration test completed successfully", flush=True)

    except ImportError:
        print("rerun-sdk not installed, skipping integration test", flush=True)
        print("Install with: pip install rerun-sdk", flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"Integration test failed: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
