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
#  stt_module_fast.py  (stt_module_map.py 기반 최적화 버전)
#  - Whisper tiny (base 대비 ~3배 빠름)
#  - 고정 응답 MP3 캐시 (시작 시 미리 생성 → 재사용)
#  - gTTS 실패 시 espeak 오프라인 fallback
# ============================================================

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
        print("[Fast] AI 모델 로딩 중... (Optimized)")

        # [최적화 1] tiny 모델 사용 (base 대비 ~3배 빠름, 명령어 인식 충분)
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 2000
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.6
        self.mp3_dir = mp3_dir
        self.mic_index = self.find_pulse_mic()
        print(f"[Fast] 마이크 번호: {self.mic_index}")

        # [최적화 2] 고정 응답 미리 캐시
        self._build_cache()

    def _build_cache(self):
        """자주 쓰는 응답을 시작 시 한 번만 gTTS로 생성해둠"""
        for text, filename in CACHED_RESPONSES.items():
            filepath = os.path.join(self.mp3_dir, filename)
            if not os.path.exists(filepath):
                try:
                    gTTS(text=text, lang='ko').save(filepath)
                    print(f"[Cache] 생성 완료: {filename}")
                except Exception as e:
                    # 인터넷 안 되면 espeak로 생성
                    print(f"[Cache] gTTS 실패, espeak 대체: {filename}")
                    os.system(f'espeak -v ko "{text}" --stdout | sox - {filepath} 2>/dev/null')

    def find_pulse_mic(self):
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'bluez' in name.lower(): return i
            if 'pulse' in name.lower() or 'default' in name.lower(): return i
        return None

    def play_beep(self, type="start"):
        time.sleep(0.05)
        cmd = "play -n -q synth 0.1 sin 800 vol 0.1" if type == "start" else "play -n -q synth 0.1 sin 600 vol 0.1"
        os.system(f"{cmd} > /dev/null 2>&1")
        time.sleep(0.05)

    def listen(self):
        try:
            mic = sr.Microphone(device_index=self.mic_index, sample_rate=16000)
            with mic as source:
                audio = self.recognizer.listen(source, phrase_time_limit=5)
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
            "캬원, 평원, 정원, 경원, 헬원, 액수로, 압도도, 앗으로,"
            "데리러, 젤리로, 데리고, 고자에게, 도와줘, 위치,"
            "지금 몇 시야, 멈췄어, 멈췄니,"
            "앞으로 가, 멈춰, 가줘, 해줘"
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
        """[최적화 3] 캐시 히트 → 즉시 재생 / 미스 → gTTS → 실패 시 espeak"""
        print(f"[Fast] 로봇: {text}")

        # 캐시에 있으면 바로 재생 (네트워크 불필요)
        if text in CACHED_RESPONSES:
            cached_path = os.path.join(self.mp3_dir, CACHED_RESPONSES[text])
            if os.path.exists(cached_path):
                os.system(f"play -q {cached_path} vol 1.0")
                return

        # 캐시에 없는 동적 응답 → gTTS 시도
        filepath = os.path.join(self.mp3_dir, filename)
        try:
            gTTS(text=text, lang='ko').save(filepath)
            os.system(f"play -q {filepath} vol 1.0")
        except:
            # [최적화 4] gTTS 실패 (와이파이 끊김) → espeak 오프라인 fallback
            print("[Fast] gTTS 실패 → espeak 오프라인 재생")
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
        print("[Fast] 로봇 '싸라' 준비 완료 (Optimized)")

    def yolo_callback(self, msg):
        class_id = msg.data
        if time.time() - self.last_warning_time < 4.0: return
        if class_id == 0:  # 빨간불 → 정지
            self.execute_node("stop", "빨간불입니다! 정지합니다.")
            self.last_warning_time = time.time()
        elif class_id == 1:  # 초록불 → 출발
            self.execute_node("forward", "초록불입니다! 출발합니다.")
            self.last_warning_time = time.time()
        elif class_id == 2:  # 정지선(토끼) → 정지
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

        # 0. Whisper 환각 필터 (반복 텍스트 무시)
        if len(set(text.split(','))) <= 2 and text.count(',') >= 2:
            self.log_and_send(f"[무시] 반복 감지: {text}", "system", send_to_web=False)
            return

        # 1. 긴급 정지
        if any(x in text for x in ['서', '서!', '멈춰', '스톱', '정지', '위험해', '멈췄어', '멈췄니', '그만', '서라']):
            self.execute_node("stop", "멈추겠습니다.")
            return

        # 2. 호출어 → "네! 말씀하세요" → 다음 명령 대기
        if any(text.startswith(x) for x in ['싸라', '사라', '자라']):
            self.bot.speak("네! 말씀하세요.")
            audio = self.bot.listen()
            if audio:
                follow_up = self.bot.transcribe(audio)
                if follow_up and len(follow_up) >= 1:
                    print(f"[Fast] 후속 인식: {follow_up}")
                    self.process_command(follow_up)
            return

        # 3. 보호자 메시지
        if any(x in text for x in ['데리', '보호자', '도와', '젤리', '탈리', '고자', '연락', '위치']):
            msg_text = "사용자가 호출했습니다."

            if "위치" in text:
                msg_text = "사용자가 현재 위치를 전송했습니다. (광주 싸피 1층)"
            elif any(x in text for x in ['와', '데리', '젤리', '탈리']):
                msg_text = "사용자가 데리러 와달라고 요청했습니다."
            elif any(x in text for x in ['도와', '살려']):
                msg_text = "사용자가 긴급 도움을 요청했습니다!"

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
            self.log_and_send(f"[로봇] {response}", "robot")
            return

        # 5. 장소 (오타 포함)
        if any(x in text for x in ['병원', '약국', '집', '싸피', '싹키', '사피', '좌키', '은행', '가자', '가줘', '평원', '캬원', '정원', '경원', '헬원']):
            target = "싸피" if any(s in text for s in ['싸피', '싹키', '좌키']) else \
                     ("병원" if any(s in text for s in ['병원', '평원', '캬원', '정원', '경원', '헬원']) else \
                     ("약국" if "약국" in text else \
                     ("집" if "집" in text else "목적지")))

            response = f"{target} 위치를 검색하고 있습니다."
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")
            self.mqtt_publish("/gae/voice_to_map", target, "search")
            return

        # 6. 주행 명령 (오타 포함)
        if any(x in text for x in ['앞으로', '전진', '출발', '액수로', '압도도', '앗으로', '아프로']):
            self.execute_node("forward", "앞으로 갑니다.")
            return

        # 7. 현재 위치 질문
        if any(x in text for x in ['어디야', '어디에', '여기 어디', '현재 위치']):
            self.bot.speak("현재 SLAM 기반으로 위치를 추적하고 있습니다.")
            self.log_and_send(f"[로봇] 위치 질문 응답", "robot")
            return

        # 8. 미인식 명령 → 안내 응답
        self.bot.speak("다시 한번 말씀해 주세요.")
        self.log_and_send(f"[미인식] {text}", "system", send_to_web=False)

    def voice_loop(self):
        while rclpy.ok():
            self.publish_status("듣는 중...")
            audio = self.bot.listen()
            if audio:
                self.publish_status("분석 중...")
                text = self.bot.transcribe(audio)
                if text and len(text) >= 1:
                    print(f"[Fast] 인식: {text}")
                    self.process_command(text)


def main(args=None):
    rclpy.init(args=args)
    node = VoiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()