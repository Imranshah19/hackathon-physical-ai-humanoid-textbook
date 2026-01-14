// JointStatePublisher.cs
// Publishes joint states from Unity ArticulationBody joints to ROS 2.
//
// Usage:
//   1. Attach to robot root GameObject
//   2. Configure topic name and publish rate
//   3. Ensure ROSConnection is configured in scene

using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;
using RosMessageTypes.Std;
using System.Collections.Generic;

public class JointStatePublisher : MonoBehaviour
{
    [Header("ROS Settings")]
    public string topicName = "/joint_states";
    public string frameId = "base_link";

    [Header("Publish Settings")]
    public float publishRate = 50f;

    private ROSConnection ros;
    private ArticulationBody[] joints;
    private float timeElapsed;
    private float publishInterval;
    private uint sequenceId;

    void Start()
    {
        // Initialize ROS connection
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<JointStateMsg>(topicName);

        // Find all articulation joints in hierarchy
        joints = GetComponentsInChildren<ArticulationBody>();

        publishInterval = 1f / publishRate;

        Debug.Log($"JointStatePublisher: Found {joints.Length} joints, publishing to {topicName}");
    }

    void FixedUpdate()
    {
        timeElapsed += Time.fixedDeltaTime;

        if (timeElapsed >= publishInterval)
        {
            PublishJointStates();
            timeElapsed = 0f;
        }
    }

    void PublishJointStates()
    {
        var names = new List<string>();
        var positions = new List<double>();
        var velocities = new List<double>();
        var efforts = new List<double>();

        foreach (var joint in joints)
        {
            // Skip fixed joints
            if (joint.jointType == ArticulationJointType.FixedJoint)
                continue;

            names.Add(joint.name);

            // Get joint state based on joint type
            if (joint.jointType == ArticulationJointType.RevoluteJoint ||
                joint.jointType == ArticulationJointType.PrismaticJoint)
            {
                positions.Add(joint.jointPosition[0]);
                velocities.Add(joint.jointVelocity[0]);
                efforts.Add(joint.jointForce[0]);
            }
            else if (joint.jointType == ArticulationJointType.SphericalJoint)
            {
                // For spherical joints, use primary axis
                positions.Add(joint.jointPosition[0]);
                velocities.Add(joint.jointVelocity[0]);
                efforts.Add(joint.jointForce[0]);
            }
        }

        // Build message
        var msg = new JointStateMsg
        {
            header = new HeaderMsg
            {
                seq = sequenceId++,
                stamp = GetCurrentTime(),
                frame_id = frameId
            },
            name = names.ToArray(),
            position = positions.ToArray(),
            velocity = velocities.ToArray(),
            effort = efforts.ToArray()
        };

        ros.Publish(topicName, msg);
    }

    RosMessageTypes.Builtin.TimeMsg GetCurrentTime()
    {
        double totalSeconds = Time.fixedTimeAsDouble;
        int secs = (int)totalSeconds;
        uint nsecs = (uint)((totalSeconds - secs) * 1e9);

        return new RosMessageTypes.Builtin.TimeMsg
        {
            sec = secs,
            nanosec = nsecs
        };
    }
}
