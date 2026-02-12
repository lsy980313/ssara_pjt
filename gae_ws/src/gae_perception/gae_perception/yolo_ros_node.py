import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import json
import time
import math
import paho.mqtt.client as mqtt

class PoseBridge(Node):
    def __init__(self):
        super().__init__('pose_bridge')
        
        # 1. [중요] 런치 파일에서 주는 파라미터를 받을 준비를 합니다.
        self.declare_parameter('broker_address', '192.168.100.246') # 기본값
        self.declare_parameter('port', 1884)                        # 기본값
        self.declare_parameter('topic', 'robot/pose')               # 기본값

        # 2. 파라미터 값을 변수로 가져옵니다.
        self.broker_address = self.get_parameter('broker_address').get_parameter_value().string_value
        self.port = self.get_parameter('port').get_parameter_value().integer_value
        self.topic = self.get_parameter('topic').get_parameter_value().string_value

        self.subscription = self.create_subscription(
            PoseStamped,
            '/slam_pose', 
            self.listener_callback,
            10
        )
        
        # MQTT 클라이언트 설정
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Jetson_Robot_Bridge")
        
        # 3. 연결 시도 (실패해도 죽지 않고 로그만 남김)
        try:
            print(f"[MQTT] Connecting to {self.broker_address}:{self.port}...")
            self.client.connect(self.broker_address, self.port, 60)
            self.client.loop_start() 
            print(f"[MQTT] Success! Connected to {self.broker_address}:{self.port}")
        except Exception as e:
            print(f"[MQTT] Connection Failed: {e}")
            # 연결 실패해도 노드가 죽지 않게 둡니다. (나중에 재시도 로직을 넣을 수도 있음)

        self.last_sent_time = 0.0
        self.last_x = 0.0
        self.last_y = 0.0

    def listener_callback(self, msg):
        current_time = time.time()
        
        # 좌표 변환 (SLAM 좌표계 -> 웹 표시용)
        # 맵이 너무 크거나 작으면 여기서 숫자를 곱해서 조정 가능
        x = msg.pose.position.x
        y = msg.pose.position.y
        
        # 0.1초 제한 (너무 많이 보내면 웹이 버벅임)
        if current_time - self.last_sent_time < 0.1:
            return
            
        # 1cm 이상 움직였을 때만 전송
        dist = math.sqrt((x - self.last_x)**2 + (y - self.last_y)**2)
        if dist < 0.01:
            return 

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
            # print(f"[Send] {json_str}") # 로그 너무 많으면 주석 처리
            
        except Exception as e:
            # 연결이 끊겨도 에러 뿜고 죽지 않도록 예외 처리
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