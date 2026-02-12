#!/usr/bin/env python3
"""
🐕 GAE Robot: Nominal Pose Setter (v2.11 - Frog Pose Fixed)
- Config v2.11의 'FROG_POSE' 값을 읽어 개구리 자세를 취합니다.
- 키보드 'p'를 누르면 자세를 잡고, 'r'을 누르면 90도로 풀립니다.
"""

import time
import sys
import os
import math
import termios
import tty

# === 하드웨어 라이브러리 ===
try:
    import board
    import busio
    from adafruit_servokit import ServoKit
except ImportError:
    print("❌ 하드웨어 라이브러리(adafruit-servokit 등)가 없습니다.")
    sys.exit(1)

# === 설정 파일 로드 (config 폴더) ===
# 현재 스크립트 위치: .../gae_hardware/gae_hardware/set_nominal_position.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# [경로 수정] 기존 '../config' -> 'config' (현재 폴더 하위의 config 폴더 참조)
config_dir = os.path.abspath(os.path.join(current_dir, 'config'))
sys.path.append(config_dir)

try:
    import hardware_config_test as hw
    print(f"✅ 설정 파일 로드됨: {hw.__file__}")
except ImportError:
    print(f"❌ 설정 파일을 찾을 수 없습니다: {config_dir}")
    sys.exit(1)

# ==========================================
# 유틸리티 함수
# ==========================================
def get_key():
    """Linux 터미널에서 엔터 없이 키 입력 받기"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def rad_to_servo_angle(rad, direction):
    """
    라디안 -> 서보 각도(0~180) 변환
    공식: 90 + (rad * 180/pi * direction)
    """
    deg = math.degrees(rad) * direction
    target_angle = 90 + deg
    
    # 하드웨어 안전 클리핑
    if target_angle < 0: target_angle = 0
    if target_angle > 180: target_angle = 180
    
    return target_angle

# ==========================================
# 로봇 컨트롤러 클래스
# ==========================================
class RobotController:
    def __init__(self):
        print("🔌 I2C 및 서보 드라이버 초기화 중...")
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.kits = {}
            
            # Front Kit (0x41)
            self.kits['front'] = ServoKit(channels=16, i2c=self.i2c, address=hw.PCA_ADDR_FRONT)
            
            # Rear Kit (0x40)
            self.kits['rear'] = ServoKit(channels=16, i2c=self.i2c, address=hw.PCA_ADDR_REAR)
            
            # 펄스 폭 설정 (전체 채널)
            for kit in self.kits.values():
                for i in range(16):
                    kit.servo[i].set_pulse_width_range(hw.SERVO_MIN_PULSE, hw.SERVO_MAX_PULSE)
                    
            print("✅ 하드웨어 연결 성공.")
            
        except Exception as e:
            print(f"❌ 하드웨어 초기화 실패: {e}")
            sys.exit(1)

    def reset_servos(self):
        """모든 서보를 90도(중립)로 이동"""
        print("\n🔄 [RESET] 모든 관절 90도 정렬 (11자 직립)...")
        for limb_name, config in hw.PIN_MAP.items():
            kit = self.kits[config['kit']]
            pins = config['pins']
            
            for pin in pins:
                kit.servo[pin].angle = 90
        print("Done.")

    def set_nominal_pose(self):
        """Config의 init_rad 값을 적용 (개구리 자세)"""
        print("\n🐸 [POSE] Nominal Pose (Crouch) 적용 중...")
        
        # 디버깅용: 한 다리의 계산 결과 출력
        debug_printed = False
        
        for limb_name, config in hw.PIN_MAP.items():
            kit = self.kits[config['kit']]
            pins = config['pins']      # [Foot, Leg, Shoulder]
            dirs = config['dirs']
            rads = config['init_rad']  # [-1.4, 0.7, 0.0]
            
            # 3개 관절 순회
            for i in range(3):
                target_angle = rad_to_servo_angle(rads[i], dirs[i])
                kit.servo[pins[i]].angle = target_angle
            
            # 첫 번째 다리만 로그 출력 (확인용)
            if not debug_printed:
                print(f"   [Debug {limb_name}]")
                # v2.11 설정값(-1.4, 0.7, 0.0)에 맞춰 로그 텍스트 수정
                print(f"   Foot(-1.4) -> PWM Angle: {rad_to_servo_angle(rads[0], dirs[0]):.1f}")
                print(f"   Leg ( 0.7) -> PWM Angle: {rad_to_servo_angle(rads[1], dirs[1]):.1f}")
                print(f"   Shdr( 0.0) -> PWM Angle: {rad_to_servo_angle(rads[2], dirs[2]):.1f}")
                debug_printed = True
                
        print("✅ 자세 적용 완료.")

# ==========================================
# 메인 실행부
# ==========================================
def main():
    robot = RobotController()
    
    print("\n" + "="*50)
    print("🎮 GAE Robot Pose Controller")
    print("   [p] : Nominal Pose (개구리 자세)")
    print("   [r] : Reset (90도 직립)")
    print("   [q] : 종료 (Reset 후 종료)")
    print("="*50)
    
    # 시작 시 안전 리셋
    robot.reset_servos()
    
    try:
        while True:
            print("\n명령 대기 [p/r/q] > ", end='', flush=True)
            key = get_key()
            
            if key == 'p':
                robot.set_nominal_pose()
            elif key == 'r':
                robot.reset_servos()
            elif key == 'q' or key == '\x03': # Ctrl+C
                print("\n종료합니다.")
                break
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n강제 종료.")
    finally:
        # 종료 시 무조건 리셋
        robot.reset_servos()
        print("👋 Safety Reset Complete.")

if __name__ == "__main__":
    main()