using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using GaussianViewer;
using Unity.VisualScripting;
using UnityEngine;

public class AlignPoints : MonoBehaviour
{
    [SerializeField] private CameraManager cameraManagerA;
    [SerializeField] private CameraManager cameraManagerB;
    [SerializeField] private Kabsch kabschSolver;
    public Transform[] transformSetA;
    public Transform[] transformSetB;
    // Start is called before the first frame update
    public void StartAlignmentProcess()
    {
        Debug.Log("Arrays: "+ cameraManagerA.cameras.Count + ", " + cameraManagerB.cameras.Count);

        var camerasA = cameraManagerA.cameras;
        var camerasB = cameraManagerB.cameras;

        // Dictionary für schnellen Zugriff auf B
        var dictB = camerasB.ToDictionary(cam => GetFrameNumber(cam.name));

        var alignedA = new List<GameObject>();
        var alignedB = new List<GameObject>();

        foreach (var camA in camerasA)
        {
            int frame = GetFrameNumber(camA.name);

            if (dictB.TryGetValue(frame, out var camB))
            {
                alignedA.Add(camA);
                alignedB.Add(camB);
            }
        }

        // 🔽 Optional: sauber nach Frame sortieren
        var sorted = alignedA
            .Select((camA, i) => new
            {
                A = camA,
                B = alignedB[i],
                Frame = GetFrameNumber(camA.name)
            })
            .OrderBy(x => x.Frame)
            .ToList();

        camerasA = sorted.Select(x => x.A).ToList();
        camerasB = sorted.Select(x => x.B).ToList();

        Debug.Log("Matched pairs: " + camerasA.Count);

        // Transform Arrays bauen
        transformSetA = camerasA.Select(cam => cam.transform).ToArray();
        transformSetB = camerasB.Select(cam => cam.transform).ToArray();

        // Kabsch
        kabschSolver.inPoints = transformSetB;
        kabschSolver.referencePoints = transformSetA;

        var kabschTransform = kabschSolver.Init();

        Debug.Log(kabschTransform);

        Vector3 worldPos = kabschTransform.GetColumn(3);
        Quaternion worldRot = kabschTransform.rotation;
        cameraManagerB.transform.SetPositionAndRotation(worldPos, worldRot);
    }

    private int GetFrameNumber(string name)
    {
        var file = Path.GetFileNameWithoutExtension(name);
        var numberPart = file.Split('_').Last();
        return int.TryParse(numberPart, out var num) ? num : -1;
    }
}
