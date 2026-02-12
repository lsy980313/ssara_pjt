import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

class DepthToWeb(Node):
    def __init__(self):
        super().__init__('depth_to_web_node')
        # 카메라 원본 데이터 구독
        self.subscription = self.create_subscription(Image, '/camera/depth/image_raw', self.listener_callback, 10)
        # 컨벤션에 맞춘 토픽으로 발행
        self.publisher = self.create_publisher(Image, '/gae_perception/camera/depth_web', 10)
        self.bridge = CvBridge()

    def listener_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        # 8비트로 정규화 (웹 브라우저 표시용)
        norm_image = cv2.normalize(cv_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        out_msg = self.bridge.cv2_to_imgmsg(norm_image, encoding='mono8')
        out_msg.header = msg.header
        self.publisher.publish(out_msg)

def main(args=None):
    rclpy.init(args=args)
    node = DepthToWeb()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
