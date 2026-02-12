import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32
from geometry_msgs.msg import Twist
import threading
import speech_recognition as sr
from faster_whisper import WhisperModel
from gtts import gTTS
import os
import io
import wave
import subprocess
import paho.mqtt.client as mqtt
from datetime import datetime

class VoiceAssistant:
    def __init__(self, mp3_dir):
        print("🤖 AI 모델 로딩 중... (Whisper Base + MQTT)")
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 2000
        self.recognizer.dynamic_energy_threshold = False
        self.mp3_dir = mp3_dir
        self.mic_index = self.find_pulse_mic()
        print(f"🎤 사용 마이크 번호: {self.mic_index}")
        print(f"📁 MP3 저장 경로: {self.mp3_dir}")

    def find_pulse_mic(self):
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'bluez' in name.lower():
                return i
            if 'pulse' in name.lower() or 'default' in name.lower():
                return i
        return None

    def listen(self):
        try:
            mic = sr.Microphone(device_index=self.mic_index, sample_rate=16000)
            with mic as source:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                return audio
        except:
            return None

    def transcribe(self, audio):
        if audio is None:
            return None
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(audio.sample_width)
            wav_file.setframerate(audio.sample_rate)
            wav_file.writeframes(audio.frame_data)
        wav_buffer.seek(0)
        
        segments, _ = self.model.transcribe(
            wav_buffer,
            language="ko",
            initial_prompt="시각장애인 안내: 앞으로 가, 멈춰, 앞에 뭐가 있어",
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        return " ".join([seg.text for seg in segments]).strip()

    def speak(self, text, filename="response.mp3"):
        filepath = os.path.join(self.mp3_dir, filename)
        print(f"🗣️ 로봇: {text}")
        try:
            gTTS(text=text, lang='ko').save(filepath)
            os.system(f"play -q {filepath} vol 2.0")
        except:
            pass

class VoiceNode(Node):
    def __init__(self):
        super().__init__('voice_node')
        
        pkg_path = "/root/gae_ws/src/gae_interface"
        self.mp3_dir = os.path.join(pkg_path, "mp3")
        os.makedirs(self.mp3_dir, exist_ok=True)
        
        # 대화 로그
        self.log_dir = os.path.join(pkg_path, "conversation_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        self.log_conversation("=== 음성 인터페이스 시작 (MQTT 통합) ===")
        
        # ROS2 토픽
        self.command_pub = self.create_publisher(String, '/gae_interface/voice/command', 10)
        self.response_pub = self.create_publisher(String, '/gae_interface/voice/response', 10)
        self.status_pub = self.create_publisher(String, '/gae_interface/voice/status', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # YOLO 구독
        self.yolo_sub = self.create_subscription(
            Int32,
            '/yolo_detection/class_id',
            self.yolo_callback,
            10
        )
        
        self.latest_object = "아무것도 없습니다"
        self.latest_class_id = None
        
        # MQTT 클라이언트 설정
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        # MQTT 브로커 연결 (localhost 기본, 필요시 IP 변경)
        mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
        mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
        
        try:
            self.mqtt_client.connect(mqtt_broker, mqtt_port, 60)
            self.mqtt_client.loop_start()
            self.get_logger().info(f"📡 MQTT 연결 성공: {mqtt_broker}:{mqtt_port}")
        except Exception as e:
            self.get_logger().error(f"❌ MQTT 연결 실패: {e}")
        
        self.bot = VoiceAssistant(self.mp3_dir)
        
        self.voice_thread = threading.Thread(target=self.voice_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        
        self.publish_status("준비 완료")
        print("✅ 시각장애인 안내 로봇 준비 완료 (MQTT 통합)")

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT 연결 성공 시 토픽 구독"""
        self.get_logger().info(f"📡 MQTT 연결 코드: {rc}")
        client.subscribe("/gae/web_to_voice")
        self.get_logger().info("📡 구독: /gae/web_to_voice")

    def on_mqtt_message(self, client, userdata, msg):
        """웹에서 온 메시지 처리"""
        try:
            text = msg.payload.decode('utf-8')
            self.get_logger().info(f"📩 웹 메시지: {text}")
            self.log_conversation(f"[웹→음성] {text}")
            
            # TTS로 음성 재생
            self.bot.speak(text, filename="web_message.mp3")
            
            # 웹으로 확인 메시지 전송
            self.mqtt_publish("/gae/voice_to_web", f"[확인] {text}")
            
        except Exception as e:
            self.get_logger().error(f"❌ MQTT 메시지 처리 오류: {e}")

    def mqtt_publish(self, topic, message):
        """MQTT 메시지 발행"""
        try:
            self.mqtt_client.publish(topic, message)
            self.get_logger().info(f"📤 MQTT 발행: {topic} -> {message}")
        except Exception as e:
            self.get_logger().error(f"❌ MQTT 발행 실패: {e}")

    def log_conversation(self, message):
        """대화 내용 파일에 기록"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")

    def yolo_callback(self, msg):
        """YOLO 클래스 ID 수신"""
        class_id = msg.data
        self.latest_class_id = class_id
        
        if class_id == 0:
            self.latest_object = "빨간불"
            self.handle_red_light()
        elif class_id == 1:
            self.latest_object = "초록불"
            self.handle_green_light()
        elif class_id == 2:
            self.latest_object = "횡단보도 정지선"
            self.handle_stop_marker()

    def handle_red_light(self):
        msg = "빨간불입니다. 멈춥니다"
        self.log_conversation(f"[YOLO] 빨간불 감지 → {msg}")
        self.publish_response(msg)
        self.bot.speak(msg)
        self.mqtt_publish("/gae/voice_to_web", f"[YOLO] {msg}")
        self.stop_robot()

    def handle_green_light(self):
        msg = "초록불입니다. 출발합니다"
        self.log_conversation(f"[YOLO] 초록불 감지 → {msg}")
        self.publish_response(msg)
        self.bot.speak(msg)
        self.mqtt_publish("/gae/voice_to_web", f"[YOLO] {msg}")

    def handle_stop_marker(self):
        msg = "횡단보도 정지선입니다. 신호를 확인하세요"
        self.log_conversation(f"[YOLO] 정지 마커 감지 → {msg}")
        self.publish_response(msg)
        self.bot.speak(msg)
        self.mqtt_publish("/gae/voice_to_web", f"[YOLO] {msg}")
        self.stop_robot()

    def stop_robot(self):
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)
        self.log_conversation("[동작] 로봇 정지")

    def publish_status(self, status):
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)

    def publish_command(self, command):
        msg = String()
        msg.data = command
        self.command_pub.publish(msg)

    def publish_response(self, response):
        msg = String()
        msg.data = response
        self.response_pub.publish(msg)

    def process_command(self, text):
        """키워드 기반 음성 명령 처리"""
        self.log_conversation(f"[사용자] {text}")
        
        # 웹으로 대화 내용 전송
        self.mqtt_publish("/gae/voice_to_web", f"[사용자] {text}")
        
        # 1. 전방 확인 (구체적)
        if any(x in text for x in ['뭐가 있어', '뭐 있어', '뭐 보여', '장애물']):
            response = f"앞에 {self.latest_object}가 있습니다"
            self.publish_response(response)
            self.bot.speak(response)
            self.mqtt_publish("/gae/voice_to_web", f"[로봇] {response}")
            
        # 2. 정지 명령
        elif any(x in text for x in ['멈춰', '서', '스톱', '정지']):
            response = "정지합니다"
            self.publish_response(response)
            self.bot.speak(response)
            self.mqtt_publish("/gae/voice_to_web", f"[로봇] {response}")
            self.stop_robot()
            
        # 3. 전진 명령
        elif any(x in text for x in ['앞으로', '전진', '출발']):
            response = "전진합니다"
            self.publish_response(response)
            self.bot.speak(response)
            self.mqtt_publish("/gae/voice_to_web", f"[로봇] {response}")
            
            # 실제 노드 실행 (예시)
            # subprocess.Popen(["ros2", "launch", "gae_bringup", "forward.launch.py"])
            
        else:
            self.log_conversation(f"❌ 명령 불일치: '{text}'")

    def voice_loop(self):
        while rclpy.ok():
            self.publish_status("듣는 중...")
            print("\n👂 듣는 중... (말씀해주세요)")
            
            audio = self.bot.listen()
            
            if audio:
                self.publish_status("분석 중...")
                text = self.bot.transcribe(audio)
                
                if text and len(text) >= 2:
                    self.process_command(text)

def main(args=None):
    os.system("apt-get install -y libsox-fmt-mp3 > /dev/null 2>&1")
    rclpy.init(args=args)
    node = VoiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
