# ==============================================================
# SpotMicro – DS3218 (no feedback servo) + MPU6050 (IMU only)
# RL Training Config (User Config + Small Push + Tilt Correction)
# ==============================================================

import isaaclab.sim as sim_utils
from isaaclab.actuators import IdealPDActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.utils import configclass
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import (
    LocomotionVelocityRoughEnvCfg,
    RewardsCfg,
    EventCfg,
    TerminationsCfg,
    CurriculumCfg,
)
from isaaclab.managers import RewardTermCfg, SceneEntityCfg, EventTermCfg, TerminationTermCfg, ObservationTermCfg, ObservationGroupCfg
from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
from isaaclab.utils.noise import AdditiveUniformNoiseCfg as Unoise
import isaaclab.envs.mdp as mdp
import copy
import torch

# ==============================================================
# [핵심] 발 순서 명시적 정의
# ==============================================================
FOOT_BODY_NAMES = [
    "front_left_foot_link",
    "front_right_foot_link",
    "rear_left_foot_link",
    "rear_right_foot_link",
]

# ==============================================================
# Custom Reward Functions (Dynamic Thresholds applied)
# ==============================================================

def flat_orientation_roll_pitch_reward(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    asset = env.scene[asset_cfg.name]
    proj_grav = asset.data.projected_gravity_b
    return torch.sum(torch.square(proj_grav[:, :2]), dim=1)

def feet_air_time_reward_custom(env: ManagerBasedRLEnv, command_name: str, sensor_cfg: SceneEntityCfg, threshold: float) -> torch.Tensor:
    contact_sensor = env.scene.sensors[sensor_cfg.name]
    air_time = contact_sensor.data.last_air_time[:, sensor_cfg.body_ids]
    contact_forces = contact_sensor.data.net_forces_w[:, sensor_cfg.body_ids, :]
    
    in_contact = torch.norm(contact_forces, dim=-1) > 1.0
    air_time_clipped = torch.clamp(air_time, max=0.5)
    
    reward_error = torch.clamp(air_time_clipped - threshold, min=0.0)
    reward = torch.sum(reward_error * (~in_contact), dim=1)
    
    # [상대 속도 기준] 명령의 50% 이상 속도로 움직여야 보상 지급
    command = env.command_manager.get_command(command_name)
    robot = env.scene["robot"]
    
    base_lin_vel = torch.norm(robot.data.root_lin_vel_b[:, :2], dim=1)
    cmd_vel_norm = torch.norm(command[:, :2], dim=1)
    
    # 조건: 명령이 유의미하게 있고(>0.1) AND 실제 속도가 명령 속도의 50%를 넘어야 함
    is_moving = (cmd_vel_norm > 0.1) & (base_lin_vel > (cmd_vel_norm * 0.5))
    
    reward *= is_moving.float()
    return reward

def foot_clearance_reward_custom(env: ManagerBasedRLEnv, target_toe_height: float, asset_cfg: SceneEntityCfg, sensor_cfg: SceneEntityCfg, command_name: str) -> torch.Tensor:
    robot = env.scene[asset_cfg.name]
    foot_pos_z = robot.data.body_pos_w[:, asset_cfg.body_ids, 2]
    
    contact_sensor = env.scene.sensors[sensor_cfg.name]
    contact_forces = contact_sensor.data.net_forces_w[:, sensor_cfg.body_ids, :]
    is_swing_phase = torch.norm(contact_forces, dim=-1) < 1.0
    
    error = torch.square(foot_pos_z - target_toe_height)
    reward = torch.exp(-error / 0.02)
    
    # [상대 속도 기준] 명령의 50% 이상 속도로 움직여야 보상 지급
    command = env.command_manager.get_command(command_name)
    base_lin_vel = torch.norm(robot.data.root_lin_vel_b[:, :2], dim=1)
    cmd_vel_norm = torch.norm(command[:, :2], dim=1)
    
    is_moving = (cmd_vel_norm > 0.1) & (base_lin_vel > (cmd_vel_norm * 0.5))
    
    return torch.sum(reward * is_swing_phase.float(), dim=1) * is_moving.float()

def trot_phase_reward_custom(env: ManagerBasedRLEnv, sensor_cfg: SceneEntityCfg) -> torch.Tensor:
    contact_sensor = env.scene.sensors[sensor_cfg.name]
    c = torch.norm(contact_sensor.data.net_forces_w[:, sensor_cfg.body_ids, :], dim=-1) > 1.0
    
    diag_sync = (c[:, 0] == c[:, 3]) & (c[:, 1] == c[:, 2])
    alternating = (c[:, 0] != c[:, 1])
    
    return (diag_sync & alternating).float()

# ==============================================================
# Commands
# ==============================================================

@configclass
class SpotMicroCommandsCfg:
    base_velocity = mdp.UniformVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(5.0, 10.0), 
        rel_standing_envs=0.1,
        rel_heading_envs=0.0,
        heading_command=False,
        ranges=mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(0.0, 0.4), 
            lin_vel_y=(0.0, 0.0),
            ang_vel_z=(-0.3, 0.3), 
            heading=(0.0, 0.0),
        ),
    )

# ==============================================================
# Observations (Method 3 Applied)
# ==============================================================

@configclass
class SpotMicroObservationsCfg:
    @configclass
    class PolicyCfg(ObservationGroupCfg):
        # [Method 3 핵심] 노이즈 강화 (0.1) - 실제 로봇에서의 오차 적응용
        base_lin_vel = ObservationTermCfg(
            func=mdp.base_lin_vel,
            params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link")},
            noise=Unoise(n_min=-0.1, n_max=0.1) 
        )
        base_ang_vel = ObservationTermCfg(func=mdp.base_ang_vel, params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link")}, noise=Unoise(n_min=-0.05, n_max=0.05))
        projected_gravity = ObservationTermCfg(func=mdp.projected_gravity, params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link")}, noise=Unoise(n_min=-0.02, n_max=0.02))
        velocity_commands = ObservationTermCfg(func=mdp.generated_commands, params={"command_name": "base_velocity"})
        actions = ObservationTermCfg(func=mdp.last_action, history_length=6)

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    @configclass
    class CriticCfg(ObservationGroupCfg):
        base_lin_vel = ObservationTermCfg(func=mdp.base_lin_vel, params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link")})
        base_ang_vel = ObservationTermCfg(func=mdp.base_ang_vel, params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link")})
        projected_gravity = ObservationTermCfg(func=mdp.projected_gravity, params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link")})
        velocity_commands = ObservationTermCfg(func=mdp.generated_commands, params={"command_name": "base_velocity"})
        joint_pos = ObservationTermCfg(func=mdp.joint_pos_rel, params={"asset_cfg": SceneEntityCfg("robot")}, history_length=6)
        actions = ObservationTermCfg(func=mdp.last_action, history_length=6)
        
        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()
    critic: CriticCfg = CriticCfg()

# ==============================================================
# Rewards
# ==============================================================

@configclass
class SpotMicroRewardsCfg(RewardsCfg):
    alive_reward = None 

    track_lin_vel_xy_exp = RewardTermCfg(func=mdp.track_lin_vel_xy_exp, weight=2.0, params={"command_name": "base_velocity", "std": 0.15})
    
    track_ang_vel_z_exp = RewardTermCfg(func=mdp.track_ang_vel_z_exp, weight=1.0, params={"command_name": "base_velocity", "std": 0.25})
    
    feet_air_time = RewardTermCfg(
        func=feet_air_time_reward_custom,
        weight=1.5, 
        params={
            "command_name": "base_velocity",
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names=FOOT_BODY_NAMES),
            "threshold": 0.17, 
        },
    )
    
    foot_clearance = RewardTermCfg(
        func=foot_clearance_reward_custom,
        weight=0.5, 
        params={
            "target_toe_height": 0.17, # 안전값 유지
            "asset_cfg": SceneEntityCfg("robot", body_names=FOOT_BODY_NAMES),
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names=FOOT_BODY_NAMES),
            "command_name": "base_velocity"
        },
    )

    trot_contact_phase = RewardTermCfg(func=trot_phase_reward_custom, weight=1.5, params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=FOOT_BODY_NAMES)})

    action_rate_l2 = RewardTermCfg(func=mdp.action_rate_l2, weight=-0.00125)
    
    # [수정] 자세 기울어짐 패널티 강화 (-0.125 -> -0.5)
    # 로봇이 한쪽으로 기우는 것을 강력하게 억제하여 평평한 등(Flat Back)을 유도합니다.
    base_orientation = RewardTermCfg(func=flat_orientation_roll_pitch_reward, weight=-0.5, params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link")})
    
    joint_pos_limits = RewardTermCfg(func=mdp.joint_pos_limits, weight=-0.05, params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_shoulder"])})

    gait = None
    flat_orientation_l2 = None
    lin_vel_z_l2 = None
    ang_vel_xy_l2 = None
    dof_torques_l2 = None
    dof_acc_l2 = None
    dof_pos_limits = None
    feet_contact_forces = None
    undesired_contacts = None
    action_smoothness = None

# ==============================================================
# Events (Domain Randomization + Small Push)
# ==============================================================

@configclass
class SpotMicroEventCfg(EventCfg):
    # 1. 마찰력 랜덤화
    physics_material = EventTermCfg(
        func=mdp.randomize_rigid_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "static_friction_range": (0.6, 1.5),
            "dynamic_friction_range": (0.6, 1.5),
            "restitution_range": (0.0, 0.0),
            "num_buckets": 64,
        },
    )

    # 2. 질량 랜덤화
    add_base_mass = EventTermCfg(
        func=mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="base_link"),
            "mass_distribution_params": (-0.2, 0.4),
            "operation": "add",
        },
    )

    # 3. [추가] 아주 작은 외력 밀기 (Micro Push)
    # 10~15초마다 아주 살짝(±0.1m/s) 밀어서 자세 제어 능력을 키웁니다.
    push_robot = EventTermCfg(
        func=mdp.push_by_setting_velocity,
        mode="interval",
        interval_range_s=(10.0, 15.0),
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="base_link"),
            "velocity_range": {
                "x": (-0.1, 0.1), 
                "y": (-0.1, 0.1),
            },
        },
    )
    
    base_com = None
    base_external_force_torque = None

    reset_base = EventTermCfg(
        func=mdp.reset_root_state_uniform, 
        mode="reset",
        params={
            "pose_range": {"x": (0.0, 0.0), "y": (0.0, 0.0), "yaw": (0.0, 0.0)},
            "velocity_range": {
                "x": (0.0, 0.0), "y": (0.0, 0.0), "z": (0.0, 0.0),
                "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0)
            },
            "asset_cfg": SceneEntityCfg("robot", body_names="base_link"),
        },
    )

    reset_robot_joints = EventTermCfg(
        func=mdp.reset_joints_by_scale, 
        mode="reset",
        params={
            "position_range": (1.0, 1.0), 
            "velocity_range": (0.0, 0.0), 
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
        },
    )

# ==============================================================
# Terminations
# ==============================================================

@configclass
class SpotMicroTerminationsCfg(TerminationsCfg):
    time_out = TerminationTermCfg(func=mdp.time_out, time_out=True)
    
    base_contact = TerminationTermCfg(
        func=mdp.illegal_contact,
        params={
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names="base_link"),
            "threshold": 50.0, 
        },
    )

    bad_orientation = TerminationTermCfg(
        func=mdp.bad_orientation,
        params={
            "limit_angle": 1.2, 
            "asset_cfg": SceneEntityCfg("robot", body_names="base_link")
        },
    )

# ==============================================================
# Main Environment Config
# ==============================================================

@configclass
class SpotMicroFlatStudentEnvCfg(LocomotionVelocityRoughEnvCfg):
    commands: SpotMicroCommandsCfg = SpotMicroCommandsCfg()
    observations: SpotMicroObservationsCfg = SpotMicroObservationsCfg()
    rewards: SpotMicroRewardsCfg = SpotMicroRewardsCfg()
    events: SpotMicroEventCfg = SpotMicroEventCfg()
    terminations: SpotMicroTerminationsCfg = SpotMicroTerminationsCfg()

    def __post_init__(self):
        self.decimation = 4
        self.sim.dt = 0.005 # 200Hz

        self.scene.height_scanner = RayCasterCfg(
            prim_path="{ENV_REGEX_NS}/Robot/base_link",
            offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 20.0)),
            attach_yaw_only=True,
            pattern_cfg=patterns.GridPatternCfg(resolution=0.1, size=[1.6, 1.0]),
            mesh_prim_paths=["/World/ground"]
        )

        self.scene.contact_forces = ContactSensorCfg(
            prim_path="{ENV_REGEX_NS}/Robot/.*",
            update_period=self.sim.dt,
            track_air_time=True, 
        )
        
        self.scene.terrain.terrain_type = "plane"
        self.curriculum.terrain_levels = None

        try:
            from .spotmicro_quad import SPOTMICRO_QUAD_CFG
            robot_cfg = copy.deepcopy(SPOTMICRO_QUAD_CFG)
        except Exception:
            raise RuntimeError("SPOTMICRO_QUAD_CFG 설정을 불러올 수 없습니다.")

        robot_cfg.prim_path = "{ENV_REGEX_NS}/Robot"
        
        robot_cfg.actuators = {
            "legs": IdealPDActuatorCfg(
                joint_names_expr=[".*_shoulder", ".*_leg", ".*_foot"],
                stiffness=25.0,   
                damping=2.5,      
                effort_limit=2.3, 
                velocity_limit=5.5, 
            )
        }

        robot_cfg.init_state = ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.22),
            joint_pos={
                ".*_shoulder": 0.0, 
                ".*_leg": 0.7,      
                ".*_foot": -1.4     
            },
            rot=(0.0, 0.0, 0.0, 1.0), 
        )

        self.scene.robot = robot_cfg
        super().__post_init__()

        self.actions.joint_pos.scale = 0.25

@configclass
class SpotMicroFlatStudentEnvCfg_PLAY(SpotMicroFlatStudentEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 32
        self.observations.policy.enable_corruption = False
