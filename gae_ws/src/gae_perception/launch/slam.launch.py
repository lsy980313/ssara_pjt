import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():
    # 1. 패키지 경로 자동 계산
    pkg_share = get_package_share_directory('gae_perception')
    astra_pkg = get_package_share_directory('astra_camera')
    rtabmap_pkg = get_package_share_directory('rtabmap_launch')

    # 2. 맵 저장 경로 설정
    home_dir = os.path.expanduser('~')
    workspace_root = os.path.join(home_dir, 'workspaces', 'sooyoung', 'S14P11C101')
    map_save_dir = os.path.join(workspace_root, 'src', 'gae_perception', 'maps')
    database_file = os.path.join(map_save_dir, 'rtabmap.db')

    if not os.path.exists(map_save_dir):
        os.makedirs(map_save_dir, exist_ok=True)

    # 3. [눈 1] 카메라 실행 (Astra Pro)
    camera_launch = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            os.path.join(astra_pkg, 'launch', 'astra_pro.launch.xml')
        ),
        launch_arguments={
            'color_fps': '30',
            'depth_fps': '30',
            'color_width': '320',  
            'color_height': '240', 
            'depth_width': '320',  
            'depth_height': '240'
        }.items()
    )

    # 4. [기억] RTAB-Map SLAM 실행
    rtabmap_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(rtabmap_pkg, 'launch', 'rtabmap.launch.py')
        ),
        launch_arguments={
            'database_path': database_file,
            'rtabmap_args': '--delete_db_on_start '
                            '--Rtabmap/DetectionRate 1 '
                            '--Mem/Strategy 1 '
                            '--Grid/FromDepth True '
                            '--Reg/Force3DoF True',
            'frame_id': 'base_link',
            'subscribe_depth': 'true',
            'subscribe_rgb': 'true',
            'approx_sync': 'true',
            'approx_sync_max_interval': '0.05', 
            'rgb_topic': '/camera/color/image_raw',
            'depth_topic': '/camera/depth/image_raw',
            'camera_info_topic': '/camera/color/camera_info',
            'qos': '2',                       
            'rviz': 'false',                  
            'rtabmap_viz': 'false'            
        }.items()
    )
    
    # 5. [관절] 정적 좌표 변환 (TF)
    tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0.1', '0', '0.1', '0', '0', '0', 'base_link', 'camera_link']
    )

    # 6. [눈 2] 웹 모니터링용 Depth 변환 노드
    depth_to_web_node = Node(
        package='gae_perception',
        executable='depth_converter',
        name='depth_converter',
        output='screen'
    )

    # 7. [웹] 비디오 서버
    web_server_node = Node(
        package='web_video_server',
        executable='web_video_server',
        name='web_server'
    )

    # 8. [지능] YOLO 객체 인식 노드
    inference_node = Node(
        package='gae_perception',
        executable='inference_node',
        name='inference_node',
        output='screen'
    )

    # 9. [판단] 장애물 회피 및 주행 결정 노드
    # decision_node = Node(
    #     package='gae_perception',
    #     executable='decision_node',
    #     name='decision_node',
    #     output='screen'
    # )

    # 10. [통신] MQTT 위치 전송 브릿지
    pose_bridge = Node(
        package='gae_perception',
        executable='pose_bridge',
        name='pose_bridge',
        output='screen',
        parameters=[{
            'broker_address': '127.0.0.1',  # MQTT 브로커 주소
            'port': 1884,
            'topic': 'robot/pose'
        }], # <--- 리스트 끝에 쉼표 확인!
        remappings=[
            ('/slam_pose', '/rtabmap/localization_pose')
        ]
    )

    return LaunchDescription([
        tf_node,
        #camera_launch,
        rtabmap_launch,
        depth_to_web_node,
        web_server_node,
        inference_node, 
        #decision_node,  
        pose_bridge,    
    ])