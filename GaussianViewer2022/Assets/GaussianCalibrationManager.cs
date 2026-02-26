using System.Collections;
using System.Collections.Generic;
using GaussianViewer;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class GaussianCalibrationManager : MonoBehaviour
{
    [SerializeField] private GameObject gaussianRenderer;
    [SerializeField] private List<TextMeshProUGUI> rotationValues;
    [SerializeField] private List<Slider> rotationSliders;
    [SerializeField] private PositionController positionController;
    // Start is called before the first frame update
    void Start()
    {
        positionController.lockMovement = true;
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void OnSliderChanged(Vector3 rotation)
    {
        var newRot = new Quaternion();
        newRot.eulerAngles = rotation;
        gaussianRenderer.transform.rotation = newRot;
        rotationValues[0].text = "" + newRot.x;
        rotationValues[1].text = "" + newRot.y;
        rotationValues[2].text = "" + newRot.z;
    }

    public void FinishSetup()
    {
        positionController.lockMovement = false;
        gameObject.SetActive(false);
    }
}
