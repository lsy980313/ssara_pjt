import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import threading
import time
import re
import speech_recognition as sr
from faster_whisper import WhisperModel
from gtts import gTTS
import os
import io
import wave
import subprocess

class VoiceAssistant:
    def __init__(self):
        print("🤖 AI 모델 로딩 중... (Whisper Tiny)")
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        
        # 🔥 [수정 1] 잡음 감지 민감도 조절 (수치가 높을수록 둔감해짐)
        self.recognizer.energy_threshold = 1000 
        self.recognizer.dynamic_energy_threshold = True
        
        self.mic_index = self.find_pulse_mic()
        print(f"🎤 사용 마이크 번호: {self.mic_index}")

    def find_pulse_mic(self):
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'pulse' in name or 'default' in name:
                return i
        return 24 # 기본값

    def listen(self):
        try:
            mic = sr.Microphone(device_index=self.mic_index, sample_rate=16000)
            with mic as source:
                # 배경 소음 측정 시간을 1초로 늘림
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                return audio
        except sr.WaitTimeoutError:
            return None
        except Exception:
            return None

    def transcribe(self, audio):
        if audio is None: return None
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(audio.sample_width)
            wav_file.setframerate(audio.sample_rate)
            wav_file.writeframes(audio.frame_data)
        wav_buffer.seek(0)
        
        # 🔥 [수정 2] 한국어 전용 프롬프트 추가 (정확도 향상)
        segments, _ = self.model.transcribe(
            wav_buffer, 
            language="ko",
            initial_prompt="이것은 로봇 명령어입니다. 앞으로 가, 멈춰, 장애물 확인."
        )
        return " ".join([seg.text for seg in segments]).strip()

    def speak(self, text):
        print(f"🗣️ 로봇: {text}")
        try:
            gTTS(text=text, lang='ko').save("response.mp3")
            os.system("play -q response.mp3 vol 2.0")
        except: pass

class SpotVoiceNode(Node):
    def __init__(self):
        super().__init__('spot_voice_node')
        self.cmd_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.yolo_subscription = self.create_subscription(String, '/yolo_result', self.yolo_callback, 10)
        self.latest_object = "아무것도 없습니다"
        
        self.bot = VoiceAssistant()
        self.voice_thread = threading.Thread(target=self.voice_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        print("✅ 스팟 보이스 노드 준비 완료!")

    def yolo_callback(self, msg):
        self.latest_object = msg.data

    def process_command(self, text):
        print(f"📝 인식됨: {text}")
        
        # 🔥 [수정 3] 발음이 뭉개져도 알아듣도록 키워드 확장
        
        # 1. 이동 명령 (앞으로, 전진, 앗주로, 가자)
        if any(x in text for x in ['앞으로', '전진', '가자', '앗주로', '출발']):
            numbers = re.findall(r'\d+', text)
            dist = int(numbers[0]) if numbers else 10 # 기본 10m
            
            self.bot.speak(f"{dist}미터 전진 노드를 실행합니다.")
            print(f"🚀 [ACTION] ros2 launch gae_bringup run.launch.py distance:={dist}")
            # 실제 연동 시 아래 주석 해제
            # subprocess.Popen(["ros2", "launch", "gae_bringup", "run.launch.py"])
            
        # 2. 네비게이션 (약국, 브이슬램)
        elif any(x in text for x in ['약국', '브이슬램', '슬램', '지도']):
            self.bot.speak("약국으로 이동하기 위해 슬램을 시작합니다.")
            print("🗺️ [ACTION] ros2 launch gae_bringup vslam.launch.py")
            
        # 3. 시각 정보 (뭐가 있어, 장애물, 장의 물, 보여)
        elif any(x in text for x in ['뭐가', '보여', '장애물', '장의 물']):
            self.bot.speak(f"전방에 {self.latest_object}가 있습니다.")
            
        # 4. 인사
        elif "안녕" in text:
            self.bot.speak("안녕하세요. 명령을 내려주세요.")
            
        else:
            # 🔥 [수정 4] 못 알아들었으면 피드백 주기
            print("❌ 명령 불일치")
            # 너무 시끄러우면 아래 줄 주석 처리
            self.bot.speak("다시 말씀해 주세요.")

    def voice_loop(self):
        while rclpy.ok():
            print("\n👂 듣는 중...")
            audio = self.bot.listen()
            if audio:
                text = self.bot.transcribe(audio)
                if text and len(text) > 1: # 한 글자 환청 무시
                    self.process_command(text)

def main(args=None):
    os.system("apt-get install -y libsox-fmt-mp3 > /dev/null 2>&1")
    rclpy.init(args=args)
    node = SpotVoiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
