import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import numpy as np

class ImuStateEstimatorNode(Node):
    def __init__(self):
        super().__init__('imu_state_estimator_node')

        # 1. 하드웨어 드라이버 데이터 구독
        self.imu_sub = self.create_subscription(
            Imu,
            '/gae_hardware/imu/data',
            self.imu_callback,
            10
        )

        # 2. [추가] 검증용 토픽 발행 (정제된 데이터를 토픽으로 확인하기 위함)
        self.processed_imu_pub = self.create_publisher(
            Imu, 
            '/gae_control/imu/processed', 
            10
        )

        # 3. 내부 변수 초기화
        self.base_ang_vel = np.zeros(3)
        self.projected_gravity = np.zeros(3)
        
        # Isaac Sim 학습 시 사용된 중력 상수
        self.GRAVITY_ACCEL = 9.81

        self.get_logger().info("🎧 IMU State Estimator Started. Monitoring /gae_hardware/imu/data...")

    def imu_callback(self, msg):
        """
        드라이버에서 이미 축 매핑([1, 0, 2])과 Z부호 반전(-1.0)이 완료된 데이터를 받음.
        """
        
        # [AI Input 1] Base Angular Velocity (rad/s)
        self.base_ang_vel = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])

        # [AI Input 2] Projected Gravity
        # 센서 +9.8 (Up) -> AI 입력 -1.0 (Down)
        raw_accel = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])
        
        # 단위화(Normalize) 및 부호 반전
        self.projected_gravity = - (raw_accel / self.GRAVITY_ACCEL)

        # ---------------------------------------------------------
        # 🔍 검증을 위한 로직 (터미널 확인용)
        # ---------------------------------------------------------
        # 1. 터미널 로그 출력 (1초에 한 번)
        self.get_logger().info(
            f"\n[AI Input Data]\n"
            f" - Ang Vel (XYZ): {self.base_ang_vel}\n"
            f" - Proj Grav (XYZ): {self.projected_gravity}", 
            throttle_duration_sec=1.0
        )

        # 2. 정제된 데이터를 토픽으로 발행 (ros2 topic echo용)
        processed_msg = Imu()
        processed_msg.header = msg.header
        processed_msg.angular_velocity.x = self.base_ang_vel[0]
        processed_msg.angular_velocity.y = self.base_ang_vel[1]
        processed_msg.angular_velocity.z = self.base_ang_vel[2]
        processed_msg.linear_acceleration.x = self.projected_gravity[0]
        processed_msg.linear_acceleration.y = self.projected_gravity[1]
        processed_msg.linear_acceleration.z = self.projected_gravity[2]
        self.processed_imu_pub.publish(processed_msg)

    def get_states(self):
        """ 나중에 Controller 노드에서 호출하여 Observation 벡터를 생성함 """
        return self.base_ang_vel, self.projected_gravity

def main(args=None):
    rclpy.init(args=args)
    node = ImuStateEstimatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down ImuStateEstimatorNode...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()