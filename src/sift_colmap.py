import subprocess
from pathlib import Path
from libs.colmap.database import COLMAPDatabase as Database
IMAGE_PATH = ""
DATABASE_PATH = ""
COLMAP_APP_ROOT = r"C:\Users\tilma\Documents\GitHub\bachelor-thesis\research\COLMAP\COLMAP.bat"
OUTPUT_PATH = ""
ROOT_PATH = ""

def run_colmap_with_sift():
    img_path = fr"{ROOT_PATH}\{IMAGE_PATH}"
    db_path = fr"{ROOT_PATH}\{DATABASE_PATH}\database.db"
    print(db_path)
    result = subprocess.run(
        [COLMAP_APP_ROOT, "feature_extractor", f"--image_path", img_path, f"--database_path", db_path, "--ImageReader.camera_model", "PINHOLE"],
        capture_output=True,
        text=True
    )
    print(result.stderr)
    print(result.stdout)
    subprocess.run(
        [COLMAP_APP_ROOT, "exhaustive_matcher", "--database_path", db_path]
    )
    subprocess.run(
        [COLMAP_APP_ROOT, "mapper", "--image_path", img_path, "--database_path", db_path, "--output_path", fr"{ROOT_PATH}\{OUTPUT_PATH}"]
    )

def build_db(path_to_db):
    path_to_db = path_to_db / "database.db"
    if path_to_db.exists():
        path_to_db.unlink()
    db = Database(str(path_to_db))
    db.create_tables()

def run(root_path, image_path, database_path, output_path):
    global ROOT_PATH, IMAGE_PATH, DATABASE_PATH, OUTPUT_PATH
    ROOT_PATH = root_path
    IMAGE_PATH = image_path
    DATABASE_PATH = database_path
    OUTPUT_PATH = output_path
    build_db(Path(database_path))
    run_colmap_with_sift()