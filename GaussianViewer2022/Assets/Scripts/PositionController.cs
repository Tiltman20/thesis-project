using TMPro;
using UnityEngine;
using System.IO;

namespace GaussianViewer{
    public class PositionController : MonoBehaviour
    {
        [SerializeField] private TextMeshProUGUI imageInfo;
        [SerializeField] private float sensitivity;
        [SerializeField] private UnityEngine.UI.Image actualImageUI;
        private int index = 0;
        public bool imageShown = false;
        public bool lockMovement;
        public void Init()
        {
            var camTransform = CameraManager.cameras[index].transform;
            gameObject.transform.position = camTransform.position;
            gameObject.transform.rotation = camTransform.rotation;
            imageInfo.text = CameraManager.image_ids[index] + " \nRotation: " + gameObject.transform.rotation;
        }

        // Update is called once per frame
        void Update()
        {
            if(lockMovement) return;
            if (Input.GetButtonDown("Jump"))
            {
                IterateCamera(1);
            }
            if (Input.GetKeyDown(KeyCode.LeftShift))
            {
                IterateCamera(-1);
            }
            if (Input.GetKeyDown(KeyCode.P))
            {
                index = LocateClosestLocation();
                gameObject.transform.position = CameraManager.cameras[index].transform.position;
                gameObject.transform.rotation = CameraManager.cameras[index].transform.rotation;
            }
            if (Input.GetKeyDown(KeyCode.G))
            {
                if (!imageShown)
                {
                    var rootPath = Application.dataPath;
                    if (Application.platform == RuntimePlatform.OSXPlayer) {
                        rootPath += "/../../";
                    }
                    else if (Application.platform == RuntimePlatform.WindowsPlayer) {
                        rootPath += "/../";
                    }
                    string[] files = Directory.GetFiles(rootPath, "images/" + CameraManager.image_ids[index] );
                    var sprite = loadImage(files[0]);
                    actualImageUI.sprite = sprite;
                    actualImageUI.color = new Color(1,1,1,1);
                    imageShown = true;
                }
                else
                {
                    imageShown = false;
                    actualImageUI.color = new Color(1,1,1,0);
                }
            }

            var forwardMovement = Input.GetAxis("Vertical") * gameObject.transform.forward;
            var sidewaysMovement = Input.GetAxis("Horizontal") * gameObject.transform.right;
            gameObject.transform.position += (forwardMovement + sidewaysMovement) * Time.deltaTime;

            float rotateHorizontal = Input.GetAxis("Mouse X");
            float rotateVertical = Input.GetAxis("Mouse Y");
            float rotateForward = Input.GetAxis("Rotation");
            transform.RotateAround(transform.position, transform.up, rotateHorizontal * sensitivity);
            transform.RotateAround(transform.position, transform.right, -rotateVertical * sensitivity);
            transform.RotateAround(transform.position, transform.forward, rotateForward * sensitivity/10);
        }

        void IterateCamera(int direction)
        {
            index += direction;
            index %= CameraManager.cameras.Count;
            var camTransform = CameraManager.cameras[index].transform;
            gameObject.transform.position = camTransform.position;
            gameObject.transform.rotation = camTransform.rotation;
            imageInfo.text = CameraManager.image_ids[index] + " \nRotation: " + gameObject.transform.rotation;
        }

        public void JumpToCamera(int index)
        {
            if (index < 0 || index >= CameraManager.cameras.Count) return;
            this.index = index;
            var camTransform = CameraManager.cameras[index].transform;
            gameObject.transform.position = camTransform.position;
            gameObject.transform.rotation = camTransform.rotation;
            imageInfo.text = CameraManager.image_ids[index] + " \nRotation: " + gameObject.transform.rotation;
        }

        int LocateClosestLocation()
        {
            int indexOfClosestLocation = 0;
            float distance = float.MaxValue;

            for(int i = 0; i<CameraManager.cameras.Count; i++)
            {
                var tmpDistance = Vector3.Distance(CameraManager.cameras[i].transform.position, transform.position);
                if (tmpDistance < distance)
                {
                    distance = tmpDistance;
                    indexOfClosestLocation = i;
                } 
            }

            return indexOfClosestLocation;
        }
        Sprite loadImage(string imgName)
        {
            byte[] imageData = File.ReadAllBytes(imgName);

            Texture2D texture = new Texture2D(2, 2);
            texture.LoadImage(imageData);

            Sprite sprite = Sprite.Create(
                texture,
                new Rect(0, 0, texture.width, texture.height),
                new Vector2(0.5f, 0.5f)
            );

            return sprite;
        }
    }
}