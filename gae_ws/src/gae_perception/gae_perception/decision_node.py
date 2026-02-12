import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import json
import numpy as np
import time

class DecisionNode(Node):
    def __init__(self):
        super().__init__('decision_node')

        # [구독] YOLO 결과 수신
        self.yolo_sub = self.create_subscription(
            String, 
            '/gae_perception/yolo_result', 
            self.yolo_callback, 
            10
        )
        
        self.depth_sub = self.create_subscription(
            Image, 
            '/camera/depth/image_raw', 
            self.depth_callback, 
            10
        )
        
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()
        
        self.dist_center = 99.9
        
        # ★ [핵심] 기억력 변수 추가
        # 빨간불을 마지막으로 본 시간을 기록합니다.
        self.last_red_time = 0.0 
        self.last_green_time = 0.0
        
        # 0.1초마다 판단 (10Hz)
        self.create_timer(0.1, self.control_loop)
        self.get_logger().info("🧠 Decision Node (기억력 강화판) 시작!")

    def depth_callback(self, msg):
        try:
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            h, w = depth_image.shape
            center_crop = depth_image[h//3 : 2*h//3, w//3 : 2*w//3]
            valid = center_crop[center_crop > 0]
            if len(valid) > 0:
                self.dist_center = np.median(valid) / 1000.0
            else:
                self.dist_center = 99.9
        except Exception:
            pass

    def yolo_callback(self, msg):
        """
        YOLO 데이터를 받아서 '마지막으로 본 시간'만 갱신합니다.
        """
        try:
            objects = json.loads(msg.data)
            
            for obj in objects:
                name = obj.get('class', '').lower() 
                
                # 빨간불을 보면 -> 현재 시간을 기록! (도장 쾅!)
                if 'red' in name or 'stop' in name:
                    self.last_red_time = time.time()
                    # self.get_logger().info(f"🚨 빨간불 감지됨! ({name})")
                    
                # 초록불을 보면 -> 현재 시간을 기록!
                elif 'green' in name:
                    self.last_green_time = time.time()
            
        except Exception:
            pass

    def control_loop(self):
        twist = Twist()
        current_time = time.time()
        
        # 1. 장애물 감지 (0.5m 이내 - 너무 예민하지 않게 줄임)
        if self.dist_center < 0.5:
            print(f"[AVOID] 🚧 장애물 감지! ({self.dist_center:.2f}m)")
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        # 2. 신호등 판단 (기억력 사용!)
        # "지금 빨간불이 보여?" 가 아니라
        # "최근 2초 안에 빨간불 본 적 있어?" 라고 물어봅니다.
        elif (current_time - self.last_red_time) < 2.0:
            print(f"[TRAFFIC] 🚨 빨간불 대기 중... (유효시간 2초)")
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            
        # 3. 초록불 판단
        # "최근 1초 안에 초록불 봤어?"
        elif (current_time - self.last_green_time) < 1.0:
            print("[TRAFFIC] 🟢 초록불! 주행합니다.")
            twist.linear.x = 0.1  # 직진 속도
            twist.angular.z = 0.0
            
        # 4. 아무것도 없을 때 (기본 주행)
        else:
            print("[DRIVE] 전방 이상 무. 직진.")
            twist.linear.x = 0.1
            twist.angular.z = 0.0

        self.cmd_pub.publish(twist)

def main():
    rclpy.init()
    node = DecisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()