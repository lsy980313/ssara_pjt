from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'gae_hardware'

setup(
    name=package_name,
    version='0.0.0',
    # ------------------------------------------------------------
    # 🛠️ [수정 포인트]
    # find_packages()는 __init__.py가 있는 폴더만 가져오는데, 
    # config 폴더도 패키지로 인식되도록 명시적으로 추가합니다.
    # ------------------------------------------------------------
    packages=[package_name, package_name + '.config'], 
    
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),

    # 🛠️ [수정] config가 gae_hardware 안으로 들어갔으니 경로 수정
    # glob('config/*.yaml')  --> glob('gae_hardware/config/*.yaml')
    (os.path.join('share', package_name, 'config'), glob('gae_hardware/config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ssafy',
    maintainer_email='ssafy@todo.todo',
    description='GAE Robot Hardware Control Package',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'imu_node = gae_hardware.imu_node:main',
            'imu_driver = gae_hardware.imu_driver:main',
        ],
    },
)