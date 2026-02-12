import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
from datetime import datetime
import time

class DataRecorder(Node):
    def __init__(self):
        # [Rule] 노드 이름: 기능_node (data_recorder_node)
        super().__init__('data_recorder_node')

        # [Rule] 절대 경로 금지 대응
        # 홈 디렉토리(~)를 자동으로 찾아서 경로 생성
        # Docker인 경우: /root/gae_ws/src
        # Host인 경우: /home/ssafy/S14P11C101/gae_ws/src
        default_home = os.path.expanduser("~")
        default_save_path = os.path.join(default_home, 'gae_ws', 'src')

        # 1. 파라미터 선언
        self.declare_parameter('topic_name', '/camera/color/image_raw')
        self.declare_parameter('save_dir', default_save_path)
        self.declare_parameter('fps', 30.0)
        self.declare_parameter('file_prefix', 'gae_perception_data') # [Rule] 패키지명 포함 권장

        # 2. 파라미터 가져오기
        self.topic_name = self.get_parameter('topic_name').get_parameter_value().string_value
        self.save_dir = self.get_parameter('save_dir').get_parameter_value().string_value
        self.fps = self.get_parameter('fps').get_parameter_value().double_value
        self.prefix = self.get_parameter('file_prefix').get_parameter_value().string_value

        # 3. 구독자 설정
        self.subscription = self.create_subscription(
            Image,
            self.topic_name,
            self.image_callback,
            10)
        
        self.bridge = CvBridge()
        self.video_writer = None
        self.start_time = None
        self.frame_count = 0
        
        # 저장 경로 확인 및 생성
        if not os.path.exists(self.save_dir):
            try:
                os.makedirs(self.save_dir)
                self.get_logger().info(f'📂 경로가 없어 새로 생성했습니다: {self.save_dir}')
            except OSError as e:
                self.get_logger().error(f'❌ 저장 경로 생성 실패: {e}')
                # 경로 생성 실패 시 /tmp로 우회하거나 종료하는 로직이 있으면 좋음
            
        self.get_logger().info(f'🎥 [GAE Recorder] 시작! 타겟 토픽: {self.topic_name}')
        self.get_logger().info(f'📂 저장 위치: {self.save_dir}')

    def image_callback(self, msg):
        try:
            # ROS Image -> OpenCV (bgr8)
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Writer 초기화 (첫 프레임 수신 시)
            if self.video_writer is None:
                height, width, _ = cv_image.shape
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # 파일명 예시: gae_perception_data_20260203_120000.mp4
                file_name = f"{self.prefix}_{now}.mp4"
                full_path = os.path.join(self.save_dir, file_name)
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(full_path, fourcc, self.fps, (width, height))
                
                self.start_time = time.time()
                self.get_logger().info(f'🔴 녹화 시작: {full_path} ({width}x{height})')

            # 프레임 쓰기
            self.video_writer.write(cv_image)
            self.frame_count += 1
            
            # 진행 상황 출력 (30프레임마다)
            if self.frame_count % 30 == 0:
                elapsed = time.time() - self.start_time
                # \r을 사용하여 같은 줄에 덮어쓰기 (로그 깔끔하게 유지)
                print(f"\r[REC] {elapsed:.1f}초 | Frames: {self.frame_count}", end="")

        except Exception as e:
            self.get_logger().error(f'⚠️ 프레임 처리 에러: {e}')

    def stop_recording(self):
        if self.video_writer is not None:
            self.video_writer.release()
            print("\n") 
            self.get_logger().info(f'💾 저장 완료. 총 {self.frame_count} 프레임.')
        else:
            self.get_logger().info('녹화된 내용이 없습니다.')

def main(args=None):
    rclpy.init(args=args)
    node = DataRecorder()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_recording()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()