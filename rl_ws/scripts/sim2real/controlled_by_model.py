"""
🐕 SpotMicro Sim2Real Controller
- hardware_config.py, servo_control.py, imu_control.py 통합 버전
- 순수 Python (ROS2 없음)
"""
import time
import torch
import numpy as np
from collections import deque
import os
import sys

# 현재 디렉토리를 path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 하드웨어 설정 import
import hardware_config as hw

# 하드웨어 라이브러리 (환경에 따라 자동 감지)
try:
    import board
    import busio
    from adafruit_servokit import ServoKit
    from mpu6050 import mpu6050
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    print("⚠️  Hardware modules not found. Running in DRY-RUN mode.")


# ==========================================
# 1. 설정 (Configuration)
# ==========================================
class Config:
    DT = 0.03  # 약 33Hz (시뮬레이션과 동일하게 유지)
    ACTION_SCALE = 0.15
    
    # 초기 관절 각도 (init_state)
    # 순서: [FL_Shoulder, FL_Leg, FL_Foot, FR_..., RL_..., RR_...]
    DEFAULT_DOF_POS = np.array([
        0.0, 0.7, -1.4,  # Front Left
        0.0, 0.7, -1.4,  # Front Right
        0.0, 0.7, -1.4,  # Rear Left
        0.0, 0.7, -1.4   # Rear Right
    ], dtype=np.float32)
    
    # 관절 범위 제한 (안전용, Radian)
    DOF_MIN = DEFAULT_DOF_POS - 0.8
    DOF_MAX = DEFAULT_DOF_POS + 0.8


# ==========================================
# 2. 하드웨어 인터페이스 (Hardware Interface)
# ==========================================
class RobotHardware:
    """
    ServoKit(PCA9685) 2개 + MPU6050 IMU 제어
    hardware_config.py의 설정을 기반으로 동작
    """
    
    # 모델 출력 순서 → 하드웨어 매핑
    # (leg_key, part_index) - part_index: 0=Foot, 1=Leg, 2=Shoulder
    JOINT_ORDER = [
        ('front-left', 2),   # 0: FL_Shoulder
        ('front-left', 1),   # 1: FL_Leg
        ('front-left', 0),   # 2: FL_Foot
        ('front-right', 2),  # 3: FR_Shoulder
        ('front-right', 1),  # 4: FR_Leg
        ('front-right', 0),  # 5: FR_Foot
        ('rear-left', 2),    # 6: RL_Shoulder
        ('rear-left', 1),    # 7: RL_Leg
        ('rear-left', 0),    # 8: RL_Foot
        ('rear-right', 2),   # 9: RR_Shoulder
        ('rear-right', 1),   # 10: RR_Leg
        ('rear-right', 0),   # 11: RR_Foot
    ]
    
    def __init__(self, config):
        print("🔌 Initializing Hardware...")
        self.cfg = config
        self.dry_run = not HARDWARE_AVAILABLE
        
        if self.dry_run:
            print("   → DRY-RUN mode: 모터/IMU 시뮬레이션")
            self.kit_front = None
            self.kit_rear = None
            self.imu = None
            return
        
        try:
            # I2C 버스 초기화 (servo_control.py 방식)
            print(f"   → I2C Bus {hw.I2C_BUS_SERVO} 초기화...")
            i2c_bus = busio.I2C(board.SCL, board.SDA)
            
            # ServoKit 초기화
            print(f"   → Front PCA9685 (0x{hw.PCA_ADDR_FRONT:02X}) 연결...")
            self.kit_front = ServoKit(
                channels=16, 
                i2c=i2c_bus, 
                address=hw.PCA_ADDR_FRONT
            )
            
            print(f"   → Rear PCA9685 (0x{hw.PCA_ADDR_REAR:02X}) 연결...")
            self.kit_rear = ServoKit(
                channels=16, 
                i2c=i2c_bus, 
                address=hw.PCA_ADDR_REAR
            )
            
            # 서보 펄스 범위 설정
            for i in range(16):
                self.kit_front.servo[i].set_pulse_width_range(
                    hw.SERVO_MIN_PULSE, hw.SERVO_MAX_PULSE
                )
                self.kit_rear.servo[i].set_pulse_width_range(
                    hw.SERVO_MIN_PULSE, hw.SERVO_MAX_PULSE
                )
            
            # IMU 초기화
            print(f"   → MPU6050 (0x{hw.MPU_ADDR:02X}) 연결...")
            self.imu = mpu6050(hw.MPU_ADDR)
            
            print("✅ Hardware initialized successfully!")
            
        except Exception as e:
            print(f"❌ Hardware initialization failed: {e}")
            print("   → Falling back to DRY-RUN mode")
            self.dry_run = True
            self.kit_front = None
            self.kit_rear = None
            self.imu = None

    def read_imu(self):
        """
        IMU에서 각속도(Gyro)와 Projected Gravity를 읽어옵니다.
        
        Returns:
            base_ang_vel: np.array([roll_rate, pitch_rate, yaw_rate]) in rad/s
            projected_gravity: np.array([gx, gy, gz]) 정규화된 중력 벡터
        """
        if self.imu is None:
            # DRY-RUN: 정지 상태 (중력은 -Z 방향)
            return np.zeros(3, dtype=np.float32), np.array([0.0, 0.0, -1.0], dtype=np.float32)
        
        try:
            # 1. 센서 데이터 읽기
            accel_data = self.imu.get_accel_data()
            gyro_data = self.imu.get_gyro_data()
            
            # 2. 배열로 변환
            raw_accel = np.array([
                accel_data['x'], 
                accel_data['y'], 
                accel_data['z']
            ], dtype=np.float32)
            
            raw_gyro = np.array([
                gyro_data['x'], 
                gyro_data['y'], 
                gyro_data['z']
            ], dtype=np.float32)
            
            # 3. 좌표계 변환 (hardware_config.py 설정 적용)
            # IMU_AXIS_MAP: 축 순서 변경, IMU_AXIS_SIGN: 부호 반전
            mapped_accel = raw_accel[hw.IMU_AXIS_MAP] * np.array(hw.IMU_AXIS_SIGN, dtype=np.float32)
            mapped_gyro = raw_gyro[hw.IMU_AXIS_MAP] * np.array(hw.IMU_AXIS_SIGN, dtype=np.float32)
            
            # 4. Gyro: deg/s → rad/s 변환
            base_ang_vel = np.radians(mapped_gyro)
            
            # 5. Projected Gravity 계산
            # 센서의 가속도를 정규화하고 부호 반전 (Up → Down)
            projected_gravity = -(mapped_accel / 9.81)
            
            return base_ang_vel.astype(np.float32), projected_gravity.astype(np.float32)
            
        except Exception as e:
            print(f"[IMU Error] {e}")
            return np.zeros(3, dtype=np.float32), np.array([0.0, 0.0, -1.0], dtype=np.float32)

    def set_actuator_positions(self, target_rad):
        """
        모델의 출력(Radian)을 서보 모터 각도(Degree)로 변환하여 전송
        
        Args:
            target_rad: np.array of shape (12,) - 12개 관절의 목표 각도 (Radian)
        """
        for i, (leg_key, part_idx) in enumerate(self.JOINT_ORDER):
            cfg = hw.PIN_MAP[leg_key]
            
            # 해당 서보킷 선택
            kit = self.kit_front if cfg['kit'] == 'front' else self.kit_rear
            
            # 핀, 방향, 오프셋 가져오기
            pin = cfg['pins'][part_idx]
            direction = cfg['dirs'][part_idx]
            offset = cfg['offset'][part_idx]
            
            # 공식: 90 + dir * (rad2deg(target) + offset)
            angle_deg = np.degrees(target_rad[i])
            servo_angle = 90.0 + direction * (angle_deg + offset)
            
            # 안전 클리핑
            servo_angle = np.clip(servo_angle, 0, 180)
            
            if self.dry_run:
                # DRY-RUN: 출력만
                pass  # 너무 많은 로그 방지
            else:
                try:
                    kit.servo[pin].angle = servo_angle
                except Exception as e:
                    print(f"[Servo Error] {leg_key} part{part_idx}: {e}")
        
        # 디버그 출력 (선택적)
        # print(f"[Servo] Target: {np.round(np.degrees(target_rad), 1)}")


# ==========================================
# 3. 정책 컨트롤러 (Policy Controller)
# ==========================================
class SpotMicroController:
    def __init__(self, model_path):
        self.cfg = Config()
        self.hw = RobotHardware(self.cfg)
        
        # 모델 로드 (CPU 모드)
        print(f"\n📦 Loading Model: {model_path}")
        self.device = torch.device("cpu")
        
        try:
            # JIT 모델 로드 (권장)
            self.model = torch.jit.load(model_path, map_location=self.device)
            self.model.eval()
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("💡 Tip: torch.jit.save(actor, 'policy.pt')로 모델을 export하세요.")
            exit(1)

        # 상태 변수 초기화
        self.action_history = deque(maxlen=6)
        for _ in range(6):
            self.action_history.append(np.zeros(12, dtype=np.float32))
        
        # 명령 속도 (고정값 - 외부 입력 연결 가능)
        self.cmd_vel = np.array([0.0, 0.0, 0.0], dtype=np.float32)  # vx, vy, wz
        
        # 성능 모니터링
        self.step_count = 0
        self.last_log_time = time.time()

    def step(self):
        start_time = time.time()

        # 1. 센서 데이터 읽기
        base_ang_vel, projected_gravity = self.hw.read_imu()
        
        # 2. 관측 벡터(Observation) 조립 (총 84개)
        # 순서: [BaseLinVel(3), BaseAngVel(3), Gravity(3), Command(3), Actions(72)]
        
        # [Blind Locomotion] 실제 속도 대신 명령 속도를 입력
        obs_lin_vel = self.cmd_vel.copy()
        obs_lin_vel[2] = 0.0  # z축 속도는 0 가정
        
        # Action History Flatten (6x12 -> 72)
        obs_actions = np.concatenate(list(self.action_history))
        
        obs_list = [
            obs_lin_vel,        # (3) 추정 선속도
            base_ang_vel,       # (3) 각속도
            projected_gravity,  # (3) 중력
            self.cmd_vel,       # (3) 명령
            obs_actions         # (72) 이전 행동
        ]
        
        obs_np = np.concatenate(obs_list).astype(np.float32)
        obs_tensor = torch.from_numpy(obs_np).unsqueeze(0).to(self.device)

        # 3. 모델 추론 (Inference)
        with torch.no_grad():
            actions_tensor = self.model(obs_tensor)
            actions = actions_tensor.cpu().numpy().flatten()

        # 4. Action History 업데이트
        self.action_history.append(actions.astype(np.float32))

        # 5. 실제 모터 각도로 변환 (Post-processing)
        target_positions = self.cfg.DEFAULT_DOF_POS + (actions * self.cfg.ACTION_SCALE)
        
        # 안전 범위 클리핑
        target_positions = np.clip(target_positions, self.cfg.DOF_MIN, self.cfg.DOF_MAX)

        # 6. 하드웨어 제어
        self.hw.set_actuator_positions(target_positions)

        # 7. 주기 맞추기 (Sleep)
        elapsed = time.time() - start_time
        sleep_time = self.cfg.DT - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        # 8. 성능 로그 (1초마다)
        self.step_count += 1
        if time.time() - self.last_log_time >= 1.0:
            freq = self.step_count / (time.time() - self.last_log_time)
            print(f"[Loop] {freq:.1f} Hz | Gravity: {projected_gravity}")
            self.step_count = 0
            self.last_log_time = time.time()


# ==========================================
# 4. 실행 (Main)
# ==========================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SpotMicro Sim2Real Controller")
    parser.add_argument("--model", type=str, default="policy.pt", help="Path to policy model (.pt)")
    args = parser.parse_args()
    
    print("=" * 50)
    print("🐕 SpotMicro Sim2Real Controller")
    print("=" * 50)
    print("⚠️  WARNING: 로봇을 공중에 들어올린 상태에서 시작하세요!")
    print("    Ctrl+C로 종료합니다.")
    print("=" * 50)
    
    input("\n▶ Enter 키를 누르면 시작합니다...")
    
    controller = SpotMicroController(args.model)
    
    try:
        print("\n🚀 Control loop started!")
        while True:
            controller.step()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping...")
        print("   → 안전하게 종료되었습니다.")