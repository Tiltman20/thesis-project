# Imports:
import shutil
import sys
import enlighten
import random
import os
import pycolmap
import cv2
import glob
import numpy as np
from progressbar import progressbar
from pathlib import Path

_project_root = Path(__file__).parent.parent
_libs_dir = _project_root / "libs"
_accel_dir = _libs_dir / "accelerated_features"

for p in (str(_project_root), str(_libs_dir), str(_accel_dir)):
    if Path(p).exists() and p not in sys.path:
        sys.path.insert(0, p)

from libs.accelerated_features.modules.xfeat import XFeat

import database

class CameraIntrisics:
    import generate_camera_intrinsics as gci

    def __init__(self, width_px, height_px, width_ratio, height_ratio, sensor_area):
        self.size_px = [width_px, height_px]
        self.aspect_ratio = [width_ratio, height_ratio]
        self.sensor_area = sensor_area

    def get_fov(self):
        return self.gci.calculate(self.size_px, self.aspect_ratio, self.sensor_area)

    def get_focal_length(self):
        return self.gci.get_real_focal_length(sensor_area=self.sensor_area, sensor_aspect=self.aspect_ratio)


def run(images_path, sfm_root_path):
    print("Setting up...")
    database.init("../database.db")
    images = load_images(images_path)
    print("Writing camera to database...")
    camera_id = write_camera(
        CameraIntrisics(
            width_px=3840, 
            height_px=2160, 
            width_ratio=3, 
            height_ratio=2, 
            sensor_area=12.2
            ),
        "PINHOLE", 
        960, 540, #Actual image width & height in pixels
        480, 270 #Image center point (Usually act_width_px/2, act_height_px/2)
        )
    preprocess_images(images, camera_id=camera_id, top_k=1024)
    build_sfm(image_path=images_path, sfm_path=sfm_root_path)


def load_images(path):
    images = glob.glob(f"{path}*.jpg")
    images.sort(key=numeric_key)
    return images

def write_camera(camera_intrisics, model, width_px, height_px, center_x, center_y):
    fov = camera_intrisics.get_focal_length()
    camera_id = database.write_camera(
        model=model, 
        width_px=width_px, 
        height_px=height_px, 
        params=[
            fov, fov, 
            center_x, center_y
        ]
    )
    return camera_id

def write_image(camera_id, image):
    return database.write_image(camera_id, image)

def preprocess_images(images, camera_id, top_k):
    features = extract_features(images, camera_id, top_k)
    match_features(features=features, k=30)

def process_match(feature0, feature1, xfeat):
    idx1, idx2 = xfeat.match(feature0["descriptors"], feature1["descriptors"], min_cossim=-1) #TODO: Evaluate different values fpr min_crossim
    return idx1, idx2

def build_sfm(image_path, sfm_path):
    incremental_mapping_with_pbar(num_images=database.num_images_in_database(), database_path=database.path, image_path=image_path, sfm_path=sfm_path)

def extract_features(images, camera_id, top_k):
    image_id = 1
    xfeat = XFeat()
    feature_array = []
    for image_path in progressbar(images):
        image_id = write_image(camera_id, image_path)
        read_image = cv2.imread(image_path)
        features = xfeat.detectAndCompute(read_image, top_k)
        write_features(image_id=image_id, features=features)
        feature_array.append(features[0])
    return feature_array


def write_features(image_id, features):
    database.write_features(image_id=image_id, features=features)

def match_features(features, k):
    xfeat = XFeat()
    for i, f1 in progressbar(enumerate(features)):
        for j, f2 in enumerate(features[i+1:min(i+k, len(features))]):
            j += (i+1) #adjust j to point to the following elements in the array
            # print("Matching", i, ",", j)
            idx1, idx2 = process_match(f1, f2, xfeat)
            matches = np.column_stack(
                [
                    idx1.cpu().numpy(), 
                    idx2.cpu().numpy()
                ]
            ).astype(np.uint32)
            F, verified = verify_geometry(f1["keypoints"].cpu().numpy(), f2["keypoints"].cpu().numpy(), matches)
            if verified is None or len(verified) < 30: continue
            write_matches(i+1, j+1, verified, F)

def write_matches(id0, id1, matches, F):
    database.write_matches(id0, id1, matches)
    database.write_two_view_geometry(id0, id1, matches, F)

def verify_geometry(keypoint0, keypoint1, matches):
    pts1 = keypoint0[matches[:,0]]
    pts2 = keypoint1[matches[:,1]]

    F, mask = cv2.findFundamentalMat(
        pts1, pts2,
        cv2.FM_RANSAC,
        ransacReprojThreshold=1.0,
        confidence=0.999,
        maxIters=10000
    )
    if F is None:
        return None, None
    inliers = mask.ravel().astype(bool)
    verified = matches[inliers]
    return F, verified

def incremental_mapping_with_pbar(num_images, database_path, image_path, sfm_path):
    with enlighten.Manager() as manager:
        with manager.counter(
            total = num_images, desc="Images registered"
        ) as pbar:
            pbar.update(0, force=True)
            reconstructions = pycolmap.incremental_mapping(
                str(database_path),
                str(image_path)+"/",
                str(sfm_path),
                initial_image_pair_callback=lambda: pbar.update(2),
                next_image_callback=lambda: pbar.update(1),
            )
    return reconstructions

# UTILITY

# Sort by numeric value in filename https://stackoverflow.com/questions/62941378/how-to-sort-glob-glob-numerically
def numeric_key(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    number = filename.split("_")[-1]
    return int(number)


run("/home/tilman/Documents/GitHub/thesis-project/images/", "/home/tilman/Documents/GitHub/thesis-project/sfm/")