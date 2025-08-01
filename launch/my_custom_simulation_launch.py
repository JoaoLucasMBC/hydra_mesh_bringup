# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is all-in-one launch script intended for use by nav2 developers."""

import os
import tempfile

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    OpaqueFunction,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnShutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.actions import SetEnvironmentVariable

from launch_ros.actions import Node


def generate_launch_description():
    # Get the launch directory
    # --- CHANGE START ---
    # Change 'nav2_bringup' to your new package name 'hydra_mesh_bringup'
    my_bringup_dir = get_package_share_directory('hydra_mesh_bringup')
    # Use your package's launch directory if you have custom launch files within it
    # launch_dir = os.path.join(my_bringup_dir, 'launch')
    # For now, let's keep it pointing to nav2_bringup's original launch directory
    # for consistency with other included launch files.
    bringup_dir = get_package_share_directory('nav2_bringup')
    launch_dir = os.path.join(bringup_dir, 'launch')
    sim_dir = get_package_share_directory('nav2_minimal_tb3_sim')

    # This checks that tb3 exists needed for the URDF. If not using TB3, its safe to remove.
    # Keep this as it's correctly finding the turtlebot3_gazebo package.
    # _ = get_package_share_directory('turtlebot3_gazebo')
    gazebo_model_path_env = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[os.path.join(my_bringup_dir, 'worlds'), os.pathsep, os.environ.get('GZ_SIM_RESOURCE_PATH', '')]
    )

    # --- CHANGE END ---

    # Create the launch configuration variables
    slam = LaunchConfiguration('slam')  
    namespace = LaunchConfiguration('namespace')
    use_namespace = LaunchConfiguration('use_namespace')
    # map_yaml_file is still used, but its default value will be overridden later or ignored if not doing SLAM
    map_yaml_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')
    use_composition = LaunchConfiguration('use_composition')
    use_respawn = LaunchConfiguration('use_respawn')

    # Launch configuration variables specific to simulation
    rviz_config_file = LaunchConfiguration('rviz_config_file')
    use_simulator = LaunchConfiguration('use_simulator')
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
    use_rviz = LaunchConfiguration('use_rviz')
    headless = LaunchConfiguration('headless')
    world = LaunchConfiguration('world') # This variable will now point to your new world

    # --- CHANGE START ---
    # Modify default values for robot spawn pose (x, y, z, R, P, Y)
    # These values need to be adjusted based on your kitchen.stl layout.
    # Start with some reasonable values (e.g., slightly offset from origin) and adjust after seeing the sim.
    pose = {'x': LaunchConfiguration('x_pose', default='-10.00'), # Example: Changed from '-2.00'
            'y': LaunchConfiguration('y_pose', default='30.00'), # Example: Changed from '-0.50'
            'z': LaunchConfiguration('z_pose', default='1.00'), # Keep z small to be on the ground
            'R': LaunchConfiguration('roll', default='0.00'),
            'P': LaunchConfiguration('pitch', default='0.00'),
            'Y': LaunchConfiguration('yaw', default='0.00')} # Example: Changed for initial orientation
    # --- CHANGE END ---

    robot_name = LaunchConfiguration('robot_name')
    robot_sdf = LaunchConfiguration('robot_sdf')

    # Map fully qualified names to relative ones so the node's namespace can be prepended.
    # In case of the transforms (tf), currently, there doesn't seem to be a better alternative
    # https://github.com/ros/geometry2/issues/32
    # https://github.com/ros/robot_state_publisher/pull/30
    # TODO(orduno) Substitute with `PushNodeRemapping`
    #              https://github.com/ros2/launch_ros/issues/56
    remappings = [('/tf', 'tf'),
                  ('/tf_static', 'tf_static')]

    # Declare the launch arguments
    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Top-level namespace')

    declare_use_namespace_cmd = DeclareLaunchArgument(
        'use_namespace',
        default_value='false',
        description='Whether to apply a namespace to the navigation stack')

    declare_slam_cmd = DeclareLaunchArgument(
        'slam',
        default_value='True',
        description='Whether run a SLAM')

    declare_map_yaml_cmd = DeclareLaunchArgument(
        'map',
        # --- CHANGE START ---
        # If you are NOT using SLAM, this map file might not be strictly used for the initial environment
        # as your Gazebo world now defines it. However, Nav2 still expects a map for static mapping.
        # You'll likely need to either:
        # 1. Provide a new 2D occupancy grid map for your kitchen (if you want to use Nav2's static map features).
        #    This map would be generated from your 3D kitchen model.
        # 2. Set 'slam' to 'True' to build a map as the robot explores.
        # For now, let's point it to a default or potentially remove it if you're solely relying on Gazebo for env.
        # Given you're providing a .world file, you might initially set SLAM to True to generate a map.
        # If you want to use a pre-existing 2D map for navigation, you'd generate one from your STL and reference it here.
        default_value=os.path.join(
            bringup_dir, 'maps', 'tb3_sandbox.yaml'),
        # If you generated a map from your kitchen and put it in your package:
        # default_value=os.path.join(get_package_share_directory('my_robot_sim_bringup'), 'maps', 'my_kitchen_map.yaml'),
        description='Full path to map file to load')
        # --- CHANGE END ---

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(bringup_dir, 'params', 'nav2_params.yaml'),
        description='Full path to the ROS2 parameters file to use for all launched nodes')

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart', default_value='true',
        description='Automatically startup the nav2 stack')

    declare_use_composition_cmd = DeclareLaunchArgument(
        'use_composition', default_value='True',
        description='Whether to use composed bringup')

    declare_use_respawn_cmd = DeclareLaunchArgument(
        'use_respawn', default_value='False',
        description='Whether to respawn if a node crashes. Applied when composition is disabled.')

    declare_rviz_config_file_cmd = DeclareLaunchArgument(
        'rviz_config_file',
        default_value=os.path.join(
            bringup_dir, 'rviz', 'nav2_default_view.rviz'),
        description='Full path to the RVIZ config file to use')

    declare_use_simulator_cmd = DeclareLaunchArgument(
        'use_simulator',
        default_value='True',
        description='Whether to start the simulator')

    declare_use_robot_state_pub_cmd = DeclareLaunchArgument(
        'use_robot_state_pub',
        default_value='True',
        description='Whether to start the robot state publisher')

    declare_use_rviz_cmd = DeclareLaunchArgument(
        'use_rviz',
        default_value='True',
        description='Whether to start RVIZ')

    declare_simulator_cmd = DeclareLaunchArgument(
        'headless',
        default_value='True',
        description='Whether to execute gzclient)')

    # --- CHANGE START ---
    # This is the most critical change for the world file
    declare_world_cmd = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(my_bringup_dir, 'worlds', 'office.sdf.xacro'), #'office.sdf.xacro'), # <--- CHANGE THIS LINE
        description='Full path to world model file to load')
    # --- CHANGE END ---

    declare_robot_name_cmd = DeclareLaunchArgument(
        'robot_name',
        default_value='turtlebot3_waffle', # You can keep this or change to 'turtlebot3_burger' if that's your model
        description='name of the robot')

    declare_robot_sdf_cmd = DeclareLaunchArgument(
        'robot_sdf',
        # This points to a default SDF for TurtleBot3. Usually this is fine.
        # If you had a custom SDF for your robot, you'd point to it here.
        default_value=os.path.join(sim_dir, 'urdf', 'gz_waffle.sdf.xacro'),
        description='Full path to robot sdf file to spawn the robot in gazebo')

    # Specify the actions
    urdf = os.path.join(sim_dir, 'urdf', 'turtlebot3_waffle.urdf')
    with open(urdf, 'r') as infp:
        robot_description = infp.read()

    start_robot_state_publisher_cmd = Node(
        condition=IfCondition(use_robot_state_pub),
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        namespace=namespace,
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'robot_description': robot_description}],
        remappings=remappings)

    rviz_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, 'rviz_launch.py')),
        condition=IfCondition(use_rviz),
        launch_arguments={'namespace': namespace,
                          'use_namespace': use_namespace,
                            'use_sim_time': use_sim_time,
                          'rviz_config': rviz_config_file}.items())

    bringup_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, 'bringup_launch.py')),
        launch_arguments={'namespace': namespace,
                          'use_namespace': use_namespace,
                          'slam': slam,
                          'map': map_yaml_file, # This map is for Nav2's 2D costmap/localization
                          'use_sim_time': use_sim_time,
                          'params_file': params_file,
                          'autostart': autostart,
                          'use_composition': use_composition,
                          'use_respawn': use_respawn}.items())

    # The SDF file for the world is a xacro file because we wanted to
    # conditionally load the SceneBroadcaster plugin based on wheter we're
    # running in headless mode. But currently, the Gazebo command line doesn't
    # take SDF strings for worlds, so the output of xacro needs to be saved into
    # a temporary file and passed to Gazebo.
    world_sdf = tempfile.mktemp(prefix='nav2_', suffix='.sdf')
    world_sdf_xacro = ExecuteProcess(
        cmd=['xacro', '-o', world_sdf, ['headless:=', headless], world])
    gazebo_server = ExecuteProcess(
        cmd=['gz', 'sim', '-r', '-s', world_sdf],
        output='screen',
        condition=IfCondition(use_simulator)
    )

    remove_temp_sdf_file = RegisterEventHandler(event_handler=OnShutdown(
        on_shutdown=[
            OpaqueFunction(function=lambda _: os.remove(world_sdf))
        ]))

    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch',
                         'gz_sim.launch.py')
        ),
        condition=IfCondition(PythonExpression(
            [use_simulator, ' and not ', headless])),
        launch_arguments={'gz_args': ['-v4 -g ']}.items(),
    )

    gz_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(sim_dir, 'launch', 'spawn_tb3.launch.py')),
        launch_arguments={'namespace': namespace,
                          'use_sim_time': use_sim_time,
                          'robot_name': robot_name,
                          'robot_sdf': robot_sdf,
                          'x_pose': pose['x'],
                          'y_pose': pose['y'],
                          'z_pose': pose['z'],
                          'roll': pose['R'],
                          'pitch': pose['P'],
                          'yaw': pose['Y']}.items())


    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(gazebo_model_path_env)

    # Declare the launch options
    ld.add_action(declare_namespace_cmd)
    ld.add_action(declare_use_namespace_cmd)
    ld.add_action(declare_slam_cmd)
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_use_composition_cmd)

    ld.add_action(declare_rviz_config_file_cmd)
    ld.add_action(declare_use_simulator_cmd)
    ld.add_action(declare_use_robot_state_pub_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_simulator_cmd)
    ld.add_action(declare_world_cmd) # This is where your world argument is declared
    ld.add_action(declare_robot_name_cmd)
    ld.add_action(declare_robot_sdf_cmd)
    ld.add_action(declare_use_respawn_cmd)

    # Add any conditioned actions
    #ld.add_action(start_gz_sim_cmd)
    #ld.add_action(start_gazebo_spawner_cmd) # This uses the pose variables you defined earlier
    ld.add_action(world_sdf_xacro)
    ld.add_action(remove_temp_sdf_file)
    ld.add_action(gz_robot)
    ld.add_action(gazebo_server)
    ld.add_action(gazebo_client)


    # Add the actions to launch all of the navigation nodes
    ld.add_action(start_robot_state_publisher_cmd)
    ld.add_action(rviz_cmd)
    ld.add_action(bringup_cmd) # This includes the main Nav2 stack

    return ld