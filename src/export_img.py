import cv2
vidcap = cv2.VideoCapture('res/videos/Rittmeier/test_1.MOV')
success,image = vidcap.read()
frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
print(frame_count)
max_images = 1000
steps = frame_count//max_images
# steps = 1

# print(frame_count, steps, max_images)

actual_count = 0

while success:
  if actual_count % steps == 0:
     cv2.imwrite("res/images/Rittmeier/test_1/frame_%s.jpg" % actual_count, image)     # save frame as JPEG file 
   #   print("img%d saved" % actual_count)
  actual_count+=1
  success,image = vidcap.read()
print("done")
