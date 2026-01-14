// DomainRandomizer.cs
// Master domain randomization controller for synthetic data generation.
//
// Usage:
//   1. Attach to empty GameObject in scene
//   2. Reference all randomizer components
//   3. Call Randomize() or trigger via ROS service

using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Std;
using System.Collections.Generic;

public class DomainRandomizer : MonoBehaviour
{
    [Header("Randomizer Components")]
    public List<Renderer> textureTargets;
    public List<Light> lights;
    public List<GameObject> spawnPrefabs;

    [Header("Texture Settings")]
    public Texture2D[] textureLibrary;
    public bool useProceduralTextures = true;

    [Header("Lighting Settings")]
    public float minIntensity = 0.5f;
    public float maxIntensity = 2.0f;
    public float minTemperature = 4000f;
    public float maxTemperature = 8000f;

    [Header("Object Settings")]
    public Vector3 spawnAreaCenter = Vector3.zero;
    public Vector3 spawnAreaSize = new Vector3(5, 0, 5);
    public int minObjects = 3;
    public int maxObjects = 10;

    [Header("ROS Settings")]
    public string serviceName = "/randomize_domain";
    public bool enableROSTrigger = true;

    private ROSConnection ros;
    private List<GameObject> spawnedObjects = new List<GameObject>();

    void Start()
    {
        if (enableROSTrigger)
        {
            ros = ROSConnection.GetOrCreateInstance();
            ros.RegisterService<TriggerRequest, TriggerResponse>(serviceName);
            ros.ImplementService<TriggerRequest, TriggerResponse>(
                serviceName, HandleRandomizeRequest
            );

            Debug.Log($"DomainRandomizer: ROS service ready at {serviceName}");
        }
    }

    TriggerResponse HandleRandomizeRequest(TriggerRequest request)
    {
        try
        {
            RandomizeAll();
            return new TriggerResponse
            {
                success = true,
                message = "Domain randomization applied successfully"
            };
        }
        catch (System.Exception e)
        {
            return new TriggerResponse
            {
                success = false,
                message = $"Randomization failed: {e.Message}"
            };
        }
    }

    [ContextMenu("Randomize All")]
    public void RandomizeAll()
    {
        Debug.Log("DomainRandomizer: Applying randomization...");

        RandomizeTextures();
        RandomizeLighting();
        RandomizeObjects();

        Debug.Log("DomainRandomizer: Randomization complete");
    }

    public void RandomizeTextures()
    {
        foreach (var renderer in textureTargets)
        {
            if (renderer == null) continue;

            if (useProceduralTextures && Random.value > 0.5f)
            {
                renderer.material.mainTexture = GenerateProceduralTexture();
            }
            else if (textureLibrary != null && textureLibrary.Length > 0)
            {
                int idx = Random.Range(0, textureLibrary.Length);
                renderer.material.mainTexture = textureLibrary[idx];
            }

            // Randomize material properties
            renderer.material.color = Random.ColorHSV(0, 1, 0.3f, 0.8f, 0.5f, 1f);
            renderer.material.SetFloat("_Metallic", Random.Range(0f, 0.3f));
            renderer.material.SetFloat("_Smoothness", Random.Range(0.1f, 0.8f));
        }
    }

    Texture2D GenerateProceduralTexture()
    {
        int size = 256;
        var texture = new Texture2D(size, size);

        Color baseColor = Random.ColorHSV(0, 1, 0.3f, 0.7f, 0.3f, 0.7f);
        float scale = Random.Range(0.05f, 0.2f);

        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                float noise = Mathf.PerlinNoise(x * scale, y * scale);
                Color c = baseColor * (0.5f + noise * 0.5f);
                texture.SetPixel(x, y, c);
            }
        }

        texture.Apply();
        return texture;
    }

    public void RandomizeLighting()
    {
        foreach (var light in lights)
        {
            if (light == null) continue;

            // Intensity
            light.intensity = Random.Range(minIntensity, maxIntensity);

            // Color temperature
            float temp = Random.Range(minTemperature, maxTemperature);
            light.color = Mathf.CorrelatedColorTemperatureToRGB(temp);

            // For directional lights, randomize direction
            if (light.type == LightType.Directional)
            {
                float elevation = Random.Range(20f, 80f);
                float azimuth = Random.Range(0f, 360f);
                light.transform.rotation = Quaternion.Euler(elevation, azimuth, 0);
            }

            // Random on/off for non-primary lights
            if (light.type != LightType.Directional)
            {
                light.enabled = Random.value > 0.3f;
            }
        }
    }

    public void RandomizeObjects()
    {
        // Clear existing spawned objects
        foreach (var obj in spawnedObjects)
        {
            if (obj != null)
                Destroy(obj);
        }
        spawnedObjects.Clear();

        if (spawnPrefabs == null || spawnPrefabs.Count == 0)
            return;

        // Spawn new objects
        int count = Random.Range(minObjects, maxObjects + 1);

        for (int i = 0; i < count; i++)
        {
            // Random prefab
            var prefab = spawnPrefabs[Random.Range(0, spawnPrefabs.Count)];

            // Random position within spawn area
            Vector3 position = spawnAreaCenter + new Vector3(
                Random.Range(-spawnAreaSize.x / 2, spawnAreaSize.x / 2),
                spawnAreaSize.y,
                Random.Range(-spawnAreaSize.z / 2, spawnAreaSize.z / 2)
            );

            // Random rotation
            Quaternion rotation = Quaternion.Euler(0, Random.Range(0, 360), 0);

            // Spawn
            var obj = Instantiate(prefab, position, rotation);

            // Random scale
            float scale = Random.Range(0.5f, 2f);
            obj.transform.localScale *= scale;

            // Random color
            var renderer = obj.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.color = Random.ColorHSV();
            }

            spawnedObjects.Add(obj);
        }
    }

    void OnDrawGizmosSelected()
    {
        // Visualize spawn area
        Gizmos.color = new Color(0, 1, 0, 0.3f);
        Gizmos.DrawCube(spawnAreaCenter, spawnAreaSize);
        Gizmos.color = Color.green;
        Gizmos.DrawWireCube(spawnAreaCenter, spawnAreaSize);
    }
}
