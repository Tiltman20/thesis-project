import sqlite3
import numpy as np
import sys


def read_colmap_cameras(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute("SELECT camera_id, model, width, height, params FROM cameras")
    rows = cursor.fetchall()

    cameras = {}

    for camera_id, model_id, width, height, params_blob in rows:
        # COLMAP speichert Parameter als Float64-Array im BLOB
        params = np.frombuffer(params_blob, dtype=np.float64)

        cameras[camera_id] = {
            "model_id": model_id,
            "width": width,
            "height": height,
            "params": params
        }

    conn.close()
    return cameras


def print_camera_parameters(cameras):
    for cam_id, cam in cameras.items():
        print("=" * 50)
        print(f"Camera ID: {cam_id}")
        print(f"Resolution: {cam['width']} x {cam['height']}")
        print(f"Model ID: {cam['model_id']}")
        print(f"Raw Params: {cam['params']}")

        # Typische Modell-Interpretationen
        params = cam["params"]

        print("\nInterpreted Parameters:")

        if len(params) == 3:
            print(f"  f, cx, cy = {params}")
        elif len(params) == 4:
            print(f"  fx, fy, cx, cy = {params}")
        elif len(params) == 5:
            print(f"  fx, fy, cx, cy, k1 = {params}")
        elif len(params) == 8:
            print(f"  fx, fy, cx, cy, k1, k2, p1, p2 = {params}")
        else:
            print("  Unknown parameter configuration.")

        print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_colmap_cameras.py path/to/database.db")
        sys.exit(1)

    database_path = sys.argv[1]
    cameras = read_colmap_cameras(database_path)
    print_camera_parameters(cameras)
