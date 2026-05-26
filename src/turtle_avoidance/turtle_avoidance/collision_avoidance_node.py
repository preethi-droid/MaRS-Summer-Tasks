#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

from rclpy.qos import qos_profile_sensor_data


class CollisionAvoidanceNode(Node):

    def __init__(self):
        super().__init__('collision_avoidance_node')

        # Declare parameter
        self.declare_parameter('safety_threshold', 1.5)

        # Publisher
        self.cmd_pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # Subscriber with Sensor Data QoS
        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            qos_profile_sensor_data
        )

        self.get_logger().info('Collision Avoidance Node Started')


    def pose_callback(self, msg):

        threshold = self.get_parameter(
            'safety_threshold'
        ).value

        x = msg.x
        y = msg.y

        twist = Twist()

        near_wall = (
            x < threshold or
            x > (11.0 - threshold) or
            y < threshold or
            y > (11.0 - threshold)
        )

        if near_wall:

            # Turn away from wall
            twist.linear.x = 1.0
            twist.angular.z = 2.0

            self.get_logger().info(
                'Wall detected! Turning away...'
            )

        else:

            # Move forward
            twist.linear.x = 2.0
            twist.angular.z = 0.0

        self.cmd_pub.publish(twist)


def main(args=None):

    rclpy.init(args=args)

    node = CollisionAvoidanceNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
