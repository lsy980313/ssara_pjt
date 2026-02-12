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
config_dir = os.path.join(current_dir, 'config')
sys.path.append(config_dir)

try:
    import hardware_config_test as hc
    print(f"✅ Hardware Config Loaded. Frog Pose: {hc.FROG_POSE}")
    
    # Config 변수 로드
    SERVO_MIN_PULSE = hc.SERVO_MIN_PULSE
    SERVO_MAX_PULSE = hc.SERVO_MAX_PULSE
    PCA_ADDR_FRONT  = hc.PCA_ADDR_FRONT
    PCA_ADDR_REAR   = hc.PCA_ADDR_REAR
    PIN_MAP         = hc.PIN_MAP
    SERVO_SAFE_MIN  = hc.SERVO_SAFE_MIN
    SERVO_SAFE_MAX  = hc.SERVO_SAFE_MAX
    
    # [중요] IMU 매핑 설정 로드
    IMU_AXIS_MAP    = hc.IMU_AXIS_MAP
    IMU_AXIS_SIGN   = hc.IMU_AXIS_SIGN
    
except ImportError:
    print("❌ Critical Error: 'hardware_config_test.py' not found.")
    sys.exit(1)

# === HARDWARE LIBRARIES ===
try:
    import board
    import busio
    from adafruit_servokit import ServoKit
    HAS_HARDWARE_MOTOR = True
except ImportError:
    print("⚠️ Motor libraries missing. Running in LOG ONLY mode.")
    HAS_HARDWARE_MOTOR = False

# ==========================================
# 1. Sim2Real Configuration
# ==========================================
class SimConfig:
    MODEL_NAME = "model_1250.pt"
    DT = 0.02             # 50Hz
    ACTION_SCALE = 0.25 
    
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
        self.prev_angles = np.full(12, 90.0)
        self._build_servo_map()

        if HAS_HARDWARE_MOTOR:
            try:
                i2c_id = getattr(hc, 'I2C_BUS_SERVO', 7) 
                try:
                    i2c = busio.I2C(board.SCL_1, board.SDA_1)
                except:
                    i2c = busio.I2C(board.SCL, board.SDA)

                self.kits['front'] = ServoKit(channels=16, i2c=i2c, address=PCA_ADDR_FRONT)
                self.kits['rear']  = ServoKit(channels=16, i2c=i2c, address=PCA_ADDR_REAR)
                
                for kit in self.kits.values():
                    kit.servo[0].set_pulse_width_range(SERVO_MIN_PULSE, SERVO_MAX_PULSE)
                
                self.get_logger().info(f"✅ Motor Driver Connected on Bus {i2c_id}.")
            except Exception as e:
                self.get_logger().error(f"❌ Motor Init Failed: {e}")
                HAS_HARDWARE_MOTOR = False

    def _build_servo_map(self):
        self.servo_map = []
        leg_order = ['front-left', 'front-right', 'rear-left', 'rear-right']
        
        for leg_key in leg_order:
            cfg = PIN_MAP[leg_key]
            kit = cfg['kit']
            pins = cfg['pins']
            dirs = cfg['dirs']
            offs = cfg['offset'] # ✅ Offset 적용됨
            
            # AI: [Shoulder, Leg, Foot] -> HW: pins[2], pins[1], pins[0]
            self.servo_map.append({'kit': kit, 'pin': pins[2], 'dir': dirs[2], 'off': offs[2]})
            self.servo_map.append({'kit': kit, 'pin': pins[1], 'dir': dirs[1], 'off': offs[1]})
            self.servo_map.append({'kit': kit, 'pin': pins[0], 'dir': dirs[0], 'off': offs[0]})

    def imu_callback(self, msg):
        self.imu_received = True
        
        # 1. Raw Data 추출
        raw_ang = [msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z]
        raw_acc = [msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z]
        
        # 2. Config 매핑 적용
        mapped_ang = [0.0, 0.0, 0.0]
        mapped_acc = [0.0, 0.0, 0.0]

        for i in range(3):
            # hc.IMU_AXIS_MAP = [1, 0, 2] -> X값 자리에 Y데이터를 넣어라
            idx = IMU_AXIS_MAP[i]
            sign = IMU_AXIS_SIGN[i]
            
            mapped_ang[i] = raw_ang[idx] * sign
            mapped_acc[i] = raw_acc[idx] * sign
            
        # 3. 데이터 저장 (Angular Velocity)
        self.ang_vel[:] = mapped_ang
        
        # 4. 데이터 저장 (Projected Gravity)
        ax, ay, az = mapped_acc
        norm = math.sqrt(ax*ax + ay*ay + az*az)
        if norm > 1e-4:
            self.proj_grav[0] = ax / norm
            self.proj_grav[1] = ay / norm
            self.proj_grav[2] = az / norm
        else:
            self.proj_grav[:] = [0.0, 0.0, -1.0]

    def set_servos(self, target_rad):
        target_deg = np.degrees(target_rad)
        final_angles = []
        for i, deg in enumerate(target_deg):
            m = self.servo_map[i]
            # ✅ Offset 적용: (각도 * 방향) + 90 + 오프셋
            angle = (deg * m['dir']) + 90.0 + m['off']
            angle = np.clip(angle, SERVO_SAFE_MIN, SERVO_SAFE_MAX)
            final_angles.append(angle)
            
        alpha = 0.7
        smooth = alpha * np.array(final_angles) + (1 - alpha) * self.prev_angles
        self.prev_angles = smooth

        if HAS_HARDWARE_MOTOR:
            for i, angle in enumerate(smooth):
                m = self.servo_map[i]
                try:
                    self.kits[m['kit']].servo[m['pin']].angle = angle
                except:
                    pass

# ==========================================
# 3. GAEController (기존 동일)
# ==========================================
class GAEController:
    def __init__(self, ros_node):
        global HAS_HARDWARE_MOTOR

        self.node = ros_node
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            print(f"🔥 GPU Acceleration Enabled: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device("cpu")
            print("⚠️ GPU not found. Falling back to CPU.")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, 'models', SimConfig.MODEL_NAME)
        
        print(f"📂 Loading Model: {model_path}")
        try:
            self.model = torch.jit.load(model_path, map_location=self.device)
            self.model.eval()
        except Exception as e:
            print(f"❌ Model Load Error: {e}")
            sys.exit(1)

        self.history_len = 6
        self.num_dofs = 12
        self.dof_history = deque([np.zeros(self.num_dofs)] * self.history_len, maxlen=self.history_len)
        self.last_action = np.zeros(self.num_dofs, dtype=np.float32)

    def get_observation(self, command):
        # ... (기존과 동일)
        ang_vel = self.node.ang_vel
        proj_grav = self.node.proj_grav
        lin_vel = command[:3] # ⚠️ 속도는 명령값으로 대체됨
        
        self.dof_history.append(self.last_action)
        history_obs = np.array(self.dof_history).flatten().astype(np.float32)
        
        obs = np.concatenate([lin_vel, ang_vel, proj_grav, command, history_obs])
        return torch.from_numpy(obs).float().unsqueeze(0).to(self.device)

    def control_loop(self):
        # ... (기존과 동일)
        print("\n🚀 GAE Controller Running (ROS2 + CUDA Mode)")
        while rclpy.ok() and not self.node.imu_received:
            rclpy.spin_once(self.node, timeout_sec=0.1)
        
        command = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        try:
            while rclpy.ok():
                start_time = time.time()
                rclpy.spin_once(self.node, timeout_sec=0)
                
                obs = self.get_observation(command)
                with torch.no_grad():
                    actions = self.model(obs).cpu().numpy().flatten()
                
                self.last_action = actions
                target_rad = SimConfig.DEFAULT_DOF_POS + (actions * SimConfig.ACTION_SCALE)
                self.node.set_servos(target_rad)
                
                elapsed = time.time() - start_time
                if SimConfig.DT > elapsed:
                    time.sleep(SimConfig.DT - elapsed)

        except KeyboardInterrupt:
            self.node.set_servos(SimConfig.DEFAULT_DOF_POS)

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