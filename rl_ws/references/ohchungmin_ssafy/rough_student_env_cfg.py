import torch
from typing import Sequence
from isaaclab.utils import configclass
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg
from isaaclab_tasks.manager_based.locomotion.velocity.config.spotmicro_quadruped.spotmicro_quad import SPOTMICRO_QUAD_CFG
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.sensors import ContactSensorCfg
import isaaclab.envs.mdp as mdp

# --- Reward Function ---
def foot_clearance(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg, target_height: float) -> torch.Tensor:
    asset = env.scene[asset_cfg.name]
    feet_pos = asset.data.body_pos_w[:, asset_cfg.body_ids]
    feet_height = feet_pos[:, :, 2] 
    error = torch.clamp(target_height - feet_height, min=0.0)
    return -torch.sum(torch.square(error), dim=1)

# --- Curriculum (Dummy for Flat) ---
def spotmicro_velocity_curriculum(env: ManagerBasedRLEnv, env_ids: Sequence[int], asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")):
    return torch.zeros(len(env_ids), device=env.device)

@configclass
class SpotMicroRoughStudentEnvCfg(LocomotionVelocityRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # ==========================================================
        # [Settings] Flat Terrain
        # ==========================================================
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None 
        self.curriculum.terrain_levels = None

        # ==========================================================
        # Observations (Blind Policy)
        # ==========================================================
        # 1. Student (Policy)
        self.observations.policy = ObsGroup()
        self.observations.policy.commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
        self.observations.policy.base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
        self.observations.policy.projected_gravity = ObsTerm(func=mdp.projected_gravity)
        self.observations.policy.actions = ObsTerm(func=mdp.last_action)

        # 2. Teacher (Critic)
        self.observations.critic = ObsGroup()
        self.observations.critic.commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
        self.observations.critic.base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
        self.observations.critic.projected_gravity = ObsTerm(func=mdp.projected_gravity)
        self.observations.critic.actions = ObsTerm(func=mdp.last_action)

        # --- 1. Robot & Sensors ---
        self.scene.robot = SPOTMICRO_QUAD_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.robot.init_state.pos = (0.0, 0.0, 0.27)
        self.scene.height_scanner = None 

        if hasattr(self.scene.robot, "actuator_models"):
            for actuator in self.scene.robot.actuator_models.values():
                actuator.delay = (1, 3)

        # [Sensor] Only tracking feet to save memory/logs
        self.scene.contact_forces = ContactSensorCfg(
            prim_path="{ENV_REGEX_NS}/Robot/.*foot.*", 
            history_length=3, 
            track_air_time=True
        )

        # --- 2. Actions & Commands ---
        self.actions.joint_pos.scale = 0.5 
        self.commands.base_velocity.ranges.lin_vel_x = (-0.2, 0.2) 
        self.commands.base_velocity.ranges.lin_vel_y = (-0.1, 0.1) 
        self.commands.base_velocity.ranges.ang_vel_z = (-0.3, 0.3)

        # --- 3. Events ---
        self.events.push_robot = None 
        self.events.add_base_mass.params["asset_cfg"].body_names = "base_link"
        self.events.add_base_mass.params["mass_distribution_params"] = (-0.2, 0.5)
        self.events.base_external_force_torque.params["asset_cfg"].body_names = "base_link"
        self.events.base_com.params["asset_cfg"].body_names = "base_link"
        self.events.reset_robot_joints.params["position_range"] = (1.0, 1.0)

        # --- 4. Rewards (Survival) ---
        self.rewards.track_lin_vel_xy_exp.weight = 7.0 
        self.rewards.track_ang_vel_z_exp.weight = 2.5  
        
        self.rewards.feet_air_time.weight = 10.0
        self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_foot_link"
        self.rewards.feet_air_time.params["threshold"] = 0.3 

        setattr(self.rewards, "foot_clearance", RewTerm(
            func=foot_clearance,
            weight=5.0,
            params={
                "asset_cfg": SceneEntityCfg("robot", body_names=".*_foot_link"),
                "target_height": 0.04, 
            },
        ))

        self.rewards.undesired_contacts = None

        setattr(self.rewards, "lin_vel_z_l2", RewTerm(func=mdp.lin_vel_z_l2, weight=-0.5))
        setattr(self.rewards, "ang_vel_xy_l2", RewTerm(func=mdp.ang_vel_xy_l2, weight=-0.05))
        self.rewards.flat_orientation_l2.weight = -5.0 
        
        setattr(self.rewards, "base_height_l2", RewTerm(
            func=mdp.base_height_l2,
            weight=-10.0,
            params={
                "target_height": 0.18,  
                "asset_cfg": SceneEntityCfg("robot", body_names="base_link")
            },
        ))

        setattr(self.rewards, "joint_deviation_l1", RewTerm(
            func=mdp.joint_deviation_l1,
            weight=-0.2,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*")}
        ))

        self.rewards.dof_torques_l2.weight = -0.0001 
        self.rewards.dof_acc_l2.weight = -2.5e-7      
        setattr(self.rewards, "action_rate_l2", RewTerm(func=mdp.action_rate_l2, weight=-0.1))
        
        setattr(self.rewards, "feet_contact_forces", RewTerm(
            func=mdp.contact_forces, 
            weight=-0.005,
            params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot_link"), "threshold": 10.0}
        ))

        # --- 5. Terminations ---
        # [REMOVED] Caused error because sensor only tracks feet now
        self.terminations.base_contact = None

@configclass
class SpotMicroRoughStudentEnvCfg_PLAY(SpotMicroRoughStudentEnvCfg):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.scene.num_envs = 32
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False
        self.events.base_external_force_torque = None
        self.events.push_robot = None