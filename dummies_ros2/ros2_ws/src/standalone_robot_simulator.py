#!/usr/bin/env python3
"""
Standalone Robot Simulator (ROS 2 없이 동작)
- ROSBridge JSON 메시지 규격 완벽 준수
- WebSocket으로 rosbridge_server 또는 Spring Boot 서버와 직접 통신
- ROS 2 설치 없이 Python만으로 테스트 가능

Usage:
    pip install websocket-client
    python standalone_robot_simulator.py
"""

import json
import math
import time
import threading
import sys
from datetime import datetime

try:
    import websocket
except ImportError:
    print("websocket-client 패키지가 필요합니다.")
    print("설치: pip install websocket-client")
    sys.exit(1)


class RobotSimulator:
    """
    ROSBridge 규격을 준수하는 스탠드얼론 로봇 시뮬레이터
    """

    def __init__(self, ws_url="ws://localhost:9090"):
        self.ws_url = ws_url
        self.ws = None
        self.running = False
        self.connected = False

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
            'bumper_pressed': False,
            'is_navigating': False,
            'nav_goal_x': 0.0,
            'nav_goal_y': 0.0,
        }

        # 타이머 스레드들
        self.timers = []

    def log(self, level, msg):
        """로그 출력"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        colors = {
            'INFO': '\033[92m',    # Green
            'WARN': '\033[93m',    # Yellow
            'ERROR': '\033[91m',   # Red
            'DEBUG': '\033[94m',   # Blue
            'RECV': '\033[96m',    # Cyan
            'SEND': '\033[95m',    # Magenta
        }
        reset = '\033[0m'
        color = colors.get(level, '')
        print(f"{color}[{timestamp}] [{level}] {msg}{reset}")

    def connect(self):
        """WebSocket 연결"""
        self.log('INFO', f'WebSocket 연결 시도: {self.ws_url}')

        def on_open(ws):
            self.connected = True
            self.log('INFO', '=' * 60)
            self.log('INFO', 'WebSocket 연결 성공!')
            self.log('INFO', '=' * 60)
            self.advertise_topics()
            self.start_publishers()

        def on_message(ws, message):
            self.handle_message(message)

        def on_error(ws, error):
            self.log('ERROR', f'WebSocket 오류: {error}')

        def on_close(ws, close_status_code, close_msg):
            self.connected = False
            self.log('WARN', 'WebSocket 연결 종료')

        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        # WebSocket 연결 (별도 스레드)
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

    def advertise_topics(self):
        """토픽 Advertise (발행 등록)"""
        topics = [
            ('/robot/status', 'std_msgs/msg/String'),
            ('/robot/pose', 'geometry_msgs/msg/Pose2D'),
            ('/battery_state', 'sensor_msgs/msg/BatteryState'),
            ('/odom', 'nav_msgs/msg/Odometry'),
            ('/scan', 'sensor_msgs/msg/LaserScan'),
            ('/bumper', 'std_msgs/msg/Bool'),
            ('/camera/image_raw/compressed', 'sensor_msgs/msg/CompressedImage'),
        ]

        for topic, msg_type in topics:
            advertise_msg = {
                "op": "advertise",
                "id": f"advertise:{topic}",
                "topic": topic,
                "type": msg_type
            }
            self.send(advertise_msg)

        self.log('INFO', f'[Advertise] {len(topics)}개 토픽 등록 완료')

    def send(self, msg):
        """메시지 전송"""
        if self.ws and self.connected:
            json_msg = json.dumps(msg)
            self.ws.send(json_msg)
            # 로그는 너무 많으면 생략
            if msg.get('op') == 'publish':
                topic = msg.get('topic', '')
                if topic in ['/robot/status', '/robot/pose']:
                    self.log('SEND', f"[{topic}] 발행")

    def handle_message(self, message):
        """수신 메시지 처리"""
        try:
            msg = json.loads(message)
            op = msg.get('op', '')
            topic = msg.get('topic', '')

            self.log('RECV', f'메시지 수신: op={op}, topic={topic}')

            if op == 'publish' and topic == '/cmd_vel':
                self.handle_cmd_vel(msg.get('msg', {}))

            elif op == 'call_service':
                service = msg.get('service', '')
                call_id = msg.get('id', '')
                self.handle_service_call(service, call_id, msg.get('args', {}))

            elif op == 'send_action_goal':
                action = msg.get('action', '')
                action_id = msg.get('id', '')
                self.handle_action_goal(action, action_id, msg.get('goal', {}))

            elif op == 'cancel_action_goal':
                action = msg.get('action', '')
                self.handle_action_cancel(action)

            elif op == 'subscribe':
                self.log('INFO', f'[Subscribe 요청] topic={topic}')

        except json.JSONDecodeError as e:
            self.log('ERROR', f'JSON 파싱 오류: {e}')

    def handle_cmd_vel(self, msg):
        """
        /cmd_vel 토픽 처리
        """
        linear = msg.get('linear', {})
        angular = msg.get('angular', {})

        linear_x = linear.get('x', 0.0)
        angular_z = angular.get('z', 0.0)

        self.state['linear_vel'] = linear_x
        self.state['angular_vel'] = angular_z

        if linear_x == 0.0 and angular_z == 0.0:
            if self.state['robot_state'] == 'MOVING':
                self.state['robot_state'] = 'IDLE'
            self.log('INFO', '[/cmd_vel] 정지 명령 수신')
        else:
            self.state['robot_state'] = 'MOVING'
            self.log('INFO', f'[/cmd_vel] 속도 명령: linear.x={linear_x:.2f} m/s, angular.z={angular_z:.2f} rad/s')

    def handle_service_call(self, service, call_id, args):
        """
        서비스 호출 처리
        """
        response = {
            "op": "service_response",
            "id": call_id,
            "service": service,
            "values": {},
            "result": True
        }

        if service == '/go_home':
            self.log('INFO', '[Service /go_home] 집으로 복귀 명령!')
            self.state['nav_goal_x'] = 0.0
            self.state['nav_goal_y'] = 0.0
            self.state['is_navigating'] = True
            self.state['robot_state'] = 'MOVING'
            response['values'] = {
                "success": True,
                "message": "Navigating to home position"
            }

        elif service == '/emergency_stop':
            self.log('WARN', '[Service /emergency_stop] 긴급 정지!')
            self.state['linear_vel'] = 0.0
            self.state['angular_vel'] = 0.0
            self.state['is_navigating'] = False
            self.state['robot_state'] = 'IDLE'
            response['values'] = {
                "success": True,
                "message": "Emergency stop executed"
            }

        elif service == '/dock':
            self.log('INFO', '[Service /dock] 충전 도킹 명령!')
            self.state['nav_goal_x'] = -1.0
            self.state['nav_goal_y'] = 0.0
            self.state['is_navigating'] = True
            self.state['robot_state'] = 'DOCKING'
            response['values'] = {
                "success": True,
                "message": "Docking to charging station"
            }

        else:
            self.log('WARN', f'[Service] 알 수 없는 서비스: {service}')
            response['result'] = False
            response['values'] = {
                "success": False,
                "message": f"Unknown service: {service}"
            }

        self.send(response)

    def handle_action_goal(self, action, action_id, goal):
        """
        액션 Goal 처리
        """
        if action == '/navigate_to_pose':
            pose = goal.get('pose', {}).get('pose', {})
            position = pose.get('position', {})
            target_x = position.get('x', 0.0)
            target_y = position.get('y', 0.0)

            self.log('INFO', f'[Action /navigate_to_pose] 목표: x={target_x:.2f}, y={target_y:.2f}')

            self.state['nav_goal_x'] = target_x
            self.state['nav_goal_y'] = target_y
            self.state['is_navigating'] = True
            self.state['robot_state'] = 'MOVING'
            self.current_action_id = action_id

            # Feedback 스레드 시작
            feedback_thread = threading.Thread(
                target=self.send_navigation_feedback,
                args=(action_id, target_x, target_y)
            )
            feedback_thread.daemon = True
            feedback_thread.start()

    def send_navigation_feedback(self, action_id, target_x, target_y):
        """
        네비게이션 Feedback 전송
        """
        while self.state['is_navigating'] and self.running:
            dx = target_x - self.state['x']
            dy = target_y - self.state['y']
            distance = math.sqrt(dx * dx + dy * dy)

            # Feedback 전송
            feedback = {
                "op": "action_feedback",
                "id": action_id,
                "action": "/navigate_to_pose",
                "values": {
                    "current_pose": {
                        "header": {"frame_id": "map"},
                        "pose": {
                            "position": {
                                "x": self.state['x'],
                                "y": self.state['y'],
                                "z": 0.0
                            },
                            "orientation": {
                                "x": 0.0,
                                "y": 0.0,
                                "z": math.sin(self.state['theta'] / 2.0),
                                "w": math.cos(self.state['theta'] / 2.0)
                            }
                        }
                    },
                    "distance_remaining": distance
                }
            }
            self.send(feedback)
            self.log('DEBUG', f'[Feedback] 남은 거리: {distance:.2f}m')

            if distance < 0.1:
                break

            time.sleep(0.5)

        # Result 전송
        if not self.state['is_navigating'] or distance < 0.1:
            result = {
                "op": "action_result",
                "id": action_id,
                "action": "/navigate_to_pose",
                "values": {},
                "status": "SUCCEEDED"
            }
            self.send(result)
            self.log('INFO', '[Action Result] 네비게이션 성공!')

    def handle_action_cancel(self, action):
        """
        액션 취소 처리
        """
        if action == '/navigate_to_pose':
            self.log('WARN', '[Action Cancel] 네비게이션 취소됨')
            self.state['is_navigating'] = False
            self.state['robot_state'] = 'IDLE'
            self.state['linear_vel'] = 0.0
            self.state['angular_vel'] = 0.0

    # =========================================================
    # Publishers
    # =========================================================

    def start_publishers(self):
        """발행 타이머 시작"""
        self.running = True

        # 시뮬레이션 업데이트 (100ms)
        self.start_timer(0.1, self.update_simulation)

        # /robot/status (1000ms)
        self.start_timer(1.0, self.publish_robot_status)

        # /robot/pose (500ms)
        self.start_timer(0.5, self.publish_robot_pose)

        # /battery_state (5000ms)
        self.start_timer(5.0, self.publish_battery_state)

        # /odom (200ms)
        self.start_timer(0.2, self.publish_odom)

        # /bumper (100ms) - 자주 발행하지 않음
        self.start_timer(1.0, self.publish_bumper)

        self.log('INFO', '[Publishers] 모든 발행 타이머 시작')

    def start_timer(self, interval, callback):
        """타이머 시작"""
        def timer_loop():
            while self.running:
                if self.connected:
                    callback()
                time.sleep(interval)

        t = threading.Thread(target=timer_loop)
        t.daemon = True
        t.start()
        self.timers.append(t)

    def get_timestamp(self):
        """ROS 타임스탬프 생성"""
        now = time.time()
        return {
            "sec": int(now),
            "nanosec": int((now % 1) * 1e9)
        }

    def publish_robot_status(self):
        """
        /robot/status 발행
        Message Type: std_msgs/msg/String (JSON)
        """
        status_json = json.dumps({
            'battery': int(self.state['battery']),
            'state': self.state['robot_state'],
            'isOnline': self.state['is_online']
        })

        msg = {
            "op": "publish",
            "topic": "/robot/status",
            "msg": {
                "data": status_json
            }
        }
        self.send(msg)

    def publish_robot_pose(self):
        """
        /robot/pose 발행
        Message Type: geometry_msgs/msg/Pose2D
        """
        msg = {
            "op": "publish",
            "topic": "/robot/pose",
            "msg": {
                "x": self.state['x'],
                "y": self.state['y'],
                "theta": self.state['theta']
            }
        }
        self.send(msg)

    def publish_battery_state(self):
        """
        /battery_state 발행
        Message Type: sensor_msgs/msg/BatteryState
        """
        percentage = self.state['battery'] / 100.0

        # power_supply_status: 1=CHARGING, 2=DISCHARGING, 4=FULL
        if self.state['robot_state'] == 'CHARGING':
            power_status = 1
        elif self.state['battery'] >= 100:
            power_status = 4
        else:
            power_status = 2

        msg = {
            "op": "publish",
            "topic": "/battery_state",
            "msg": {
                "header": {
                    "stamp": self.get_timestamp(),
                    "frame_id": "battery"
                },
                "voltage": 11.0 + (percentage * 1.6),
                "temperature": 25.0,
                "current": 1.5 if self.state['robot_state'] == 'CHARGING' else -0.5,
                "charge": percentage * 10.0,
                "capacity": 10.0,
                "design_capacity": 10.0,
                "percentage": percentage,
                "power_supply_status": power_status,
                "power_supply_health": 1,
                "power_supply_technology": 2,
                "present": True
            }
        }
        self.send(msg)

    def publish_odom(self):
        """
        /odom 발행
        Message Type: nav_msgs/msg/Odometry
        """
        theta = self.state['theta']

        msg = {
            "op": "publish",
            "topic": "/odom",
            "msg": {
                "header": {
                    "stamp": self.get_timestamp(),
                    "frame_id": "odom"
                },
                "child_frame_id": "base_link",
                "pose": {
                    "pose": {
                        "position": {
                            "x": self.state['x'],
                            "y": self.state['y'],
                            "z": 0.0
                        },
                        "orientation": {
                            "x": 0.0,
                            "y": 0.0,
                            "z": math.sin(theta / 2.0),
                            "w": math.cos(theta / 2.0)
                        }
                    },
                    "covariance": [0.0] * 36
                },
                "twist": {
                    "twist": {
                        "linear": {
                            "x": self.state['linear_vel'],
                            "y": 0.0,
                            "z": 0.0
                        },
                        "angular": {
                            "x": 0.0,
                            "y": 0.0,
                            "z": self.state['angular_vel']
                        }
                    },
                    "covariance": [0.0] * 36
                }
            }
        }
        self.send(msg)

    def publish_bumper(self):
        """
        /bumper 발행
        Message Type: std_msgs/msg/Bool
        """
        msg = {
            "op": "publish",
            "topic": "/bumper",
            "msg": {
                "data": self.state['bumper_pressed']
            }
        }
        self.send(msg)

    # =========================================================
    # Simulation
    # =========================================================

    def update_simulation(self):
        """시뮬레이션 상태 업데이트"""
        dt = 0.1

        # cmd_vel에 의한 이동
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

        # 배터리 시뮬레이션
        if self.state['robot_state'] == 'CHARGING':
            self.state['battery'] = min(100, self.state['battery'] + 0.5)
            if self.state['battery'] >= 100:
                self.state['robot_state'] = 'IDLE'
                self.log('INFO', '[시뮬레이션] 충전 완료!')
        elif self.state['robot_state'] == 'MOVING':
            self.state['battery'] = max(0, self.state['battery'] - 0.01)

    def stop(self):
        """시뮬레이터 종료"""
        self.running = False
        if self.ws:
            self.ws.close()


def main():
    print()
    print("=" * 60)
    print("  Robot Simulator (Standalone - No ROS 2 Required)")
    print("  ROSBridge JSON 메시지 규격 준수")
    print("=" * 60)
    print()

    # WebSocket URL (rosbridge_server 기본 포트)
    ws_url = "ws://localhost:9090"

    print(f"연결 대상: {ws_url}")
    print()
    print("주의: rosbridge_server가 실행 중이어야 합니다.")
    print("  ros2 launch rosbridge_server rosbridge_websocket_launch.xml")
    print()
    print("또는 Spring Boot 서버의 WebSocket 엔드포인트로 변경하세요.")
    print()

    simulator = RobotSimulator(ws_url)
    simulator.connect()

    try:
        print("Ctrl+C로 종료")
        print()
        while True:
            time.sleep(1)
            if simulator.connected:
                state = simulator.state
                print(f"\r[상태] 배터리: {state['battery']:.0f}% | "
                      f"위치: ({state['x']:.2f}, {state['y']:.2f}) | "
                      f"상태: {state['robot_state']}", end='', flush=True)
    except KeyboardInterrupt:
        print()
        print("종료 중...")
        simulator.stop()


if __name__ == '__main__':
    main()
