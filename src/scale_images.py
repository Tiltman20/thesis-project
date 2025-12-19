import cv2
import os
import glob

root_folder = "res\\images\\test-room-04"

os.makedirs(root_folder + "\\scaled", exist_ok=True)

def resize(image, scale, count, filename):
    if image is None:
        return

    h, w = image.shape[:2]
    img_small = cv2.resize(image, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(root_folder + "\\scaled", f"{filename}.jpg"), img_small)
  # print(os.path.join(output_folder, f"{str(count)}.jpg"))


def main():
    count = 0
    images = glob.glob(f"{root_folder}\\*.JPG")
    for i in images:
        name = os.path.splitext(os.path.basename(i))[0]
        resize(cv2.imread(i), 0.5, count, name)
        count += 1

main()
print("done")