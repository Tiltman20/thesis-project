using System.Collections;
using System.Collections.Generic;
using System.IO;
using GaussianSplatting;
using GaussianSplatting.Runtime;
using TMPro;
using UnityEngine;

public class GaussianLoader : MonoBehaviour
{
    [SerializeField] private List<GaussianSplatRenderer> gaussianSpatRenderers;
    [SerializeField] private TextMeshProUGUI versionText;

    private List<string> filenames = new();
    // Start is called before the first frame update
    void Start()
    {
        int i = 0;
        foreach (var gaussianSpatRenderer in gaussianSpatRenderers) {
            LoadAsset(gaussianSpatRenderer, i);
            i++;
        }
        foreach (var filename in filenames)
        {
            versionText.text += filename + "\n";
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
        Debug.Log(rootPath);
        string[] files = Directory.GetFiles(rootPath, "*.ply");
        filenames.Add(files[0]);
        filenames.Add(files[1]);
        GaussianSplatRuntimeAssetCreator creator = new GaussianSplatRuntimeAssetCreator();
        var asset = creator.CreateAsset("test", files[index]);
        gaussianSpatRenderer.InjectAsset(asset);
    }
}
