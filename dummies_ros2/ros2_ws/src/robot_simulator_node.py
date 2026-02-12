#!/usr/bin/env python3
"""
Robot Simulator Node for ROS 2
- ROSBridge JSON 메시지 규격 완벽 준수
- Spring Boot 서버와 rosbridge_server를 통해 통신
- 하드웨어 없이 노트북에서 테스트 가능

Usage:
    1. rosbridge_server 실행: ros2 launch rosbridge_server rosbridge_websocket_launch.xml
    2. 이 노드 실행: python3 robot_simulator_node.py
"""

import json
import math
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

# Message Types
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Pose2D, Twist, PoseStamped
from sensor_msgs.msg import BatteryState, LaserScan, CompressedImage
from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger

# Action Type
from nav2_msgs.action import NavigateToPose


class RobotSimulatorNode(Node):
    """
    ROSBridge 규격을 준수하는 로봇 시뮬레이터 노드
    """

    def __init__(self):
        super().__init__('robot_simulator_node')

        self.get_logger().info('=' * 60)
        self.get_logger().info('Robot Simulator Node 초기화 중...')
        self.get_logger().info('=' * 60)

        # Callback group for concurrent execution
        self.callback_group = ReentrantCallbackGroup()

        # =====================================================
        # Robot State (시뮬레이션용)
        # =====================================================
        self.robot_state = {
            'battery': 85,
            'state': 'IDLE',  # IDLE, MOVING, CHARGING, ERROR, DOCKING
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

        # =====================================================
        # Publishers (로봇 → 서버)
        # =====================================================

        # /robot/status - std_msgs/msg/String (JSON)
        self.pub_robot_status = self.create_publisher(
            String, '/robot/status', 10
        )

        # /robot/pose - geometry_msgs/msg/Pose2D
        self.pub_robot_pose = self.create_publisher(
            Pose2D, '/robot/pose', 10
        )

        # /battery_state - sensor_msgs/msg/BatteryState
        self.pub_battery_state = self.create_publisher(
            BatteryState, '/battery_state', 10
        )

        # /odom - nav_msgs/msg/Odometry
        self.pub_odom = self.create_publisher(
            Odometry, '/odom', 10
        )

        # /scan - sensor_msgs/msg/LaserScan
        self.pub_scan = self.create_publisher(
            LaserScan, '/scan', 10
        )

        # /bumper - std_msgs/msg/Bool
        self.pub_bumper = self.create_publisher(
            Bool, '/bumper', 10
        )

        # /camera/image_raw/compressed - sensor_msgs/msg/CompressedImage
        self.pub_camera = self.create_publisher(
            CompressedImage, '/camera/image_raw/compressed', 10
        )

        self.get_logger().info('[Publishers] 7개 토픽 등록 완료')

        # =====================================================
        # Subscribers (서버 → 로봇)
        # =====================================================

        # /cmd_vel - geometry_msgs/msg/Twist
        self.sub_cmd_vel = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10
        )

        self.get_logger().info('[Subscribers] /cmd_vel 구독 완료')

        # =====================================================
        # Services (서버 → 로봇)
        # =====================================================

        # /go_home - std_srvs/srv/Trigger
        self.srv_go_home = self.create_service(
            Trigger, '/go_home', self.go_home_callback,
            callback_group=self.callback_group
        )

        # /emergency_stop - std_srvs/srv/Trigger
        self.srv_emergency_stop = self.create_service(
            Trigger, '/emergency_stop', self.emergency_stop_callback,
            callback_group=self.callback_group
        )

        # /dock - std_srvs/srv/Trigger
        self.srv_dock = self.create_service(
            Trigger, '/dock', self.dock_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('[Services] /go_home, /emergency_stop, /dock 서비스 등록 완료')

        # =====================================================
        # Action Server (서버 → 로봇)
        # =====================================================

        # /navigate_to_pose - nav2_msgs/action/NavigateToPose
        self._action_server = ActionServer(
            self,
            NavigateToPose,
            '/navigate_to_pose',
            self.navigate_to_pose_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('[Actions] /navigate_to_pose 액션 서버 등록 완료')

        # =====================================================
        # Timers (주기적 발행)
        # =====================================================

        # /robot/status - 1000ms (1Hz)
        self.timer_status = self.create_timer(1.0, self.publish_robot_status)

        # /robot/pose - 500ms (2Hz)
        self.timer_pose = self.create_timer(0.5, self.publish_robot_pose)

        # /battery_state - 5000ms (0.2Hz)
        self.timer_battery = self.create_timer(5.0, self.publish_battery_state)

        # /odom - 200ms (5Hz)
        self.timer_odom = self.create_timer(0.2, self.publish_odom)

        # /scan - 1000ms (1Hz)
        self.timer_scan = self.create_timer(1.0, self.publish_scan)

        # /bumper - 100ms (10Hz)
        self.timer_bumper = self.create_timer(0.1, self.publish_bumper)

        # /camera - 100ms (10Hz) - 부하가 크므로 1000ms로 조정
        self.timer_camera = self.create_timer(1.0, self.publish_camera)

        # 시뮬레이션 업데이트 (위치, 배터리 등)
        self.timer_simulation = self.create_timer(0.1, self.update_simulation)

        self.get_logger().info('[Timers] 모든 타이머 설정 완료')
        self.get_logger().info('=' * 60)
        self.get_logger().info('Robot Simulator Node 시작!')
        self.get_logger().info('rosbridge_server (ws://localhost:9090) 와 연결 대기 중...')
        self.get_logger().info('=' * 60)

    # =========================================================
    # Publisher Callbacks
    # =========================================================

    def publish_robot_status(self):
        """
        /robot/status 토픽 발행
        Message Type: std_msgs/msg/String (JSON)
        주기: 1000ms
        """
        status_json = json.dumps({
            'battery': self.robot_state['battery'],
            'state': self.robot_state['state'],
            'isOnline': self.robot_state['is_online']
        })

        msg = String()
        msg.data = status_json
        self.pub_robot_status.publish(msg)

        self.get_logger().debug(
            f'[/robot/status] battery={self.robot_state["battery"]}, '
            f'state={self.robot_state["state"]}'
        )

    def publish_robot_pose(self):
        """
        /robot/pose 토픽 발행
        Message Type: geometry_msgs/msg/Pose2D
        주기: 500ms
        """
        msg = Pose2D()
        msg.x = self.robot_state['x']
        msg.y = self.robot_state['y']
        msg.theta = self.robot_state['theta']
        self.pub_robot_pose.publish(msg)

        self.get_logger().debug(
            f'[/robot/pose] x={msg.x:.2f}, y={msg.y:.2f}, theta={msg.theta:.2f}'
        )

    def publish_battery_state(self):
        """
        /battery_state 토픽 발행
        Message Type: sensor_msgs/msg/BatteryState
        주기: 5000ms
        """
        msg = BatteryState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'battery'

        percentage = self.robot_state['battery'] / 100.0
        msg.voltage = 11.0 + (percentage * 1.6)  # 11.0V ~ 12.6V
        msg.temperature = 25.0
        msg.current = -0.5 if self.robot_state['state'] != 'CHARGING' else 1.5
        msg.charge = percentage * 10.0
        msg.capacity = 10.0
        msg.design_capacity = 10.0
        msg.percentage = percentage

        # power_supply_status: 0=UNKNOWN, 1=CHARGING, 2=DISCHARGING, 3=NOT_CHARGING, 4=FULL
        if self.robot_state['state'] == 'CHARGING':
            msg.power_supply_status = 1
        elif self.robot_state['battery'] >= 100:
            msg.power_supply_status = 4
        else:
            msg.power_supply_status = 2

        msg.power_supply_health = 1  # GOOD
        msg.power_supply_technology = 2  # LION
        msg.present = True

        self.pub_battery_state.publish(msg)

        self.get_logger().debug(
            f'[/battery_state] percentage={percentage:.2f}, voltage={msg.voltage:.1f}V'
        )

    def publish_odom(self):
        """
        /odom 토픽 발행
        Message Type: nav_msgs/msg/Odometry
        주기: 200ms
        """
        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_link'

        # Position
        msg.pose.pose.position.x = self.robot_state['x']
        msg.pose.pose.position.y = self.robot_state['y']
        msg.pose.pose.position.z = 0.0

        # Orientation (quaternion from theta)
        theta = self.robot_state['theta']
        msg.pose.pose.orientation.x = 0.0
        msg.pose.pose.orientation.y = 0.0
        msg.pose.pose.orientation.z = math.sin(theta / 2.0)
        msg.pose.pose.orientation.w = math.cos(theta / 2.0)

        # Velocity
        msg.twist.twist.linear.x = self.robot_state['linear_vel']
        msg.twist.twist.linear.y = 0.0
        msg.twist.twist.linear.z = 0.0
        msg.twist.twist.angular.x = 0.0
        msg.twist.twist.angular.y = 0.0
        msg.twist.twist.angular.z = self.robot_state['angular_vel']

        # Covariance (36 elements, zeros for simulation)
        msg.pose.covariance = [0.0] * 36
        msg.twist.covariance = [0.0] * 36

        self.pub_odom.publish(msg)

    def publish_scan(self):
        """
        /scan 토픽 발행
        Message Type: sensor_msgs/msg/LaserScan
        주기: 1000ms
        """
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser'

        msg.angle_min = -math.pi
        msg.angle_max = math.pi
        msg.angle_increment = math.radians(1.0)  # 1도 간격, 360개
        msg.time_increment = 0.0
        msg.scan_time = 0.1
        msg.range_min = 0.1
        msg.range_max = 10.0

        # 시뮬레이션: 랜덤한 거리 값 (실제로는 센서 데이터)
        num_readings = int((msg.angle_max - msg.angle_min) / msg.angle_increment)
        msg.ranges = [5.0 + math.sin(i * 0.1) for i in range(num_readings)]
        msg.intensities = []

        self.pub_scan.publish(msg)

    def publish_bumper(self):
        """
        /bumper 토픽 발행
        Message Type: std_msgs/msg/Bool
        주기: 100ms
        """
        msg = Bool()
        msg.data = self.robot_state['bumper_pressed']
        self.pub_bumper.publish(msg)

    def publish_camera(self):
        """
        /camera/image_raw/compressed 토픽 발행
        Message Type: sensor_msgs/msg/CompressedImage
        주기: 100ms (시뮬레이션에서는 1000ms)
        """
        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera'
        msg.format = 'jpeg'

        # 시뮬레이션: 더미 이미지 데이터 (1x1 검은색 JPEG)
        # 실제로는 카메라 센서 데이터
        msg.data = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
            0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
            0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
            0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0x7F, 0xFF,
            0xD9
        ])

        self.pub_camera.publish(msg)

    # =========================================================
    # Subscriber Callbacks
    # =========================================================

    def cmd_vel_callback(self, msg: Twist):
        """
        /cmd_vel 토픽 수신 (서버 → 로봇)
        Message Type: geometry_msgs/msg/Twist
        """
        linear_x = msg.linear.x
        angular_z = msg.angular.z

        self.robot_state['linear_vel'] = linear_x
        self.robot_state['angular_vel'] = angular_z

        # 상태 업데이트
        if linear_x == 0.0 and angular_z == 0.0:
            if self.robot_state['state'] == 'MOVING':
                self.robot_state['state'] = 'IDLE'
            self.get_logger().info('[/cmd_vel] 정지 명령 수신')
        else:
            self.robot_state['state'] = 'MOVING'
            self.get_logger().info(
                f'[/cmd_vel] 속도 명령 수신: linear.x={linear_x:.2f} m/s, '
                f'angular.z={angular_z:.2f} rad/s'
            )

    # =========================================================
    # Service Callbacks
    # =========================================================

    def go_home_callback(self, request, response):
        """
        /go_home 서비스 핸들러
        Service Type: std_srvs/srv/Trigger
        """
        self.get_logger().info('[Service /go_home] 집으로 복귀 명령 수신!')

        # 홈 위치 (0, 0)으로 네비게이션 시작
        self.robot_state['nav_goal_x'] = 0.0
        self.robot_state['nav_goal_y'] = 0.0
        self.robot_state['is_navigating'] = True
        self.robot_state['state'] = 'MOVING'

        response.success = True
        response.message = 'Navigating to home position'
        return response

    def emergency_stop_callback(self, request, response):
        """
        /emergency_stop 서비스 핸들러
        Service Type: std_srvs/srv/Trigger
        """
        self.get_logger().warn('[Service /emergency_stop] 긴급 정지!')

        # 모든 동작 중지
        self.robot_state['linear_vel'] = 0.0
        self.robot_state['angular_vel'] = 0.0
        self.robot_state['is_navigating'] = False
        self.robot_state['state'] = 'IDLE'

        response.success = True
        response.message = 'Emergency stop executed'
        return response

    def dock_callback(self, request, response):
        """
        /dock 서비스 핸들러
        Service Type: std_srvs/srv/Trigger
        """
        self.get_logger().info('[Service /dock] 충전 도킹 명령 수신!')

        # 충전 스테이션 위치 (-1, 0)으로 네비게이션 시작
        self.robot_state['nav_goal_x'] = -1.0
        self.robot_state['nav_goal_y'] = 0.0
        self.robot_state['is_navigating'] = True
        self.robot_state['state'] = 'DOCKING'

        response.success = True
        response.message = 'Docking to charging station'
        return response

    # =========================================================
    # Action Server Callback
    # =========================================================

    async def navigate_to_pose_callback(self, goal_handle):
        """
        /navigate_to_pose 액션 서버 핸들러
        Action Type: nav2_msgs/action/NavigateToPose
        """
        goal = goal_handle.request
        target_x = goal.pose.pose.position.x
        target_y = goal.pose.pose.position.y

        self.get_logger().info(
            f'[Action /navigate_to_pose] 목표 수신: x={target_x:.2f}, y={target_y:.2f}'
        )

        # 네비게이션 시작
        self.robot_state['nav_goal_x'] = target_x
        self.robot_state['nav_goal_y'] = target_y
        self.robot_state['is_navigating'] = True
        self.robot_state['state'] = 'MOVING'

        feedback_msg = NavigateToPose.Feedback()

        # 시뮬레이션: 목표까지 이동
        while self.robot_state['is_navigating']:
            # 현재 위치와 목표 사이 거리 계산
            dx = target_x - self.robot_state['x']
            dy = target_y - self.robot_state['y']
            distance = math.sqrt(dx * dx + dy * dy)

            # 목표 도달 체크
            if distance < 0.1:
                self.robot_state['is_navigating'] = False
                self.robot_state['state'] = 'IDLE'
                self.get_logger().info('[Action /navigate_to_pose] 목표 도달!')
                break

            # Feedback 전송
            feedback_msg.current_pose.header.stamp = self.get_clock().now().to_msg()
            feedback_msg.current_pose.header.frame_id = 'map'
            feedback_msg.current_pose.pose.position.x = self.robot_state['x']
            feedback_msg.current_pose.pose.position.y = self.robot_state['y']
            feedback_msg.current_pose.pose.position.z = 0.0
            feedback_msg.distance_remaining = float(distance)

            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().debug(
                f'[Action Feedback] 남은 거리: {distance:.2f}m'
            )

            # 잠시 대기 (시뮬레이션)
            await self._sleep(0.5)

            # 취소 체크
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.robot_state['is_navigating'] = False
                self.robot_state['state'] = 'IDLE'
                self.get_logger().warn('[Action /navigate_to_pose] 네비게이션 취소됨')
                return NavigateToPose.Result()

        # 성공
        goal_handle.succeed()
        result = NavigateToPose.Result()
        return result

    async def _sleep(self, seconds):
        """비동기 sleep"""
        import asyncio
        await asyncio.sleep(seconds)

    # =========================================================
    # Simulation Update
    # =========================================================

    def update_simulation(self):
        """
        시뮬레이션 상태 업데이트 (100ms 주기)
        """
        dt = 0.1  # 100ms

        # 속도에 따른 위치 업데이트
        if self.robot_state['linear_vel'] != 0.0 or self.robot_state['angular_vel'] != 0.0:
            # 각도 업데이트
            self.robot_state['theta'] += self.robot_state['angular_vel'] * dt
            self.robot_state['theta'] = self.robot_state['theta'] % (2 * math.pi)

            # 위치 업데이트
            self.robot_state['x'] += self.robot_state['linear_vel'] * math.cos(self.robot_state['theta']) * dt
            self.robot_state['y'] += self.robot_state['linear_vel'] * math.sin(self.robot_state['theta']) * dt

        # 네비게이션 중일 때 자동 이동
        if self.robot_state['is_navigating']:
            dx = self.robot_state['nav_goal_x'] - self.robot_state['x']
            dy = self.robot_state['nav_goal_y'] - self.robot_state['y']
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 0.1:
                # 목표 방향으로 이동
                target_theta = math.atan2(dy, dx)
                self.robot_state['theta'] = target_theta

                # 이동 속도 (0.3 m/s)
                speed = min(0.3, distance)
                self.robot_state['x'] += speed * math.cos(target_theta) * dt
                self.robot_state['y'] += speed * math.sin(target_theta) * dt
                self.robot_state['linear_vel'] = speed
            else:
                # 목표 도달
                self.robot_state['x'] = self.robot_state['nav_goal_x']
                self.robot_state['y'] = self.robot_state['nav_goal_y']
                self.robot_state['linear_vel'] = 0.0
                self.robot_state['is_navigating'] = False

                # 도킹 완료 시 충전 시작
                if self.robot_state['state'] == 'DOCKING':
                    self.robot_state['state'] = 'CHARGING'
                    self.get_logger().info('[시뮬레이션] 충전 시작!')
                else:
                    self.robot_state['state'] = 'IDLE'

        # 배터리 시뮬레이션
        if self.robot_state['state'] == 'CHARGING':
            self.robot_state['battery'] = min(100, self.robot_state['battery'] + 0.5)
            if self.robot_state['battery'] >= 100:
                self.robot_state['state'] = 'IDLE'
                self.get_logger().info('[시뮬레이션] 충전 완료!')
        elif self.robot_state['state'] == 'MOVING':
            self.robot_state['battery'] = max(0, self.robot_state['battery'] - 0.01)


def main(args=None):
    rclpy.init(args=args)

    node = RobotSimulatorNode()

    # 멀티스레드 실행 (Action, Service 동시 처리)
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
