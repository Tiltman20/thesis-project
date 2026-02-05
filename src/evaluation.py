import cv2
from skimage import data, img_as_float
from skimage.metrics import structural_similarity as ssim
import os

def main():
    print("Starting evaluation...")
    #Load images from latest folder in eval/real and eval/synthetic:
    real_images = os.listdir("eval/real")
    synthetic_images = os.listdir("eval/synthetic")
    print("Real images:", real_images)
    # images = os.listdir("images")
    # for image in images:
    #     print(image)

if __name__ == "__main__":
    main()