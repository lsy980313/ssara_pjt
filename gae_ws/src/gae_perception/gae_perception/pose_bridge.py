import rclpy
from rclpy.node import Node
# ★ [수정 1] 메시지 타입을 SLAM이 주는 대로 바꿉니다.
from geometry_msgs.msg import PoseWithCovarianceStamped 
import json
import time
import math
import paho.mqtt.client as mqtt

class PoseBridge(Node):
    def __init__(self):
        super().__init__('pose_bridge')
        
        self.declare_parameter('broker_address', '192.168.100.246')
        self.declare_parameter('port', 1884)
        self.declare_parameter('topic', 'robot/pose')

        self.broker_address = self.get_parameter('broker_address').get_parameter_value().string_value
        self.port = self.get_parameter('port').get_parameter_value().integer_value
        self.topic = self.get_parameter('topic').get_parameter_value().string_value

        # ★ [수정 2] 구독할 때도 바뀐 타입을 씁니다.
        self.subscription = self.create_subscription(
            PoseWithCovarianceStamped,
            '/slam_pose', 
            self.listener_callback,
            10
        )
        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Jetson_Robot_Bridge")
        
        try:
            print(f"[MQTT] Connecting to {self.broker_address}:{self.port}...")
            self.client.connect(self.broker_address, self.port, 60)
            self.client.loop_start() 
            print(f"[MQTT] Success! Connected to {self.broker_address}:{self.port}")
        except Exception as e:
            print(f"[MQTT] Connection Failed: {e}")

        self.last_sent_time = 0.0
        self.last_x = 0.0
        self.last_y = 0.0

    def listener_callback(self, msg):
        current_time = time.time()
        
        # ★ [수정 3] 좌표 꺼내는 경로가 한 단계 더 깊어집니다. (.pose가 두 번!)
        # PoseWithCovarianceStamped 구조: msg -> pose(오차포함) -> pose(좌표) -> position -> x
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        
        # 0.1초 쿨타임 (이건 놔두기)
        if current_time - self.last_sent_time < 0.1:
            return
            
        # ★ [수정 4] 1cm 이동 제한을 없애고 싶으면 여기를 주석 처리하세요.
        # (지금은 주석 처리 해뒀습니다. 숨만 쉬어도 보냅니다!)
        # dist = math.sqrt((x - self.last_x)**2 + (y - self.last_y)**2)
        # if dist < 0.01:
        #    return 

        payload = {
            'x': round(x, 2),
            'y': round(y, 2),
            'state': 'active'
        }
        
        try:
            json_str = json.dumps(payload)
            self.client.publish(self.topic, json_str)
            
            self.last_sent_time = current_time
            self.last_x = x
            self.last_y = y
            
            # 로그로 확인 (너무 빠르면 주석 처리)
            # print(f"[Send] {json_str}")
            
        except Exception as e:
            print(f"[Error] Publish failed: {e}")

    def destroy_node(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except:
            pass
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = PoseBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()