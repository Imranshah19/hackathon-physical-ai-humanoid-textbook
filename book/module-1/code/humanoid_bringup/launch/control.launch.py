#!/usr/bin/env python3
"""
Control nodes launch file for humanoid robot.

Launches joint publisher, subscriber, and services.
Can be included in other launch files.
"""

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Generate launch description for control nodes."""

    # Package directory
    bringup_pkg = get_package_share_directory('humanoid_bringup')

    # ==================== Launch Arguments ====================

    joint_name_arg = DeclareLaunchArgument(
        'joint_name',
        default_value='head_pan',
        description='Joint to control'
    )

    publish_rate_arg = DeclareLaunchArgument(
        'publish_rate',
        default_value='50.0',
        description='Command publish rate in Hz'
    )

    # Get configurations
    joint_name = LaunchConfiguration('joint_name')
    publish_rate = LaunchConfiguration('publish_rate')

    # ==================== Nodes ====================

    # Joint command publisher
    joint_publisher = Node(
        package='humanoid_control',
        executable='joint_publisher',
        name='joint_publisher',
        parameters=[{
            'joint_name': joint_name,
            'publish_rate': publish_rate,
            'amplitude': 0.5,
            'frequency': 0.5,
        }],
        output='screen'
    )

    # Joint command subscriber
    joint_subscriber = Node(
        package='humanoid_control',
        executable='joint_subscriber',
        name='joint_subscriber',
        output='screen'
    )

    # Joint limits service
    joint_limits_server = Node(
        package='humanoid_control',
        executable='joint_limits_service',
        name='joint_limits_server',
        output='screen'
    )

    # Move action server
    move_action_server = Node(
        package='humanoid_control',
        executable='move_action_server',
        name='move_action_server',
        output='screen'
    )

    # ==================== Launch Description ====================

    return LaunchDescription([
        # Arguments
        joint_name_arg,
        publish_rate_arg,

        # Nodes
        joint_publisher,
        joint_subscriber,
        joint_limits_server,
        move_action_server,
    ])
