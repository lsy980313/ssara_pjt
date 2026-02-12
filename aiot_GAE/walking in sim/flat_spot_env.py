import isaaclab.sim as sim_utils
from isaaclab.actuators import IdealPDActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.utils import configclass
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg, RewardsCfg, EventCfg, TerminationsCfg
from isaaclab.managers import RewardTermCfg, SceneEntityCfg, EventTermCfg, TerminationTermCfg, ObservationTermCfg, ObservationGroupCfg
from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
from isaaclab.utils.noise import AdditiveUniformNoiseCfg as Unoise
import isaaclab.envs.mdp as mdp 
import torch
import copy

##
# Custom Reward Functions
##

def flat_orientation_roll_pitch_reward(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    """Yaw를 제외하고 오직 Roll과 Pitch의 기울기만 패널티로 계산합니다."""
    asset = env.scene[asset_cfg.name]
    proj_grav = asset.data.projected_gravity_b
    return torch.sum(torch.square(proj_grav[:, :2]), dim=1)

def feet_air_time_reward_custom(env: ManagerBasedRLEnv, command_name: str, sensor_cfg: SceneEntityCfg, threshold: float) -> torch.Tensor:
    """발이 공중에 떠 있는 시간 보상"""
    contact_sensor = env.scene.sensors[sensor_cfg.name]
    air_time = contact_sensor.data.last_air_time[:, sensor_cfg.body_ids]
    contact_forces = contact_sensor.data.net_forces_w[:, sensor_cfg.body_ids, :]
    in_contact = torch.norm(contact_forces, dim=-1) > 1.0
    
    # 목표 시간(threshold)을 넘기면 보너스 지급 (min=0.0)
    reward_error = torch.clamp(air_time - threshold, min=0.0)
    reward = torch.sum(reward_error * in_contact, dim=1)
    
    command = env.command_manager.get_command(command_name)
    # 제자리 회전 시에는 끔 (선속도가 있을 때만 활성화)
    reward *= (torch.norm(command[:, :2], dim=1) > 0.1)
    return reward

def foot_clearance_reward_custom(env: ManagerBasedRLEnv, target_toe_height: float, asset_cfg: SceneEntityCfg, command_name: str) -> torch.Tensor:
    """발 높이(Clearance) 보상"""
    robot = env.scene[asset_cfg.name]
    foot_pos_z = robot.data.body_pos_w[:, asset_cfg.body_ids, 2]
    error = torch.square(foot_pos_z - target_toe_height)
    reward = torch.exp(-error / 0.02)
    command = env.command_manager.get_command(command_name)
    moving_mask = torch.norm(command[:, :2], dim=1) > 0.1
    return torch.sum(reward, dim=1) * moving_mask.float()

def trot_phase_reward_custom(env: ManagerBasedRLEnv, sensor_cfg: SceneEntityCfg) -> torch.Tensor:
    """
    [Solution K 유지] Trot Phase 강제 보상
    대각선 다리 쌍(Diagonal Pairs)이 동일한 접촉 상태일 때만 보상.
    """
    contact_sensor = env.scene.sensors[sensor_cfg.name]
    contact = torch.norm(contact_sensor.data.net_forces_w[:, sensor_cfg.body_ids, :], dim=-1) > 1.0
    
    pair1_synced = (contact[:, 0] == contact[:, 3]) # FL & RR
    pair2_synced = (contact[:, 1] == contact[:, 2]) # FR & RL
    
    return (pair1_synced & pair2_synced).float()

try:
    import isaaclab_tasks.manager_based.locomotion.velocity.config.spot.mdp as spot_mdp
except ImportError:
    spot_mdp = mdp

@configclass
class SpotMicroCommandsCfg:
    """
    [Step 1 유지: 직진 전용 모드]
    """
    base_velocity = mdp.UniformVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(5.0, 10.0),
        rel_standing_envs=0.1,
        rel_heading_envs=0.0,
        heading_command=False, 
        ranges=mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(0.1, 0.4), 
            lin_vel_y=(0.0, 0.0), 
            ang_vel_z=(0.0, 0.0),      
            heading=(0, 0)
        ),
    )

@configclass
class SpotMicroObservationsCfg:
    """관측치 설정 (Policy/Critic 분리 유지)"""
    @configclass
    class PolicyCfg(ObservationGroupCfg):
        base_ang_vel = ObservationTermCfg(func=mdp.base_ang_vel, params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link")}, noise=Unoise(n_min=-0.1, n_max=0.1))
        projected_gravity = ObservationTermCfg(func=mdp.projected_gravity, params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link")}, noise=Unoise(n_min=-0.02, n_max=0.02))
        velocity_commands = ObservationTermCfg(func=mdp.generated_commands, params={"command_name": "base_velocity"})
        joint_pos = ObservationTermCfg(func=mdp.joint_pos_rel, params={"asset_cfg": SceneEntityCfg("robot")}, history_length=6, noise=Unoise(n_min=-0.01, n_max=0.01))
        actions = ObservationTermCfg(func=mdp.last_action, history_length=6)

        def __post_init__(self):
            self.enable_corruption = True 
            self.concatenate_terms = True

    @configclass
    class CriticCfg(ObservationGroupCfg):
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

@configclass
class SpotMicroRewardsCfg(RewardsCfg):
    """
    [Solution L: 안전장치 재가동]
    """
    alive_reward = RewardTermCfg(func=mdp.is_alive, weight=0.5)
    
    # [수정] 속도 기준 강화 (0.5 -> 0.25)
    # 너무 제멋대로 뛰지 않도록 규제합니다.
    track_lin_vel_xy_exp = RewardTermCfg(func=mdp.track_lin_vel_xy_exp, weight=4.0, params={"command_name": "base_velocity", "std": 0.25})
    track_ang_vel_z_exp = RewardTermCfg(func=mdp.track_ang_vel_z_exp, weight=4.0, params={"command_name": "base_velocity", "std": 0.25})
    
    # [수정] Air Time 목표 현실화 (0.25 -> 0.22)
    feet_air_time = RewardTermCfg(func=feet_air_time_reward_custom, weight=5.0, params={"command_name": "base_velocity", "sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot_link"), "threshold": 0.22})
    
    foot_clearance = RewardTermCfg(func=foot_clearance_reward_custom, weight=5.0, params={"target_toe_height": 0.10, "asset_cfg": SceneEntityCfg("robot", body_names=".*_foot_link"), "command_name": "base_velocity"})

    gait = RewardTermCfg(func=getattr(spot_mdp, "GaitReward", mdp.joint_vel_l2), weight=2.0, params={"std": 0.1, "max_err": 0.2, "velocity_threshold": 0.1, "synced_feet_pair_names": (("front_left_foot_link", "rear_right_foot_link"), ("front_right_foot_link", "rear_left_foot_link")), "asset_cfg": SceneEntityCfg("robot"), "sensor_cfg": SceneEntityCfg("contact_forces")})
    
    trot_contact_phase = RewardTermCfg(func=trot_phase_reward_custom, weight=5.0, params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot_link")})
    
    # [수정] 진동 패널티 복구 (-0.002 -> -0.005)
    # 다시 안전벨트를 맵니다. 떨림을 방지합니다.
    action_rate_l2 = RewardTermCfg(func=mdp.action_rate_l2, weight=-0.005)

    base_orientation = RewardTermCfg(func=flat_orientation_roll_pitch_reward, weight=-0.5, params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link")})
    joint_pos_limits = RewardTermCfg(func=mdp.joint_pos_limits, weight=-0.5, params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_shoulder"])})

    flat_orientation_l2 = None
    lin_vel_z_l2 = None
    ang_vel_xy_l2 = None
    dof_torques_l2 = None
    dof_acc_l2 = None
    dof_pos_limits = None
    feet_contact_forces = None
    undesired_contacts = None
    action_smoothness = None

@configclass
class SpotMicroEventCfg(EventCfg):
    physics_material = EventTermCfg(func=mdp.randomize_rigid_body_material, mode="startup", params={"asset_cfg": SceneEntityCfg("robot", body_names=".*"), "static_friction_range": (0.8, 1.2), "dynamic_friction_range": (0.8, 1.0), "restitution_range": (0.0, 0.0), "num_buckets": 64})
    add_base_mass = EventTermCfg(func=mdp.randomize_rigid_body_mass, mode="startup", params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link"), "mass_distribution_params": (-0.2, 0.2), "operation": "add"})
    push_robot = EventTermCfg(func=mdp.push_by_setting_velocity, mode="interval", interval_range_s=(10.0, 15.0), params={"asset_cfg": SceneEntityCfg("robot", body_names="base_link"), "velocity_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5)}})
    base_com = None
    base_external_force_torque = None

@configclass
class SpotMicroTerminationsCfg(TerminationsCfg):
    time_out = TerminationTermCfg(func=mdp.time_out, time_out=True)
    base_contact = TerminationTermCfg(func=mdp.illegal_contact, params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names="base_link"), "threshold": 40.0})

@configclass
class SpotMicroFlatStudentEnvCfg(LocomotionVelocityRoughEnvCfg):
    commands: SpotMicroCommandsCfg = SpotMicroCommandsCfg() 
    observations: SpotMicroObservationsCfg = SpotMicroObservationsCfg()
    rewards: SpotMicroRewardsCfg = SpotMicroRewardsCfg()
    events: SpotMicroEventCfg = SpotMicroEventCfg()
    terminations: SpotMicroTerminationsCfg = SpotMicroTerminationsCfg()

    def __post_init__(self):
        self.decimation = 4 
        self.sim.dt = 0.005 
        self.scene.height_scanner = RayCasterCfg(prim_path="{ENV_REGEX_NS}/Robot/base_link", offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 20.0)), attach_yaw_only=True, pattern_cfg=patterns.GridPatternCfg(resolution=0.1, size=[1.6, 1.0]), mesh_prim_paths=["/World/ground"])
        self.scene.contact_forces = ContactSensorCfg(prim_path="{ENV_REGEX_NS}/Robot/.*", update_period=self.sim.dt, track_air_time=True)
        self.scene.terrain.terrain_type = "plane"
        self.curriculum.terrain_levels = None 

        try:
            from .spotmicro_quad import SPOTMICRO_QUAD_CFG
            robot_cfg = copy.deepcopy(SPOTMICRO_QUAD_CFG)
        except (ImportError, NameError):
            print("Warning: SPOTMICRO_QUAD_CFG not found.")
            return

        robot_cfg.prim_path = "{ENV_REGEX_NS}/Robot"
        
        robot_cfg.actuators = {
            "shoulders": IdealPDActuatorCfg(joint_names_expr=[".*_shoulder"], stiffness=25.0, damping=1.0, effort_limit=2.0, velocity_limit=6.5),
            "legs_feet": IdealPDActuatorCfg(joint_names_expr=[".*_leg", ".*_foot"], stiffness=25.0, damping=1.0, effort_limit=2.0, velocity_limit=6.5),
        }
        
        robot_cfg.init_state = ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, 0.18), joint_pos={".*_shoulder": 0.0, ".*_leg": 0.7, ".*_foot": -1.1})
        self.scene.robot = robot_cfg
        super().__post_init__()
        
        self.actions.joint_pos.scale = 0.30 

@configclass
class SpotMicroFlatStudentEnvCfg_PLAY(SpotMicroFlatStudentEnvCfg):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.scene.num_envs = 32
        self.observations.policy.enable_corruption = False