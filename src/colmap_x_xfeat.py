from pathlib import Path
# import pycolmap
import shutil
import sys
from pycolmap import logging
import sqlite3
import enlighten

import random

import os

# Try to import pycolmap and give actionable error if C++ backend is missing
try:
    import pycolmap
except Exception as _pycolmap_err:
    # Short, actionable diagnostics and recommended fixes
    print("Error: Cannot import pycolmap C++ backend (pycolmap._core).")
    print(f"Original error: {_pycolmap_err}")
    print("")
    print("Possible fixes (choose what applies to your setup):")
    print("  1) Install the Python package (try):")
    print("       python -m pip install pycolmap")
    print("  2) If you built pycolmap from source, ensure the compiled extension is on your PYTHONPATH")
    print("     and that any required DLLs are findable (on Windows add their folder to PATH).")
    print("  3) On Windows, install the Microsoft Visual C++ Redistributable (2015-2022).")
    print("  4) Read pycolmap README for platform-specific build/install instructions:")
    print("       https://github.com/mihaidusmanu/pycolmap")
    print("")
    print("Exiting. Fix the installation above and re-run the script.")
    raise SystemExit(1)

_project_root = Path(__file__).parent.parent
_libs_dir = _project_root / "libs"
_accel_dir = _libs_dir / "accelerated_features"

for p in (str(_project_root), str(_libs_dir), str(_accel_dir)):
    if Path(p).exists() and p not in sys.path:
        sys.path.insert(0, p)

from libs.accelerated_features.modules.xfeat import XFeat
from libs.colmap.database import COLMAPDatabase as Database
import cv2
import glob
import numpy as np
from progressbar import progressbar

class xFeatImplementation:

    def build_db(self, path_to_db):
        if path_to_db.exists():
            path_to_db.unlink()
        self.db = Database(str(path_to_db))
        self.db.create_tables()
    
    def write_camera_to_db(self):
        self.db.add_camera(
            model=1,
            width=960,
            height=540,
            params=[572, 467, 960/2, 540/2]
        )
        self.db.commit()
    
    def create_camera(self, id, model, focal_length, width, height):
        cam = pycolmap.Camera.create(id, model, focal_length, width, height)
        return cam
    
    def write_descriptor_to_db(self, image_id, descriptor):
        self.db.add_descriptors(image_id, descriptor)
    
    def write_keypoints_to_db(self, image_id, keypoints):
        self.db.add_keypoints(image_id, keypoints)
    
    def add_image_to_db(self, img_id, cam_id, path):
        self.db.add_image(str(path).split("\\")[-1], camera_id=cam_id, image_id=img_id)
        self.num_images += 1


    # Taken from: database.py
    def image_ids_to_pair_id(self, image_id1, image_id2):
        if image_id1 > image_id2:
            image_id1, image_id2 = image_id2, image_id1
        return image_id1 * (2**31 - 1) + image_id2
    

    #Taken from: database.py
    def pair_id_to_image_ids(self, pair_id):
        image_id2 = pair_id % (2**31 - 1)
        image_id1 = (pair_id - image_id2) / (2**31 - 1)
        return image_id1, image_id2
        

    def __init__(self, path_to_db):
        self.xfeat = XFeat()
        self.features = []
        self.matches = []
        self.num_images = 1
        self.build_db(path_to_db)
    
    def extract_features(self, id, img, top_k):
        output = self.xfeat.detectAndCompute(img, top_k)
        # print(output[0]["descriptors"].cpu().numpy().astype(np.float32))
        # print()
        # print()
        # print(output[0]["keypoints"].cpu().numpy().astype(np.float32))
        self.write_descriptor_to_db(id, output[0]["descriptors"].cpu().numpy().astype(np.float32))
        self.write_keypoints_to_db(id, output[0]["keypoints"].cpu().numpy().astype(np.float32))
        return output[0]

    def match_features(self, feature1, feature2):
        idx1, idx2 = self.xfeat.match(feature1["descriptors"], feature2["descriptors"], min_cossim=-1) #for -1 see xfeat.match implementation
        # print(idx1.cpu().numpy(), "\n", idx2.cpu().numpy())
        return (idx1.cpu().numpy(), idx2.cpu().numpy(),)
    
    def find_feature_idx(self, features, values):
        indexes = []
        keypoints = features["keypoints"].cpu().numpy().astype(np.float32)
        for value in values:
            idx = np.where(np.all(keypoints == value, axis=1))[0][0]
            indexes.append(int(idx))
        return indexes


    def extract_and_math_features(self, path_to_img_folder, k_max):
        images = glob.glob(f"{path_to_img_folder}*.jpg")

        # Sort by numeric value in filename https://stackoverflow.com/questions/62941378/how-to-sort-glob-glob-numerically
        def numeric_key(path):
            filename = os.path.splitext(os.path.basename(path))[0]
            number = filename.split("_")[-1]
            return int(number)
        
        images.sort(key=numeric_key)

        cam_id = 1
        img_id = 1
        self.write_camera_to_db()
        print("Extracting features...")
        for img in progressbar(images):
            self.add_image_to_db(img_id, cam_id, img)
            to_extract = cv2.imread(img)
            output = self.extract_features(img_id, to_extract, k_max)
            self.features.append(output)
            img_id += 1
            # cam_id += 1
        self.db.commit()

        print("Features extracted.\nMatching features...")

        num_images = len(self.features)

        for i, f1 in progressbar(enumerate(self.features)):
            for j in range(i + 1, min(num_images, i+5)):   # nur Paare i < j
                f2 = self.features[j]

                match = self.match_features(f1, f2)
                if len(match[0]) < 15:
                    continue

                matches_for_db = np.column_stack([match[0], match[1]]).astype(np.uint32)
                # print(f"Image {i} -> Image {j} with len {len(matches_for_db)}")

                # Speichere Matches
                self.db.add_matches(i + 1, j + 1, matches_for_db)

                if i % 50 == 0:
                    self.draw_matches(images[i], images[j], matches_for_db, f1, f2)

                # Geometrie: fundamental matrix preferred
                self.db.add_two_view_geometry(i + 1, j + 1, matches_for_db, config=2)

            self.db.commit()


    def draw_matches(self, img1, img2,  matches, feat1, feat2):
        #print(img1, img2, feat1["keypoints"][0].cpu().numpy(), feat2["keypoints"][0].cpu().numpy())
        left_img = cv2.imread(img1)
        right_img = cv2.imread(img2)

        height, width = left_img.shape[:2]
        canvas = np.zeros((height, width*2, 3), dtype=left_img.dtype)
        canvas[:height, :width] = left_img
        canvas[:height, width:2*width] = right_img

        # Draw points:
        for i in range(len(matches)):
            if i % 50 != 0:
                continue
            f1 = feat1["keypoints"][matches[i][0]]
            f2 = feat2["keypoints"][matches[i][1]]

            color = self.generate_random_color()

            pt1 = f1.cpu().numpy()
            cv2.circle(canvas, tuple(pt1.astype(int)), 3, color, -1)

            pt2 = f2.cpu().numpy()
            pt2[0] += width
            cv2.circle(canvas, tuple(pt2.astype(int)), 3, color, -1)

            cv2.line(canvas, pt1.astype(int), pt2.astype(int), color)

        img1_name = os.path.splitext(os.path.basename(img1))[0]
        img2_name = os.path.splitext(os.path.basename(img2))[0]
        img_path = img1.split("\\")[:-1]
        cv2.imwrite("\\".join(img_path) + "\\matches\\" + f"{img1_name}_{img2_name}.jpg", canvas)


    def write_matches_to_database(self, id1, id2, matches):
        self.db.add_matches(id1, id2, matches)

    def generate_random_color(self):
        rand1 = random.randint(100, 255)
        rand2 = random.randint(100, 255)
        rand3 = random.randint(100, 255)
        color = [rand1, rand2, rand3]
        decider = random.randint(0,2)
        for i in range(len(color)):
            if i != decider:
                color[i] = 0
        return color

def incremental_mapping_with_pbar(database_path, image_path, sfm_path):
    db = pycolmap.Database()
    db.open(str(database_path))
    try:
        num_images = db.num_images
    finally:
        db.close()
    with enlighten.Manager() as manager:
        with manager.counter(
            total = num_images, desc="Images registered"
        ) as pbar:
            pbar.update(0, force=True)
            reconstructions = pycolmap.incremental_mapping(
                str(database_path),
                str(image_path),
                str(sfm_path),
                initial_image_pair_callback=lambda: pbar.update(2),
                next_image_callback=lambda: pbar.update(1),
            )
    return reconstructions

def run():
    output_path = Path("res/test_results/test8")
    image_path = Path("res/images/test8/scaled")
    database_path = output_path / "database.db"
    sfm_path = output_path / "sfm"
    mvs_path = output_path / "mvs"

    output_path.mkdir(exist_ok=True)
    logging.set_log_destination(logging.INFO, output_path / "INFO.log")
    
    imp = xFeatImplementation(database_path)
    imp.extract_and_math_features(str(image_path)+"\\", 15000)

    # # print(imp.pair_id_to_image_ids(2147483649.0))

    
    sfm_count = 1
    while sfm_path.exists():
        sfm_path = output_path / f"sfm{sfm_count}"
        sfm_count += 1
    sfm_path.mkdir(exist_ok=True)
    print("Built SfM Path")
    
    imp.db.close()

    recs = pycolmap.incremental_mapping(
                str(database_path),
                str(image_path),
                str(sfm_path)
            )
    for idx, rec in recs.items():
        logging.info(f"#{idx} {rec.summary()}")
    # dense reconstruction
    # pycolmap.undistort_images(mvs_path, output_path/"sfm23"/"0", image_path)
    # pycolmap.patch_match_stereo(mvs_path)  # requires compilation with CUDA
    # pycolmap.stereo_fusion(mvs_path / "dense.ply", mvs_path)
    

if __name__ == "__main__":
    run()
    

    # conn = sqlite3.connect("mydb.db")

# Aktiviert Logging aller ausgeführten SQL-Statements
    # conn.set_trace_callback(print)
    # img1 = None
    # img2 = None
    # img1 = cv2.imread("testimages/test3/frame0.jpg")
    # img2 = cv2.imread("testimages/test3/frame36.jpg")

    # img1 = imp.xfeat.parse_input(img1)
    # img2 = imp.xfeat.parse_input(img2)

    # out1 = imp.xfeat.detectAndCompute(img1, top_k=256)[0]
    # out2 = imp.xfeat.detectAndCompute(img2, top_k=256)[0]

    # idxs0, idxs1 = imp.xfeat.match(out1['descriptors'], out2['descriptors'], min_cossim=-1 )

    # print(out1['keypoints'][idxs0].cpu().numpy(), out2['keypoints'][idxs1].cpu().numpy())



