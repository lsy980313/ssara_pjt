from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='gae_interface',
            executable='voice_final',
            name='voice_node',
            output='screen'
        )
    ])
