# hydra_mesh_bringup

A ROS 2 launch package that brings up Navigation2 in Gazebo using a 3D mesh extracted by the MIT Hydra project.

## Goal

The goal of this project is to leverage the metric‑semantic mesh produced by MIT’s Hydra system—“Hydra: A Real‑time Spatial Perception System for 3D Scene Graph Construction and Optimization” (RSS 2022)—to create a Gazebo‑based simulation environment for Navigation2. This can be later integrated with other simulations and real robots for testing and development with Hydra.

## Dependencies

Before building, make sure you have the following installed:

- **ROS 2** (Humble Hawksbill or later)  
- **Navigation2** (`ros-humble-navigation2`, `ros-humble-nav2-bringup`)  
- **SLAM Toolbox** (`ros-humble-slam-toolbox`)  
- **Gazebo ROS packages** (`ros-humble-gazebo-ros-pkgs`)  
- **gazebo_plugins** (`ros-humble-gazebo-plugins`)  
- **xacro** (`ros-humble-xacro`)  
- **ament_cmake**, **rclcpp**, **rviz2**, etc. (standard ROS 2 build tools)

## Installation

1. Clone into your workspace:

   ```bash
   cd ~/ros2_ws/src
   git clone https://github.com/your-org/hydra_mesh_bringup.git
   ```
2. Install any missing ROS 2 dependencies:

   ```bash
   cd ~/ros2_ws
   rosdep install -i --from-path src --rosdistro humble -y
   ```
3. Build and source:

   ```bash
   colcon build
   source install/setup.bash
   ```

## Meshes Folder

Inside the `worlds/` directory, you **must** create a `*_model/` folder for each world that you create. Furthermore, you need to create a `meshes/` folder inside that directory. This is where you will place the 3D mesh files extracted by Hydra. For example:

```
worlds/
├── office.sdf.xacro
├── office_model/
│   ├── model.sdf
│   ├── model.config
│   └── meshes/
│       └── office_mesh.dae
```

## Usage

Launch the full stack (mapping, navigation, simulation) with:

```bash
ros2 launch hydra_mesh_bringup my_custom_simulation_launch.py headless:=false
```

* `headless:=true` runs Gazebo in headless mode.
* Additional arguments (e.g. `map:=…`, `use_sim_time:=true`) can be passed as needed.

## References

* **Hydra**: Hughes, N., Chang, Y., & Carlone, L. “Hydra: A Real‑time Spatial Perception System for 3D Scene Graph Construction and Optimization.” *Robotics: Science and Systems*, 2022 ([ResearchGate][1]).


[1]: https://www.researchgate.net/publication/358259707_Hydra_A_Real-time_Spatial_Perception_Engine_for_3D_Scene_Graph_Construction_and_Optimization?utm_source=chatgpt.com "Hydra: A Real-time Spatial Perception Engine for 3D Scene Graph ..."