import colmap_x_xfeat as cf
import export_img as exim
import scale_images as scim
import sift_colmap as scmp
from pathlib import Path
import argparse
import subprocess
import os

APP_ROOT = ""
COLMAP_APP_ROOT = r"C:\Users\tilma\Documents\GitHub\bachelor-thesis\research\COLMAP\COLMAP.bat"
VIDEO_PATH = "res/videos/Rittmeier/test_1.MOV"


def main():
    parser = argparse.ArgumentParser(description="Pipeline for xFeat supplied COLMAP")
    parser.add_argument(
        "--noimport",
        action="store_true",
        help="Do not import images"
    )
    parser.add_argument(
        "--noscale",
        action="store_true",
        help="Do not scale images"
    )
    parser.add_argument(
        "--sift",
        action="store_true",
        help="use sift for colmap"
    )
    parser .add_argument(
        "--norender",
        action="store_true",
        help="Render Gaussian Splattings afterwards"
    )
    parser.add_argument(
        "-s",
        action="store",
        type=str,
        help="App root path"
    )
    parser.add_argument(
        "--top_k",
        action="store",
        type=int,
        default=8192,
        help="Number of top matches to use for feature extraction (default: 8192)"
    )
    args = parser.parse_args()
    if args.s == "":
        print("No Path provided!")
        return
    APP_ROOT = args.s
    if not os.path.exists(APP_ROOT):
        os.makedirs(APP_ROOT)
    IMAGE_PATH = APP_ROOT + r"\images"
    COLMAP_BASE_PATH = APP_ROOT + r"\sparse"
    DATABASE_PATH = APP_ROOT
    if not args.noimport:
        exim.export_images(VIDEO_PATH, IMAGE_PATH)
    if not args.noscale:
        scim.scale_images(IMAGE_PATH, 0.25)
    if not os.path.exists(COLMAP_BASE_PATH):
        os.makedirs(COLMAP_BASE_PATH)
    if args.sift:
        pass
        scmp.run(
            root_path=fr"C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1", 
            image_path=IMAGE_PATH, 
            database_path=DATABASE_PATH, 
            output_path=COLMAP_BASE_PATH,
            top_k=args.top_k
        )
    else:
        pass
        cf.top_k_matches = args.top_k
        cf.run(Path(COLMAP_BASE_PATH),
                IMAGE_PATH,
                Path(DATABASE_PATH)
                )
    if not args.norender:
        subprocess.run([
            r"C:\Users\tilma\Documents\GitHub\bachelor-thesis\thesis-project-1\src\render_gaussians.bat",
            fr"{APP_ROOT}"
            ])
    

if __name__ == "__main__":
    main()