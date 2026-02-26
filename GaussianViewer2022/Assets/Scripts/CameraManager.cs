using System.Collections.Generic;
using UnityEngine;
using System.Collections;
using System;

namespace GaussianViewer{
    public class CameraManager : MonoBehaviour
    {
        [SerializeField] private GameObject cameraVisualiserPrefab;
        [SerializeField] private BinaryImageParserNew parser;
        [SerializeField] private GameObject cameraParent;
        [SerializeField] private GameObject cameraObject;
        [SerializeField] private PositionController positionController;
        [SerializeField] private Camera unityCamera;
        [SerializeField] private string BinaryPath;
        public List<Vector3> positions;
        public List<Quaternion> rotations;
        public List<GameObject> cameras;
        public List<String> image_ids;
        public List<BinaryImageParserNew.CameraPose> camPoses;
        // Start is called once before the first execution of Update after the MonoBehaviour is created
        void Start()
        {
            // Debug.Log(SystemInfo.graphicsDeviceType);
            parser.pathToBinary = BinaryPath;
            camPoses = parser.Parse();
            var camParams = parser.ParseCameras();
            var fovY = parser.calculateFOV(camParams[0]);
            
            positions = new List<Vector3>();
            rotations = new List<Quaternion>();
            image_ids = new List<string>();
            cameras = new List<GameObject>();

            StartCoroutine(DrawCameras());
        }

        IEnumerator DrawCameras()
        {
            Debug.Log(string.Format("Loading {0} camera poses...", camPoses.Count));

            Transform parent = cameraParent.transform;
            foreach(var pose in camPoses)
            {
                var visualiser = Instantiate(cameraVisualiserPrefab);

                visualiser.transform.SetParent(parent);
                visualiser.transform.localPosition = pose.PositionWorld;
                visualiser.transform.rotation = pose.Rotation;
                visualiser.name = pose.ImageName;
                visualiser.GetComponent<CameraVisualiser>().target = cameraObject;
                visualiser.GetComponent<CameraVisualiser>().imageName.text = pose.ImageName;
                image_ids.Add(pose.ImageName);
                cameras.Add(visualiser);
            }
            parent.localScale = new Vector3(1, -1, 1);
            yield return null;
        }   
        void ApplyColmapIntrinsics(float fovY)
        {
            unityCamera.fieldOfView = fovY;
            unityCamera.usePhysicalProperties = false;
        }
        
    }
}
