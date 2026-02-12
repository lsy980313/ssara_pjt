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

class VoiceAssistant:
    def __init__(self, mp3_dir):
        print("🤖 AI 모델 로딩 중... (Whisper Base)")
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
        
        # 발행 토픽
        self.command_pub = self.create_publisher(String, '/gae_interface/voice/command', 10)
        self.response_pub = self.create_publisher(String, '/gae_interface/voice/response', 10)
        self.status_pub = self.create_publisher(String, '/gae_interface/voice/status', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 🔥 YOLO 결과 구독 (클래스 ID)
        self.yolo_sub = self.create_subscription(
            Int32,
            '/yolo_detection/class_id',  # YOLO 클래스 ID 토픽
            self.yolo_callback,
            10
        )
        
        self.latest_object = "아무것도 없습니다"
        self.latest_class_id = None
        
        self.bot = VoiceAssistant(self.mp3_dir)
        
        self.voice_thread = threading.Thread(target=self.voice_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        
        self.publish_status("준비 완료")
        print("✅ 시각장애인 안내 로봇 준비 완료!")

    def yolo_callback(self, msg):
        """YOLO 클래스 ID 수신"""
        class_id = msg.data
        self.latest_class_id = class_id
        
        # 클래스별 처리
        if class_id == 0:  # 빨간불
            self.latest_object = "빨간불"
            self.handle_red_light()
        elif class_id == 1:  # 초록불
            self.latest_object = "초록불"
            self.handle_green_light()
        elif class_id == 2:  # 정지 마커
            self.latest_object = "횡단보도 정지선"
            self.handle_stop_marker()
        else:
            self.latest_object = f"알 수 없는 물체 (클래스 {class_id})"

    def handle_red_light(self):
        """빨간불 → 자동 정지"""
        self.publish_response("빨간불입니다. 멈춥니다")
        self.bot.speak("빨간불입니다. 멈춥니다")
        self.stop_robot()
        self.get_logger().info("[YOLO] 빨간불 감지 → 정지")

    def handle_green_light(self):
        """초록불 → 자동 출발"""
        self.publish_response("초록불입니다. 출발합니다")
        self.bot.speak("초록불입니다. 출발합니다")
        # 실제 전진 노드 실행
        try:
            subprocess.Popen(["ros2", "launch", "gae_bringup", "forward.launch.py"])
            self.get_logger().info("[YOLO] 초록불 감지 → forward.launch.py 실행")
        except Exception as e:
            self.get_logger().error(f"[ERROR] forward.launch.py 실행 실패: {e}")

    def handle_stop_marker(self):
        """정지 마커 → 정지 + 안내"""
        self.publish_response("횡단보도 정지선입니다. 신호를 확인하세요")
        self.bot.speak("횡단보도 정지선입니다. 신호를 확인하세요")
        self.stop_robot()
        self.get_logger().info("[YOLO] 정지 마커 감지 → 정지")

    def stop_robot(self):
        """로봇 정지"""
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_vel_pub.publish(twist)
        self.get_logger().info("[동작] 정지")

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
        """음성 명령 처리"""
        print(f"📝 인식됨: '{text}'")
        
        if len(text) < 2:
            return
        
        # 1. 전진 명령
        if any(x in text for x in ['앞으로', '전진', '가', '출발', '고']):
            self.publish_command(f"전진: {text}")
            self.publish_response("전진합니다")
            self.bot.speak("전진합니다")
            
            # 🔥 테스트용 더미 노드 실행
            test_file = "/root/gae_ws/test_forward.sh"
            if os.path.exists(test_file):
                subprocess.Popen(["bash", test_file])
                self.get_logger().info(f"[TEST] {test_file} 실행")
            else:
                self.get_logger().warn(f"[TEST] {test_file} 없음")
            
        # 2. 정지 명령
        elif any(x in text for x in ['멈춰', '서', '스톱', '정지']):
            self.publish_command(f"정지: {text}")
            self.publish_response("정지합니다")
            self.bot.speak("정지합니다")
            self.stop_robot()
            
        # 3. 전방 확인 🔥 수정
        elif any(x in text for x in ['뭐가', '보여', '앞에', '있어']):
            self.publish_command(f"전방 확인: {text}")
            response = f"앞에 {self.latest_object}가 있습니다"
            self.publish_response(response)
            self.bot.speak(response)
        
        else:
            print(f"❌ 명령 불일치: '{text}'")

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
