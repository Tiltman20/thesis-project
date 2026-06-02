using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace GaussianViewer{
    public class ImageGrabber : MonoBehaviour {

        [SerializeField] private Camera Cam;
        [SerializeField] private PositionController positionController;
        public int FileCounter = 0;
        private string uniqueRootPath;
        private readonly HashSet<string> savedRealImages = new();
        CameraManager CameraManager => positionController.currentCameraManager;


        public void InitGrabber()
        {
            RenderTexture rt = new RenderTexture(1920, 1080, 24, RenderTextureFormat.ARGB32);
            rt.Create();

            Cam.targetTexture = rt;

            //Build unique id from date and time:
            var uniqueString = System.DateTime.Now.ToString("yyyyMMdd_HHmmss");
            uniqueRootPath = Application.dataPath + "/../eval/" + uniqueString + "/";
            // Debug.Log(uniqueRootPath);
            //Generate folders:
            Directory.CreateDirectory(uniqueRootPath);
            Directory.CreateDirectory(uniqueRootPath + "real/");
            Directory.CreateDirectory(uniqueRootPath + "sift/");
            Directory.CreateDirectory(uniqueRootPath + "xfeat/");
            savedRealImages.Clear();
        }

        public void CamCapture(int index, string method)
        {
            RenderTexture currentRT = RenderTexture.active;
            RenderTexture.active = Cam.targetTexture;

            Cam.Render();

            Texture2D Image = new Texture2D(Cam.targetTexture.width, Cam.targetTexture.height);
            Image.ReadPixels(new Rect(0, 0, Cam.targetTexture.width, Cam.targetTexture.height), 0, 0);
            Image.Apply();
            RenderTexture.active = currentRT;

            var Bytes = Image.EncodeToPNG();
            Destroy(Image);

            Debug.Log(uniqueRootPath + method + "/" + CameraManager.image_ids[index]);

            File.WriteAllBytes(uniqueRootPath + method + "/" + CameraManager.image_ids[index], Bytes);
        }
        public void SaveImageFromInputData(int index)
        {
            SaveImageFromInputData(CameraManager.image_ids[index]);
        }

        public void SaveImageFromInputData(string imgName)
        {
            var rootPath = Application.dataPath;
            if (Application.platform == RuntimePlatform.OSXPlayer) {
                rootPath += "/../../";
            }
            else if (Application.platform == RuntimePlatform.WindowsPlayer) {
                rootPath += "/../";
            }

            var destPath = uniqueRootPath + "real/" + imgName;
            if (savedRealImages.Contains(imgName) && File.Exists(destPath))
            {
                return;
            }

            var sourcePath = Path.Combine(rootPath, "images", imgName);
            if (!File.Exists(sourcePath))
            {
                Debug.LogWarning("Could not find input image for evaluation: " + sourcePath);
                return;
            }

            File.Copy(sourcePath, destPath, true);
            savedRealImages.Add(imgName);
        }
    }
}
