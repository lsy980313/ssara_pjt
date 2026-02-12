import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from ultralytics import YOLO
import cv2
import json
import os
import numpy as np
import message_filters

class InferenceNode(Node):
    def __init__(self):
        super().__init__('inference_node')
        
        # 1. 모델 경로 (엔진 파일)
        self.weights_path = '/root/gae_ws/src/gae_perception/weights/best.engine'
        
        # 2. 모델 로드 (task='detect' 명시 권장)
        if os.path.exists(self.weights_path):
            print(f"[TensorRT] 엔진 로드됨: {self.weights_path}")
            self.model = YOLO(self.weights_path, task='detect') 
        else:
            print(f"[YOLO] 모델 없음. 기본 모델 사용.")
            self.model = YOLO('yolov8n.pt')

        # 3. RGB & Depth 동기화 구독
        self.rgb_sub = message_filters.Subscriber(self, Image, '/camera/color/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')
        
        self.ts = message_filters.ApproximateTimeSynchronizer([self.rgb_sub, self.depth_sub], 10, 0.1)
        self.ts.registerCallback(self.callback)

        # 4. 결과 스피커
        self.pub_json = self.create_publisher(String, '/gae_perception/yolo_result', 1)
        self.pub_img = self.create_publisher(Image, '/gae_perception/yolo_image', 1)
        
        self.bridge = CvBridge()
        
        # 프레임 스킵 (TensorRT는 빨라서 스킵 줄여도 되지만, 일단 안전하게 5 유지)
        self.frame_count = 0
        self.skip_rate = 5 
        
        print(f"[YOLO] 고속 추론 모드 시작 (Skip: {self.skip_rate})")

    def callback(self, rgb_msg, depth_msg):
        self.frame_count += 1
        if self.frame_count % self.skip_rate != 0:
            return

        # 1. 이미지 변환
        cv_image = self.bridge.imgmsg_to_cv2(rgb_msg, desired_encoding='bgr8')
        depth_image = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding='passthrough')

        # 2. 추론 (중요: imgsz=640으로 변경!)
        results = self.model.predict(
            cv_image, 
            device=0, 
            imgsz=640,  # 👈 [핵심 수정] 엔진 크기에 맞춰 640으로 변경
            half=True, 
            verbose=False, 
            conf=0.4 
        )
        
        detected_list = []
        annotated_frame = cv_image.copy()

        # 3. 결과 그리기
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0])
                name = self.model.names[cls_id]
                conf = float(box.conf[0])

                # 중앙점 계산
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                # 거리 측정
                h, w = depth_image.shape
                dist_m = 0.0
                roi_size = 5  # 주변 5픽셀(총 10x10박스)을 봄
                if (cy - roi_size >= 0) and (cy + roi_size < h) and \
                   (cx - roi_size >= 0) and (cx + roi_size < w):
                    
                    # 1. 중심 주변을 잘라냄 (Crop)
                    roi = depth_image[cy-roi_size : cy+roi_size, cx-roi_size : cx+roi_size]
                    
                    # 2. 0이 아닌 유효한 값만 골라냄 (0은 에러값이므로 제외)
                    valid_pixels = roi[roi > 0]
                    
                    if len(valid_pixels) > 0:
                        # 3. 평균 대신 '중간값(median)' 사용 -> 튀는 값 무시 효과 탁월!
                        dist_m = np.median(valid_pixels) / 1000.0
                    else:
                        dist_m = 0.0 # 측정 불가
                else:
                    dist_m = 0.0
                
                # [안전 장치] 60cm(0.6m)보다 가까우면 믿지 마라 (하드웨어 한계)
                if dist_m > 0 and dist_m < 0.6:
                     # (선택) 그냥 0.6으로 퉁치거나, 'Too Close'라고 표시
                     dist_m = 0.5  # "아주 가깝다"는 의미로 고정값

                # 리스트 추가
                detected_list.append({
                    "class": name, 
                    "score": round(conf, 2),
                    "dist_m": round(dist_m, 2)
                })

                # 화면 그리기
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # 점수(%)와 거리(m) 표시
                conf_percent = int(conf * 100)
                
                if dist_m > 0:
                    label = f"{name} {conf_percent}% {dist_m:.2f}m"
                else:
                    label = f"{name} {conf_percent}% (?)"
                
                t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(annotated_frame, (x1, y1 - 20), (x1 + t_size[0], y1), (0, 255, 0), -1)
                cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                
                #cv2.circle(annotated_frame, (cx, cy), 5, (0, 0, 255), -1)

        # 4. 전송
        self.pub_json.publish(String(data=json.dumps(detected_list)))
        self.pub_img.publish(self.bridge.cv2_to_imgmsg(annotated_frame, encoding="bgr8"))

def main():
    rclpy.init()
    rclpy.spin(InferenceNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()