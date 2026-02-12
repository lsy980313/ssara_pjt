import torch
from typing import Sequence
from isaaclab.utils import configclass
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg
from isaaclab_tasks.manager_based.locomotion.velocity.config.spotmicro_quadruped.spotmicro_quad import SPOTMICRO_QUAD_CFG
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.sensors import ContactSensorCfg
import isaaclab.envs.mdp as mdp

# --- 커스텀 커리큘럼 로직 (승급/강등 기준 완화) ---
def spotmicro_velocity_curriculum(env: ManagerBasedRLEnv, env_ids: Sequence[int], asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")):
    asset = env.scene[asset_cfg.name]
    command = env.command_manager.get_command("base_velocity")[env_ids, :2]
    distance = torch.norm(asset.data.root_pos_w[env_ids, :2] - env.scene.env_origins[env_ids, :2], dim=1)
    
    target_distance = torch.norm(command, dim=1) * 20.0
    
    # 승급은 40% 이상 주행 시, 강등은 10% 미만 주행 시로 기준 완화 (안정성 확보)
    move_up = (distance > (target_distance * 0.50)) & (target_distance > 0.5)
    move_down = (distance < (target_distance * 0.10)) & (target_distance > 0.5)
    
    env.scene.terrain.terrain_levels[env_ids] += move_up.long()
    env.scene.terrain.terrain_levels[env_ids] -= move_down.long()
    
    max_level = 9
    if hasattr(env.scene.terrain.cfg.terrain_generator, "num_rows"):
        max_level = env.scene.terrain.cfg.terrain_generator.num_rows - 1
    env.scene.terrain.terrain_levels[env_ids] = torch.clamp(env.scene.terrain.terrain_levels[env_ids], 0, max_level)
    
    return torch.mean(env.scene.terrain.terrain_levels[env_ids].float())

@configclass
class SpotMicroRoughEnvCfg(LocomotionVelocityRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # --- 커스텀 승급 시스템 연결 ---
        if hasattr(self.curriculum, "terrain_levels"):
            self.curriculum.terrain_levels = CurrTerm(
                func=spotmicro_velocity_curriculum,
                params={"asset_cfg": SceneEntityCfg("robot")}
            )

        # --- 1. 로봇 및 센서 설정 ---
        self.scene.robot = SPOTMICRO_QUAD_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.robot.init_state.pos = (0.0, 0.0, 0.28) 
        self.scene.contact_forces = ContactSensorCfg(
            prim_path="{ENV_REGEX_NS}/Robot/.*", 
            history_length=3, 
            track_air_time=True
        )
        self.scene.height_scanner.prim_path = "{ENV_REGEX_NS}/Robot/base_link"

        # --- 2. 지형 설정 ---
        self.scene.terrain.terrain_generator.sub_terrains["boxes"].grid_height_range = (0.025, 0.1)
        self.scene.terrain.terrain_generator.sub_terrains["random_rough"].noise_range = (0.01, 0.06)
        self.scene.terrain.terrain_generator.sub_terrains["random_rough"].noise_step = 0.01

        # --- 3. 동작 및 속도 범위 ---
        self.actions.joint_pos.scale = 1.0
        self.commands.base_velocity.ranges.lin_vel_x = (-0.4, 0.4) 
        self.commands.base_velocity.ranges.lin_vel_y = (-0.2, 0.2) 
        self.commands.base_velocity.ranges.ang_vel_z = (-0.6, 0.6)

        # --- 4. 이벤트 설정 ---
        self.events.push_robot = None
        self.events.add_base_mass.params["asset_cfg"].body_names = "base_link"
        self.events.add_base_mass.params["mass_distribution_params"] = (-0.2, 1.0)
        self.events.base_external_force_torque.params["asset_cfg"].body_names = "base_link"
        self.events.base_com.params["asset_cfg"].body_names = "base_link"
        self.events.reset_robot_joints.params["position_range"] = (1.0, 1.0)

       # --- 5. 보상 설정 (안정화 버전) ---
        
        # 주행 성능
        self.rewards.track_lin_vel_xy_exp.weight = 7.0 
        self.rewards.track_ang_vel_z_exp.weight = 2.5  
        
        # 발 공중 시간 (임계값 0.12로 유지, 소형 로봇 최적화)
        self.rewards.feet_air_time.weight = 5.0 
        self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_foot_link"
        self.rewards.feet_air_time.params["threshold"] = 0.15

        # 원치 않는 접촉 (유지)
        self.rewards.undesired_contacts = RewTerm(
            func=mdp.undesired_contacts,
            weight=-5.0,
            params={
                "sensor_cfg": SceneEntityCfg("contact_forces", 
                    body_names=["base_link", ".*_shoulder_link", ".*_leg_link"]),
                "threshold": 1.0,
            },
        )

        # 안정성 및 높이 (가중치를 조금 더 차분하게 조정)
        setattr(self.rewards, "lin_vel_z_l2", RewTerm(func=mdp.lin_vel_z_l2, weight=-0.5))
        setattr(self.rewards, "ang_vel_xy_l2", RewTerm(func=mdp.ang_vel_xy_l2, weight=-0.05))
        self.rewards.flat_orientation_l2.weight = -1.0
        
        setattr(self.rewards, "base_height_l2", RewTerm(
            func=mdp.base_height_l2,
            weight=-5.0, # -7.0에서 다시 -5.0으로 하향 (폭주 방지)
            params={
                "target_height": 0.19, # 0.17에서 0.16으로 조정
                "asset_cfg": SceneEntityCfg("robot", body_names="base_link")
            },
        ))

        # 기본 자세 유지 (유지)
        setattr(self.rewards, "joint_deviation_l1", RewTerm(
            func=mdp.joint_deviation_l1,
            weight=-0.25, # -0.3에서 약간 하향
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*")}
        ))

        # 규제 및 떨림 방지 (이 부분은 강화된 상태 유지)
        self.rewards.dof_torques_l2.weight = -0.0001 
        self.rewards.dof_acc_l2.weight = -5.0e-7      
        setattr(self.rewards, "action_rate_l2", RewTerm(func=mdp.action_rate_l2, weight=-0.05)) # 떨림 방지
        
        # [수정 핵심] 발바닥 충격력 보상 대폭 하향
        setattr(self.rewards, "feet_contact_forces", RewTerm(
            func=mdp.contact_forces, 
            weight=-0.005, # -0.05에서 -0.005로 10배 하향 조정
            params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot_link"), "threshold": 10.0}
        ))

        # --- 6. 종료 조건 ---
        self.terminations.base_contact.params["sensor_cfg"].body_names = "base_link"

@configclass
class SpotMicroRoughEnvCfg_PLAY(SpotMicroRoughEnvCfg):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False
        self.events.base_external_force_torque = None
        self.events.push_robot = None