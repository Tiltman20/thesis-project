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
        // rotationSliders[0].onValueChanged += OnSliderChanged(new Vector3(rotationSliders[0].value, 0, 0));
        // rotationSliders[1].onValueChanged += OnSliderChanged(new Vector3(0, rotationSliders[1].value, 0));
        // rotationSliders[2].onValueChanged += OnSliderChanged(new Vector3(0, 0, rotationSliders[2].value));
        rotationSliders[0].onValueChanged.AddListener(value =>
        {
            OnSliderChanged(new Vector3(value, rotationSliders[1].value, rotationSliders[2].value));
        });
        rotationSliders[1].onValueChanged.AddListener(value =>
        {
            OnSliderChanged(new Vector3(rotationSliders[0].value, value, rotationSliders[2].value));
        });
        rotationSliders[2].onValueChanged.AddListener(value =>
        {
            OnSliderChanged(new Vector3(rotationSliders[0].value, rotationSliders[1].value, value));
        });
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
