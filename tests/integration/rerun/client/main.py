#!/usr/bin/env python3
"""
Integration test client for Rerun interface.

This script tests the client recording stream functionality by connecting
to a Rerun server and logging some test data.
"""

import time
import rerun as rr

from make87.interfaces.rerun import RerunInterface


def main():
    print("Starting Rerun client integration test...", flush=True)

    # Create interface instance
    interface = RerunInterface("rerun_test")

    print("Creating client recording stream...", flush=True)
    recording = interface.get_client_recording_stream("rerun_client")

    print("Client recording stream created successfully", flush=True)
    print("Connected to Rerun server, starting to log data...", flush=True)

    # Log some test data
    print("Logging test data...")

    # Log points
    recording.log(
        "integration_test/points",
        rr.Points3D(
            positions=[[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]],
            colors=[[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        ),
    )

    # Log text
    recording.log(
        "integration_test/status", rr.TextLog("Integration test client is running", level=rr.TextLogLevel.INFO)
    )

    # Log scalars with timestamps
    for i in range(10):
        recording.set_time("step", sequence=i)
        recording.log("integration_test/scalars", rr.Scalars([float(i * i)]))
        time.sleep(0.1)

    # Log images
    import numpy as np

    test_image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    recording.log("integration_test/image", rr.Image(test_image))

    # Log more complex data over time
    for i in range(5):
        recording.set_time("step", sequence=10 + i)
        # Log transform
        recording.log(
            f"integration_test/transform_{i}",
            rr.Transform3D(translation=[float(i), 0.0, 0.0], rotation=rr.Quaternion(xyzw=[0, 0, 0, 1])),
        )
        time.sleep(0.2)

    print("Test data logged successfully", flush=True)
    print("Client integration test completed successfully", flush=True)


if __name__ == "__main__":
    main()
