<h1 style="text-align:center;">Gaussian Splatting in Construction Sites</h1>
<h4 style="text-align:center;">A comparison of different approaches to feature extraction and matching in structure from motion</h4>

This repository is the actual implementation and supporting material of my bachelor thesis. The topic is the improvement of COLMAPS approach to structure from motion by changing the feature extraction and matching to a more novel and modern approach using XFeat (https://github.com/verlab/accelerated_features) instead of SIFT.
For installation run ```pip install -r requirements.txt```, install COLMAP (https://colmap.github.io) and Gaussian Splatting by INRIA (https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/).
The .bat - files are not fully functional as of now, however, the Python-file ```execute-pipeline.py``` utilising the following arguments:
```
--noimport: do not convert the source video to images
--noscale: do not scale the extracted images
--sift: use SIFT for COLMAP
--norender: Do not render the Gaussian Splattings afterwards
-s <path>: Base path for project
--top_k <amount>: Set the top_k features to be utilised for feature matching
```


<h1 style="text-align:center;">Gaussian Viewer</h1>
The Gaussian Viewer is a Unity Viewer based on UnityGaussianSplatting (https://github.com/aras-p/UnityGaussianSplatting) and runs in Unity 2022.3.47f1 and can be used with the following instructions after building the project in Unity:

### Change gaussian splattings

Files to change:
- point_cloud.ply from XFeat as point_cloud-xfeat
- point_cloud.ply from SIFT as point_cloud-sift
- copy images from used dataset in "images" folder
- copy cameras.bin & images.bin from colmap results from respective approach (XFeat or SIFT) in sift/xfeat-data
Start application


### Running the application
- Start the GaussianViewer2022.exe file
- Manual Inspection:
	- Press "Align Cameras"
	- Press "Finish Setup"
- Automatic Evaluation:
	- Press "Start Evaluation"
- Controls:
	- WASD for basic movement
	- Q/E for rotation adjustments along Z-axis
	- Space: jump to next camera in track
	- LShift: Jump to previous camera
	- P: find nearest camera position
	- G: Show input image
	- Tab: hide UI
	- I: switch gaussian splatting, keep camera
	- J: switch gaussian splatting, keep position


Please bear in mind, that this viewer is only a tool for the evaluation of the changes made to COLMAPs pipeline and thus is only supportive material which is not fully implemented for easy use.
