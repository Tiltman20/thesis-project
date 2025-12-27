import colmap_x_xfeat as cf
import export_img as exim
import scale_images as scim
from pathlib import Path
import argparse
import subprocess

VIDEO_PATH = "res/videos/Rittmeier/test_1.MOV"
IMAGE_PATH = "res/colmap-test/Rittmeier/test_3/images"
COLMAP_BASE_PATH = Path("res/colmap-test/Rittmeier/test_3/sparse")

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
    args = parser.parse_args()
    if not args.noimport:
        exim.export_images(VIDEO_PATH, IMAGE_PATH, 750)
    if not args.noscale:
        scim.scale_images(IMAGE_PATH, 0.25)
    cf.run(COLMAP_BASE_PATH, IMAGE_PATH)


if __name__ == "__main__":
    main()