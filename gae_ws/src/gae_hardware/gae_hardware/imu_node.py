import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import board
import busio
import adafruit_mpu6050
import numpy as np
import yaml
import os
import time

# config 패키지에서 하드웨어 설정 가져오기
from gae_hardware.config import hardware_config as hw_cfg

# 👇 ROS 패키지 경로를 찾아주는 마법의 도구
from ament_index_python.packages import get_package_share_directory

class ImuNode(Node):
    def __init__(self):
        super().__init__('imu_node') # 노드 이름은 규칙(기능_node)에 맞음 (imu_node)
        
        # ---------------------------------------------------------
        # 🛠️ [수정] 컨벤션 적용: /(패키지)/(장비)/(기능)
        # Old: '/imu/data'
        # New: '/gae_hardware/imu/data'
        # ---------------------------------------------------------
        self.imu_pub = self.create_publisher(Imu, '/gae_hardware/imu/data', 10)
        
        # 2. Timer 설정 (50Hz = 0.02s) 
        # -> RL 모델의 제어 주기와 맞추는 게 일반적입니다.
        self.timer = self.create_timer(0.02, self.timer_callback)

        # 3. I2C 연결 (하드웨어 설정 사용)
        try:
            # Jetson Orin Nano의 I2C 버스 1번 사용
            i2c = busio.I2C(board.SCL_1, board.SDA_1)
            self.mpu = adafruit_mpu6050.MPU6050(i2c, address=hw_cfg.MPU_ADDR)
            self.get_logger().info(f"✅ IMU Connected on Bus {hw_cfg.I2C_BUS_IMU}")
        except Exception as e:
            self.get_logger().error(f"❌ IMU Connection Failed: {e}")
            # 센서 없으면 노드 죽이기
            self.destroy_node()
            return

        # 4. 캘리브레이션 데이터 로딩
        self.accel_offset = np.zeros(3)
        self.gyro_offset = np.zeros(3)
        self.load_calibration_file()

        # 5. [Sim2Real] 축 방향 설정
        self.axis_sign = np.array(hw_cfg.IMU_AXIS_SIGN)
        
        # 👇 [추가할 코드] 매핑 설정(순서 섞기) 가져오기
        self.axis_map = hw_cfg.IMU_AXIS_MAP 
        self.get_logger().info(f"ℹ️  Sim2Real Axis Sign: {self.axis_sign}")
        self.get_logger().info(f"ℹ️  Sim2Real Axis Map : {self.axis_map}") # 로그 확인용

    def load_calibration_file(self):
        """ROS 2 표준 방식으로 share 폴더에서 yaml 파일을 찾습니다."""
        try:
            # 1. gae_hardware 패키지의 share 폴더 경로 찾기
            # (예: /root/gae_ws/install/gae_hardware/share/gae_hardware)
            package_share_directory = get_package_share_directory('gae_hardware')
            
            # 2. config 폴더 안의 yaml 파일 경로 완성
            yaml_path = os.path.join(package_share_directory, 'config', 'imu_calibration.yaml')
            
            # 3. 파일 읽기
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
                calib = data['/**']['ros__parameters']['imu_calibration']
                
                self.accel_offset = np.array([
                    calib['accel_offset_x'], calib['accel_offset_y'], calib['accel_offset_z']
                ])
                self.gyro_offset = np.array([
                    calib['gyro_offset_x'], calib['gyro_offset_y'], calib['gyro_offset_z']
                ])
                self.get_logger().info(f"✅ Calibration Loaded from {yaml_path}")
                self.get_logger().info(f"   Accel Offset: {self.accel_offset}")
                self.get_logger().info(f"   Gyro Offset : {self.gyro_offset}")

        except FileNotFoundError:
            self.get_logger().warn(f"⚠️  Config file not found at: {yaml_path}")
            self.get_logger().warn("   -> Please run 'colcon build' to install config files.")
        except Exception as e:
            self.get_logger().warn(f"⚠️  Failed to load calibration ({e}). Using raw data.")

    def timer_callback(self):
        try:
            # 1. Raw Data 읽기
            raw_accel = np.array(self.mpu.acceleration)
            raw_gyro = np.array(self.mpu.gyro)

            # ---------------------------------------------------------
            # 🛠️ [수정됨] 매핑(순서바꾸기) -> 부호반전 적용
            # ---------------------------------------------------------
            
            # (1) 축 순서 섞기 (Numpy 팬시 인덱싱 기능)
            # config에서 [1, 0, 2]로 설정했으므로, [y, x, z] 순서로 자동 변환됨
            remapped_accel = raw_accel[self.axis_map]
            remapped_gyro  = raw_gyro[self.axis_map]

            # (2) 부호 뒤집기
            aligned_accel = remapped_accel * self.axis_sign
            aligned_gyro  = remapped_gyro  * self.axis_sign
            
            # ---------------------------------------------------------

            # 3. [Sim2Real] 오차 제거 (Calibration)
            # 주의: 축을 바꿨으므로 캘리브레이션(offset)도 다시 잡는 게 좋습니다.
            clean_accel = aligned_accel - self.accel_offset
            clean_gyro = aligned_gyro - self.gyro_offset

            # 4. ROS 메시지 생성 및 발행
            msg = Imu()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "base_link" 

            msg.linear_acceleration.x = clean_accel[0]
            msg.linear_acceleration.y = clean_accel[1]
            msg.linear_acceleration.z = clean_accel[2]

            msg.angular_velocity.x = clean_gyro[0]
            msg.angular_velocity.y = clean_gyro[1]
            msg.angular_velocity.z = clean_gyro[2]

            self.imu_pub.publish(msg)

        except OSError:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = ImuNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()