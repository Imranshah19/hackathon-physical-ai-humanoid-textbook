#!/usr/bin/env python3
"""
Simulation launch file for humanoid robot.

Launches robot state publisher, control nodes, and visualization.
Demonstrates comprehensive launch file with arguments and conditions.
"""

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Generate launch description for humanoid simulation."""

    # Package directories
    description_pkg = get_package_share_directory('humanoid_description')
    bringup_pkg = get_package_share_directory('humanoid_bringup')

    # ==================== Launch Arguments ====================

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz2 visualization'
    )

    use_joint_gui_arg = DeclareLaunchArgument(
        'use_joint_gui',
        default_value='true',
        description='Launch joint state publisher GUI'
    )

    # Get configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    use_joint_gui = LaunchConfiguration('use_joint_gui')

    # ==================== Robot Description ====================

    xacro_file = os.path.join(
        description_pkg, 'urdf', 'humanoid.urdf.xacro'
    )
    robot_description = Command(['xacro ', xacro_file])

    # ==================== Nodes ====================

    # Robot state publisher - publishes TF from joint states
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }],
        output='screen'
    )

    # Joint state publisher (static, no GUI)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        condition=UnlessCondition(use_joint_gui)
    )

    # Joint state publisher GUI (interactive)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(use_joint_gui)
    )

    # RViz2 visualization
    rviz_config = os.path.join(description_pkg, 'rviz', 'display.rviz')
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        condition=IfCondition(use_rviz),
        output='screen'
    )

    # ==================== Launch Description ====================

    return LaunchDescription([
        # Arguments
        use_sim_time_arg,
        use_rviz_arg,
        use_joint_gui_arg,

        # Nodes
        robot_state_publisher,
        joint_state_publisher,
        joint_state_publisher_gui,
        rviz2,
    ])
