using System.Collections;
using System.Collections.Generic;
using System.IO;
using GaussianSplatting;
using GaussianSplatting.Runtime;
using UnityEngine;

public class GaussianLoader : MonoBehaviour
{
    [SerializeField] private GaussianSplatRenderer gaussianSpatRenderer;
    // Start is called before the first frame update
    void Start()
    {
        LoadAsset();
    }
    private void LoadAsset()
    {
        var rootPath = Application.dataPath;
        if (Application.platform == RuntimePlatform.OSXPlayer) {
            rootPath += "/../../";
        }
        else if (Application.platform == RuntimePlatform.WindowsPlayer) {
            rootPath += "/../";
        }
        Debug.Log(rootPath);
        string[] files = Directory.GetFiles(rootPath, "*.ply");
        GaussianSplatRuntimeAssetCreator creator = new GaussianSplatRuntimeAssetCreator();
        var asset = creator.CreateAsset("test", files[0]);
        gaussianSpatRenderer.InjectAsset(asset);
    }
}
