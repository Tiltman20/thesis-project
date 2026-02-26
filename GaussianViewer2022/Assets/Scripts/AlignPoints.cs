using System.Collections;
using System.Collections.Generic;
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
        GameObject[] camerasA = cameraManagerA.cameras.ToArray();
        GameObject[] camerasB = cameraManagerB.cameras.ToArray();

        camerasA = camerasA.OrderBy(cam => cam.name).ToArray();
        camerasB = camerasB.OrderBy(cam => cam.name).ToArray();

        transformSetA = new Transform[camerasA.Length];
        transformSetB = new Transform[camerasB.Length];

        for (int i = 0; i < transformSetA.Length; i++)
        {
            transformSetA[i] = camerasA[i].transform;
            transformSetB[i] = camerasB[i].transform;
            Debug.Log(camerasA[i].name == camerasB[i].name);
            
        }
        kabschSolver.inPoints = transformSetB;
        kabschSolver.referencePoints = transformSetA;
        var kabschTransform = kabschSolver.Init();

        Debug.Log(kabschTransform);

        Vector3 worldPos = kabschTransform.GetColumn(3);
        Quaternion worldRot = kabschTransform.rotation;
        cameraManagerB.transform.SetPositionAndRotation(worldPos, worldRot);

        // for (int i = 0; i < cameraManagerA.cameras.Count; i++)
        // {
        //     cameraManagerA.cameras[i].transform.position = kabschSolver.kabschTransform.MultiplyPoint3x4(kabschSolver.points[i]);
        // }
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
