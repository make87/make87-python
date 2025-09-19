#!/usr/bin/env python3
"""
Integration test client for Rerun interface.

This script tests the client recording stream functionality by connecting
to a Rerun server and logging some test data.
"""

import time
import sys

from make87.interfaces.rerun import RerunInterface


def main():
    """Main client test function."""
    try:
        # Import rerun here to check if it's available
        import rerun as rr

        print("Starting Rerun client integration test...", flush=True)

        # Create interface instance
        interface = RerunInterface("rerun_test")

        print("Creating client recording stream...", flush=True)
        recording = interface.get_client_recording_stream("rerun_client")

        print("Client recording stream created successfully", flush=True)

        # Set the global recording stream
        rr.set_global_data_recording(recording)

        # Log some test data
        print("Logging test data...")

        # Log points
        rr.log(
            "integration_test/points",
            rr.Points3D(
                positions=[[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]],
                colors=[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
            ),
        )

        # Log text
        rr.log("integration_test/status", rr.TextLog("Integration test client is running", level=rr.TextLogLevel.INFO))

        # Log scalars
        for i in range(10):
            rr.set_time("step", sequence=i)
            rr.log("integration_test/scalars", rr.Scalars([float(i * i)]))
            time.sleep(0.1)

        print("Test data logged successfully", flush=True)
        print("Client integration test completed successfully", flush=True)

    except ImportError:
        print("rerun-sdk not installed, skipping integration test", flush=True)
        print("Install with: pip install rerun-sdk", flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"Integration test failed: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
