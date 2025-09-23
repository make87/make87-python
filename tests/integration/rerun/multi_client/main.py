#!/usr/bin/env python3
"""
Multi-client integration test for Rerun interface.

This script tests the multi-client recording stream functionality by connecting
to multiple Rerun servers and logging test data to each.
"""

import time
import numpy as np
import rerun as rr

from make87.interfaces.rerun import RerunInterface


def main():
    print("Starting Rerun multi-client integration test...", flush=True)

    # Create interface instance
    interface = RerunInterface("rerun_test")

    print("Creating multi-client recording streams...", flush=True)
    recordings = interface.get_multi_client_recording_streams("MULTI_RERUN_CLIENT")

    print(f"Multi-client recording streams created successfully: {len(recordings)} streams", flush=True)
    print("Connected to Rerun servers, starting to log data...", flush=True)

    # Log test data to each recording stream
    for i, recording in enumerate(recordings, 1):
        print(f"Logging data to server {i}...", flush=True)

        # Log status
        recording.log(
            f"multi_client/server_{i}/status",
            rr.TextLog(f"Multi-client connected to server {i}", level=rr.TextLogLevel.INFO),
        )

        # Log unique points for each server
        recording.log(
            f"multi_client/server_{i}/points",
            rr.Points3D(
                positions=[[float(i), float(i), float(i)], [float(i + 0.5), float(i + 0.5), float(i + 0.5)]],
                colors=[
                    [255 * i // 3, 255 * (i - 1) // 3, 255 * (i - 2) // 3],
                    [200 * i // 3, 200 * (i - 1) // 3, 200 * (i - 2) // 3],
                ],
            ),
        )

        # Log scalars with timestamps
        for step in range(5):
            recording.set_time("step", sequence=step)
            recording.log(f"multi_client/server_{i}/scalar", rr.Scalars([float(i * step)]))
            time.sleep(0.1)

        # Log a unique image for each server
        test_image = np.full((32, 32, 3), i * 80, dtype=np.uint8)  # Different brightness per server
        recording.log(f"multi_client/server_{i}/image", rr.Image(test_image))

        # Log transform
        recording.log(
            f"multi_client/server_{i}/transform",
            rr.Transform3D(translation=[float(i), 0.0, 0.0], rotation=rr.Quaternion(xyzw=[0, 0, 0, 1])),
        )

        print(f"Data logged to server {i} successfully", flush=True)
        time.sleep(0.5)  # Brief pause between servers

    print("Test data logged to all servers successfully", flush=True)
    print("Multi-client integration test completed successfully", flush=True)


if __name__ == "__main__":
    main()
