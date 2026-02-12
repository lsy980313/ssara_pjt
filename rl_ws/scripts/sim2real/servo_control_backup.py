#!/usr/bin/env python3
import time
import sys
import os
import board
import busio
from adafruit_servokit import ServoKit

# ---------------------------------------------------------
# [설정 파일 Import]
# ---------------------------------------------------------
# 현재 위치: .../gae_hardware/tools/
current_dir = os.path.dirname(os.path.abspath(__file__))

# 목표 위치: .../gae_hardware/gae_hardware/config/
# (상위 폴더로 이동 후 gae_hardware/config 진입)
config_dir = os.path.abspath(os.path.join(current_dir, '../gae_hardware/config'))
sys.path.append(config_dir)

try:
    import hardware_config_test as hw
    print(f"✅ 설정 파일 로드 성공: {config_dir}/hardware_config.py")
except ImportError:
    print(f"❌ 설정 파일을 찾을 수 없습니다. 경로를 확인하세요: {config_dir}")
    sys.exit(1)

# Initialize Kits (Global or specific scope? User snippet puts them in main, but my code relied on global or passed vars)
# For compatibility with my existing functions, I will attempt to initialize them here or modify functions.
# However, the user snippet initializes them in main(). 
# My 'get_joint_info' relies on 'kit_front'/'kit_rear' global if I don't pass them.
# I will initialize them globally to None for now, to keep existing logic working partially.
kit_front = None
kit_rear = None


def get_joint_info(joint_name_input):
    """
    Input string example: 'fl_foot', 'rr_sh', 'front-left leg'
    Returns: (kit_instance, pin_number, direction, kit_name)
    """
    joint_name_input = joint_name_input.lower().replace("_", " ").replace("-", " ").strip()
    parts = joint_name_input.split()
    
    if len(parts) < 2:
        return None, None, None, None

    # Identify Leg (FL, FR, RL, RR)
    leg_key = None
    if 'fl' in parts or ('front' in parts and 'left' in parts):
        leg_key = 'front-left'
    elif 'fr' in parts or ('front' in parts and 'right' in parts):
        leg_key = 'front-right'
    elif 'rl' in parts or ('rear' in parts and 'left' in parts):
        leg_key = 'rear-left'
    elif 'rr' in parts or ('rear' in parts and 'right' in parts):
        leg_key = 'rear-right'
    
    if not leg_key:
        return None, None, None, None

    # Identify Part (Foot, Leg, Shoulder)
    part_idx = -1
    if 'foot' in parts:
        part_idx = 0 # hw says index 0
    elif 'leg' in parts or 'thigh' in parts:
        part_idx = 1 # hw says index 1
    elif 'sh' in parts or 'shoulder' in parts:
        part_idx = 2 # hw says index 2
    
    if part_idx == -1:
        return None, None, None, None

    config_data = hw.PIN_MAP[leg_key]
    kit_type = config_data['kit'] # 'front' or 'rear'
    pin = config_data['pins'][part_idx]
    direction = config_data['dirs'][part_idx]
    
    kit = kit_front if kit_type == 'front' else kit_rear
    
    return kit, pin, direction, f"{leg_key} (Kit: {kit_type})"

def move_servo(kit, pin, angle, dry_run=False):
    if dry_run or kit is None:
        print(f"[Dry-Run] Check Pin {pin} -> Angle {angle:.2f}")
        return
    
    try:
        # Safety Clip
        safe_angle = max(0, min(180, angle))
        kit.servo[pin].angle = safe_angle
        print(f"[Moved] Pin {pin} -> {safe_angle:.2f} deg")
    except Exception as e:
        print(f"[Error] Servo move failed: {e}")

def main():
    print("=== SpotMicro Servo Control (Manual) ===")
    print("Format: <joint_name> <angle_deg>")
    print("Example: front-left-foot 30")
    print("Example: rear-right-sh -15")
    print("Type 'q' or 'quit' to exit.")
    print("========================================")

    global kit_front, kit_rear

    try:
        # Initialize I2C and Kits as per user snippet
        print(f"\\n🔌 I2C Bus Initializing...")
        i2c_bus = busio.I2C(board.SCL, board.SDA)
        
        print(f"🔌 Front(0x41) 연결 중...")
        kit_front = ServoKit(channels=16, i2c=i2c_bus, address=hw.PCA_ADDR_FRONT)
        
        print(f"🔌 Rear(0x40) 연결 중...")
        kit_rear = ServoKit(channels=16, i2c=i2c_bus, address=hw.PCA_ADDR_REAR)
        print("✅ Kits Initialized.")
        
    except Exception as e:
        print(f"❌ Hardware Initialization Failed: {e}")
        print("Starting in DRY-RUN mode (No Hardware)")
        kit_front = None
        kit_rear = None

    dry_run = False
    if kit_front is None and kit_rear is None:
        print("[Warning] No ServoKit detected. Running in DRY-RUN mode.")
        dry_run = True

    while True:
        try:
            user_input = input("\nCommand >> ").strip()
            if user_input.lower() in ['q', 'quit', 'exit']:
                break
            
            if not user_input:
                continue

            # Split input into Joint and Angle
            # Expecting last part to be the angle number
            parts = user_input.split()
            if len(parts) < 2:
                print("[Error] Invalid format.")
                continue

            try:
                angle_input = float(parts[-1])
                joint_str = " ".join(parts[:-1])
            except ValueError:
                print("[Error] Could not parse angle.")
                continue

            # Find Joint
            kit, pin, direction, leg_name = get_joint_info(joint_str)
            
            if pin is None:
                print(f"[Error] Unknown joint: '{joint_str}'")
                continue

            # Apply Formula: (dirs * input) + 90
            # hw_cfg.py 'dirs' elements are 1.0 or -1.0
            target_angle = (direction * angle_input) + 90.0

            print(f"Target: {leg_name} (Pin {pin})")
            print(f"Formula: ({direction} * {angle_input}) + 90 = {target_angle}")
            
            move_servo(kit, pin, target_angle, dry_run=dry_run)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"[Error] Unexpected: {e}")

if __name__ == "__main__":
    main()