using GaussianViewer;
using UnityEngine;

public class UIManager : MonoBehaviour
{
    [SerializeField] private PositionController positionController;
    [SerializeField] private GameObject[] canvases;
    [SerializeField] private CameraManager currentCameraManager => positionController.currentCameraManager;

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Tab))
        {
            foreach (var c in canvases)
            {
                c.SetActive(!c.activeSelf);
            }
            foreach (var c in currentCameraManager.cameras)
            {
                c.SetActive(!c.activeSelf);
            }
        }
    }
}
