import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # [Rule] 절대 경로 금지 대응
    # 실행하는 환경(Docker/Host)에 맞춰 홈 디렉토리 자동 탐색
    # 예: Docker -> /root/gae_ws/src
    # 예: Host -> /home/ssafy/workspaces/.../gae_ws/src
    # (참고: 실제 작업 공간 이름은 사용자마다 다를 수 있으므로 안전하게 src까지만 지정하거나 실행 시 인자로 받음)
    
    # 기본값은 '현재 사용자의 홈/gae_ws/src'로 설정
    default_save_path = os.path.join(os.path.expanduser('~'), 'gae_ws', 'src')

    # 1. 저장 경로 파라미터 선언
    save_dir_arg = DeclareLaunchArgument(
        'save_dir',
        default_value=default_save_path,
        description='Directory to save video files (Absolute path recommended)'
    )

    # 2. 카메라 실행 파일 경로 가져오기
    # [External Lib] astra_camera 패키지 활용
    astra_pkg = get_package_share_directory('astra_camera')
    
    astra_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(astra_pkg, 'launch', 'astra_pro.launch.xml')
        )
    )

    # 3. 레코더 노드 실행
    # [Rule] 노드 이름: 기능_node (data_recorder_node)
    recorder_node = Node(
        package='gae_perception',
        executable='data_recorder',
        name='data_recorder_node',
        output='screen',
        parameters=[{
            'topic_name': '/camera/color/image_raw', # 카메라는 외부 패키지라 기본 토픽 유지
            'save_dir': LaunchConfiguration('save_dir'),
            'fps': 30.0,
            'file_prefix': 'yolov8n_dataset' # 파일명 접두사
        }]
    )

    return LaunchDescription([
        save_dir_arg,
        astra_launch,
        recorder_node
    ])