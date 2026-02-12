#!/usr/bin/env python3
"""
MQTT Bridge Node for ROS 2
- Publishes robot status data to Spring Boot server
- Subscribes to command topics from Spring Boot server
"""

import json
import rclpy
from rclpy.node import Node
import paho.mqtt.client as mqtt


class MqttBridgeNode(Node):
    def __init__(self):
        super().__init__('mqtt_bridge_node')

        # MQTT Configuration
        self.mqtt_host = 'localhost'
        self.mqtt_port = 1883

        # Topics - Publish (Robot -> Server)
        self.topic_status = 'robot/status'

        # Topics - Subscribe (Server -> Robot)
        self.topic_cmd_move = 'robot/cmd/move'
        self.topic_cmd_nav = 'robot/cmd/nav'

        # Robot state
        self.battery = 100

        # MQTT Client Setup
        self.mqtt_client = mqtt.Client(client_id='ros2-mqtt-bridge')
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        self.mqtt_client.on_message = self.on_message

        # Connect to MQTT Broker
        try:
            self.mqtt_client.connect(self.mqtt_host, self.mqtt_port)
            self.mqtt_client.loop_start()  # Non-blocking async loop
            self.get_logger().info(f'Connecting to MQTT broker at {self.mqtt_host}:{self.mqtt_port}')
        except Exception as e:
            self.get_logger().error(f'Failed to connect to MQTT broker: {e}')
            return

        # Timer: publish every 1 second
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info('MQTT Bridge Node started - publishing every 1 second')

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.get_logger().info('Connected to MQTT broker successfully!')

            # Subscribe to command topics
            client.subscribe(self.topic_cmd_move, qos=1)
            client.subscribe(self.topic_cmd_nav, qos=1)
            self.get_logger().info(f'Subscribed to: {self.topic_cmd_move}, {self.topic_cmd_nav}')
        else:
            self.get_logger().error(f'MQTT connection failed with code: {rc}')

    def on_mqtt_disconnect(self, client, userdata, rc):
        self.get_logger().warn('Disconnected from MQTT broker')

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages from Spring Boot server"""
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
        except json.JSONDecodeError as e:
            self.get_logger().error(f'Failed to parse JSON: {e}')
            return

        self.get_logger().info('')
        self.get_logger().info('=' * 50)

        if topic == self.topic_cmd_move:
            action = payload.get('action', '')

            if action == 'home':
                self.get_logger().info('[명령 수신] 🏠 집으로 이동합니다!')
                # TODO: Nav2 연동 - 홈 위치로 네비게이션 Goal 전송

            elif action == 'stop':
                self.get_logger().info('[명령 수신] 🛑 긴급 정지!')
                # TODO: Nav2 연동 - 현재 네비게이션 취소 및 로봇 정지

            else:
                self.get_logger().warn(f'[명령 수신] 알 수 없는 action: {action}')

        elif topic == self.topic_cmd_nav:
            x = payload.get('x', 0.0)
            y = payload.get('y', 0.0)
            self.get_logger().info(f'[명령 수신] 📍 좌표 이동: (x={x}, y={y})')
            # TODO: Nav2 연동 - 지정 좌표로 네비게이션 Goal 전송

        else:
            self.get_logger().warn(f'[명령 수신] 알 수 없는 토픽: {topic}')

        self.get_logger().info('=' * 50)
        self.get_logger().info('')

    def timer_callback(self):
        # Build status message
        status_data = {
            'battery': self.battery,
            'state': 'WALK',
            'isOnline': True
        }

        # Publish to MQTT
        payload = json.dumps(status_data)
        result = self.mqtt_client.publish(self.topic_status, payload, qos=1)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            self.get_logger().info(
                f'Published to [{self.topic_status}] -> battery: {self.battery}, state: WALK'
            )
        else:
            self.get_logger().error(f'Failed to publish message: {result.rc}')

        # Decrease battery (min 0)
        self.battery = max(0, self.battery - 1)

        # Reset battery when it reaches 0
        if self.battery == 0:
            self.battery = 100
            self.get_logger().info('Battery reset to 100')

    def destroy_node(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        self.get_logger().info('MQTT Bridge Node shutting down')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = MqttBridgeNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
