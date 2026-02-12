#!/usr/bin/env python3
import time
import sys
import os
try:
    import board
    import busio
    from adafruit_servokit import ServoKit
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    print("⚠️  Hardware modules not found. Running in simulation/dry-run mode.")

# ---------------------------------------------------------
# [설정 파일 Import]
# ---------------------------------------------------------
# 현재 위치: .../scripts/sim2real/
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    import hardware_config as hw
    print(f"✅ 설정 파일 로드 성공: {current_dir}/hardware_config.py")
except ImportError:
    print(f"❌ 설정 파일을 찾을 수 없습니다. 경로를 확인하세요: {current_dir}")
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
    Returns: (kit_instance, pin_number, direction, offset, kit_name)
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
    offset = config_data['offset'][part_idx]
    
    kit = kit_front if kit_type == 'front' else kit_rear
    
    return kit, pin, direction, offset, f"{leg_key} (Kit: {kit_type})"

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
            kit, pin, direction, offset, leg_name = get_joint_info(joint_str)
            
            if pin is None:
                print(f"[Error] Unknown joint: '{joint_str}'")
                continue

            # Apply Formula: 90 + dir * (input + offset)
            target_angle = 90.0 + direction * (angle_input + offset)

            print(f"Target: {leg_name} (Pin {pin})")
            print(f"Formula: 90 + {direction} * ({angle_input} + {offset}) = {target_angle}")
            
            move_servo(kit, pin, target_angle, dry_run=dry_run)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"[Error] Unexpected: {e}")

if __name__ == "__main__":
    main()