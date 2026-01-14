// RGBCameraPublisher.cs
// Streams RGB camera images from Unity to ROS 2.
//
// Usage:
//   1. Attach to a Camera GameObject
//   2. Configure resolution and publish rate
//   3. Camera will render to texture and publish

using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;
using RosMessageTypes.Std;
using System;

public class RGBCameraPublisher : MonoBehaviour
{
    [Header("Camera Settings")]
    public Camera targetCamera;
    public int width = 640;
    public int height = 480;

    [Header("Publish Settings")]
    public float publishRate = 30f;
    public string topicName = "/camera/image_raw";
    public string frameId = "camera_link";

    [Header("Options")]
    public bool flipVertical = true;  // ROS convention

    private ROSConnection ros;
    private RenderTexture renderTexture;
    private Texture2D texture2D;
    private float timeElapsed;
    private uint sequenceId;

    void Start()
    {
        // Auto-assign camera if not set
        if (targetCamera == null)
            targetCamera = GetComponent<Camera>();

        if (targetCamera == null)
        {
            Debug.LogError("RGBCameraPublisher: No camera assigned!");
            enabled = false;
            return;
        }

        // Initialize ROS
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<ImageMsg>(topicName);

        // Create render texture
        renderTexture = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
        renderTexture.antiAliasing = 1;
        targetCamera.targetTexture = renderTexture;

        // Create texture for reading pixels
        texture2D = new Texture2D(width, height, TextureFormat.RGB24, false);

        Debug.Log($"RGBCameraPublisher: {width}x{height} @ {publishRate}Hz -> {topicName}");
    }

    void Update()
    {
        timeElapsed += Time.deltaTime;

        if (timeElapsed >= 1f / publishRate)
        {
            CaptureAndPublish();
            timeElapsed = 0f;
        }
    }

    void CaptureAndPublish()
    {
        // Render camera to texture
        targetCamera.Render();

        // Read pixels from render texture
        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = renderTexture;

        texture2D.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        texture2D.Apply();

        RenderTexture.active = currentRT;

        // Get raw bytes
        byte[] rawData = texture2D.GetRawTextureData();

        // Flip vertically if needed (Unity Y-up vs ROS convention)
        byte[] imageData = flipVertical ? FlipImageVertically(rawData, width, height, 3) : rawData;

        // Create and publish message
        var msg = new ImageMsg
        {
            header = new HeaderMsg
            {
                seq = sequenceId++,
                stamp = GetCurrentTime(),
                frame_id = frameId
            },
            height = (uint)height,
            width = (uint)width,
            encoding = "rgb8",
            is_bigendian = 0,
            step = (uint)(width * 3),
            data = imageData
        };

        ros.Publish(topicName, msg);
    }

    byte[] FlipImageVertically(byte[] data, int w, int h, int channels)
    {
        byte[] flipped = new byte[data.Length];
        int rowSize = w * channels;

        for (int y = 0; y < h; y++)
        {
            int srcRow = y * rowSize;
            int dstRow = (h - 1 - y) * rowSize;
            Array.Copy(data, srcRow, flipped, dstRow, rowSize);
        }

        return flipped;
    }

    RosMessageTypes.Builtin.TimeMsg GetCurrentTime()
    {
        double totalSeconds = Time.timeAsDouble;
        int secs = (int)totalSeconds;
        uint nsecs = (uint)((totalSeconds - secs) * 1e9);

        return new RosMessageTypes.Builtin.TimeMsg { sec = secs, nanosec = nsecs };
    }

    void OnDestroy()
    {
        if (renderTexture != null)
        {
            renderTexture.Release();
            Destroy(renderTexture);
        }

        if (texture2D != null)
        {
            Destroy(texture2D);
        }
    }
}
