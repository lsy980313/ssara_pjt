#!/usr/bin/env python3
import time
import sys
import os
import math
import board
import busio
from adafruit_servokit import ServoKit

# ---------------------------------------------------------
# [설정 파일 Import]
# ---------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.abspath(os.path.join(current_dir, '../gae_hardware/config'))
sys.path.append(config_dir)

try:
    import hardware_config as hw
    print(f"✅ 설정 파일 로드 성공: {config_dir}/hardware_config.py")
except ImportError:
    print(f"❌ 설정 파일을 찾을 수 없습니다. 경로를 확인하세요: {config_dir}")
    sys.exit(1)

# ---------------------------------------------------------
# [Global Variables]
# ---------------------------------------------------------
kit_front = None
kit_rear = None

# ✅ [수정] 현재 로봇의 자세(각도)를 저장하는 변수 (초기값 0.0)
# hw.ALL_ZERO_POSE는 '기준값'으로만 쓰고, 변하는 값은 여기에 저장합니다.
current_pose = [0.0, 0.0, 0.0] 

def get_joint_info(joint_name_input):
    """ 기존과 동일: 관절 이름 파싱 """
    joint_name_input = joint_name_input.lower().replace("_", " ").replace("-", " ").strip()
    parts = joint_name_input.split()
    
    if len(parts) < 2: return None, None, None, None, None

    leg_key = None
    if 'fl' in parts or ('front' in parts and 'left' in parts): leg_key = 'front-left'
    elif 'fr' in parts or ('front' in parts and 'right' in parts): leg_key = 'front-right'
    elif 'rl' in parts or ('rear' in parts and 'left' in parts): leg_key = 'rear-left'
    elif 'rr' in parts or ('rear' in parts and 'right' in parts): leg_key = 'rear-right'
    
    if not leg_key: return None, None, None, None, None

    part_idx = -1
    if 'foot' in parts: part_idx = 0 
    elif 'leg' in parts or 'thigh' in parts: part_idx = 1 
    elif 'sh' in parts or 'shoulder' in parts: part_idx = 2 
    
    if part_idx == -1: return None, None, None, None, None

    config_data = hw.PIN_MAP[leg_key]
    kit_type = config_data['kit']
    pin = config_data['pins'][part_idx]
    direction = config_data['dirs'][part_idx]
    offset = config_data.get('offset', [0.0, 0.0, 0.0])[part_idx]
    kit = kit_front if kit_type == 'front' else kit_rear
    
    return kit, pin, direction, offset, f"{leg_key} (Kit: {kit_type})"

def move_servo_raw(kit, pin, angle, dry_run=False):
    """ 안전하게 서보 하나를 움직이는 함수 """
    if dry_run or kit is None: return
    try:
        safe_angle = max(0, min(180, angle))
        kit.servo[pin].angle = safe_angle
    except Exception as e:
        pass

# ---------------------------------------------------------
# [New] 전체 모터 일괄 제어 및 스무스 무빙 함수
# ---------------------------------------------------------
def apply_whole_pose(input_deg_list, dry_run=False):
    """
    [Foot, Leg, Shoulder] 각도(Degree)를 받아서
    모든 다리의 오프셋을 계산한 뒤 모터에 적용하는 함수
    """
    global kit_front, kit_rear

    for leg_key, config in hw.PIN_MAP.items():
        target_kit = kit_front if config['kit'] == 'front' else kit_rear
        
        for i in range(3): # 0:Foot, 1:Leg, 2:Shoulder
            pin = config['pins'][i]
            direction = config['dirs'][i]
            offset = config.get('offset', [0.0, 0.0, 0.0])[i]
            
            # ✅ 공식 적용: (Direction * (Input + Offset)) + 90
            input_val = input_deg_list[i]
            target_angle = (direction * (input_val + offset)) + 90.0
            
            move_servo_raw(target_kit, pin, target_angle, dry_run)

def smooth_move(target_rads, duration=1.0, steps=50, dry_run=False):
    """
    현재 자세(current_pose)에서 목표 자세(target_rads)까지
    duration(초) 동안 부드럽게 보간(Interpolation)하여 이동
    """
    # ✅ [수정] global hw.XXX 삭제 -> global current_pose 사용
    global current_pose 
    
    # 1. 목표값 변환 (Radian -> Degree)
    target_deg = [math.degrees(val) for val in target_rads]
    
    # 2. 시작값(Start)과 변화량(Delta) 계산
    # ✅ [수정] Config 값이 아닌 현재 저장된 자세에서 시작
    start_deg = list(current_pose) 
    delta_deg = [t - s for t, s in zip(target_deg, start_deg)]
    
    # 3. 시간 계산
    dt = duration / steps
    
    print(f"🌊 Smooth Move: {duration}s 동안 이동 중...")
    
    # 4. 루프 실행
    for step in range(1, steps + 1):
        progress = step / steps # 0.0 ~ 1.0
        
        # 현재 스텝의 임시 각도 계산
        temp_pose = [
            start_deg[i] + (delta_deg[i] * progress)
            for i in range(3)
        ]
        
        # 모터에 전송
        apply_whole_pose(temp_pose, dry_run)
        time.sleep(dt)
        
    # 5. 최종 상태 업데이트
    # ✅ [수정] Config 값 훼손 방지 -> 현재 자세 변수 업데이트
    current_pose = list(target_deg)
    print("✅ Move Complete.")

# ---------------------------------------------------------
# [Main Function]
# ---------------------------------------------------------
def main():
    print("=== SpotMicro Servo Control (Smooth v2.1 Fixed) ===")
    print("Commands:")
    print("   👉 'f' : Smooth Sit (Frog Pose)")
    print("   👉 'r' : Smooth Stand (Reset to 0)")
    print("   👉 'q' : Quit")
    print("   👉 '<joint> <angle>' : Manual Control (Instant)")
    print("===========================================")

    # ✅ [수정] global 선언부에서 점(.) 제거
    global kit_front, kit_rear, current_pose
    dry_run = False

    try:
        print(f"\n🔌 I2C Bus Initializing...")
        i2c_bus = busio.I2C(board.SCL, board.SDA)
        kit_front = ServoKit(channels=16, i2c=i2c_bus, address=hw.PCA_ADDR_FRONT)
        kit_rear = ServoKit(channels=16, i2c=i2c_bus, address=hw.PCA_ADDR_REAR)
        print("✅ Kits Initialized.")

        print("⚙️ Applying Servo Pulse Width Range (500~2500µs)")
        for i in range(16):
            kit_front.servo[i].set_pulse_width_range(
                hw.SERVO_MIN_PULSE,
                hw.SERVO_MAX_PULSE
            )
            kit_rear.servo[i].set_pulse_width_range(
                hw.SERVO_MIN_PULSE,
                hw.SERVO_MAX_PULSE
            )
        
        # -------------------------------------------------------------
        # [Init] 초기화: 현재 오프셋 상태(0도)로 즉시 정렬
        # -------------------------------------------------------------
        print("\n🔄 [Init] 초기화: 정자세(0도) 정렬")
        
        # ✅ [수정] Config에서 0점 기준을 가져와 current_pose 초기화
        current_pose = list(hw.ALL_ZERO_POSE) 
        
        # 초기 자세 적용
        apply_whole_pose(current_pose, dry_run) 
        print("✅ Ready.\n")
        
    except Exception as e:
        print(f"❌ HW Init Failed: {e}")
        dry_run = True

    while True:
        try:
            user_input = input("\nCommand >> ").strip().lower()
            if not user_input: continue

            if user_input in ['q', 'quit', 'exit']:
                break

            # ---------------------------------------------------------
            # 2. 개구리 자세 (f)
            # ---------------------------------------------------------
            elif user_input == 'f':
                print("\n🐸 [F] Sitting Down (Smooth)...")
                if hasattr(hw, 'FROG_POSE'):
                    smooth_move(hw.FROG_POSE, duration=1.0, dry_run=dry_run)
                else:
                    print("⚠️ Config에 FROG_POSE가 없습니다.")
                continue

            # ---------------------------------------------------------
            # 3. 리셋/정상화 (r)
            # ---------------------------------------------------------
            elif user_input == 'r':
                print("\n🔄 [R] Standing Up (Smooth)...")
                # 0도(정자세) 라디안 값 (Config에 있다면 hw.ALL_ZERO_POSE 써도 됨)
                stand_pose_rad = hw.ALL_ZERO_POSE 
                smooth_move(stand_pose_rad, duration=1.0, dry_run=dry_run)
                continue

            # ---------------------------------------------------------
            # 4. 개별 관절 제어 (Manual)
            # ---------------------------------------------------------
            parts = user_input.split()
            if len(parts) < 2:
                print("[Error] Format: <joint> <angle>")
                continue

            try:
                angle_input = float(parts[-1])
                joint_str = " ".join(parts[:-1])
            except ValueError:
                print("[Error] 각도 숫자가 아닙니다.")
                continue

            kit, pin, direction, offset, leg_name = get_joint_info(joint_str)
            
            if pin is None:
                print(f"[Error] 알 수 없는 관절: '{joint_str}'")
                continue

            # 개별 제어 공식
            target_angle = (direction * (angle_input + offset)) + 90.0
            print(f"Target: {leg_name} -> Input {angle_input} (Actual {target_angle:.1f})")
            
            move_servo_raw(kit, pin, target_angle, dry_run)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"[Error] {e}")

if __name__ == "__main__":
    main()