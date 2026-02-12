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
import json
import time
from datetime import datetime, timedelta, timezone

# ============================================================
#  [설정] 듣기 모드 선택 (여기만 바꾸면 됩니다!)
#  True  = 똑똑한 모드 (300 + Dynamic) : 작은 소리도 잘 들음, 소음 적응
#  False = 둔감한 모드 (2000 + Fixed)  : 아주 큰 소리만 들음 (시끄러운 곳용)
# ============================================================
USE_SMART_MODE = True  # <--- 현재: 똑똑한 모드 (기본값)

# 자주 사용하는 고정 응답 목록 (시작 시 미리 MP3로 생성)
CACHED_RESPONSES = {
    "네! 말씀하세요.": "cache_ne.mp3",
    "멈추겠습니다.": "cache_stop.mp3",
    "앞으로 갑니다.": "cache_forward.mp3",
    "보호자에게 메시지를 보냈습니다.": "cache_guardian.mp3",
    "빨간불입니다! 정지합니다.": "cache_redlight.mp3",
    "초록불입니다! 출발합니다.": "cache_green.mp3",
    "정지선을 확인했습니다.": "cache_marker.mp3",
}

class VoiceAssistant:
    def __init__(self, mp3_dir):
        print("[System] AI 모델 로딩 중...")

        # [최적화] tiny 모델 사용
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        self.mp3_dir = mp3_dir
        self.mic_index = self.find_pulse_mic()
        print(f"[System] 마이크 번호: {self.mic_index}")

        # ---------------------------------------------------------
        # [설정 적용] 300(Smart) vs 2000(Original) 모드 자동 적용
        # ---------------------------------------------------------
        if USE_SMART_MODE:
            print("MODE: [똑똑한 모드] 켜짐 (감도 300, 소음 적응 ON)")
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.dynamic_energy_adjustment_damping = 0.15
            self.recognizer.dynamic_energy_ratio = 1.5
            self.recognizer.pause_threshold = 0.8
        else:
            print("MODE: [둔감한 모드] 켜짐 (감도 2000, 고정)")
            self.recognizer.energy_threshold = 2000
            self.recognizer.dynamic_energy_threshold = False
            self.recognizer.pause_threshold = 0.6

        # 캐시 생성
        self._build_cache()

    def _build_cache(self):
        """자주 쓰는 응답을 시작 시 한 번만 gTTS로 생성해둠"""
        for text, filename in CACHED_RESPONSES.items():
            filepath = os.path.join(self.mp3_dir, filename)
            if not os.path.exists(filepath):
                try:
                    gTTS(text=text, lang='ko').save(filepath)
                except Exception as e:
                    os.system(f'espeak -v ko "{text}" --stdout | sox - {filepath} 2>/dev/null')

    def find_pulse_mic(self):
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'bluez' in name.lower(): return i
            if 'pulse' in name.lower() or 'default' in name.lower(): return i
        return None

    def play_beep(self, type="start"):
        # [조용함] 비프음 기능은 있지만, listen()에서 호출 안 함
        time.sleep(0.05)
        cmd = "play -n -q synth 0.1 sin 800 vol 0.1" if type == "start" else "play -n -q synth 0.1 sin 600 vol 0.1"
        os.system(f"{cmd} > /dev/null 2>&1")
        time.sleep(0.05)

    def listen(self):
        try:
            mic = sr.Microphone(device_index=self.mic_index, sample_rate=16000)
            with mic as source:
                # [똑똑한 모드일 때만] 주변 소음 0.5초 듣고 환경 적응
                if USE_SMART_MODE:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # [조용함] self.play_beep("start") 제거됨 (소리 안 남)
                # print("👂 듣는 중...")

                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)

                # [조용함] self.play_beep("end") 제거됨
                return audio
        except:
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

        context_words = (
            "싸라, 사라, 자라, 병원, 약국, 싸피, 싹키, 사피, 좌키,"
            "데리러, 젤리로, 데리고, 고자에게, 도와줘, 위치,"
            "지금 몇 시야, 멈췄어, 멈췄니, 앞으로 가, 멈춰, 가줘, 해줘"
        )

        segments, _ = self.model.transcribe(
            wav_buffer,
            language="ko",
            initial_prompt=context_words,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        return " ".join([seg.text for seg in segments]).strip()

    def speak(self, text, filename="response.mp3"):
        print(f"🗣️ 로봇: {text}")
        if text in CACHED_RESPONSES:
            cached_path = os.path.join(self.mp3_dir, CACHED_RESPONSES[text])
            if os.path.exists(cached_path):
                os.system(f"play -q {cached_path} vol 1.0")
                return

        filepath = os.path.join(self.mp3_dir, filename)
        try:
            gTTS(text=text, lang='ko').save(filepath)
            os.system(f"play -q {filepath} vol 1.0")
        except:
            os.system(f'espeak -v ko "{text}" 2>/dev/null')


class VoiceNode(Node):
    def __init__(self):
        super().__init__('voice_node')

        pkg_path = "/root/gae_ws/src/gae_interface"
        self.mp3_dir = os.path.join(pkg_path, "mp3")
        os.makedirs(self.mp3_dir, exist_ok=True)
        self.log_file = os.path.join(pkg_path, "conversation_logs", f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        self.command_pub = self.create_publisher(String, '/gae_interface/voice/command', 10)
        self.status_pub = self.create_publisher(String, '/gae_interface/voice/status', 10)
        self.yolo_sub = self.create_subscription(Int32, '/yolo_detection/class_id', self.yolo_callback, 10)

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        try:
            self.mqtt_client.connect(os.getenv('MQTT_BROKER', 'localhost'), int(os.getenv('MQTT_PORT', '1883')), 60)
            self.mqtt_client.loop_start()
        except: pass

        self.bot = VoiceAssistant(self.mp3_dir)
        self.last_warning_time = 0

        threading.Thread(target=self.voice_loop, daemon=True).start()
        print("[Main] 로봇 음성 시스템 시작")

    def yolo_callback(self, msg):
        class_id = msg.data
        if time.time() - self.last_warning_time < 4.0: return
        if class_id == 0:  # 빨간불
            self.execute_node("stop", "빨간불입니다! 정지합니다.")
            self.last_warning_time = time.time()
        elif class_id == 1:  # 초록불
            self.execute_node("forward", "초록불입니다! 출발합니다.")
            self.last_warning_time = time.time()
        elif class_id == 2:  # 정지선
            self.execute_node("stop", "정지선을 확인했습니다.")
            self.last_warning_time = time.time()

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            try: data = json.loads(payload)
            except: data = {"type": "text", "text": payload}

            if msg.topic == "/gae/map_to_voice":
                msg_type = data.get("type", "")
                if msg_type == "nav_guide":
                    guide_text = data.get("text", "")
                    self.bot.speak(guide_text)
                    self.log_and_send(f"[네비] {guide_text}", "robot")
                    return

                target = data.get("target", "목적지")
                distance = data.get("distance", "")
                if distance: response = f"{target}까지 {distance} 남았습니다."
                else: response = f"{target} 위치를 찾았습니다. 안내를 시작합니다."
                self.bot.speak(response)
                self.log_and_send(f"[로봇] {response}", "robot")

            elif msg.topic == "/gae/web_to_voice":
                self.bot.speak(f"보호자 메시지. {data.get('text', payload)}")
        except: pass

    def on_mqtt_connect(self, client, userdata, flags, rc):
        client.subscribe("/gae/web_to_voice")
        client.subscribe("/gae/map_to_voice")

    def mqtt_publish(self, topic, message, msg_type="conversation"):
        try:
            payload = json.dumps({"type": msg_type, "message": message, "timestamp": datetime.now().isoformat()}, ensure_ascii=False)
            self.mqtt_client.publish(topic, payload)
        except: pass

    def log_and_send(self, message, msg_type="conversation", send_to_web=True):
        kst = timezone(timedelta(hours=9))
        kst_now = datetime.now(kst)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{kst_now.strftime('%H:%M:%S')}] {message}\n")
        if send_to_web:
            self.mqtt_publish("/gae/voice_to_web", message, msg_type)

    def execute_node(self, action, response_text):
        self.bot.speak(response_text)
        self.log_and_send(f"[로봇] {response_text}", "robot")
        node_map = {"forward": "ros2 launch gae_control forward.launch.py", "stop": "ros2 launch gae_control stop.launch.py"}
        if action in node_map:
            try:
                proc = subprocess.Popen(node_map[action].split())
                self.log_and_send(f"[실행] {action} 노드 (PID: {proc.pid})", "action", send_to_web=False)
            except Exception as e:
                self.log_and_send(f"[에러] {action} 실패: {e}", "error", send_to_web=False)

    def publish_status(self, status):
        msg = String(); msg.data = status; self.status_pub.publish(msg)

    def process_command(self, text):
        self.log_and_send(f"[사용자] {text}", "user")

        # 0. Whisper 환각 필터
        if len(set(text.split(','))) <= 2 and text.count(',') >= 2:
            return

        # 1. 긴급 정지
        if any(x in text for x in ['서', '서!', '멈춰', '스톱', '정지', '위험해', '멈췄어', '멈췄니', '그만', '서라']):
            self.execute_node("stop", "멈추겠습니다.")
            return

        # 2. 호출어
        if any(text.startswith(x) for x in ['싸라', '사라', '자라']):
            self.bot.speak("네! 말씀하세요.")
            # 상시 소통을 위해 호출 후 즉시 듣기 모드 진입
            audio = self.bot.listen()
            if audio:
                follow_up = self.bot.transcribe(audio)
                if follow_up and len(follow_up) >= 1:
                    print(f"[Follow-up] {follow_up}")
                    self.process_command(follow_up)
            return

        # 3. 보호자 메시지
        if any(x in text for x in ['데리', '보호자', '도와', '젤리', '탈리', '고자', '연락', '위치']):
            msg_text = "사용자가 호출했습니다."
            if "위치" in text: msg_text = "사용자가 현재 위치를 전송했습니다."
            elif any(x in text for x in ['와', '데리', '젤리']): msg_text = "사용자가 데리러 와달라고 요청했습니다."
            elif any(x in text for x in ['도와', '살려']): msg_text = "긴급 도움 요청!"

            self.mqtt_publish("/gae/voice_to_web", msg_text, "emergency")
            self.bot.speak("보호자에게 메시지를 보냈습니다.")
            self.log_and_send(f"[로봇] {msg_text}", "robot")
            return

        # 4. 시간
        if any(x in text for x in ['시간', '몇 시', '언제']):
            kst = timezone(timedelta(hours=9))
            now = datetime.now(kst)
            response = f"현재 {now.hour}시 {now.minute}분입니다."
            self.bot.speak(response)
            return

        # 5. 장소
        if any(x in text for x in ['병원', '약국', '집', '싸피', '싹키', '사피', '좌키', '은행', '가자', '가줘', '평원']):
            target = "싸피" if any(s in text for s in ['싸피', '싹키', '좌키']) else \
                     ("병원" if any(s in text for s in ['병원', '평원']) else \
                     ("약국" if "약국" in text else \
                     ("집" if "집" in text else "목적지")))

            response = f"{target} 위치를 검색하고 있습니다."
            self.bot.speak(response)
            self.mqtt_publish("/gae/voice_to_map", target, "search")
            return

        # 6. 주행
        if any(x in text for x in ['앞으로', '전진', '출발', '가']):
            self.execute_node("forward", "앞으로 갑니다.")
            return

        # 7. 미인식 (상시 소통이므로 조용히 넘어감 or 짧게 대답)
        # self.bot.speak("다시 한번 말씀해 주세요.")

    def voice_loop(self):
        while rclpy.ok():
            self.publish_status("듣는 중...")
            audio = self.bot.listen()
            if audio:
                self.publish_status("분석 중...")
                text = self.bot.transcribe(audio)
                if text and len(text) >= 1:
                    print(f"[인식] {text}")
                    self.process_command(text)

def main(args=None):
    rclpy.init(args=args)
    node = VoiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
