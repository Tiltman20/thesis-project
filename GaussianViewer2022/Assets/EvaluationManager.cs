using System.Collections.Generic;
using GaussianViewer;
using UnityEngine;

public class EvaluationManager : MonoBehaviour
{
    [SerializeField] private GameObject cameraVisParent;
    [SerializeField] private GameObject infoCanvas; 
    [SerializeField] private GameObject setupCanvas;
    [SerializeField] private int sampleSize = 10;
    [SerializeField] private PositionController positionController;
    [SerializeField] private ImageGrabber imageGrabber;
    [SerializeField] private string batchFileName = "run_evaluation.bat";
    [SerializeField] private TMPro.TextMeshProUGUI debugText;
    private CameraManager CameraManager => positionController.currentCameraManager;

    public void StartEvaluation()
    {
        cameraVisParent.SetActive(false);
        foreach (var c in CameraManager.cameras)
        {
            c.SetActive(false);
        }
        infoCanvas.SetActive(false);
        setupCanvas.SetActive(false);
        imageGrabber.InitGrabber();
        int stepsize = Mathf.FloorToInt(CameraManager.camPoses.Count / sampleSize);
        for (int i = 0; i < CameraManager.camPoses.Count; i+=stepsize)
        {
            ProcessStep(i);
        }
        StartPythonEvaluation();
    }

    private void ProcessStep(int index)
    {
        // Save Actual Image:
        imageGrabber.SaveImageFromInputData(index);

        // Save Camera Image:
        positionController.JumpToCamera(index);
        imageGrabber.CamCapture(index);

    }

    private void StartPythonEvaluation()
    {
        //Start venv and run script
        System.Diagnostics.Process.Start("CMD.exe",  batchFileName);
    }
}
