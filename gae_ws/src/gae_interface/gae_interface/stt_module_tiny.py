import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import threading
import speech_recognition as sr
from faster_whisper import WhisperModel
from gtts import gTTS
import os
import io
import wave

class VoiceAssistant:
    def __init__(self, mp3_dir):
        print("🤖 AI 모델 로딩 중... (Whisper Tiny)")
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 1000
        self.recognizer.dynamic_energy_threshold = True
        self.mp3_dir = mp3_dir
        self.mic_index = self.find_pulse_mic()
        print(f"🎤 사용 마이크 번호: {self.mic_index}")
        print(f"📁 MP3 저장 경로: {self.mp3_dir}")

    def find_pulse_mic(self):
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'pulse' in name.lower() or 'default' in name.lower():
                return i
        return None

    def listen(self):
        try:
            mic = sr.Microphone(device_index=self.mic_index, sample_rate=16000)
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
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
            initial_prompt="로봇 명령어: 앞으로, 멈춰, 장애물 확인"
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
        
        # MP3 저장 디렉토리 설정
        pkg_path = "/root/gae_ws/src/gae_interface"
        self.mp3_dir = os.path.join(pkg_path, "mp3")
        os.makedirs(self.mp3_dir, exist_ok=True)
        
        # 토픽 발행자
        self.command_pub = self.create_publisher(String, '/gae_interface/voice/command', 10)
        self.response_pub = self.create_publisher(String, '/gae_interface/voice/response', 10)
        self.status_pub = self.create_publisher(String, '/gae_interface/voice/status', 10)
        
        self.bot = VoiceAssistant(self.mp3_dir)
        
        self.voice_thread = threading.Thread(target=self.voice_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        
        self.publish_status("준비 완료")
        print("✅ 음성 노드 준비 완료!")

    def publish_status(self, status):
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)
        self.get_logger().info(f"[상태] {status}")

    def publish_command(self, command):
        msg = String()
        msg.data = command
        self.command_pub.publish(msg)
        self.get_logger().info(f"[명령] {command}")

    def publish_response(self, response):
        msg = String()
        msg.data = response
        self.response_pub.publish(msg)
        self.get_logger().info(f"[응답] {response}")

    def voice_loop(self):
        while rclpy.ok():
            self.publish_status("듣는 중...")
            audio = self.bot.listen()
            
            if audio:
                self.publish_status("분석 중...")
                text = self.bot.transcribe(audio)
                
                if text and len(text) > 1:
                    self.publish_command(text)
                    
                    # 간단한 응답 예시
                    response = f"'{text}' 명령을 받았습니다"
                    self.publish_response(response)
                    self.bot.speak(response)

def main(args=None):
    os.system("apt-get install -y libsox-fmt-mp3 > /dev/null 2>&1")
    rclpy.init(args=args)
    node = VoiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
