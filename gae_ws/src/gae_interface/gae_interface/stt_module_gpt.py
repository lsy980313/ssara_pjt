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
from openai import OpenAI
import json
from datetime import datetime

class VoiceAssistant:
    def __init__(self, mp3_dir, api_key):
        print("🤖 AI 모델 로딩 중... (Whisper Base + GPT-4o-mini)")
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 2000
        self.recognizer.dynamic_energy_threshold = False
        self.mp3_dir = mp3_dir
        self.mic_index = self.find_pulse_mic()
        
        # OpenAI 클라이언트 (새 버전)
        self.client = OpenAI(api_key=api_key)
        
        print(f"🎤 사용 마이크 번호: {self.mic_index}")
        print(f"📁 MP3 저장 경로: {self.mp3_dir}")
        print(f"🧠 GPT-4o-mini 연동 완료")

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

    def analyze_command_with_gpt(self, text, latest_object):
        """GPT-4o-mini로 명령 분석"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """너는 시각장애인 안내 로봇이야. 사용자 음성을 분석해서 JSON으로 응답해:
{
  "action": "forward|stop|check|unknown",
  "response": "사용자에게 할 음성 응답",
  "reason": "판단 이유"
}

- forward: 앞으로 가기 (예: "앞으로 가", "출발", "전진", "으로 가", "가")
- stop: 멈추기 (예: "멈춰", "정지", "서")
- check: 전방 확인 (예: "앞에 뭐가 있어?", "뭐 보여?", "장애물 있어?")
- unknown: 이해 못함

현재 전방 상황: """ + latest_object
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=150,
                temperature=0.3,
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"🧠 GPT 분석: {result}")
            return result
            
        except Exception as e:
            print(f"❌ GPT 에러: {e}")
            return {
                "action": "unknown",
                "response": "다시 말씀해주세요",
                "reason": f"GPT 오류: {str(e)}"
            }

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
        
        # OpenAI API 키
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.get_logger().error("❌ OPENAI_API_KEY 환경 변수가 설정되지 않았습니다!")
            raise ValueError("OPENAI_API_KEY required")
        
        pkg_path = "/root/gae_ws/src/gae_interface"
        self.mp3_dir = os.path.join(pkg_path, "mp3")
        os.makedirs(self.mp3_dir, exist_ok=True)
        
        # 대화 로그
        self.log_dir = os.path.join(pkg_path, "conversation_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        self.log_conversation("=== 음성 인터페이스 시작 ===")
        
        # 토픽
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
        
        self.bot = VoiceAssistant(self.mp3_dir, api_key)
        
        self.voice_thread = threading.Thread(target=self.voice_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        
        self.publish_status("준비 완료")
        print("✅ 시각장애인 안내 로봇 준비 완료 (GPT 통합)")

    def log_conversation(self, message):
        """대화 내용 파일에 기록"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"📝 로그 저장: {message}")

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
        else:
            self.latest_object = f"알 수 없는 물체 (클래스 {class_id})"

    def handle_red_light(self):
        msg = "빨간불입니다. 멈춥니다"
        self.log_conversation(f"[YOLO] 빨간불 감지 → {msg}")
        self.publish_response(msg)
        self.bot.speak(msg)
        self.stop_robot()

    def handle_green_light(self):
        msg = "초록불입니다. 출발합니다"
        self.log_conversation(f"[YOLO] 초록불 감지 → {msg}")
        self.publish_response(msg)
        self.bot.speak(msg)

    def handle_stop_marker(self):
        msg = "횡단보도 정지선입니다. 신호를 확인하세요"
        self.log_conversation(f"[YOLO] 정지 마커 감지 → {msg}")
        self.publish_response(msg)
        self.bot.speak(msg)
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
        """GPT로 음성 명령 처리"""
        self.log_conversation(f"[사용자] {text}")
        
        # GPT 분석
        result = self.bot.analyze_command_with_gpt(text, self.latest_object)
        action = result.get("action", "unknown")
        response = result.get("response", "이해하지 못했습니다")
        reason = result.get("reason", "")
        
        self.log_conversation(f"[GPT 분석] action={action}, reason={reason}")
        self.log_conversation(f"[로봇] {response}")
        
        # 동작 실행
        if action == "forward":
            self.publish_command(f"전진: {text}")
            self.publish_response(response)
            self.bot.speak(response)
            
            test_file = "/root/gae_ws/test_forward.sh"
            if os.path.exists(test_file):
                subprocess.Popen(["bash", test_file])
                self.log_conversation(f"[동작] {test_file} 실행")
                
        elif action == "stop":
            self.publish_command(f"정지: {text}")
            self.publish_response(response)
            self.bot.speak(response)
            self.stop_robot()
            
        elif action == "check":
            self.publish_command(f"전방 확인: {text}")
            self.publish_response(response)
            self.bot.speak(response)
            
        else:
            self.publish_response(response)
            self.bot.speak(response)

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
