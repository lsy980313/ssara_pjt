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

class VoiceAssistant:
    def __init__(self, mp3_dir):
        print("🤖 AI 모델 로딩 중... (고감도 음성 인식)")
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        
        # [충돌 해결] 음성 인식 민감도 설정 (환경 적응형으로 설정)
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8
        
        self.mp3_dir = mp3_dir
        self.mic_index = self.find_pulse_mic()
        print(f"🎤 사용 마이크 번호: {self.mic_index}")

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
                # 주변 소음 적응
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

        # 발음 변형 힌트 (Whisper가 더 잘 알아듣게)
        context_words = (
            "싸라, 사라, 자라, 살아, 따라,"
            "병원, 약국, 집, 은행, 빵집, 카페, 편의점,"
            "싸피, 싹키, 사피, 좌키, 쌓피,"
            "평원, 캬원, 정원, 경원, 헬원, 뱅원,"
            "데리러, 젤리로, 데리고, 고자에게, 도와줘, 위치,"
            "지금 몇 시야, 멈췄어, 멈췄니,"
            "앞으로 가, 멈춰, 가줘, 해줘,"
            "앞에 뭐가 보여, 뭐 있어, 상황,"
            "근처, 어디, 찾아줘"
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
        filepath = os.path.join(self.mp3_dir, filename)
        print(f"🗣️ 로봇: {text}")
        try:
            gTTS(text=text, lang='ko').save(filepath)
            os.system(f"play -q {filepath} vol 1.0")
        except: pass

class VoiceNode(Node):
    def __init__(self):
        super().__init__('voice_node')
        
        pkg_path = "/root/gae_ws/src/gae_interface"
        self.mp3_dir = os.path.join(pkg_path, "mp3")
        os.makedirs(self.mp3_dir, exist_ok=True)
        self.log_file = os.path.join(pkg_path, "conversation_logs", f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        # ROS2 토픽
        self.command_pub = self.create_publisher(String, '/gae_interface/voice/command', 10)
        self.status_pub = self.create_publisher(String, '/gae_interface/voice/status', 10)
        self.yolo_sub = self.create_subscription(Int32, '/yolo_detection/class_id', self.yolo_callback, 10)
        
        # YOLO 상태 초기화 (중요!)
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
        print("✅ 로봇 '싸라' 준비 완료")

    def yolo_callback(self, msg):
        """YOLO 객체 인식 결과 처리"""
        class_id = msg.data
        
        # YOLO 결과 업데이트
        if class_id == 0: 
            self.latest_object = "빨간불"
        elif class_id == 1: 
            self.latest_object = "초록불"
        elif class_id == 2: 
            self.latest_object = "횡단보도 정지선"
        else: 
            self.latest_object = "장애물"
        
        # 빨간불 자동 경고 (3초마다 한 번만)
        if class_id == 0 and time.time() - self.last_warning_time > 3.0:
            self.execute_node("stop", "빨간불입니다! 정지합니다.")
            self.last_warning_time = time.time()

    def on_mqtt_message(self, client, userdata, msg):
        """웹에서 온 메시지 처리"""
        try:
            payload = msg.payload.decode('utf-8')
            try: 
                data = json.loads(payload)
            except: 
                data = {"type": "text", "text": payload}
            
            # 지도 검색 결과
            if msg.topic == "/gae/map_to_voice":
                msg_type = data.get("type", "")
                
                # 네비게이션 안내 (실시간 방향 안내)
                if msg_type == "nav_guide":
                    guide_text = data.get("text", "")
                    self.bot.speak(guide_text)
                    self.log_and_send(f"[네비] {guide_text}", "robot")
                    return

                # 검색 결과
                target = data.get("target", "목적지")
                distance = data.get("distance", "")
                if distance: 
                    response = f"{target}까지 {distance} 남았습니다."
                else: 
                    response = f"{target} 위치를 찾았습니다. 안내를 시작합니다."
                self.bot.speak(response)
                self.log_and_send(f"[로봇] {response}", "robot")

            # 보호자 메시지
            elif msg.topic == "/gae/web_to_voice":
                self.bot.speak(f"보호자 메시지. {data.get('text', payload)}")
        except: 
            pass

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT 연결 성공 시 구독"""
        client.subscribe("/gae/web_to_voice")
        client.subscribe("/gae/map_to_voice")

    def mqtt_publish(self, topic, message, msg_type="conversation"):
        """MQTT 메시지 발행"""
        try:
            payload = json.dumps({
                "type": msg_type, 
                "message": message, 
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)
            self.mqtt_client.publish(topic, payload)
        except: 
            pass

    def log_and_send(self, message, msg_type="conversation", send_to_web=True):
        """로그 저장 + 웹 전송"""
        kst = timezone(timedelta(hours=9))
        kst_now = datetime.now(kst)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{kst_now.strftime('%H:%M:%S')}] {message}\n")
        if send_to_web:
            self.mqtt_publish("/gae/voice_to_web", message, msg_type)

    def execute_node(self, action, response_text):
        """하드웨어 제어 노드 실행"""
        self.bot.speak(response_text)
        self.log_and_send(f"[로봇] {response_text}", "robot")
        
        node_map = {
            "forward": "ros2 launch gae_control forward.launch.py", 
            "stop": "ros2 launch gae_control stop.launch.py"
        }
        
        if action in node_map:
            try: 
                proc = subprocess.Popen(node_map[action].split())
                self.log_and_send(f"[실행] {action} 노드 (PID: {proc.pid})", "action", send_to_web=False)
            except Exception as e: 
                self.log_and_send(f"[에러] {action} 실패: {e}", "error", send_to_web=False)

    def publish_status(self, status):
        """ROS2 상태 토픽 발행"""
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)

    def process_command(self, text):
        """음성 명령 처리"""
        self.log_and_send(f"[사용자] {text}", "user")

        # 1. 🚨 긴급 정지 (최우선)
        if any(x in text for x in ['서', '서!', '멈춰', '스톱', '정지', '위험해']):
            self.execute_node("stop", "멈추겠습니다.")
            return

        # 2. 🐶 호출어
        if any(text.startswith(x) for x in ['싸라', '사라', '자라', '살아', '따라']): 
            self.bot.speak("네!")
            self.log_and_send(f"[로봇] 네!", "robot")
            return

        # 3. 🆘 보호자 연락
        if any(x in text for x in ['데리', '보호자', '도와', '젤리', '탈리', '보고자', '와달', '오라고', '고자', '연락']):
            msg_text = "사용자가 호출했습니다."
            
            if any(x in text for x in ['위치', '어디']): 
                msg_text = "사용자가 현재 위치를 전송했습니다."
            elif any(x in text for x in ['와', '데리', '젤리', '탈리']): 
                msg_text = "사용자가 데리러 와달라고 요청했습니다."
            elif any(x in text for x in ['도와', '살려', '위험']): 
                msg_text = "🚨 사용자가 긴급 도움을 요청했습니다!"
            
            self.mqtt_publish("/gae/voice_to_web", msg_text, "emergency")
            self.bot.speak("보호자에게 메시지를 보냈습니다.")
            self.log_and_send(f"[보호자] {msg_text}", "robot")
            return

        # 4. ⏰ 시간
        if any(x in text for x in ['시간', '몇 시', '언제']):
            kst = timezone(timedelta(hours=9))
            now = datetime.now(kst)
            ampm = "오전" if now.hour < 12 else "오후"
            h = now.hour if now.hour <= 12 else now.hour - 12
            response = f"현재 {ampm} {h}시 {now.minute}분입니다."
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")
            return

        # 5. 🗺️ 장소 검색 (모든 장소 + 근처 검색)
        places = ['병원', '약국', '집', '은행', '빵집', '카페', '편의점', '버스', '정류장', '화장실']
        place_variants = {
            '병원': ['평원', '캬원', '정원', '경원', '헬원', '뱅원'],
            '싸피': ['싸피', '싹키', '사피', '좌키', '쌓피']
        }
        
        # 근처/어디 키워드 또는 특정 장소 언급
        if any(x in text for x in ['근처', '어디', '찾아', '가자', '가줘'] + places):
            target = None
            
            # 장소 매칭
            for place in places:
                if place in text:
                    target = place
                    break
            
            # 변형 발음 매칭
            if not target:
                for standard, variants in place_variants.items():
                    if any(v in text for v in variants):
                        target = standard
                        break
            
            # 장소가 명확하지 않으면 "목적지"
            if not target:
                target = "목적지"
            
            response = f"{target} 위치를 검색하고 있습니다."
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")
            self.mqtt_publish("/gae/voice_to_map", target, "search")
            self.log_and_send(f"[검색] {target}", "search", send_to_web=False)
            return

        # 6. 🚦 전방 확인
        if any(x in text for x in ['뭐가', '뭐 있', '보여', '상황', '앞에']):
            obj = self.latest_object
            if "아무것도" in obj: 
                response = "앞에 아무것도 없습니다."
            else: 
                response = f"앞에 {obj}가 있습니다."
            self.bot.speak(response)
            self.log_and_send(f"[로봇] {response}", "robot")
            return

        # 7. 🚗 주행 명령
        if any(x in text for x in ['앞으로', '전진', '출발', '가']):
            self.execute_node("forward", "앞으로 갑니다.")
            return

        # 8. 이해 못함
        self.bot.speak("다시 말씀해 주세요.")
        self.log_and_send(f"[로봇] 다시 말씀해 주세요 (미인식: {text})", "robot")

    def voice_loop(self):
        """음성 인식 루프"""
        while rclpy.ok():
            self.publish_status("듣는 중...")
            audio = self.bot.listen()
            if audio:
                self.publish_status("분석 중...")
                text = self.bot.transcribe(audio)
                if text and len(text) >= 1: 
                    print(f"📝 인식됨: {text}")
                    self.process_command(text)

def main(args=None):
    rclpy.init(args=args)
    node = VoiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()