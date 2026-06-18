# MaRS Summer Tasks

## Task 1
This is about ROS2 workspace, packages, nodes, topics, publishers and subscribers programs in C++ and python

---

### Creating a ROS2 Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```
"mkdir" is used to create a directory, here a workspace which will have all the packages.
"cd" is used to enter into our workspace

Packages are built inside our workspace using the following command
```bash
colcon build
```

To source our workspace
```bash
source install/setup.bash
```

---

### Creating a Python Package

First, we enter the src directory
```bash
cd ~/ros2_ws/src
```

and then create a python package
```bash
ros2 pkg create --build-type ament_python py_pubsub
```

the package has the following structure
```
my_package/
      package.xml
      resource/my_package
      setup.cfg
      setup.py
      my_package/
```
---

### Creating a C++ Package

A C++ package is created in a similar fashion, like a python package
```bash
ros2 pkg create --build-type ament_cmake cpp_pubsub
```

the package has the following structure
```
my_package/
     CMakeLists.txt
     include/my_package/
     package.xml
     src/
```
---

### ROS2 Nodes and Topics

#### Nodes
Each node in ROS will be responsible for a single, modular purpose. So, a complete robotic system consists of many such nodes.

#### Topics
Topics act as buses between all the nodes, through which the data will be moved between the nodes.

### Python & C++ Publisher and Subscriber Node

Inside the ros2_ws/src, a package is created. We get the talker and listener code inside this package, where we add the dependencies and the entry points and finally run them

#### Run Publisher (Python)
```bash
ros2 run py_pubsub talker
```

#### Run Subscriber (Python)
```bash
ros2 run py_pubsub listener
```

#### Run Publisher (C++)
```bash
ros2 run cpp_pubsub talker
```

#### Run Subscriber (C++)
```bash
ros2 run cpp_pubsub listener
```

## Task 2
This was about some ROS2 implementations using Turtlesim. This includes QoS, dynamic parameters, launch files and custom actions. It was also about the architectural shift from ROS1 to ROS2.

---

### Subtask A: Auto-Avoidance Telemetry Node
First, a python package named turtle_safety is created inside our workspace.

#### QoS Profiles and Parameters 
In this node, we subscribed to the turtle's position (/turtle1/pose). Instead of default settings, we used qos_profile_sensor_data. This is because sensor data needs to be fast. If a position packet is delayed on the network, it is better to drop it and get the newest one rather than wait.

We also declared a dynamic parameter called safety_threshold to act as a safety bubble around the turtle. To change this parameter while the node is running (without restarting the code), we use:

```bash
ros2 param set /collision_avoidance_node safety_threshold 3.0
```

---

#### Launch Files and Topic Remapping
To avoid opening many terminals, we wrote a launch file avoidance_launch.py that starts the simulator and our safety node together, while passing a custom value for the safety parameter.

```bash
ros2 launch turtle_safety avoidance_launch.py
```

We wanted to control the turtle manually, but if both our keyboard and our safety node publish to /turtle1/cmd_vel, the turtle will glitch. To fix this, we remapped the keyboard topic to /user_cmd_vel

```bash
ros2 run turtlesim turtle_teleop_key --ros-args -r /turtle1/cmd_vel:=/user_cmd_vel
```

---

### Subtask B: Circular Patrol & Actions
Actions are used for long-running tasks where we need a Goal, continuous Feedback, and a final Result.

#### Creating the Interface Package
Because custom messages and actions must be built using Cmake, we had to create a separate C++ package just for the action file.

```bash
ros2 pkg create --build-type ament_cmake turtle_interfaces
```

Inside, we defined ExecuteCircle.action which takes a radius goal, gives distance traveled as feedback, and returns a success boolean as a result.

---

#### Action Server and Client
Back in our python package, we wrote the server and client. The Action Server does the math to drive in a circle (w = v / radius). We had to use a MultiThreadedExecutor so the node could drive the motors and check the wall sensors at the exact same time.

To run the Action Server:
```bash
ros2 run turtle_safety circle_patrol_server
```

To run the Action Client (asking the turtle to drive a circle with a radius of 2.0 meters):
```bash
ros2 run turtle_safety circle_patrol_client 2.0
```

---

### A. ROS 1 vs ROS 2 Architectural Shift

#### 1. ROS 1 Master (roscore) and SPOF

In ROS 1, there is a central system called the **ROS Master (roscore)**.

- It keeps track of all active nodes in the system
- It helps nodes find each other
- It manages the communication setup

The problem is:

- If the ROS Master stops working, the whole system breaks
- Nodes cannot find each other anymore
- This is called a **Single Point of Failure (SPOF)**

So basically, one process controls everything. If it dies, everything else also dies.

---

#### 2. ROS 2 Decentralized Architecture

ROS 2 does not use a central master.

Instead:

- Each node exists independently
- Nodes discover each other automatically
- Communication happens directly between nodes

This is done using **DDS (Data Distribution Service)**.


- No central server
- No single failure point
- Nodes just join the network and announce themselves

So the system is more like a peer-to-peer network.

---

#### 3. ROS 1 vs ROS 2 Communication

##### ROS 1 (TCPROS / UDPROS)

- Uses **TCPROS** (TCP) or **UDPROS** (UDP)
- First, nodes ask the ROS Master for information
- Then they connect directly to each other
- Master is only used for setup

Flow:
1. Node registers with roscore
2. Nodes ask roscore for connection info
3. Direct connection is created between nodes

---

##### ROS 2 (DDS Wire Protocol)

- Uses **DDS middleware**
- Communication is continuous and decentralized
- Nodes publish and subscribe directly through DDS

Flow:
1. Node joins network
2. DDS discovery finds other nodes
3. Data flows through DDS automatically

No central lookup step is needed.

---

### B. DDS (Data Distribution Service)

DDS is the middleware that makes ROS 2 work without a master.

---

#### 1. Discoverability Mechanism (How nodes find each other)

When two ROS 2 nodes are on the same Wi-Fi:

- They use **Simple Discovery Protocol (SDP)**
- They send **multicast UDP packets** on the network
- These packets announce:
  - Node name
  - Topics
  - Data types

So:

- Every node "shouts" what it offers
- Other nodes listen and connect automatically

No server is needed. Only network broadcasting.

---

#### 2. DDS Vendors in ROS 2

ROS 2 supports multiple DDS implementations.

Common ones:

- **eProsima Fast DDS**
- **Eclipse Cyclone DDS**
- **RTI Connext DDS**

There are others too, but these are the main ones used.

---

### Switching DDS implementation

You can switch DDS vendors using this environment variable:

```bash
RMW_IMPLEMENTATION
```

---

## Task 3

This task involved creating a 4-wheel rover using Xacro/URDF, spawning it inside Ignition Gazebo, visualizing it in RViz2, and understanding TF trees and state publishers.

---

### Robot Description using Xacro

The robot was modeled using Xacro.

The model consists of:

- A central chassis represented by a rectangular box
- Four wheels attached to the chassis
- Continuous joints connecting the wheels
- Visual, collision and inertial properties

Xacro properties were used to make dimensions and masses easier to modify.

---

### Gazebo Simulation

A custom SDF world was created and loaded through a launch file.

The world contains:

- Ground plane
- Lighting
- Custom obstacle objects

The rover is spawned automatically when the launch file is executed.

---

### Robot State Publisher and Joint State Publisher

The robot_state_publisher node publishes transforms generated from the URDF model.

The joint_state_publisher node publishes wheel joint states so that wheel positions and rotations can be visualized correctly in RViz2.

These nodes are launched together with the simulation.

---

### TF Tree

TF trees define the relationship between coordinate frames of the robot.

The TF tree was visualized in RViz2 to verify that all transforms were being published correctly.

---

### Building the Package

```bash
colcon build --packages-select rover_robot --symlink-install
```

---

### Running the Simulation

To launch the gazebo and spawn the rover
```bash
ros2 launch rover_robot sim.launch.py
```

Gazebo Bridge to synchronize ROS2 topics with Gazebo topics
```bash
ros2 run ros_gz_bridge parameter_bridge /cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist /model/rover_robot/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry /model/rover_robot/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V /clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock --ros-args -r /model/rover_robot/tf:=/tf
```

For teleoperation
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

RViz2
```bash
rviz2 --ros-args -p use_sim_time:=true
```

To run the tf2_tools
```bash
ros2 run tf2_tools view_frames
```

---

## Task 4

This task was about upgrading our basic rover. We added sensors (a camera, LiDAR, and IMU), set up a control system to move the robot's arm, and built a data bridge so Gazebo and RViz2 could talk to each other properly.

---

### Adding Sensors with Xacro

We edited our robot's Xacro file to add three new pieces of hardware:

- **LiDAR:** Mounted on top of a pole (mast) to scan the room 360 degrees and look for obstacles.
- **Camera:** Placed on the robot's arm to give us a live video feed.
- **IMU:** Hidden inside the main body to measure the robot's acceleration and tilt.

---

### Controlling the Robot (Drivetrain vs. Arm)

We split the robot's movement into two separate control systems so they wouldn't interfere with each other:

- **Driving the Wheels:** Handled by Gazebo's built-in `DiffDrive` plugin. It takes our keyboard inputs (`/cmd_vel`) and spins the wheels.
- **Moving the Arm:** Handled by `ros2_control`. This system focuses purely on the arm's joint, letting us lift or rotate the camera smoothly without messing up the wheel movements.

---

### Sharing Joint Positions

If a joint moves in Gazebo, RViz2 needs to know about it instantly so the 3D hologram does not glitch out:

- **Wheel Rotations:** We added an Ignition plugin that watches the wheels spin and sends those exact spinning angles over to RViz2.
- **Fixed Parts (IMU):** Since the IMU is glued tight to the chassis and does not have a moving joint, we added a Pose Publisher plugin to force Gazebo to tell RViz2 exactly where it is at all times.

---

### Setting up the Network Bridge

We set up a giant command-line bridge that translates everything—keyboard commands, camera video, LiDAR scans, and structural transforms (TFs), so both programs stay perfectly in sync. 

We also switched the center of the world in RViz2 to `odom` so that the virtual camera stays fixed to the ground while the rover drives away.

---

### Running the Simulation

Updated Gazebo Bridge to synchronize ROS2 topics with Gazebo topics
```bash
ros2 run ros_gz_bridge parameter_bridge /cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist /model/rover_robot/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry /model/rover_robot/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V /clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock /scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan /camera/image_raw@sensor_msgs/msg/Image[ignition.msgs.Image /camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo /imu@sensor_msgs/msg/Imu[ignition.msgs.IMU /joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model --ros-args -r /model/rover_robot/tf:=/t
```

To launch the arm controller slider panel
```bash
ros2 run rqt_joint_trajectory_controller rqt_joint_trajectory_controller
```

---
