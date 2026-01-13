using System.Collections.Generic;
using System.IO;
using System.Linq.Expressions;
using System.Text;
using JetBrains.Annotations;
using UnityEditor;
using UnityEngine;
using System.Numerics;
using System;

namespace GaussianViewer{
    public class BinaryImageParserNew : MonoBehaviour
    {
        [SerializeField]private string pathToImageBinary;
        [SerializeField] private string pathToCameraBinary;
        private string path = "BinaryLog.txt";
        public class CameraPose
        {
            public ulong ImageId {get; set;}
            public string ImageName {get; set;}
            public UnityEngine.Vector3 PositionWorld {get; set;}
            public UnityEngine.Quaternion Rotation{get; set;}
        }

        public class ColmapCamera
        {
            public ulong CameraId {get; set;}
            public int ModelId {get; set;}
            public int Width {get; set;}
            public int Height {get; set;}
            public double[] Params {get; set;}
        }

        public List<CameraPose> Parse()
        {
            var poses = new List<CameraPose>();

            using var fs = new FileStream(pathToImageBinary, FileMode.Open, FileAccess.Read);
            using var br = new BinaryReader(fs);

            ulong numImages = br.ReadUInt64();

            for (ulong i = 0; i<numImages; i++)
            {
                ulong imageId = br.ReadUInt32();

                double qw = br.ReadDouble();
                double qx = br.ReadDouble();
                double qy = br.ReadDouble();
                double qz = br.ReadDouble();


                double tx = br.ReadDouble();
                double ty = br.ReadDouble();
                double tz = br.ReadDouble();

                ulong cameraId = br.ReadUInt32();

                string imageName = ReadNullTerminatedString(br);

                ulong numPoints2D = br.ReadUInt64();

                for (ulong p = 0; p<numPoints2D; p++)
                {
                    br.ReadDouble();
                    br.ReadDouble();
                    br.ReadUInt64();
                }

                var C = ComputeCameraCenter(qw, qx, qy, qz, tx, ty, tz);
                var R = ColmapToUnityRotation(qw, qx, qy, qz);
                var newRotation = new UnityEngine.Quaternion((float)qx, (float)qy, (float)qz, (float)qw);
                UnityEngine.Vector3 UnityVectorC = new UnityEngine.Vector3((float)C.x, (float)C.y, (float)C.z);

                poses.Add(new CameraPose{
                    ImageId = imageId,
                    ImageName = imageName,
                    PositionWorld = UnityVectorC,
                    Rotation = R
                });
                string text = string.Format("Image ID: {0} \nImageName: {8} \nCamera ID:{9} \nRotation: {1}, {2}, {3}, {4} \nPosition: {5}, {6}, {7} \n#############", imageId,qx,qy,qz,qw,tx,ty,tz,imageName,cameraId);
                File.AppendAllText(path, text + Environment.NewLine);
            }

            return poses;
        }

        private string ReadNullTerminatedString(BinaryReader br)
        {
            var bytes = new List<byte>();
            byte b;
            while ((b = br.ReadByte()) != 0) bytes.Add(b);
            return Encoding.UTF8.GetString(bytes.ToArray());
        }

        public double[,] QuaternionToRotation3x3(
        double qw, double qx, double qy, double qz)
        {
            // Normalisieren (double!)
            double norm = Mathf.Sqrt((float)(qw*qw + qx*qx + qy*qy + qz*qz));
            qw /= norm;
            qx /= norm;
            qy /= norm;
            qz /= norm;

            return new double[,]
            {
                { 1 - 2*(qy*qy + qz*qz),     2*(qx*qy - qz*qw),     2*(qx*qz + qy*qw) },
                {     2*(qx*qy + qz*qw), 1 - 2*(qx*qx + qz*qz),     2*(qy*qz - qx*qw) },
                {     2*(qx*qz - qy*qw),     2*(qy*qz + qx*qw), 1 - 2*(qx*qx + qy*qy) }
            };
        }
        public (double x, double y, double z) ComputeCameraCenter(
        double qw, double qx, double qy, double qz,
        double tx, double ty, double tz)
        {
            var R = QuaternionToRotation3x3(qw, qx, qy, qz);

            // R^T * t
            double cx = -(R[0,0] * tx + R[1,0] * ty + R[2,0] * tz);
            double cy = -(R[0,1] * tx + R[1,1] * ty + R[2,1] * tz);
            double cz = -(R[0,2] * tx + R[1,2] * ty + R[2,2] * tz);

            return (cx, cy, cz);
        }

        UnityEngine.Quaternion ColmapToUnityRotation(
        double qw, double qx, double qy, double qz)
        {
            // world → camera
            var q_wc = new UnityEngine.Quaternion(
                (float)qx,
                (float)qy,
                (float)qz,
                (float)qw
            );

            // camera → world
            var q_cw = UnityEngine.Quaternion.Inverse(q_wc);

            // right-handed → left-handed (Z flip)
            return new UnityEngine.Quaternion(
                q_cw.x,
                q_cw.y,
                q_cw.z,
                q_cw.w
            );
        }
    

        public List<ColmapCamera> ParseCameras()
        {
            var cameras = new List<ColmapCamera>();

            using var fs = new FileStream(pathToCameraBinary, FileMode.Open, FileAccess.Read);
            using var br = new BinaryReader(fs);

            ulong numCameras = br.ReadUInt64();

            for (uint i = 0; i < numCameras; i++)
            {
                uint cameraId = br.ReadUInt32();
                uint modelId = br.ReadUInt32();
                ulong width = br.ReadUInt64();
                ulong height = br.ReadUInt64();

                int numParams = GetNumParams((int)modelId);
                double[] parameters = new double[numParams];

                for (int p = 0; p < numParams; p++)
                    parameters[p] = br.ReadDouble();

                cameras.Add(new ColmapCamera
                {
                    CameraId = cameraId,
                    ModelId = (int)modelId,
                    Width = (int)width,
                    Height = (int)height,
                    Params = parameters
                });
            }

            return cameras;
        }
        static int GetNumParams(int modelId)
        {
            return modelId switch
            {
                0 => 3, // SIMPLE_PINHOLE
                1 => 4, // PINHOLE
                2 => 4, // SIMPLE_RADIAL
                4 => 8, // OPENCV
                5 => 8, // OPENCV_FISHEYE
                _ => throw new Exception($"Unknown camera model {modelId}")
            };
        }

        public float calculateFOV(ColmapCamera camera)
        {
            // float fy = (float)camera.Params[1];
            // float height = camera.Height;

            // float fovY = 2f * Mathf.Atan(height / (2f * fy)) * Mathf.Rad2Deg;
            // return fovY;
            if (camera.ModelId != 1) // PINHOLE
                throw new Exception("FOV calculation assumes PINHOLE camera model");

            float fy = (float)camera.Params[1];
            float h  = camera.Height;

            if (fy <= 0 || float.IsNaN(fy) || float.IsInfinity(fy))
                throw new Exception($"Invalid fy: {fy}");

            return 2f * Mathf.Atan(h / (2f * fy)) * Mathf.Rad2Deg;
        }

    }
}