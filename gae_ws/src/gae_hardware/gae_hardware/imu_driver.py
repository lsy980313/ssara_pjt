import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import numpy as np
import board
import busio
import adafruit_mpu6050
import yaml
import os
import sys

# ---------------------------------------------------------
# ⚙️ Hardware Config Import (Single Source of Truth)
# ---------------------------------------------------------
# 현재 파일 위치를 기준으로 config 폴더를 path에 추가하여 모듈처럼 import
current_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(current_dir, 'config')
sys.path.append(config_dir)

try:
    import hardware_config_test as hw_config
    # 하드웨어 설정 파일에서 값 가져오기
    IMU_AXIS_MAP  = hw_config.IMU_AXIS_MAP
    IMU_AXIS_SIGN = hw_config.IMU_AXIS_SIGN
    MPU_ADDR      = hw_config.MPU_ADDR
    I2C_BUS_ID    = hw_config.I2C_BUS_IMU
except ImportError:
    print("❌ Critical Error: 'hardware_config_test.py' not found in config/.")
    sys.exit(1)
except AttributeError as e:
    print(f"❌ Critical Error: Missing configuration in hardware_config_test.py: {e}")
    sys.exit(1)

# ---------------------------------------------------------

class ImuDriverNode(Node):
    def __init__(self):
        super().__init__('imu_driver_node')
        
        # 1. I2C 및 센서 연결
        try:
            # Jetson Board Pin Mapping (SCL_1, SDA_1 usually maps to Bus 1)
            self.i2c = busio.I2C(board.SCL_1, board.SDA_1)
            self.mpu = adafruit_mpu6050.MPU6050(self.i2c, address=MPU_ADDR)
            self.get_logger().info(f"✅ MPU6050 Connected at 0x{MPU_ADDR:X} on Bus {I2C_BUS_ID}")
            
            # (선택) 센서 범위 설정 (필요시 hw_config로 이동 가능)
            self.mpu.accelerometer_range = adafruit_mpu6050.Range.RANGE_8_G
            self.mpu.gyro_range = adafruit_mpu6050.GyroRange.RANGE_500_DPS
            
        except Exception as e:
            self.get_logger().error(f"❌ Failed to connect MPU6050: {e}")
            sys.exit(1)

        # 2. 캘리브레이션 데이터 로드 (Bias)
        self.bias_accel = np.array([0.0, 0.0, 0.0])
        self.bias_gyro  = np.array([0.0, 0.0, 0.0])
        self.load_calibration_file()

        # 3. Publisher 설정 (컨벤션 적용)
        # 규칙: /(패키지)/(장비)/(기능)
        topic_name = '/gae_hardware/imu/data'
        self.imu_pub = self.create_publisher(Imu, topic_name, 10)
        
        # 4. 타이머 설정 (200Hz)
        self.timer = self.create_timer(0.005, self.publish_imu_data)
        
        self.get_logger().info(f"🚀 IMU Driver Started. Topic: {topic_name}")

    def load_calibration_file(self):
        """ config/imu_sensor_bias.yaml 파일을 읽어서 Bias 변수에 저장 """
        # 절대 경로 대신 패키지 내부 상대 경로 사용
        config_path = os.path.join(config_dir, 'imu_sensor_bias.yaml')

        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
                bias_data = data['/**']['ros__parameters']['imu_sensor_bias']
                
                self.bias_accel = np.array([
                    bias_data['accel_bias_x'],
                    bias_data['accel_bias_y'],
                    bias_data['accel_bias_z']
                ])
                self.bias_gyro = np.array([
                    bias_data['gyro_bias_x'],
                    bias_data['gyro_bias_y'],
                    bias_data['gyro_bias_z']
                ])
                self.get_logger().info(f"✅ Calibration Bias Loaded.")
        except Exception as e:
            self.get_logger().warn(f"⚠️ Failed to load calibration file: {e}")
            self.get_logger().warn("   Using default bias (0.0).")

    def publish_imu_data(self):
        try:
            # 1. Raw 데이터 읽기
            raw_accel = np.array(self.mpu.acceleration)
            raw_gyro  = np.array(self.mpu.gyro)

            # 2. 축 매핑 & 부호 보정 (hw_config에서 가져온 설정 적용)
            mapped_accel = raw_accel[IMU_AXIS_MAP] * IMU_AXIS_SIGN
            mapped_gyro  = raw_gyro[IMU_AXIS_MAP]  * IMU_AXIS_SIGN

            # 3. 바이어스 제거 (캘리브레이션 적용)
            clean_accel = mapped_accel - self.bias_accel
            clean_gyro  = mapped_gyro  - self.bias_gyro

            # 4. ROS 메시지 생성
            msg = Imu()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "imu_link"

            # [AI Input 1] base_ang_vel (회전 속도)
            msg.angular_velocity.x = clean_gyro[0]
            msg.angular_velocity.y = clean_gyro[1]
            msg.angular_velocity.z = clean_gyro[2]

            # [AI Input 2] projected_gravity Source (선형 가속도)
            # 받는 쪽(Estimator/RL)에서 9.8로 나누어 사용
            msg.linear_acceleration.x = clean_accel[0]
            msg.linear_acceleration.y = clean_accel[1]
            msg.linear_acceleration.z = clean_accel[2]

            self.imu_pub.publish(msg)

        except OSError:
            # I2C 일시적 통신 오류 무시
            pass

def main(args=None):
    rclpy.init(args=args)
    node = ImuDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()