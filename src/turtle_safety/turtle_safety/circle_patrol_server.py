#!/usr/bin/env python3
import rclpy
import time
import math
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.qos import qos_profile_sensor_data

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_interfaces.action import ExecuteCircle

class CirclePatrolServer(Node):
    def __init__(self):
        super().__init__('circle_patrol_server')

        
        self.cb_group = ReentrantCallbackGroup()

        
        self.current_pose = None
        self.safety_threshold = 1.5 

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.pose_sub = self.create_subscription(
            Pose, 
            '/turtle1/pose', 
            self.pose_callback, 
            qos_profile_sensor_data,
            callback_group=self.cb_group
        )

        self._action_server = ActionServer(
            self,
            ExecuteCircle,
            'execute_circle',
            self.execute_callback,
            callback_group=self.cb_group
        )
        self.get_logger().info("Circle Patrol Action Server is Ready.")

    def pose_callback(self, msg):
        self.current_pose = msg

    def check_wall_collision(self):
        if self.current_pose is None:
            return False
        x, y = self.current_pose.x, self.current_pose.y
        min_dist = min(x, 11.0 - x, y, 11.0 - y)
        return min_dist < self.safety_threshold

    def execute_callback(self, goal_handle):
        self.get_logger().info(f"Received goal request! Radius: {goal_handle.request.radius}")

        
        while self.current_pose is None:
            time.sleep(0.1)

        start_x = self.current_pose.x
        start_y = self.current_pose.y

        
        v = 1.5 
        r = goal_handle.request.radius
        w = v / r

        cmd = Twist()
        cmd.linear.x = v
        cmd.angular.z = w

        feedback_msg = ExecuteCircle.Feedback()
        result = ExecuteCircle.Result()

        start_time = self.get_clock().now()

        while rclpy.ok():
            
            self.cmd_pub.publish(cmd)

            
            elapsed_time = (self.get_clock().now() - start_time).nanoseconds / 1e9
            distance_traveled = v * elapsed_time

            
            feedback_msg.distance_traveled = distance_traveled
            feedback_msg.current_status = "Patrolling..."
            goal_handle.publish_feedback(feedback_msg)

            
            if self.check_wall_collision():
                self.get_logger().warn("Mission Aborted: Boundary Collision Imminent!")

                
                stop_cmd = Twist()
                self.cmd_pub.publish(stop_cmd)

                goal_handle.abort()
                result.success = False
                result.final_report = "Mission Aborted: Boundary Collision Imminent!"
                return result

            
            dist_to_start = math.hypot(self.current_pose.x - start_x, self.current_pose.y - start_y)

            if distance_traveled > (math.pi * r) and dist_to_start < 0.2:
                self.get_logger().info("Circle complete! Returning to base state.")

                stop_cmd = Twist()
                self.cmd_pub.publish(stop_cmd)

                goal_handle.succeed()
                result.success = True
                result.final_report = f"Success! Total distance: {distance_traveled:.2f} meters."
                return result

            time.sleep(0.1)

def main(args=None):
    rclpy.init(args=args)
    node = CirclePatrolServer()
    
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
