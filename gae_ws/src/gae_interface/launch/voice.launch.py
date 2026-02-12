from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    exe = LaunchConfiguration('exe')

    return LaunchDescription([
        DeclareLaunchArgument(
            'exe',
            default_value='voice_tiny',
            description='gae_interface executable: voice_tiny | voice_small | voice_base'
        ),
        Node(
            package='gae_interface',
            executable=exe,
            name='spot_voice_node',
            output='screen',
            parameters=[]
        )
    ])
