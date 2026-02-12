from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'gae_interface'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ssafy',
    maintainer_email='ssafy@todo.todo',
    description='Voice interface for GAE robot',
    license='Apache-2.0',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'voice_tiny = gae_interface.stt_module_tiny:main',
            'voice_base = gae_interface.stt_module_base:main',
            'voice_small = gae_interface.stt_module_small:main',
            'voice_gpt = gae_interface.stt_module_gpt:main',
            'voice_mqtt = gae_interface.stt_module_mqtt:main',
            'voice_final = gae_interface.stt_module_final:main',
            'voice_map = gae_interface.stt_module_map:main',
            'voice_fast = gae_interface.stt_module_fast:main',
            'pose_bridge_fix = gae_interface.pose_bridge_fix:main',
        ],
    },
)
