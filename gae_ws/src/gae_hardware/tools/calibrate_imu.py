import time
import board
import busio
import adafruit_mpu6050
import numpy as np
import yaml
import os
import sys

# ==========================================
# 🛠️ [경로 설정 - 컨벤션 준수 ✅]
# ==========================================
# 1. 현재 이 파일(tool script)의 위치: .../gae_hardware/tools
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. 프로젝트 루트(상위 폴더): .../gae_hardware
project_root = os.path.dirname(current_dir)

# 3. 목표 Config 폴더: .../gae_hardware/gae_hardware/config
# (구조상 src/gae_hardware/gae_hardware/config 인지, src/gae_hardware/config 인지 확인)
# 일반적인 ROS2 Python 패키지 구조를 고려하여 탐색
target_config_path = os.path.join(project_root, 'gae_hardware', 'config')

# 만약 경로가 없다면, 한 단계 위 바로 config가 있는지 확인 (Fallback)
if not os.path.exists(target_config_path):
    target_config_path = os.path.join(project_root, 'config')

# 경로 추가 및 확인
sys.path.append(target_config_path)
print(f"📂 Config Directory Found: {target_config_path}")

try:
    import hardware_config_test as hw_cfg
    print(f"✅ Config Loaded successfully.")
except ImportError:
    print("⚠️ Config file not found. Using Default Safety Settings.")
    class hw_cfg:
        MPU_ADDR = 0x68
        IMU_AXIS_MAP  = [1, 0, 2]         
        IMU_AXIS_SIGN = [1.0, 1.0, -1.0]

# ==========================================
# ⚙️ 설정
# ==========================================
SAMPLES = 6000  
SAMPLE_DT = 0.005 

def calibrate():
    print("\n🐕 --- GAE Robot IMU Calibration (Relative Path Mode) --- 🐕")

    # 1. I2C 연결
    try:
        i2c = busio.I2C(board.SCL_1, board.SDA_1)
        mpu = adafruit_mpu6050.MPU6050(i2c, address=hw_cfg.MPU_ADDR)
        print("✅ MPU-6050 Connected.")
    except Exception as e:
        print(f"❌ Hardware Error: {e}")
        return

    print("\n⚠️  [준비 사항]")
    print(" 1. 로봇을 '평평한 바닥'에 두세요.")
    print(" 2. 배 밑에 박스를 받쳐서 움직이지 않게 고정하세요.")
    print(" 3. 모터 전원을 끄고 진동이 없는 상태여야 합니다.")
    print(" 4. 엔터를 누르면 시작합니다.")
    input() 

    print(f"\n⏳ {SAMPLES}개 데이터 수집 중... (약 {SAMPLES*SAMPLE_DT}초 소요)")
    time.sleep(1)

    accel_samples = []
    gyro_samples = []

    for i in range(SAMPLES):
        try:
            raw_accel = np.array(mpu.acceleration)
            raw_gyro  = np.array(mpu.gyro)

            accel = raw_accel[hw_cfg.IMU_AXIS_MAP] * hw_cfg.IMU_AXIS_SIGN
            gyro  = raw_gyro[hw_cfg.IMU_AXIS_MAP]  * hw_cfg.IMU_AXIS_SIGN

            accel_samples.append(accel)
            gyro_samples.append(gyro)

            if i % 500 == 0:
                print(f"   {i}/{SAMPLES} | Reading...", end='\r')

        except OSError:
            continue
        time.sleep(SAMPLE_DT)

    # 3. 평균 계산
    accel_avg = np.mean(np.array(accel_samples), axis=0)
    gyro_avg  = np.mean(np.array(gyro_samples), axis=0)

    # =========================================================
    # 🔥 [핵심 수정] 가속도 Z축 보정 로직
    # =========================================================
    gravity_g = 9.80665
    target_z = -gravity_g if accel_avg[2] < 0 else gravity_g

    bias_accel_x = accel_avg[0] - 0.0
    bias_accel_y = accel_avg[1] - 0.0
    bias_accel_z = 0.0  # Safe Mode

    bias_gyro_x = gyro_avg[0]
    bias_gyro_y = gyro_avg[1]
    bias_gyro_z = gyro_avg[2]

    print("\n\n📊 Calibration Result")
    print(f"  Gyro Bias : X={bias_gyro_x:.3f}, Y={bias_gyro_y:.3f}, Z={bias_gyro_z:.3f}")
    print(f"  Accel Bias: X={bias_accel_x:.3f}, Y={bias_accel_y:.3f}, Z={bias_accel_z:.3f}")

    # 4. YAML 저장 (동적으로 찾은 경로 사용)
    os.makedirs(target_config_path, exist_ok=True)
    file_path = os.path.join(target_config_path, 'imu_sensor_bias.yaml')

    calib_data = {
        '/**': {
            'ros__parameters': {
                'imu_sensor_bias': {
                    'accel_bias_x': float(bias_accel_x),
                    'accel_bias_y': float(bias_accel_y),
                    'accel_bias_z': float(bias_accel_z),
                    'gyro_bias_x':  float(bias_gyro_x),
                    'gyro_bias_y':  float(bias_gyro_y),
                    'gyro_bias_z':  float(bias_gyro_z),
                }
            }
        }
    }

    with open(file_path, 'w') as f:
        yaml.dump(calib_data, f, default_flow_style=False)

    print(f"\n✅ 저장 완료: {file_path}")
    print("👉 Git Commit 시 이 파일도 함께 포함시키세요!")

if __name__ == '__main__':
    calibrate()