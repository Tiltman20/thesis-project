import pycolmap
import numpy as np
import os

path = ""

def init(db_path):
    if os.path.exists(db_path):
        print("Deleting previous database")
        os.remove(db_path)
    global path
    path = db_path

def connect():
    return pycolmap.Database.open(path)

def write_image(camera_id, image_path):
    db = connect()
    image = pycolmap.Image(
        name=image_path.split("/")[-1],
        camera_id=camera_id
    )
    image_id = db.write_image(image)
    db.close()
    return image_id

def write_camera(model, width_px, height_px, params):
    if camera_exists(1): return 1
    db = connect()
    camera = pycolmap.Camera(
        model=model,
        width=width_px,
        height=height_px,
        params=params
    )
    camera_id = db.write_camera(camera=camera)
    db.close()
    return camera_id

def write_features(image_id, features):
    if features_exist(image_id): return
    db = connect()
    descriptors = pycolmap.FeatureDescriptors(pycolmap.FeatureExtractorType.UNDEFINED, _get_descriptors(features))
    db.write_descriptors(image_id=image_id, descriptors=descriptors)
    db.write_keypoints(image_id=image_id, keypoints=_get_keypoints(features))

def _get_keypoints(features):
    feature = features[0]
    keypoints = feature["keypoints"]
    if hasattr(keypoints, "detach"):
        keypoints = keypoints.detach().cpu().numpy()
    return np.asarray(keypoints, dtype=np.float32)

def _get_descriptors(features):
    feature = features[0]
    descriptors = feature["descriptors"]
    if hasattr(descriptors, "detach"):
        descriptors = descriptors.detach().cpu().numpy()
    return np.asarray(descriptors, dtype=np.uint8)

def features_exist(image_id):
    db = connect()
    try:
        keypoints = db.read_keypoints(image_id)
        descriptors = db.read_descriptors(image_id)

        return len(keypoints) > 0 and len(descriptors.data) > 0
    finally:
        db.close()

def camera_exists(camera_id):
    db = connect()
    try:
        return db.exists_camera(camera_id)
    finally:
        db.close()

def num_images_in_database():
    db = connect()
    num = db.num_images()
    db.close()
    return num

def write_matches(image_id_1, image_id_2, matches):
    # print("Writing matches:", image_id_1, "with", image_id_2, ",", len(matches), "matches.")
    db = connect()
    db.write_matches(
        image_id_1,
        image_id_2,
        matches
    )
    db.close()

def write_two_view_geometry(image_id_1, image_id_2, matches, F):
    geometry = pycolmap.TwoViewGeometry()
    geometry.F = F.astype(np.float64)
    geometry.inlier_matches = matches.astype(np.uint32)
    geometry.config = 2
    db = connect()
    db.write_two_view_geometry(image_id1=image_id_1, image_id2=image_id_2, two_view_geometry=geometry)