from isaaclab.utils import configclass
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg
from isaaclab_tasks.manager_based.locomotion.velocity.config.spotmicro_quadruped.spotmicro_quad import SPOTMICRO_QUAD_CFG
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import ContactSensorCfg
import isaaclab.envs.mdp as mdp

@configclass
class SpotMicroFlatEnvCfg(LocomotionVelocityRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # --- 로봇 및 센서 설정 ---
        self.scene.robot = SPOTMICRO_QUAD_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.contact_forces = ContactSensorCfg(
            prim_path="{ENV_REGEX_NS}/Robot/.*", 
            history_length=3, 
            track_air_time=True
        )

        # 평지 지형 설정
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None
        self.scene.height_scanner = None
        self.observations.policy.height_scan = None
        self.curriculum.terrain_levels = None

        # --- 동작 및 속도 범위 확장 ---
        self.actions.joint_pos.scale = 0.5
        self.commands.base_velocity.ranges.lin_vel_x = (-0.6, 0.6) 
        self.commands.base_velocity.ranges.lin_vel_y = (-0.3, 0.3) 
        self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)

        # --- 이벤트 설정 (오류 수정: base -> base_link) ---
        self.events.push_robot = None
        self.events.add_base_mass.params["asset_cfg"].body_names = "base_link"
        self.events.add_base_mass.params["mass_distribution_params"] = (-0.2, 1.0)
        self.events.base_external_force_torque.params["asset_cfg"].body_names = "base_link"
        self.events.base_com.params["asset_cfg"].body_names = "base_link"
        self.events.reset_robot_joints.params["position_range"] = (1.0, 1.0)

        # --- 보상 설정 (움직임 중심 강화) ---
        self.rewards.track_lin_vel_xy_exp.weight = 5.0 
        self.rewards.track_ang_vel_z_exp.weight = 2.5  
        self.rewards.feet_air_time.weight = 2.0 
        self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_foot_link"

        # 오류 수정: .*THIGH -> .*_leg_link
        self.rewards.undesired_contacts = RewTerm(
            func=mdp.undesired_contacts,
            weight=-5.0,
            params={
                "sensor_cfg": SceneEntityCfg("contact_forces", 
                    body_names=["base_link", ".*_shoulder_link", ".*_leg_link"]),
                "threshold": 1.0,
            },
        )

        setattr(self.rewards, "lin_vel_z_l2", RewTerm(func=mdp.lin_vel_z_l2, weight=-0.5))
        setattr(self.rewards, "ang_vel_xy_l2", RewTerm(func=mdp.ang_vel_xy_l2, weight=-0.05))
        self.rewards.flat_orientation_l2.weight = -1.0
        
        setattr(self.rewards, "base_height_l2", RewTerm(
            func=mdp.base_height_l2,
            weight=-2.0,
            params={
                "target_height": 0.18,
                "asset_cfg": SceneEntityCfg("robot", body_names="base_link")
            },
        ))

        self.rewards.dof_torques_l2.weight = -0.00005 
        self.rewards.dof_acc_l2.weight = -1.0e-7      
        setattr(self.rewards, "action_rate_l2", RewTerm(func=mdp.action_rate_l2, weight=-0.01))
        setattr(self.rewards, "feet_contact_forces", RewTerm(
            func=mdp.contact_forces, 
            weight=-0.001,
            params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot_link"), "threshold": 10.0}
        ))

        self.terminations.base_contact.params["sensor_cfg"].body_names = "base_link"

# --- [추가] 시각화(Play)를 위한 전용 설정 클래스 ---
@configclass
class SpotMicroFlatEnvCfg_PLAY(SpotMicroFlatEnvCfg):
    def __post_init__(self) -> None:
        super().__post_init__()
        # 시각화를 위해 로봇 수와 간격 조정
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        # 센서 데이터 노이즈(Corruption) 비활성화
        self.observations.policy.enable_corruption = False
        # 무작위 푸시 및 힘 이벤트 비활성화
        self.events.base_external_force_torque = None
        self.events.push_robot = None