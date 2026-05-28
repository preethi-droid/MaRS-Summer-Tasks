#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class CollisionAvoidanceNode(Node):
    def __init__(self):
        super().__init__('collision_avoidance_node')

        self.declare_parameter('safety_threshold', 1.5)
        
        self.latest_user_cmd = Twist()
        
        self.last_cmd_time = self.get_clock().now() 
        
        self.cmd_timeout = 0.3 

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        self.user_cmd_sub = self.create_subscription(
            Twist, 
            '/user_cmd_vel', 
            self.user_cmd_callback, 
            10
        )
        
        self.pose_sub = self.create_subscription(
            Pose, 
            '/turtle1/pose', 
            self.pose_callback, 
            qos_profile_sensor_data
        )

        self.get_logger().info("Safety Node Started. Waiting for user commands on /user_cmd_vel...")

    def user_cmd_callback(self, msg):
        self.latest_user_cmd = msg
        
        self.last_cmd_time = self.get_clock().now()

    def pose_callback(self, msg):
        threshold = self.get_parameter('safety_threshold').value

        dist_left = msg.x
        dist_right = 11.0 - msg.x
        dist_bottom = msg.y
        dist_top = 11.0 - msg.y

        min_distance = min(dist_left, dist_right, dist_bottom, dist_top)

        final_cmd = Twist()

        if min_distance < threshold:
            self.get_logger().warn(f"Wall detected! Escaping zone...", throttle_duration_sec=1.0)
            final_cmd.linear.x = 0.5  
            final_cmd.angular.z = 1.5 
            self.latest_user_cmd = Twist()
        else:
            
            time_since_last_cmd = (self.get_clock().now() - self.last_cmd_time).nanoseconds / 1e9
            
            if time_since_last_cmd > self.cmd_timeout:
                
                self.latest_user_cmd = Twist()
            
            
            final_cmd = self.latest_user_cmd

        self.cmd_pub.publish(final_cmd)

def main(args=None):
    rclpy.init(args=args)
    node = CollisionAvoidanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
