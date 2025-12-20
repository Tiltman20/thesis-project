import cv2
import os
import glob
import progressbar

def resize(root_folder, image, scale, count, filename):
    if image is None:
        return

    h, w = image.shape[:2]
    img_small = cv2.resize(image, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(root_folder + "\\scaled", f"{filename}.jpg"), img_small)

def scale_images(root_folder, scale_factor):
    os.makedirs(root_folder + "\\scaled", exist_ok=True)
    count = 0
    images = glob.glob(f"{root_folder}\\*.JPG")
    for i in progressbar.progressbar(images, prefix="Scaling Images:"):
        name = os.path.splitext(os.path.basename(i))[0]
        resize(root_folder, cv2.imread(i), scale_factor, count, name)
        count += 1
