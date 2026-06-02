using System.Collections;
using System.Collections.Generic;
using System.Linq;
using GaussianViewer;
using UnityEngine;

public class EvaluationManager : MonoBehaviour
{
    // [SerializeField] private GameObject[] cameraVisParents;
    [SerializeField] private CameraManager[] camManagers;
    [SerializeField] private GameObject infoCanvas; 
    [SerializeField] private GameObject setupCanvas;
    [SerializeField] private int sampleSize = 10;
    [SerializeField] private PositionController positionController;
    [SerializeField] private ImageGrabber imageGrabber;
    [SerializeField] private string batchFileName = "run_evaluation.bat";
    [SerializeField] private TMPro.TextMeshProUGUI debugText;
    private CameraManager CameraManager => positionController.currentCameraManager;
    private readonly List<string> evaluationImageIds = new();

    public void Evaluate()
    {
        foreach(var p in camManagers)
        {
            foreach(var c in p.cameras)
            {
                c.SetActive(false);
            }
        }
        
        infoCanvas.SetActive(false);
        setupCanvas.SetActive(false);
        imageGrabber.InitGrabber();
        BuildEvaluationImageList();
        StartCoroutine(EvaluationController());
    }

    IEnumerator EvaluationController()
    {
        foreach(var m in camManagers)
        {
            m.gameObject.SetActive(false);
        }
        camManagers[0].gameObject.SetActive(true);
        yield return StartCoroutine(StartEvaluation(CameraManager.extractionMethod));
        positionController.cameraManagerIndex++;
        camManagers[1].gameObject.SetActive(true);
        yield return StartCoroutine(StartEvaluation(CameraManager.extractionMethod));
        yield return null;
    }

    IEnumerator StartEvaluation(string method)
    {
        Debug.Log(CameraManager.extractionMethod);
        foreach (var imageId in evaluationImageIds)
        {
            StartCoroutine(ProcessStep(imageId, method));
            yield return null;
        }

        Debug.Log("Finished Evaluation");
        // StartPythonEvaluation();
    }

    IEnumerator ProcessStep(string imageId, string method)
    {
        int index = CameraManager.image_ids.IndexOf(imageId);
        if (index == -1)
        {
            Debug.LogWarning("Skipping evaluation image because it is missing in " + method + ": " + imageId);
            yield break;
        }

        // Save Actual Image:
        imageGrabber.SaveImageFromInputData(imageId);

        // Save Camera Image:
        positionController.JumpToCamera(index);
        imageGrabber.CamCapture(index, method);
        yield return null;
    }

    IEnumerator StartPythonEvaluation()
    {
        //Start venv and run script
        System.Diagnostics.Process.Start("CMD.exe",  batchFileName);
        yield return null;
    }

    private void BuildEvaluationImageList()
    {
        evaluationImageIds.Clear();
        if (camManagers.Length == 0)
        {
            return;
        }

        var sharedImageIds = camManagers[0].image_ids
            .Where(imageId => camManagers.All(manager => manager.image_ids.Contains(imageId)))
            .Distinct()
            .ToList();

        if (sharedImageIds.Count == 0)
        {
            Debug.LogWarning("No shared image ids found for evaluation.");
            return;
        }

        int targetCount = Mathf.Min(sampleSize, sharedImageIds.Count);
        float step = (float)sharedImageIds.Count / targetCount;
        for (int i = 0; i < targetCount; i++)
        {
            int sampleIndex = Mathf.Min(Mathf.FloorToInt(i * step), sharedImageIds.Count - 1);
            evaluationImageIds.Add(sharedImageIds[sampleIndex]);
        }

        Debug.Log("Prepared " + evaluationImageIds.Count + " shared evaluation images.");
    }
}
