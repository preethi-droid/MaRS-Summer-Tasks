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

##Task 2

### ROS2 Turtle Avoidance

This has 2 main parts:

- Collision avoidance using publishers/subscribers
- Circular patrol using ROS2 Actions

I used Python (`rclpy`) for everything.

---

#### Folder Structure

```bash
ros2_ws/
└── src/
    └── turtle_avoidance/
```

Main files:

```bash
collision_avoidance_node.py
circle_patrol_server.py
circle_patrol_client.py
ExecuteCircle.action
avoidance_launch.py
```

---

#### Part A - Collision Avoidance

In this part, the turtle continuously checks where it is inside the turtlesim window.

The turtlesim area is roughly:

```text
11 x 11
```

If the turtle gets too close to a wall, it automatically turns away

Otherwise, it just keeps moving forward.

---

#### Subscriber

The node subscribes to:

```bash
/turtle1/pose
```

to get:
- x coordinate
- y coordinate
- orientation (`theta`)

I used the sensor QoS profile for this:

```python
from rclpy.qos import qos_profile_sensor_data
```

---

#### Publisher

The node publishes velocity commands to:

```bash
/turtle1/cmd_vel
```

using:

```python
geometry_msgs/msg/Twist
```

---

#### Safety Threshold Parameter

I created a ROS2 parameter called:

```python
safety_threshold
```

Default value:

```python
1.5
```

This controls how close the turtle is allowed to go near walls before turning.

It can also be changed during runtime without restarting the node:

```bash
ros2 param set /collision_avoidance_node safety_threshold 3.0
```

---

#### Launch File

I also created a launch file:

```bash
avoidance_launch.py
```

This launches:
- turtlesim node
- collision avoidance node

together.

Run using:

```bash
ros2 launch turtle_avoidance avoidance_launch.py
```

---

### Part B - Circular Patrol using Actions

This part was based on ROS2 Actions.

I created:
- a custom action
- an action server
- an action client

The turtle moves in a circular path based on the radius sent by the client.

---

#### Custom Action

File:

```bash
ExecuteCircle.action
```

Structure:

```text
float32 radius
---
bool success
string final_report
---
float32 distance_traveled
string current_status
```

---

#### Circle Logic

The turtle moves in a circle using:

```text
w = v / radius
```

where:
- `v` = linear velocity
- `w` = angular velocity

I fixed the linear velocity and calculated angular velocity dynamically depending on the radius.

---

#### Feedback

While the turtle moves, the server continuously sends feedback to the client:

```python
feedback_msg.distance_traveled = distance
```

The client prints the travelled distance continuously in the terminal.

---

#### Abort Condition

If the turtle gets too close to the wall while doing the circular patrol:
- the action gets aborted
- the turtle stops
- a failure message is returned


---

#### Build

```bash
cd ~/ros2_ws

colcon build

source install/setup.bash
```

---

#### Run Turtlesim

```bash
ros2 run turtlesim turtlesim_node
```

---

#### Run Server

```bash
ros2 run turtle_avoidance circle_patrol_server
```

---

#### Run Client

```bash
ros2 run turtle_avoidance circle_patrol_client
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
