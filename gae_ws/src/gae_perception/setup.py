from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'gae_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # Launch 파일 설치
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        
        # [수정 1] maps 폴더가 최상위에도 있다면 유지, 없다면 빈 리스트가 되어 문제 없음
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
        
        # [수정 2] Config 폴더 처리 (여기가 핵심!)
        # config 폴더 안의 '파일'만 골라냄 (maps 같은 폴더는 제외)
        (os.path.join('share', package_name, 'config'), [f for f in glob('config/*') if os.path.isfile(f)]),
        
        # [수정 3] Config 내부의 maps 폴더를 따로 등록
        # config/maps 안에 있는 파일들을 install/share/.../config/maps 로 복사
        (os.path.join('share', package_name, 'config', 'maps'), glob('config/maps/*')),
        
        # Weights 파일 설치
        (os.path.join('share', package_name, 'weights'), glob('weights/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ssafy',
    maintainer_email='ssafy@todo.todo',
    description='GAE Robot Perception Package',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'depth_converter = gae_perception.depth_to_web:main',
            'decision_node = gae_perception.decision_node:main',
            'inference_node = gae_perception.inference_node:main',
            'pose_bridge = gae_perception.pose_bridge:main',
        ],
    },
)