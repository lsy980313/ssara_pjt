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
#  stt_module_fast.py (Integrated Version)
#  - Base: HEAD (Whisper tiny + MP3 Caching for Speed)
#  - Feature: Remote (Dynamic Mic, Map Search, YOLO, Nav)
# ============================================================

# 자주 사용하는 고정 응답 (속도 향상용 캐시)
CACHED_RESPONSES = {
    "네! 말씀하세요.": "cache_ne.mp3",
    "네!": "cache_ne_short.mp3",
    "멈추겠습니다.": "cache_stop.mp3",
    "앞으로 갑니다.": "cache_forward.mp3",
    "보호자에게 메시지를 보냈습니다.": "cache_guardian.mp3",
    "빨간불입니다! 정지합니다.": "cache_redlight.mp3",
    "초록불입니다! 출발합니다.": "cache_green.mp3",
    "정지선을 확인했습니다.": "cache_marker.mp3",
    "다시 말씀해 주세요.": "cache_retry.mp3",
    "앞에 아무것도 없습니다.": "cache_nothing.mp3",
    "현재 SLAM 기반으로 위치를 추적하고 있습니다.": "cache_slam.mp3"
}

class VoiceAssistant:
    def __init__(self, mp3_dir):
        print("[Fast] AI 모델 로딩 중... (Tiny + Optimized)")
        # [최적화 1] tiny 모델 사용
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")

        self.recognizer = sr.Recognizer()
        # [기능 1] 마이크 감도 설정 (Remote의 Dynamic 설정 채택 - 소음 환경 대응)
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8
        
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
                except Exception as e:
                    # 인터넷 안 되면 espeak로 생성
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
                # [기능 2] 주변 소음 적응 (Remote)
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                self.play_beep("start")
                print("👂 말씀하세요...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                self.play_beep("end")
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

        # [기능 3] 통합된 단어 힌트
        context_words = (
            "싸라, 사라, 자라, 병원, 약국, 집, 싸피, 싹키, 사피, 좌키,"
            "데리러, 젤리로, 도와줘, 위치, 정지, 출발,"
            "앞으로 가, 멈춰, 검색, 찾아줘, 어디야, 편의점, 은행,"
            "앞에 뭐가 보여, 상황, 근처"
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
        print(f"🗣️ 로봇: {text}")

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

        # ROS2 토픽
        self.command_pub = self.create_publisher(String, '/gae_interface/voice/command', 10)
        self.status_pub = self.create_publisher(String, '/gae_interface/voice/status', 10)
        self.yolo_sub = self.create_subscription(Int32, '/yolo_detection/class_id', self.yolo_callback, 10)
        
        # [기능 4] YOLO 상태 변수 (Remote)
        self.latest_object = "아무것도 없습니다"
        self.last_warning_time = 0
        
        # MQTT 설정
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        try:
            self.mqtt_client.connect(os.getenv('MQTT_BROKER', 'localhost'), int(os.getenv('MQTT_PORT', '1883')), 60)
            self.mqtt_client.loop_start()
        except: pass

        self.bot = VoiceAssistant(self.mp3_dir)
        
        threading.Thread(target=self.voice_loop, daemon=True).start()
        print("✅ 로봇 '싸라' 준비 완료 (Fast + Features)")

    def yolo_callback(self, msg):
        class_id = msg.data
        # [기능 4] 객체 정보 업데이트
        if class_id == 0: self.latest_object = "빨간불"
        elif class_id == 1: self.latest_object = "초록불"
        elif class_id == 2: self.latest_object = "횡단보도 정지선"
        else: self.latest_object = "장애물"

        # 빨간불 자동 멈춤
        if class_id == 0 and time.time() - self.last_warning_time > 3.0:
            self.execute_node("stop", "빨간불입니다! 정지합니다.")
            self.last_warning_time = time.time()

    def on_mqtt_connect(self, client, userdata, flags, rc):
        client.subscribe("/gae/web_to_voice")
        client.subscribe("/gae/map_to_voice")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            try: data = json.loads(payload)
            except: data = {"type": "text", "text": payload}

            if msg.topic == "/gae/map_to_voice":
                msg_type = data.get("type", "")
                
                # [기능 5] 네비게이션 가이드 (Remote)
                if msg_type == "nav_guide":
                    guide_text = data.get("text", "")
                    self.bot.speak(guide_text)
                    self.log_and_send(f"[네비] {guide_text}", "robot")
                    return

                target = data.get("target", "목적지")
                distance = data.get("distance", "")
                response = f"{target}까지 {distance} 남았습니다." if distance else f"{target} 위치를 찾았습니다."
                self.bot.speak(response)
                self.log_and_send(f"[로봇] {response}", "robot")

            elif msg.topic == "/gae/web_to_voice":
                self.bot.speak(f"보호자 메시지. {data.get('text', payload)}")
        except: pass

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

        # 0. Whisper 환각 필터 (HEAD)
        if len(set(text.split(','))) <= 2 and text.count(',') >= 2:
            self.log_and_send(f"[무시] 반복 감지: {text}", "system", send_to_web=False)
            return

        # 1. 긴급 정지
        if any(x in text for x in ['서', '서!', '멈춰', '스톱', '정지', '위험해', '그만']):
            self.execute_node("stop", "멈추겠습니다.")
            return

        # 2. 호출어
        if any(text.startswith(x) for x in ['싸라', '사라', '자라']):
            self.bot.speak("네! 말씀하세요.")
            # 후속 명령 대기 (HEAD 방식)
            audio = self.bot.listen()
            if audio:
                follow_up = self.bot.transcribe(audio)
                if follow_up and len(follow_up) >= 1:
                    print(f"[Fast] 후속 인식: {follow_up}")
                    self.process_command(follow_up)
            return

        # 3. 보호자/위치
        if any(x in text for x in ['데리', '보호자', '도와', '젤리', '위치', '어디', '연락']):
            msg_text = "사용자가 호출했습니다."
            if "위치" in text: msg_text = "사용자가 현재 위치를 전송했습니다."
            elif "도와" in text: msg_text = "🚨 긴급 도움 요청!"
            elif any(x in text for x in ['와', '데리']): msg_text = "사용자가 데리러 와달라고 요청했습니다."
            
            self.mqtt_publish("/gae/voice_to_web", msg_text, "emergency")
            self.bot.speak("보호자에게 메시지를 보냈습니다.")
            return

        # 4. 시간 (Remote 방식 - AM/PM)
        if any(x in text for x in ['시간', '몇 시', '언제']):
            kst = timezone(timedelta(hours=9))
            now = datetime.now(kst)
            ampm = "오전" if now.hour < 12 else "오후"
            h = now.hour if now.hour <= 12 else now.hour - 12
            response = f"현재 {ampm} {h}시 {now.minute}분입니다."
            self.bot.speak(response)
            return

        # 5. 장소 검색 (Remote의 강력한 검색 기능)
        places = ['병원', '약국', '집', '은행', '빵집', '카페', '편의점', '버스', '정류장', '싸피']
        if any(x in text for x in ['근처', '어디', '찾아', '가자'] + places):
            target = next((p for p in places if p in text), "목적지")
            response = f"{target} 위치를 검색하고 있습니다."
            self.bot.speak(response)
            self.mqtt_publish("/gae/voice_to_map", target, "search")
            return

        # 6. 전방 상황 (YOLO) - "앞에 뭐 있어?" (Remote)
        if any(x in text for x in ['뭐가', '뭐 있', '보여', '상황', '앞에']):
            self.bot.speak(f"앞에 {self.latest_object}가 있습니다.")
            return

        # 7. 주행 명령
        if any(x in text for x in ['앞으로', '전진', '출발']):
            self.execute_node("forward", "앞으로 갑니다.")
            return

        # 8. 현재 위치 질문 (SLAM - HEAD)
        if any(x in text for x in ['어디야', '여기 어디', '현재 위치']):
            self.bot.speak("현재 SLAM 기반으로 위치를 추적하고 있습니다.")
            return

        self.bot.speak("다시 말씀해 주세요.")

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