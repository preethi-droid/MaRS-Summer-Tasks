from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim_node'
        ),

        Node(
            package='turtle_avoidance',
            executable='collision_avoidance_node',
            name='collision_avoidance_node',

            parameters=[
                {'safety_threshold': 2.5}
            ]
        )

    ])
