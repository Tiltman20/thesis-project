import cv2
from skimage import data, img_as_float
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import lpips
import os
import csv
import numpy as np
import torch
import matplotlib.pyplot as plt

def main():
    print("Starting evaluation...")
    #Load images from latest folder in eval/real and eval/synthetic:
    print("CWD:", os.getcwd())
    eval_folders = os.listdir("eval")
    real_images = os.listdir("eval/" + eval_folders[-1] + "/real")
    splat_images = os.listdir("eval/" + eval_folders[-1] + "/splat")
    if len(real_images) != len(splat_images):
        return
    
    loss_fn_alex = lpips.LPIPS(net='alex')
    ssim_results = []
    psnr_results = []
    lpips_results = []
    for i in range(len(real_images)):
        real_image = cv2.imread("eval/" + eval_folders[-1] + "/real/" + real_images[i])
        splat_image = cv2.imread("eval/" + eval_folders[-1] + "/splat/" + splat_images[i])
        splat_image = cv2.resize(splat_image, (real_image.shape[1], real_image.shape[0]))
        real_tensor = torch.from_numpy(real_image).permute(2,0,1).unsqueeze(0).float() / 255.0 * 2 - 1
        splat_tensor = torch.from_numpy(splat_image).permute(2,0,1).unsqueeze(0).float() / 255.0 * 2 - 1
        ssim_value = ssim(real_image, splat_image, multichannel=True, channel_axis=2)
        psnr_value = psnr(real_image, splat_image, data_range=255)
        lpips_value = loss_fn_alex(real_tensor, splat_tensor)
        ssim_results.append([real_images[i], splat_images[i], ssim_value])
        psnr_results.append([real_images[i], splat_images[i], psnr_value])
        lpips_results.append([real_images[i], splat_images[i], lpips_value.item()])
        

    save_results(ssim_results, f"eval/{eval_folders[-1]}/ssim_results.csv", "SSIM")
    save_results(psnr_results, f"eval/{eval_folders[-1]}/psnr_results.csv", "PSNR")
    save_results(lpips_results, f"eval/{eval_folders[-1]}/lpips_results.csv", "LPIPS")

    plot_results(
        ssim_results,
        psnr_results,
        lpips_results
    )


def save_results(results, path, type):
    with open(path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Real", "Splat", type])
        for result in results:
            writer.writerow(result)

def plot_results(ssim_results, psnr_results, lpips_results):
    fig1 = plot_result(ssim_results, "SSIM", "SSIM Value", 0)
    fig2 = plot_result(psnr_results, "PSNR", "PSNR Value", 1)
    fig3 = plot_result(lpips_results, "LPIPS", "LPIPS Value", 2)
    plt.show()

def plot_result(result, title, ylabel, idx):
    figure = plt.figure(idx)
    values = [r[2] for r in result]
    names = [r[0] for r in result]
    plt.scatter(range(len(values)), values, label=title, marker="o")
    for i, name in enumerate(names):
        plt.annotate(name, (i, values[i]), textcoords="offset points", xytext=(0,10), ha='center')
    plt.legend()
    plt.title("Evaluation Metrics " + title)
    plt.xlabel("Image Index")
    plt.ylabel(ylabel)
    return figure

if __name__ == "__main__":
    main()