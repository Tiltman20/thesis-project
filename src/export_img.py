import cv2
import progressbar as progressbar


def export_images(video_path, image_path):
  vidcap = cv2.VideoCapture(video_path)
  success,image = vidcap.read()
  frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
  max_images = 200
  steps = frame_count//max_images
  actual_count = 0

  for i in progressbar.progressbar(range(frame_count), 0, frame_count, prefix="Exporting Images:"):
    if actual_count % steps == 0:
      cv2.imwrite(image_path + "/frame_%s.jpg" % actual_count, image)     # save frame as JPEG file 
    actual_count+=1
    success,image = vidcap.read()
    if not success:
      break