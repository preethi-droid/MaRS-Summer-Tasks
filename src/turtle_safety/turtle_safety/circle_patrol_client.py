#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from turtle_interfaces.action import ExecuteCircle

class CirclePatrolClient(Node):
    def __init__(self):
        super().__init__('circle_patrol_client')
        self._action_client = ActionClient(self, ExecuteCircle, 'execute_circle')

    def send_goal(self, radius):
        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()

        goal_msg = ExecuteCircle.Goal()
        goal_msg.radius = float(radius)

        self.get_logger().info(f'Sending goal to patrol circle with radius: {radius}')

        
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, 
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        
        sys.stdout.write(f"\rFeedback -> Status: {feedback.current_status} | Distance Traveled: {feedback.distance_traveled:.2f}m")
        sys.stdout.flush()

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('\nGoal rejected by server.')
            return

        self.get_logger().info('\nGoal accepted! Patrolling...')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'\n--- FINAL RESULT ---')
        self.get_logger().info(f'Success: {result.success}')
        self.get_logger().info(f'Report: {result.final_report}')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    client = CirclePatrolClient()

    
    target_radius = 3.0
    if len(sys.argv) > 1:
        target_radius = float(sys.argv[1])

    client.send_goal(target_radius)
    rclpy.spin(client)

if __name__ == '__main__':
    main()
