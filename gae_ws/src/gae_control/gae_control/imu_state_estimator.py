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

        # 2. 내부 변수 초기화
        self.base_ang_vel = np.zeros(3)
        self.projected_gravity = np.zeros(3)
        
        # Isaac Sim 학습 시 사용된 중력 상수
        self.GRAVITY_ACCEL = 9.81

        self.get_logger().info("🎧 IMU State Estimator Started. Ready for AI Input.")

    def imu_callback(self, msg):
        """
        드라이버에서 이미 축 매핑([1, 0, 2])과 Z부호 반전(-1.0)이 완료된 데이터를 받음.
        """
        
        # [AI Input 1] Base Angular Velocity
        # 드라이버에서 정렬된 X, Y, Z를 그대로 사용 (단위: rad/s)
        self.base_ang_vel = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])

        # [AI Input 2] Projected Gravity (중요!)
        # 센서 측정값(가속도)과 AI 기대값(중력 방향)은 부호가 반대입니다.
        # 센서 +9.8 (Up) -> AI 입력 -1.0 (Down)
        raw_accel = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])
        
        # 단위화(Normalize) 및 부호 반전
        self.projected_gravity = - (raw_accel / self.GRAVITY_ACCEL)

        # 🔍 디버깅용 (필요 시 주석 해제)
        self.get_logger().info(f"Gravity Vector (AI Input): {self.projected_gravity}", throttle_duration_sec=1.0)

    def get_states(self):
        """ 나중에 Controller 노드에서 호출하여 Observation 벡터를 생성함 """
        return self.base_ang_vel, self.projected_gravity

def main(args=None):
    rclpy.init(args=args)
    node = ImuStateEstimatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()