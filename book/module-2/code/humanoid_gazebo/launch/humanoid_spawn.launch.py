#!/usr/bin/env python3
"""
Launch file to spawn humanoid robot in Gazebo with full bridge.

Usage:
    ros2 launch humanoid_gazebo humanoid_spawn.launch.py
    ros2 launch humanoid_gazebo humanoid_spawn.launch.py z:=1.5
"""

import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    GroupAction,
)
from launch.substitutions import LaunchConfiguration, Command
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Package directories
    pkg_description = get_package_share_directory('humanoid_description')
    pkg_gazebo = get_package_share_directory('humanoid_gazebo')
    gz_sim_share = get_package_share_directory('ros_gz_sim')

    # URDF file path
    urdf_file = os.path.join(pkg_description, 'urdf', 'humanoid.urdf.xacro')
    world_file = os.path.join(pkg_gazebo, 'worlds', 'humanoid_world.sdf')

    # Process XACRO
    robot_description = Command(['xacro ', urdf_file])

    # Launch arguments
    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )

    spawn_x = DeclareLaunchArgument('x', default_value='0.0')
    spawn_y = DeclareLaunchArgument('y', default_value='0.0')
    spawn_z = DeclareLaunchArgument('z', default_value='1.0')

    # Gazebo simulation
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r {world_file}',
        }.items()
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }]
    )

    # Spawn robot in Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'humanoid',
            '-x', LaunchConfiguration('x'),
            '-y', LaunchConfiguration('y'),
            '-z', LaunchConfiguration('z'),
        ],
        output='screen'
    )

    # Bridge for clock and joint states
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        arguments=[
            # Clock
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Joint states
            '/world/humanoid_world/model/humanoid/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            # CMD for joints (example for one joint)
            '/model/humanoid/joint/left_hip_pitch/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
        ],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time,
        spawn_x,
        spawn_y,
        spawn_z,
        gazebo,
        robot_state_publisher,
        spawn_robot,
        bridge,
    ])
