using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace GaussianViewer{
    public class ImageGrabber : MonoBehaviour {

        [SerializeField] private Camera Cam;
        public int FileCounter = 0;
        private string uniqueRootPath;


        public void InitGrabber()
        {
            RenderTexture rt = new RenderTexture(1920, 1080, 24, RenderTextureFormat.ARGB32);
            rt.Create();

            Cam.targetTexture = rt;

            //Build unique id from date and time:
            var uniqueString = System.DateTime.Now.ToString("yyyyMMdd_HHmmss");
            uniqueRootPath = Application.dataPath + "/../eval/" + uniqueString + "/";
            Debug.Log(uniqueRootPath);
            //Generate folders:
            Directory.CreateDirectory(uniqueRootPath);
            Directory.CreateDirectory(uniqueRootPath + "real/");
            Directory.CreateDirectory(uniqueRootPath + "splat/");
        }

        public void CamCapture(int index)
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

            File.WriteAllBytes(uniqueRootPath + "splat/" + CameraManager.image_ids[index], Bytes);
        }
        public void SaveImageFromInputData(int index)
        {
            var rootPath = Application.dataPath;
            if (Application.platform == RuntimePlatform.OSXPlayer) {
                rootPath += "/../../";
            }
            else if (Application.platform == RuntimePlatform.WindowsPlayer) {
                rootPath += "/../";
            }
            var imgName = CameraManager.image_ids[index];
            Debug.Log(rootPath + "images/");
            
            var destPath = uniqueRootPath + "real/" + imgName;
            File.Copy(rootPath+"images/"+imgName, destPath, true);
        }
    }
}