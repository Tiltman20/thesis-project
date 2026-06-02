using System.Collections;
using System.Collections.Generic;
using System.IO;
using GaussianSplatting;
using GaussianSplatting.Runtime;
using GaussianViewer;
using TMPro;
using UnityEngine;

public class GaussianLoader : MonoBehaviour
{
    [SerializeField] private List<GaussianSplatRenderer> gaussianSpatRenderers;
    [SerializeField] private TextMeshProUGUI versionText;
    [SerializeField] private PositionController posC;
    [SerializeField] private CameraManager[] cameraManagers;

    private List<string> filenames = new();
    // Start is called before the first frame update
    void Start()
    {
        int i = 0;
        foreach (var gaussianSpatRenderer in gaussianSpatRenderers) {
            LoadAsset(gaussianSpatRenderer, i);
            i++;
        }
    }
    private void LoadAsset(GaussianSplatRenderer gaussianSpatRenderer, int index)
    {
        var rootPath = Application.dataPath;
        if (Application.platform == RuntimePlatform.OSXPlayer) {
            rootPath += "/../../";
        }
        else if (Application.platform == RuntimePlatform.WindowsPlayer) {
            rootPath += "/../";
        }
        // Debug.Log("Root Path: " + rootPath);
        string[] files = Directory.GetFiles(rootPath, "*.ply");
        // Debug.Log("Files:\n"+ files[0] + "\n" + files[1]);
        filenames.Add(files[0]);
        filenames.Add(files[1]);
        if(files[0].Contains("sift")) posC.siftIndex = 0;
        else posC.siftIndex = 1;
        GaussianSplatRuntimeAssetCreator creator = new GaussianSplatRuntimeAssetCreator();
        var asset = creator.CreateAsset("test", files[index]);
        gaussianSpatRenderer.InjectAsset(asset);
        cameraManagers[posC.siftIndex].extractionMethod = "sift";
        cameraManagers[(posC.siftIndex+1)%2].extractionMethod = "xfeat";
    }
}
