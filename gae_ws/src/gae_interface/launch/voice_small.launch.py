from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='gae_interface',
            executable='voice_small',
            name='voice_node',
            output='screen',
            parameters=[]
        )
    ])
