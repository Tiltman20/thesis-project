import cv2
import os
import progressbar as progressbar


def export_images(video_path, image_path, max_images = 200):
  if not os.path.exists(image_path):
    os.makedirs(image_path)
  vidcap = cv2.VideoCapture(video_path)
  success,image = vidcap.read()
  frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
  steps = frame_count//max_images
  actual_count = 0

  for i in progressbar.progressbar(range(frame_count), 0, frame_count, prefix="Exporting Images:"):
    if actual_count % steps == 0:
      img_small = cv2.resize(image, (960, 540), interpolation=cv2.INTER_AREA)
      cv2.imwrite(image_path + "/frame_%s.jpg" % actual_count, img_small)
    actual_count+=1
    success,image = vidcap.read()
    if not success:
      break