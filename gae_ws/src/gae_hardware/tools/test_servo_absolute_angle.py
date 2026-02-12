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

# ---------------------------------------------------------
# [매핑 테이블 정의]
# 입력된 이름(foot, leg, shoulder)을 배열 인덱스로 변환
# ---------------------------------------------------------
JOINT_INDEX_MAP = {
    'foot': 0,      # 구 Knee (무릎)
    'leg': 1,       # 구 Shoulder (어깨/높이)
    'shoulder': 2   # 구 Hip (골반/회전) -> [주의 대상]
}

def main():
    print("\n" + "="*60)
    print("🚀 GAE Robot: 직관적 이름 제어 모드 (Named Control)")
    print(f"ℹ️  I2C Bus: {hw.I2C_BUS_SERVO}")
    print("⚠️  주의: 모든 잠금이 해제되었습니다.")
    print("="*60)

    # 변수 초기화
    kit_front = None
    kit_rear = None

    try:
        # 1. I2C 버스 초기화
        i2c_bus = busio.I2C(board.SCL, board.SDA)

        # 2. ServoKit 인스턴스 생성
        print(f"\n🔌 Front(0x41) 연결 중...")
        kit_front = ServoKit(channels=16, i2c=i2c_bus, address=hw.PCA_ADDR_FRONT)
        
        print(f"🔌 Rear(0x40) 연결 중...")
        kit_rear = ServoKit(channels=16, i2c=i2c_bus, address=hw.PCA_ADDR_REAR)

        # 드라이버 매핑 (Kit 객체 찾기용)
        kit_obj_map = {
            'front': kit_front,
            'rear': kit_rear
        }

        # ---------------------------------------------------------
        # 3. [경고용] 잠금 핀 정보 로드
        # ---------------------------------------------------------
        locked_pins = [] 
        if hasattr(hw, 'LOCKED_PINS'):
            print("\n🛡️  [감지됨] 아래 핀들이 'Shoulder(골반)' 보호 구역입니다.")
            for k_name, pins in hw.LOCKED_PINS.items():
                target_addr = hw.PCA_ADDR_FRONT if k_name == 'front' else hw.PCA_ADDR_REAR
                for p in pins:
                    locked_pins.append((target_addr, p))
        else:
            print("\nℹ️  Config 파일에 'LOCKED_PINS'가 없습니다.")
        
        # ---------------------------------------------------------
        # 4. 초기화 (모든 모터 90도 기립)
        # ---------------------------------------------------------
        print(f"\n⚙️  펄스 폭 설정: {hw.SERVO_MIN_PULSE} ~ {hw.SERVO_MAX_PULSE}")
        
        # 활성 모터 리스트 생성
        active_motors = []
        for limb_key, info in hw.PIN_MAP.items():
            k_name = info['kit']
            if k_name in kit_obj_map:
                target_kit = kit_obj_map[k_name]
                for pin in info['pins']:
                    target_kit.servo[pin].set_pulse_width_range(hw.SERVO_MIN_PULSE, hw.SERVO_MAX_PULSE)
                    active_motors.append((target_kit, pin))

        print("\n🦵 [초기화] 모든 관절 90도 정렬...")
        for kit, pin in active_motors:
            kit.servo[pin].angle = 90
            time.sleep(0.05)
        
        print("✅ 초기화 완료. 토크 유지 중.\n")

        # ---------------------------------------------------------
        # 5. 사용자 입력 루프 (이름 기반 제어)
        # ---------------------------------------------------------
        while True:
            print("-" * 60)
            print("🎮 입력 형식: [부위이름] [각도]")
            print("   👉 예시: front-right-leg 110      (앞-오른쪽-높이관절 110도)")
            print("   👉 예시: rear-left-foot 45        (뒤-왼쪽-발 45도)")
            print("   👉 예시: front-left-shoulder 90   (앞-왼쪽-회전관절 90도 -> 경고)")
            print("   (종료: 'q')")
            
            try:
                user_input = input("\n명령 > ").strip().lower()
            except EOFError:
                break

            if user_input in ['q', 'quit', 'exit']:
                raise KeyboardInterrupt

            try:
                parts = user_input.split()
                if len(parts) != 2:
                    print("⚠️  형식이 틀렸습니다. (예: front-right-leg 110)")
                    continue

                full_name = parts[0]   # 예: front-right-leg
                try:
                    target_angle = int(parts[1])
                except ValueError:
                    print("⚠️  각도는 숫자여야 합니다.")
                    continue

                # -----------------------------------------------------
                # 🧩 이름 파싱 (Parsing Logic)
                # 구조: {방향}-{좌우}-{관절}  (예: front-right-leg)
                # -----------------------------------------------------
                name_parts = full_name.split('-')
                
                if len(name_parts) != 3:
                    print(f"⚠️  이름 형식이 올바르지 않습니다: {full_name}")
                    print("   (형식: front-right-leg / rear-left-foot 등)")
                    continue

                direction = name_parts[0] # front / rear
                side = name_parts[1]      # left / right
                joint = name_parts[2]     # foot / leg / shoulder

                # 1. Limb Key 재조립 (config의 키 값과 매칭)
                limb_key = f"{direction}-{side}"  # 예: front-right
                
                # 2. Config 검증
                if limb_key not in hw.PIN_MAP:
                    print(f"⚠️  존재하지 않는 다리입니다: {limb_key}")
                    continue
                
                if joint not in JOINT_INDEX_MAP:
                    print(f"⚠️  존재하지 않는 관절입니다: {joint}")
                    print(f"   (가능한 관절: {list(JOINT_INDEX_MAP.keys())})")
                    continue

                # 3. 하드웨어 정보 추출
                limb_config = hw.PIN_MAP[limb_key]
                kit_name = limb_config['kit']          # 'front' or 'rear'
                joint_idx = JOINT_INDEX_MAP[joint]     # 0, 1, or 2
                pin_num = limb_config['pins'][joint_idx] # 실제 핀 번호
                
                target_kit = kit_obj_map[kit_name]
                
                # 경고용 주소 확인
                current_addr = hw.PCA_ADDR_FRONT if kit_name == 'front' else hw.PCA_ADDR_REAR
                kit_str_disp = "Front" if kit_name == 'front' else "Rear"

                # -----------------------------------------------------
                # 🛡️ 안전 경고 (Shoulder 감지)
                # -----------------------------------------------------
                if (current_addr, pin_num) in locked_pins:
                     print(f"⚠️  [경고] {limb_key.upper()}-{joint.upper()} (Pin {pin_num})는 'Shoulder'입니다!")
                     print("   👉 회전 관절이므로 와장창 주의하세요.")

                # 범위 보정
                if target_angle < 0: target_angle = 0
                if target_angle > 180: target_angle = 180

                # 실행
                print(f"🚀 실행: {limb_key}-{joint} (Pin {pin_num}) -> {target_angle}°")
                target_kit.servo[pin_num].angle = target_angle
                
            except Exception as e:
                print(f"❌ 처리 중 에러 발생: {e}")

    # ---------------------------------------------------------
    # [종료 루틴]
    # ---------------------------------------------------------
    except KeyboardInterrupt:
        print("\n\n🛑 종료 신호 감지! 안전 복귀 시작...")
        
        if kit_front and kit_rear:
            try:
                print("🔄 모든 모터 90도로 복귀...")
                for kit, pin in active_motors:
                    kit.servo[pin].angle = 90
                    time.sleep(0.05)
                print("✅ 복귀 완료. 안전하게 종료되었습니다.")
            except Exception as e:
                print(f"⚠️ 복귀 중 에러: {e}")
        else:
            print("⚠️ 모터 연결 전 종료됨.")

    except Exception as e:
        print(f"\n❌ 치명적 에러: {e}")

if __name__ == "__main__":
    main()