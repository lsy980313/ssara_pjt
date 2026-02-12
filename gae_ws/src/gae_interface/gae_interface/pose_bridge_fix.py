import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from nav_msgs.msg import Odometry
import json
import time
import math
import paho.mqtt.client as mqtt

<<<<<<< HEAD

class PoseBridgeFix(Node):
    def __init__(self):
        super().__init__('pose_bridge_fix')

        # QoS: RTAB-Map은 BEST_EFFORT로 퍼블리시
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        self.subscription = self.create_subscription(
            Odometry,
            '/rtabmap/odom',
            self.listener_callback,
=======
class PoseBridgeFix(Node):
    def __init__(self):
        super().__init__('pose_bridge_fix')
        
        # [핵심] SLAM 데이터 유실 방지를 위한 QoS 설정 (Best Effort)
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        self.subscription = self.create_subscription(
            Odometry, 
            '/rtabmap/odom', 
            self.listener_callback, 
>>>>>>> 3ba0dc4868ca15d0da3a7e78bdbedcdd7d0bbdd2
            qos
        )

        self.broker_address = "localhost"
        self.port = 1883
        self.topic = "robot/pose"

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Taeyeon_Pose_Bridge")
<<<<<<< HEAD

=======
        
>>>>>>> 3ba0dc4868ca15d0da3a7e78bdbedcdd7d0bbdd2
        try:
            self.client.connect(self.broker_address, self.port, 60)
            self.client.loop_start()
            print(f"[MQTT] Pose Bridge Connected: {self.broker_address}:{self.port}")
        except Exception as e:
            print(f"[MQTT] Connection Failed: {e}")

        self.last_sent_time = 0.0
<<<<<<< HEAD
        self.last_x = None
        self.last_y = None
        self.initialized = False  # 첫 유효 좌표를 받았는지
=======
        self.last_x = 0.0
        self.last_y = 0.0
        self.initialized = False
>>>>>>> 3ba0dc4868ca15d0da3a7e78bdbedcdd7d0bbdd2

    def listener_callback(self, msg):
        current_time = time.time()
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

<<<<<<< HEAD
        # [필터 1] (0, 0) 원점 리셋 무시 - SLAM 트래킹 잃으면 (0,0)으로 돌아감
        if abs(x) < 0.001 and abs(y) < 0.001:
            if self.initialized:
                print("[Skip] SLAM tracking lost (0,0 reset)")
            return

        # 첫 유효 좌표 초기화
=======
        # [필터 1] (0,0) 원점 리셋 무시 (SLAM 트래킹 로스트 방지)
        if abs(x) < 0.001 and abs(y) < 0.001:
            if self.initialized:
                # print("[Skip] SLAM tracking lost (0,0 reset)")
                pass
            return

>>>>>>> 3ba0dc4868ca15d0da3a7e78bdbedcdd7d0bbdd2
        if not self.initialized:
            self.last_x = x
            self.last_y = y
            self.initialized = True
            print(f"[Init] First valid pose: x={x:.3f}, y={y:.3f}")

<<<<<<< HEAD
        # [필터 2] 0.3초 간격 제한 (0.1초는 너무 잦음 → 웹 부하)
        if current_time - self.last_sent_time < 0.3:
            return

        # [필터 3] 순간이동 무시 - 1m 이상 점프는 SLAM 오류
        dist = math.sqrt((x - self.last_x)**2 + (y - self.last_y)**2)
        if dist > 1.0:
            print(f"[Skip] Jump detected: {dist:.2f}m (SLAM error)")
            return

        # [필터 4] 3cm 미만 이동은 무시 (떨림 제거, 기존 1cm에서 상향)
=======
        # [필터 2] 0.3초 간격 제한 (웹 부하 감소)
        if current_time - self.last_sent_time < 0.3:
            return

        dist = math.sqrt((x - self.last_x)**2 + (y - self.last_y)**2)

        # [필터 3] 1m 이상 순간이동 = SLAM 오류로 간주하고 무시
        if dist > 1.0:
            print(f"[Skip] Jump detected: {dist:.2f}m")
            return

        # [필터 4] 3cm 미만 떨림은 무시 (제자리 정지 시)
>>>>>>> 3ba0dc4868ca15d0da3a7e78bdbedcdd7d0bbdd2
        if dist < 0.03:
            return

        payload = {
<<<<<<< HEAD
            'x': round(x, 3),
            'y': round(y, 3),
            'state': 'active'
        }

=======
            'x': round(x, 3), 
            'y': round(y, 3), 
            'state': 'active'
        }
        
>>>>>>> 3ba0dc4868ca15d0da3a7e78bdbedcdd7d0bbdd2
        try:
            json_str = json.dumps(payload)
            self.client.publish(self.topic, json_str)
            self.last_sent_time = current_time
            self.last_x = x
            self.last_y = y
            print(f"[Send] {json_str}")
        except Exception as e:
<<<<<<< HEAD
            print(f"[Error] Failed to publish: {e}")
=======
            print(f"[Error] {e}")
>>>>>>> 3ba0dc4868ca15d0da3a7e78bdbedcdd7d0bbdd2

    def destroy_node(self):
        self.client.loop_stop()
        self.client.disconnect()
        super().destroy_node()

<<<<<<< HEAD

=======
>>>>>>> 3ba0dc4868ca15d0da3a7e78bdbedcdd7d0bbdd2
def main(args=None):
    rclpy.init(args=args)
    node = PoseBridgeFix()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
