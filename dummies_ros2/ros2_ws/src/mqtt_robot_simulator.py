#!/usr/bin/env python3
"""
MQTT Robot Simulator
- Spring Boot 서버와 MQTT로 직접 통신
- 로봇 상태 발행 및 명령 수신

Usage:
    pip install paho-mqtt
    python mqtt_robot_simulator.py
"""

import json
import math
import time
import threading
import sys
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("paho-mqtt 패키지가 필요합니다.")
    print("설치: pip install paho-mqtt")
    sys.exit(1)


class MqttRobotSimulator:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.running = False
        self.connected = False

        # MQTT Topics
        self.topic_status = "robot/status"       # 발행: 로봇 상태
        self.topic_pose = "robot/pose"           # 발행: 로봇 위치
        self.topic_battery = "robot/battery"     # 발행: 배터리 상태
        self.topic_cmd_move = "robot/cmd/move"   # 구독: 이동 명령
        self.topic_cmd_nav = "robot/cmd/nav"     # 구독: 네비게이션 명령

        # 로봇 상태
        self.state = {
            'battery': 85,
            'robot_state': 'IDLE',  # IDLE, MOVING, CHARGING, ERROR, DOCKING
            'is_online': True,
            'x': 0.0,
            'y': 0.0,
            'theta': 0.0,
            'linear_vel': 0.0,
            'angular_vel': 0.0,
            'is_navigating': False,
            'nav_goal_x': 0.0,
            'nav_goal_y': 0.0,
        }

        # MQTT Client
        self.client = mqtt.Client(client_id='robot-simulator', protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def log(self, level, msg):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        colors = {
            'INFO': '\033[92m',
            'WARN': '\033[93m',
            'ERROR': '\033[91m',
            'RECV': '\033[96m',
            'SEND': '\033[95m',
        }
        reset = '\033[0m'
        color = colors.get(level, '')
        print(f"{color}[{timestamp}] [{level}] {msg}{reset}")

    def connect(self):
        """MQTT 브로커 연결"""
        self.log('INFO', f'MQTT 브로커 연결 시도: {self.broker_host}:{self.broker_port}')
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
        except Exception as e:
            self.log('ERROR', f'연결 실패: {e}')
            return False
        return True

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            self.log('INFO', '=' * 60)
            self.log('INFO', 'MQTT 브로커 연결 성공!')
            self.log('INFO', '=' * 60)

            # 명령 토픽 구독
            client.subscribe(self.topic_cmd_move, qos=1)
            client.subscribe(self.topic_cmd_nav, qos=1)
            self.log('INFO', f'[Subscribe] {self.topic_cmd_move}, {self.topic_cmd_nav}')

            # 발행 시작
            self.start_publishers()
        else:
            self.log('ERROR', f'연결 실패, 코드: {rc}')

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.log('WARN', 'MQTT 브로커 연결 해제')

    def on_message(self, client, userdata, msg):
        """메시지 수신 처리"""
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
        except json.JSONDecodeError:
            payload = msg.payload.decode('utf-8')

        self.log('RECV', f'[{topic}] {payload}')

        if topic == self.topic_cmd_move:
            self.handle_cmd_move(payload)
        elif topic == self.topic_cmd_nav:
            self.handle_cmd_nav(payload)

    def handle_cmd_move(self, payload):
        """이동 명령 처리"""
        action = payload.get('action', '') if isinstance(payload, dict) else payload

        if action == 'home':
            self.log('INFO', '[명령] 집으로 이동!')
            self.state['nav_goal_x'] = 0.0
            self.state['nav_goal_y'] = 0.0
            self.state['is_navigating'] = True
            self.state['robot_state'] = 'MOVING'

        elif action == 'stop':
            self.log('WARN', '[명령] 긴급 정지!')
            self.state['linear_vel'] = 0.0
            self.state['angular_vel'] = 0.0
            self.state['is_navigating'] = False
            self.state['robot_state'] = 'IDLE'

        elif action == 'dock':
            self.log('INFO', '[명령] 충전 도킹!')
            self.state['nav_goal_x'] = -1.0
            self.state['nav_goal_y'] = 0.0
            self.state['is_navigating'] = True
            self.state['robot_state'] = 'DOCKING'

        elif action == 'forward':
            self.log('INFO', '[명령] 전진')
            self.state['linear_vel'] = 0.3
            self.state['angular_vel'] = 0.0
            self.state['robot_state'] = 'MOVING'

        elif action == 'backward':
            self.log('INFO', '[명령] 후진')
            self.state['linear_vel'] = -0.3
            self.state['angular_vel'] = 0.0
            self.state['robot_state'] = 'MOVING'

        elif action == 'left':
            self.log('INFO', '[명령] 좌회전')
            self.state['linear_vel'] = 0.0
            self.state['angular_vel'] = 0.5
            self.state['robot_state'] = 'MOVING'

        elif action == 'right':
            self.log('INFO', '[명령] 우회전')
            self.state['linear_vel'] = 0.0
            self.state['angular_vel'] = -0.5
            self.state['robot_state'] = 'MOVING'

        else:
            self.log('WARN', f'[명령] 알 수 없는 action: {action}')

    def handle_cmd_nav(self, payload):
        """네비게이션 명령 처리"""
        x = payload.get('x', 0.0)
        y = payload.get('y', 0.0)
        self.log('INFO', f'[명령] 좌표 이동: ({x}, {y})')

        self.state['nav_goal_x'] = x
        self.state['nav_goal_y'] = y
        self.state['is_navigating'] = True
        self.state['robot_state'] = 'MOVING'

    def start_publishers(self):
        """발행 타이머 시작"""
        self.running = True

        # 시뮬레이션 업데이트 (100ms)
        self.start_timer(0.1, self.update_simulation)

        # 상태 발행 (1000ms)
        self.start_timer(1.0, self.publish_status)

        # 위치 발행 (500ms)
        self.start_timer(0.5, self.publish_pose)

        # 배터리 발행 (5000ms)
        self.start_timer(5.0, self.publish_battery)

        self.log('INFO', '[Publishers] 모든 발행 타이머 시작')

    def start_timer(self, interval, callback):
        def timer_loop():
            while self.running:
                if self.connected:
                    callback()
                time.sleep(interval)

        t = threading.Thread(target=timer_loop)
        t.daemon = True
        t.start()

    def publish_status(self):
        """로봇 상태 발행"""
        payload = {
            'battery': int(self.state['battery']),
            'state': self.state['robot_state'],
            'isOnline': self.state['is_online']
        }
        self.client.publish(self.topic_status, json.dumps(payload), qos=1)
        self.log('SEND', f'[{self.topic_status}] battery={payload["battery"]}%, state={payload["state"]}')

    def publish_pose(self):
        """로봇 위치 발행"""
        payload = {
            'x': round(self.state['x'], 2),
            'y': round(self.state['y'], 2),
            'theta': round(self.state['theta'], 2)
        }
        self.client.publish(self.topic_pose, json.dumps(payload), qos=1)

    def publish_battery(self):
        """배터리 상태 발행"""
        payload = {
            'percentage': self.state['battery'] / 100.0,
            'voltage': 11.0 + (self.state['battery'] / 100.0 * 1.6),
            'charging': self.state['robot_state'] == 'CHARGING'
        }
        self.client.publish(self.topic_battery, json.dumps(payload), qos=1)

    def update_simulation(self):
        """시뮬레이션 업데이트"""
        dt = 0.1

        # 속도에 따른 위치 업데이트
        if self.state['linear_vel'] != 0.0 or self.state['angular_vel'] != 0.0:
            self.state['theta'] += self.state['angular_vel'] * dt
            self.state['theta'] = self.state['theta'] % (2 * math.pi)
            self.state['x'] += self.state['linear_vel'] * math.cos(self.state['theta']) * dt
            self.state['y'] += self.state['linear_vel'] * math.sin(self.state['theta']) * dt

        # 네비게이션 자동 이동
        if self.state['is_navigating']:
            dx = self.state['nav_goal_x'] - self.state['x']
            dy = self.state['nav_goal_y'] - self.state['y']
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 0.1:
                target_theta = math.atan2(dy, dx)
                self.state['theta'] = target_theta
                speed = min(0.3, distance)
                self.state['x'] += speed * math.cos(target_theta) * dt
                self.state['y'] += speed * math.sin(target_theta) * dt
                self.state['linear_vel'] = speed
            else:
                self.state['x'] = self.state['nav_goal_x']
                self.state['y'] = self.state['nav_goal_y']
                self.state['linear_vel'] = 0.0
                self.state['is_navigating'] = False

                if self.state['robot_state'] == 'DOCKING':
                    self.state['robot_state'] = 'CHARGING'
                    self.log('INFO', '[시뮬레이션] 도킹 완료, 충전 시작!')
                else:
                    self.state['robot_state'] = 'IDLE'
                    self.log('INFO', '[시뮬레이션] 목표 도달!')

        # 배터리 시뮬레이션
        if self.state['robot_state'] == 'CHARGING':
            self.state['battery'] = min(100, self.state['battery'] + 0.5)
            if self.state['battery'] >= 100:
                self.state['robot_state'] = 'IDLE'
                self.log('INFO', '[시뮬레이션] 충전 완료!')
        elif self.state['robot_state'] == 'MOVING':
            self.state['battery'] = max(0, self.state['battery'] - 0.02)

    def stop(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()


def main():
    print()
    print("=" * 60)
    print("  MQTT Robot Simulator")
    print("  Spring Boot 서버와 직접 통신")
    print("=" * 60)
    print()

    simulator = MqttRobotSimulator()

    if not simulator.connect():
        print("MQTT 브로커에 연결할 수 없습니다.")
        print("mosquitto 또는 다른 MQTT 브로커가 실행 중인지 확인하세요.")
        sys.exit(1)

    try:
        print("Ctrl+C로 종료")
        print()
        while True:
            time.sleep(1)
            if simulator.connected:
                state = simulator.state
                print(f"\r[상태] 배터리: {state['battery']:.0f}% | "
                      f"위치: ({state['x']:.2f}, {state['y']:.2f}) | "
                      f"상태: {state['robot_state']:<10}", end='', flush=True)
    except KeyboardInterrupt:
        print()
        print("종료 중...")
        simulator.stop()


if __name__ == '__main__':
    main()
