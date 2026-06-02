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

### Subtask A: Auto-Avoidance Telemetry Node
First, a python package named turtle_safety is created inside our workspace.

#### QoS Profiles and Parameters 
In this node, we subscribed to the turtle's position (/turtle1/pose). Instead of default settings, we used qos_profile_sensor_data. This is because sensor data needs to be fast. If a position packet is delayed on the network, it is better to drop it and get the newest one rather than wait.

We also declared a dynamic parameter called safety_threshold to act as a safety bubble around the turtle. To change this parameter while the node is running (without restarting the code), we use:

```bash
ros2 param set /collision_avoidance_node safety_threshold 3.0
```
#### Launch Files and Topic Remapping
To avoid opening many terminals, we wrote a launch file avoidance_launch.py that starts the simulator and our safety node together, while passing a custom value for the safety parameter.

```bash
ros2 launch turtle_safety avoidance_launch.py
```

We wanted to control the turtle manually, but if both our keyboard and our safety node publish to /turtle1/cmd_vel, the turtle will glitch. To fix this, we remapped the keyboard topic to /user_cmd_vel

```bash
ros2 run turtlesim turtle_teleop_key --ros-args -r /turtle1/cmd_vel:=/user_cmd_vel
```

### Subtask B: Circular Patrol & Actions
Actions are used for long-running tasks where we need a Goal, continuous Feedback, and a final Result.

#### Creating the Interface Package
Because custom messages and actions must be built using Cmake, we had to create a separate C++ package just for the action file.

```bash
ros2 pkg create --build-type ament_cmake turtle_interfaces
```

Inside, we defined ExecuteCircle.action which takes a radius goal, gives distance traveled as feedback, and returns a success boolean as a result.

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
