from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'gae_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # Launch 파일이 있다면 (나중에 launch 폴더 생기면 주석 해제)
        # (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        
        # Config (설정 파일)
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        
        # Models (강화학습 모델 등)
        (os.path.join('share', package_name, 'models'), glob('gae_control/models/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ssafy',
    maintainer_email='ssafy@todo.todo',
    description='GAE Robot Control Package',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 나중에 노드 실행 파일 등록하는 곳
            # 'node_name = gae_control.node_file:main'
            'imu_state_estimator = gae_control.imu_state_estimator:main',
        ],
    },
)