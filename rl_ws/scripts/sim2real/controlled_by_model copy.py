import time
import torch
import numpy as np
from collections import deque
import math

# === 하드웨어 라이브러리 (환경에 맞게 주석 해제) ===
# from adafruit_servokit import ServoKit
# from mpu6050 import mpu6050

# ==========================================
# 1. 설정 (Configuration) - 학습 코드와 일치시켜야 함
# ==========================================
class Config:
    DT = 0.03  # 50Hz (시뮬레이션과 동일하게 유지)
    ACTION_SCALE = 0.15
    
    # 초기 관절 각도 (init_state)
    # 순서: [FL_Shoulder, FL_Leg, FL_Foot, FR_..., RL_..., RR_...]
    # URDF와 하드웨어 연결 순서를 반드시 맞춰야 합니다.
    DEFAULT_DOF_POS = np.array([
        
        0.0, 0.7, -1.4,  # Front Left
        0.0, 0.7, -1.4,  # Front Right
        0.0, 0.7, -1.4,  # Rear Left
        0.0, 0.7, -1.4   # Rear Right
    ], dtype=np.float32)
    
    # [방향 보정] 시뮬레이션(URDF)과 실제 서보의 회전 방향 매핑 (1.0 또는 -1.0)
    # 예: 왼쪽 다리는 1.0인데 오른쪽 다리는 거울상이라 -1.0을 줘야 같은 방향(앞)으로 갈 수 있음
    # 실제 로봇을 띄워놓고 테스트하며 맞춰야 합니다.
    SERVO_DIRECTIONS = np.array([
        #shr leg foot
        1.0, -1.0, -1.0,   # FL (Shoulder, Leg, Foot)
        1.0, 1.0, 1.0, # FR (오른쪽 어깨/다리는 반대일 확률 높음)
        -1.0, -1.0, -1.0,   # RL
        -1.0, 1.0, 1.0  # RR
    ], dtype=np.float32)

    # [0점 보정] 조립 오차 보정값 (Degree 단위)
    # 예: 0도를 줬는데 살짝 삐뚤어져 있다면 여기에 5도, -3도 등을 입력
    SERVO_OFFSETS = np.array([
        0.0, 0.0, 0.0,
        0.0, 0.0, 0.0,
        0.0, 0.0, 0.0,
        0.0, 0.0, 0.0
    ], dtype=np.float32)

    # 관절 범위 제한 (안전용, Radian)
    DOF_MIN = DEFAULT_DOF_POS - 0.8
    DOF_MAX = DEFAULT_DOF_POS + 0.8

# ==========================================
# 2. 하드웨어 인터페이스 (Hardware Interface)
# ==========================================
class RobotHardware:
    def __init__(self, config):
        print("Initializing Hardware...")
        self.cfg = config
        
        # 1) 서보 모터 컨트롤러 (PCA9685)
        # self.kit = ServoKit(channels=16)
        
        # 2) IMU 센서 (MPU6050)
        # self.imu = mpu6050(0x68)
        pass

    def read_imu(self):
        """
        IMU에서 각속도(Gyro)와 자세(Roll, Pitch)를 읽어옵니다.
        """
        # [실제 구현 시 주석 해제 및 수정]
        # gyro_data = self.imu.get_gyro_data()
        # accel_data = self.imu.get_accel_data()
        
        # == 더미 데이터 (테스트용) ==
        roll, pitch = 0.0, 0.0
        gyro_x, gyro_y, gyro_z = 0.0, 0.0, 0.0
        # ==========================
        
        # 자이로: [Roll rate, Pitch rate, Yaw rate] (rad/s)
        base_ang_vel = np.array([gyro_x, gyro_y, gyro_z], dtype=np.float32)
        
        # 중력 벡터 계산 (Projected Gravity)
        # 로봇 몸체 좌표계에서 중력이 어디로 작용하는지 계산
        g_x = -np.sin(pitch)
        g_y = np.sin(roll) * np.cos(pitch)
        g_z = -np.cos(roll) * np.cos(pitch)
        projected_gravity = np.array([g_x, g_y, g_z], dtype=np.float32)

        return base_ang_vel, projected_gravity

    def set_actuator_positions(self, target_positions):
        """
        계산된 목표 각도(Radian)를 서보 모터(Degree/PWM)로 변환하여 전송
        """
        # 1. 방향 보정 적용 (Simulation -> Real Robot Direction)
        # 시뮬레이션 값에 하드웨어 방향(-1 or 1)을 곱해줍니다.
        corrected_positions = target_positions * self.cfg.SERVO_DIRECTIONS

        # 2. Radian -> Degree 변환
        degrees = np.degrees(corrected_positions)
        
        # 3. 오프셋 적용 및 하드웨어 전송
        # [실제 구현]
        # for i, deg in enumerate(degrees):
        #     # 오프셋 적용 (조립 오차 보정)
        #     final_angle_deg = deg + self.cfg.SERVO_OFFSETS[i]
        #
        #     # 서보 모터 중심값(90도) 기준 매핑
        #     # (서보마다 다르므로 확인 필요, 보통 0~180도 입력)
        #     servo_command = 90 + final_angle_deg
        #     
        #     # 안전 범위 클리핑
        #     servo_command = max(0, min(180, servo_command))
        #     
        #     self.kit.servo[i].angle = servo_command
        
        # 디버깅 출력 (주석 처리 가능)
        # print(f"Cmd Deg: {np.round(degrees + self.cfg.SERVO_OFFSETS, 1)}")
        pass

# ==========================================
# 3. 정책 컨트롤러 (Policy Controller)
# ==========================================
class SpotMicroController:
    def __init__(self, model_path):
        self.cfg = Config()
        self.hw = RobotHardware(self.cfg) # Config 전달
        
        # 모델 로드 (CPU 모드)
        print(f"Loading Model: {model_path}")
        self.device = torch.device("cpu")
        try:
            # 전체 체크포인트라면 'model_state_dict' 등의 키를 확인해야 함
            # 여기서는 Actor 신경망만 추출했다고 가정하거나, 전체 모델 로드 시도
            loaded_dict = torch.load(model_path, map_location=self.device)
            
            # rsl_rl의 경우 'model' 키 안에 actor가 있음. 구조에 따라 수정 필요.
            # 가장 간단한 방법: rsl_rl에서 play.py로 export한 jit 모델(.pt)을 사용하는 것
            if 'model_state_dict' in loaded_dict:
                self.model = loaded_dict['model_state_dict'] # 구조 파악 필요
                print("Warning: Raw checkpoint loaded. Provide JIT exported model for safety.")
            else:
                # JIT 모델 로드 (권장)
                self.model = torch.jit.load(model_path, map_location=self.device)
                
            self.model.eval()
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Tip: Use 'torch.jit.save(actor_critic.actor, 'policy.pt')' in training code to export.")
            exit()

        # 상태 변수 초기화
        self.action_history = deque(maxlen=6)
        # 초기 히스토리는 0으로 채움 (6스텝 * 12관절 = 72개)
        for _ in range(6):
            self.action_history.append(np.zeros(12, dtype=np.float32))
            
        self.cmd_vel = np.array([0.0, 0.0, 0.0], dtype=np.float32) # vx, vy, wz

    def get_user_command(self):
        """
        키보드나 조이스틱 입력을 받아서 cmd_vel 업데이트
        """
        # [구현 필요] 예: PS4 컨트롤러, 키보드 입력 등
        # 여기서는 테스트를 위해 앞으로 천천히 가는 명령 설정
        self.cmd_vel = np.array([0.2, 0.0, 0.0], dtype=np.float32) # 0.2 m/s 전진

    def step(self):
        start_time = time.time()

        # 1. 센서 데이터 읽기
        base_ang_vel, projected_gravity = self.hw.read_imu()
        
        # 2. 관측 벡터(Observation) 조립 (총 84개)
        # 순서: [BaseLinVel(3), BaseAngVel(3), Gravity(3), Command(3), Actions(72)]
        
        # [Method 3] 실제 속도 대신 '명령 속도'를 입력 (Blind Locomotion)
        obs_lin_vel = self.cmd_vel.copy() 
        obs_lin_vel[2] = 0.0 # z축 속도는 0 가정
        
        # Action History Flatten (6x12 -> 72)
        obs_actions = np.concatenate(self.action_history)
        
        obs_list = [
            obs_lin_vel,        # (3) 추정 선속도
            base_ang_vel,       # (3) 각속도
            projected_gravity,  # (3) 중력
            self.cmd_vel,       # (3) 명령
            obs_actions         # (72) 이전 행동
        ]
        
        obs_tensor = torch.from_numpy(np.concatenate(obs_list)).float().unsqueeze(0).to(self.device)

        # 3. 모델 추론 (Inference)
        with torch.no_grad():
            # 모델 출력은 Raw Action (보통 -1 ~ 1 사이 값)
            actions_tensor = self.model(obs_tensor)
            actions = actions_tensor.cpu().numpy().flatten()

        # 4. Action History 업데이트
        self.action_history.append(actions)

        # 5. 실제 모터 각도로 변환 (Post-processing)
        # Target = Default + (Action * Scale)
        target_positions = self.cfg.DEFAULT_DOF_POS + (actions * self.cfg.ACTION_SCALE)
        
        # 안전 범위 클리핑
        target_positions = np.clip(target_positions, self.cfg.DOF_MIN, self.cfg.DOF_MAX)

        # 6. 하드웨어 제어
        self.hw.set_actuator_positions(target_positions)

        # 7. 50Hz 주기 맞추기 (Sleep)
        elapsed = time.time() - start_time
        sleep_time = self.cfg.DT - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

# ==========================================
# 4. 실행 (Main)
# ==========================================
if __name__ == "__main__":
    # 모델 파일 경로 지정 (학습된 .pt 파일)
    MODEL_PATH = "policy.pt" 
    
    print("Starting Spot Micro Controller...")
    print("WARNING: Ensure the robot is hanged up (legs in air) for safety!")
    time.sleep(2) # 준비 시간
    
    controller = SpotMicroController(MODEL_PATH)
    
    try:
        while True:
            controller.get_user_command() # 사용자 입력 확인
            controller.step()             # 제어 루프 실행
    except KeyboardInterrupt:
        print("Stopping...")
        # 안전하게 종료하는 코드 (모터 힘 풀기 등) 추가 가능