#!/usr/bin/env python3
"""
Launch ROS TCP endpoint for Unity connection.

Usage:
    ros2 launch humanoid_unity unity_bridge.launch.py
    ros2 launch humanoid_unity unity_bridge.launch.py ros_ip:=192.168.1.100
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Launch arguments
    ros_ip = DeclareLaunchArgument(
        'ros_ip',
        default_value='0.0.0.0',
        description='ROS IP address for TCP endpoint'
    )

    ros_port = DeclareLaunchArgument(
        'ros_port',
        default_value='10000',
        description='ROS TCP port'
    )

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )

    # TCP endpoint node
    tcp_endpoint = Node(
        package='ros_tcp_endpoint',
        executable='default_server_endpoint',
        name='ros_tcp_endpoint',
        parameters=[{
            'ROS_IP': LaunchConfiguration('ros_ip'),
            'ROS_TCP_PORT': LaunchConfiguration('ros_port'),
        }],
        output='screen'
    )

    # Optional: Relay Unity topics to standard names
    joint_state_relay = Node(
        package='topic_tools',
        executable='relay',
        name='joint_state_relay',
        arguments=['/unity/joint_states', '/joint_states'],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    # Optional: Relay camera topic
    camera_relay = Node(
        package='topic_tools',
        executable='relay',
        name='camera_relay',
        arguments=['/unity/camera/image_raw', '/camera/image_raw'],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    return LaunchDescription([
        ros_ip,
        ros_port,
        use_sim_time,
        tcp_endpoint,
        joint_state_relay,
        camera_relay,
    ])
