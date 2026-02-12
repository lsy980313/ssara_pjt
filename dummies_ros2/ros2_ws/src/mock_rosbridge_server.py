#!/usr/bin/env python3
"""
Mock ROSBridge Server
- rosbridge_server 없이 로봇 시뮬레이터와 Spring Boot 서버 연결 테스트
- ROSBridge v2.0 프로토콜 지원

Usage:
    pip install websockets
    python mock_rosbridge_server.py
"""

import asyncio
import json
import sys
from datetime import datetime

try:
    import websockets
except ImportError:
    print("websockets 패키지가 필요합니다.")
    print("설치: pip install websockets")
    sys.exit(1)


class MockRosbridgeServer:
    def __init__(self, host="0.0.0.0", port=9090):
        self.host = host
        self.port = port
        self.clients = set()
        self.subscriptions = {}  # topic -> set of clients
        self.advertised = {}     # topic -> client (publisher)

    def log(self, level, msg):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        colors = {
            'INFO': '\033[92m',
            'WARN': '\033[93m',
            'ERROR': '\033[91m',
            'RECV': '\033[96m',
            'SEND': '\033[95m',
            'CONN': '\033[94m',
        }
        reset = '\033[0m'
        color = colors.get(level, '')
        print(f"{color}[{timestamp}] [{level}] {msg}{reset}")

    async def handler(self, websocket, path=None):
        """WebSocket 연결 핸들러"""
        client_id = id(websocket)
        self.clients.add(websocket)
        self.log('CONN', f'클라이언트 연결: {client_id} (총 {len(self.clients)}명)')

        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            # 구독 정리
            for topic in list(self.subscriptions.keys()):
                self.subscriptions[topic].discard(websocket)
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]
            self.log('CONN', f'클라이언트 연결 해제: {client_id} (총 {len(self.clients)}명)')

    async def handle_message(self, sender, message):
        """메시지 처리"""
        try:
            msg = json.loads(message)
            op = msg.get('op', '')

            if op == 'advertise':
                topic = msg.get('topic', '')
                msg_type = msg.get('type', '')
                self.advertised[topic] = sender
                self.log('INFO', f'[Advertise] topic={topic}, type={msg_type}')

            elif op == 'subscribe':
                topic = msg.get('topic', '')
                msg_type = msg.get('type', '')
                if topic not in self.subscriptions:
                    self.subscriptions[topic] = set()
                self.subscriptions[topic].add(sender)
                self.log('INFO', f'[Subscribe] topic={topic}, type={msg_type}')

            elif op == 'unsubscribe':
                topic = msg.get('topic', '')
                if topic in self.subscriptions:
                    self.subscriptions[topic].discard(sender)
                self.log('INFO', f'[Unsubscribe] topic={topic}')

            elif op == 'publish':
                topic = msg.get('topic', '')
                # 해당 토픽을 구독하는 모든 클라이언트에게 전달
                if topic in self.subscriptions:
                    for client in self.subscriptions[topic]:
                        if client != sender:  # 발신자 제외
                            try:
                                await client.send(message)
                            except:
                                pass
                # 특정 토픽은 로그 출력
                if topic in ['/robot/status', '/robot/pose', '/cmd_vel']:
                    self.log('RECV', f'[Publish] topic={topic}')

            elif op == 'call_service':
                service = msg.get('service', '')
                self.log('RECV', f'[Service Call] service={service}')
                # 서비스 호출을 모든 클라이언트에게 브로드캐스트
                for client in self.clients:
                    if client != sender:
                        try:
                            await client.send(message)
                        except:
                            pass

            elif op == 'service_response':
                service = msg.get('service', '')
                self.log('SEND', f'[Service Response] service={service}')
                # 응답을 모든 클라이언트에게 브로드캐스트
                for client in self.clients:
                    if client != sender:
                        try:
                            await client.send(message)
                        except:
                            pass

            elif op == 'send_action_goal':
                action = msg.get('action', '')
                self.log('RECV', f'[Action Goal] action={action}')
                for client in self.clients:
                    if client != sender:
                        try:
                            await client.send(message)
                        except:
                            pass

            elif op == 'action_feedback':
                action = msg.get('action', '')
                self.log('SEND', f'[Action Feedback] action={action}')
                for client in self.clients:
                    if client != sender:
                        try:
                            await client.send(message)
                        except:
                            pass

            elif op == 'action_result':
                action = msg.get('action', '')
                self.log('SEND', f'[Action Result] action={action}')
                for client in self.clients:
                    if client != sender:
                        try:
                            await client.send(message)
                        except:
                            pass

            elif op == 'cancel_action_goal':
                action = msg.get('action', '')
                self.log('RECV', f'[Action Cancel] action={action}')
                for client in self.clients:
                    if client != sender:
                        try:
                            await client.send(message)
                        except:
                            pass

            else:
                self.log('WARN', f'[Unknown op] {op}')

        except json.JSONDecodeError as e:
            self.log('ERROR', f'JSON 파싱 오류: {e}')

    async def start(self):
        """서버 시작"""
        print()
        print("=" * 60)
        print("  Mock ROSBridge Server")
        print("  ROSBridge v2.0 프로토콜 지원")
        print("=" * 60)
        print()
        print(f"WebSocket 서버 시작: ws://{self.host}:{self.port}")
        print()
        print("연결 대기 중...")
        print("  - 로봇 시뮬레이터: python standalone_robot_simulator.py")
        print("  - Spring Boot 서버: rosbridge.url=ws://localhost:9090")
        print()
        print("Ctrl+C로 종료")
        print()

        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()  # 무한 대기


def main():
    server = MockRosbridgeServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n종료...")


if __name__ == '__main__':
    main()
