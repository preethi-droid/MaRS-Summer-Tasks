#!/usr/bin/env python3

import math
import time

import rclpy

from rclpy.node import Node
from rclpy.action import ActionServer

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from turtle_avoidance.action import ExecuteCircle


class CirclePatrolServer(Node):

    def __init__(self):

        super().__init__('circle_patrol_server')

        self.cmd_pub = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.current_pose = None

        self.action_server = ActionServer(
            self,
            ExecuteCircle,
            'execute_circle',
            self.execute_callback
        )

        self.get_logger().info('Circle Patrol Server Started')


    def pose_callback(self, msg):
        self.current_pose = msg


    def execute_callback(self, goal_handle):

        self.get_logger().info('Executing Circle Patrol')

        radius = goal_handle.request.radius

        linear_speed = 1.5
        angular_speed = linear_speed / radius

        twist = Twist()
        twist.linear.x = linear_speed
        twist.angular.z = angular_speed

        while self.current_pose is None:
            pass

        start_x = self.current_pose.x
        start_y = self.current_pose.y

        tolerance = 0.2

        start_time = time.time()

        feedback_msg = ExecuteCircle.Feedback()

        loop_completed = False

        while rclpy.ok():

            x = self.current_pose.x
            y = self.current_pose.y

            # Wall collision check
            threshold = 1.0

            if (
                x < threshold or
                x > (11.0 - threshold) or
                y < threshold or
                y > (11.0 - threshold)
            ):

                stop_msg = Twist()
                self.cmd_pub.publish(stop_msg)

                goal_handle.abort()

                result = ExecuteCircle.Result()
                result.success = False
                result.final_report = (
                    'Mission Aborted: Boundary Collision Imminent!'
                )

                return result

            self.cmd_pub.publish(twist)

            elapsed = time.time() - start_time

            distance = linear_speed * elapsed

            feedback_msg.distance_traveled = distance
            feedback_msg.current_status = 'Moving in circular path'

            goal_handle.publish_feedback(feedback_msg)

            distance_from_start = math.sqrt(
                (x - start_x) ** 2 +
                (y - start_y) ** 2
            )

            # Prevent instant completion
            if elapsed > 5.0 and distance_from_start < tolerance:
                loop_completed = True
                break

            time.sleep(0.1)

        stop_msg = Twist()
        self.cmd_pub.publish(stop_msg)

        goal_handle.succeed()

        result = ExecuteCircle.Result()

        result.success = True
        result.final_report = (
            'Full circular patrol completed successfully!'
        )

        return result


def main(args=None):

    rclpy.init(args=args)

    node = CirclePatrolServer()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
