import time
import sys
import os
import math
import numpy as np
import torch
from collections import deque

# ROS2 Imports
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

# ---------------------------------------------------------
# ⚙️ Hardware Config Import
# ---------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Config 경로 설정 (../../gae_hardware/gae_hardware/config)
config_path = os.path.join(current_dir, '../../gae_hardware/gae_hardware/config')
config_dir = os.path.abspath(config_path)
sys.path.append(config_dir)

print(f"📂 Searching Config at: {config_dir}") 

try:
    import hardware_config_test as hc
    print(f"✅ Hardware Config Loaded. Frog Pose: {hc.FROG_POSE}")
    
    SERVO_MIN_PULSE = hc.SERVO_MIN_PULSE
    SERVO_MAX_PULSE = hc.SERVO_MAX_PULSE
    PCA_ADDR_FRONT  = hc.PCA_ADDR_FRONT
    PCA_ADDR_REAR   = hc.PCA_ADDR_REAR
    PIN_MAP         = hc.PIN_MAP
    SERVO_SAFE_MIN  = hc.SERVO_SAFE_MIN
    SERVO_SAFE_MAX  = hc.SERVO_SAFE_MAX
    
    IMU_AXIS_MAP    = hc.IMU_AXIS_MAP
    IMU_AXIS_SIGN   = hc.IMU_AXIS_SIGN
    
except ImportError:
    print(f"❌ Critical Error: 'hardware_config_test.py' not found in {config_dir}")
    sys.exit(1)

# === HARDWARE LIBRARIES ===
try:
    from adafruit_servokit import ServoKit
    # 🔥 [핵심 수정] 7번 버스를 강제로 잡기 위한 라이브러리
    from adafruit_extended_bus import ExtendedI2C as I2C
    HAS_HARDWARE_MOTOR = True
except ImportError:
    print("⚠️ Motor libraries or 'adafruit-extended-bus' missing.")
    print("👉 Run: pip3 install adafruit-circuitpython-extended-bus")
    HAS_HARDWARE_MOTOR = False

# ==========================================
# 1. Sim2Real Configuration
# ==========================================
class SimConfig:
    MODEL_NAME = "policy_2200.pt"
    DT = 0.02             # 50Hz
    ACTION_SCALE = 0.15 # tunning_point 1 원래 0.03 ~ 0.25
    
    _val_shoulder = hc.FROG_POSE[2] 
    _val_leg      = hc.FROG_POSE[1] 
    _val_foot     = hc.FROG_POSE[0] 
    
    _base_leg_rl_order = [_val_shoulder, _val_leg, _val_foot]
    
    DEFAULT_DOF_POS = np.array(
        _base_leg_rl_order * 4, 
        dtype=np.float32
    )

# ==========================================
# 2. ROS2 Node & Hardware Interface
# ==========================================
class GAEHardwareNode(Node):
    def __init__(self):
        global HAS_HARDWARE_MOTOR
        
        super().__init__('gae_sim2real_node')
        
        self.imu_sub = self.create_subscription(
            Imu,
            '/gae_control/imu/processed',
            self.imu_callback,
            10
        )
        
        self.ang_vel = np.zeros(3, dtype=np.float32)
        self.proj_grav = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.imu_received = False

        self.kits = {}

        self._build_servo_map()

        self.prev_angles = np.array(
            [90.0 + m['off'] for m in self.servo_map],
            dtype=np.float32
        )

        if HAS_HARDWARE_MOTOR:
            try:
                # 🔥 [핵심 수정] I2C Bus 7번 강제 지정
                print("🔌 Connecting to I2C Bus 7...")
                i2c = I2C(7) 

                # 모터 드라이버 연결 시도
                self.kits['front'] = ServoKit(channels=16, i2c=i2c, address=PCA_ADDR_FRONT)
                self.kits['rear']  = ServoKit(channels=16, i2c=i2c, address=PCA_ADDR_REAR)
                
                # 🔥 [수정됨] 모든 채널에 대해 펄스 폭 설정 적용
                for kit in self.kits.values():
                    for i in range(16):  # 0번부터 15번 핀까지 모두 순회
                        kit.servo[i].set_pulse_width_range(SERVO_MIN_PULSE, SERVO_MAX_PULSE)
                
                self.get_logger().info(f"✅ Motor Driver Connected & All Servos Configured.")
                
            except Exception as e:
                self.get_logger().error(f"❌ Motor Init Failed: {e}")
                self.get_logger().error("👉 Check if addresses 0x40/0x41 exist on 'i2cdetect -y -r 7'")
                HAS_HARDWARE_MOTOR = False

        init_pose = np.zeros(12, dtype=np.float32)
        self.set_servos(init_pose, raw=True)

    def _build_servo_map(self):
        self.servo_map = []
        leg_order = ['front-left', 'front-right', 'rear-left', 'rear-right']
        
        for leg_key in leg_order:
            cfg = PIN_MAP[leg_key]
            kit = cfg['kit']
            pins = cfg['pins']
            dirs = cfg['dirs']
            offs = cfg['offset']
            
            self.servo_map.append({'kit': kit, 'pin': pins[2], 'dir': dirs[2], 'off': offs[2]})
            self.servo_map.append({'kit': kit, 'pin': pins[1], 'dir': dirs[1], 'off': offs[1]})
            self.servo_map.append({'kit': kit, 'pin': pins[0], 'dir': dirs[0], 'off': offs[0]})

    def imu_callback(self, msg):
        self.imu_received = True
        
        raw_ang = [msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z]
        raw_acc = [msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z]
        
        mapped_ang = [0.0, 0.0, 0.0]
        mapped_acc = [0.0, 0.0, 0.0]

        for i in range(3):
            idx = IMU_AXIS_MAP[i]
            sign = IMU_AXIS_SIGN[i]
            mapped_ang[i] = raw_ang[idx] * sign
            mapped_acc[i] = raw_acc[idx] * sign
            
        self.ang_vel[:] = mapped_ang
        
        ax, ay, az = mapped_acc
        norm = math.sqrt(ax*ax + ay*ay + az*az)
        if norm > 1e-4:
            self.proj_grav[0] = ax / norm
            self.proj_grav[1] = ay / norm
            self.proj_grav[2] = az / norm
        else:
            self.proj_grav[:] = [0.0, 0.0, -1.0]

    def set_servos(self, target_rad, raw=False):
        target_deg = np.degrees(target_rad)
        final_angles = []

        for i, deg in enumerate(target_deg):
            m = self.servo_map[i]
            angle = (deg * m['dir']) + 90.0 + m['off']

            if not raw:
                angle = np.clip(angle, SERVO_SAFE_MIN, SERVO_SAFE_MAX)

            final_angles.append(angle)

        if not raw:
            alpha = 0.85
            smooth = alpha * np.array(final_angles) + (1 - alpha) * self.prev_angles
            self.prev_angles = smooth
        else:
            smooth = np.array(final_angles)
            self.prev_angles = smooth.copy()

        if HAS_HARDWARE_MOTOR:
            for i, angle in enumerate(smooth):
                m = self.servo_map[i]
                self.kits[m['kit']].servo[m['pin']].angle = angle


# ==========================================
# 3. GAEController
# ==========================================
class GAEController:
    def __init__(self, ros_node):
        self.node = ros_node
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            print(f"🔥 GPU Acceleration Enabled: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device("cpu")
            print("⚠️ GPU not found. Falling back to CPU.")
        
        # 📂 모델 경로 설정
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path_try_1 = os.path.join(script_dir, 'models', SimConfig.MODEL_NAME)
        path_try_2 = os.path.join(os.path.dirname(script_dir), 'models', SimConfig.MODEL_NAME)

        if os.path.exists(path_try_1):
            model_path = path_try_1
        elif os.path.exists(path_try_2):
            model_path = path_try_2
        else:
            print(f"❌ Model not found in:\n  1) {path_try_1}\n  2) {path_try_2}")
            sys.exit(1)
        
        print(f"📂 Loading Model: {model_path}")
        try:
            # JIT 로드 방식 권장
            self.model = torch.jit.load(model_path, map_location=self.device)
            self.model.eval()
        except Exception as e:
            print(f"❌ Model Load Error: {e}")
            sys.exit(1)

        self.history_len = 6
        self.num_dofs = 12
        self.last_joint_pos = SimConfig.DEFAULT_DOF_POS.copy() 
        self.dof_history = deque(
            [np.zeros(self.num_dofs, dtype=np.float32) for _ in range(self.history_len)], maxlen=self.history_len)

        self.last_action = np.zeros(self.num_dofs, dtype=np.float32)

    def startup_sequence(self):
        """
        로봇을 0도(Neutral)에서 시작 자세(Frog Pose)로 부드럽게 이동시킵니다.
        움직이는 동안에도 ROS 통신(spin_once)을 유지합니다.
        """
        print("\n⏳ [Safety Start] Moving to NEUTRAL (0,0,0) to check Offsets...")
        
        zero_pose = np.zeros(12, dtype=np.float32)

        # 🔥 다시 한 번 RAW 동기화
        self.node.set_servos(zero_pose, raw=True)
        time.sleep(0.3)
        
        # 1. 0도 자세 유지 (2초) - 오프셋 확인용
        # time.sleep 대신 spin_once를 써야 센서 데이터가 계속 갱신됩니다.
        for _ in range(100): 
            self.node.set_servos(zero_pose)
            rclpy.spin_once(self.node, timeout_sec=0.02)
            time.sleep(0.001) # CPU 과부하 방지용 미세 딜레이
            
        print("✅ Check your offsets now! (Robot should be in Neutral Pose)")
        
        # 눈으로 확인할 시간 1초 (여기서는 멈춰도 되므로 sleep 사용)
        time.sleep(1.0) 
        
        print("\n🐸 Moving to FROG POSE softly...")
        
        # 2. Interpolation: Neutral -> Frog Pose (2초)
        steps = 100 
        target_pose = SimConfig.DEFAULT_DOF_POS
        
        for i in range(steps):
            ratio = (i + 1) / steps
            # 선형 보간 (Linear Interpolation)
            current_cmd = zero_pose * (1 - ratio) + target_pose * ratio
            
            self.node.set_servos(current_cmd)
            rclpy.spin_once(self.node, timeout_sec=0.02) # 움직이면서도 센서 수신
            
        print("✅ Frog Pose Reached. Ready for RL Loop.\n")

    def get_observation(self, command):
        ang_vel = self.node.ang_vel
        proj_grav = self.node.proj_grav
        lin_vel = command[:3]
        history_obs = np.array(self.dof_history).flatten().astype(np.float32)
        obs = np.concatenate([lin_vel, ang_vel, proj_grav, command, history_obs])
        return torch.from_numpy(obs).float().unsqueeze(0).to(self.device)

    def control_loop(self):
        print("\n🚀 GAE Controller Initialization...")

        # 1️⃣ [순서 변경] IMU 데이터가 들어올 때까지 먼저 기다립니다.
        # 센서가 없는데 움직이기 시작하면 위험합니다.
        print("📡 Waiting for IMU data...")
        while rclpy.ok() and not self.node.imu_received:
            rclpy.spin_once(self.node, timeout_sec=0.1)
        print("✅ IMU Connected!")

        # 2️⃣ [안전 시작] 스타트업 시퀀스 실행
        self.startup_sequence()

        # 3️⃣ [RL 루프 시작]
        print("🚀 Starting RL Control Loop (ROS2 + CUDA Mode)")
        command = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        try:
            while rclpy.ok():
                start_time = time.time()
                
                # ROS 콜백 처리 (IMU 데이터 갱신)
                rclpy.spin_once(self.node, timeout_sec=0)
                
                # 관측 및 추론
                obs = self.get_observation(command)
                with torch.no_grad():
                    actions = self.model(obs).cpu().numpy().flatten()

                # 안전 클리핑
                actions = np.clip(actions, -0.5, 0.5) 

                self.last_action = actions
                
                # 🔥 [중요] 튜닝 중에는 타겟을 고정 (Frog Pose 유지)
                # 모델이 뱉는 action을 서보에 반영하지 않고, 자세 유지력만 테스트
                # target_rad = SimConfig.DEFAULT_DOF_POS 
                
                # 나중에 걷게 하려면 아래 주석을 해제하고 위 줄을 주석 처리하세요
                target_rad = SimConfig.DEFAULT_DOF_POS + (actions * SimConfig.ACTION_SCALE)

                self.node.set_servos(target_rad)

                # History 업데이트
                relative_pos = (target_rad - SimConfig.DEFAULT_DOF_POS).astype(np.float32)
                self.last_joint_pos = target_rad.copy()        
                self.dof_history.append(relative_pos)           
                
                # 50Hz 주기 맞추기
                elapsed = time.time() - start_time
                if SimConfig.DT > elapsed:
                    time.sleep(SimConfig.DT - elapsed)

        except KeyboardInterrupt:
            print("\n🛑 KeyboardInterrupt Received. Keeping current pose...")
            # 종료 시 안전하게 현재 자세 유지 (혹은 0도로 가려면 아래 주석 해제)
            # self.node.set_servos(np.zeros(12)) 
            pass

def main(args=None):
    rclpy.init(args=args)
    hw_node = GAEHardwareNode()
    controller = GAEController(hw_node)
    try:
        controller.control_loop()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        hw_node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()