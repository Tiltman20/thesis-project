using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class CameraVisualiser : MonoBehaviour
{
    public TextMeshProUGUI imageName;
    public GameObject target;
    [SerializeField]private Canvas imageNameCanvas;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (target != null)
        {
            gameObject.transform.LookAt(target.transform.position - gameObject.transform.position);
        }
    }
}
