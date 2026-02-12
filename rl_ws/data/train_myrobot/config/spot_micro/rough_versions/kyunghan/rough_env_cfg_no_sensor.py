from isaaclab.utils import configclass
from .rough_env_cfg import SpotMicroRoughEnvCfg
from .spotmicro_quad import SPOTMICRO_QUAD_CFG

@configclass
class SpotMicroRoughNoSensorEnvCfg(SpotMicroRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # [수정] 로봇 설정 덮어쓰기
        # 부모 클래스에서 정의된 로봇이 있다면 교체, 없으면 새로 정의
        # 중복 소환 방지를 위해 replace() 사용 시 주의 (이미 부모에서 생성된 경우 덮어써야 함)
        
        # LocomotionVelocityRoughEnvCfg -> SpotMicroRoughEnvCfg -> NoSensorEnvCfg
        # self.scene.robot = SPOTMICRO_QUAD_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

        # --- Phase 1: 보상 가중치 조정 (2026-02-01) ---
        self.rewards.track_lin_vel_xy_exp.weight = 7.0 
        self.rewards.track_ang_vel_z_exp.weight = 3.5 
        self.rewards.flat_orientation_l2.weight = -0.5
        self.rewards.action_rate_l2.weight = -0.005

        # --- Phase 2: 명령 범위 확대 (2026-02-04) ---
        # [Fix] 움직임 활성화 및 탐색 유도 (속도 범위 현실화)
        self.commands.base_velocity.ranges.lin_vel_x = (-0.6, 0.6)
        self.commands.base_velocity.ranges.lin_vel_y = (-0.3, 0.3)
        self.commands.base_velocity.ranges.ang_vel_z = (-0.6, 0.6)

        # --- 센서 비활성화 ---
        self.scene.height_scanner = None
        # 주의: Base Contact 종료 조건을 위해 contact_forces 센서는 scene에 남겨둠 (물리 계산용)
        # self.scene.contact_forces = None 

        # --- 관측 비활성화 (로봇이 센서 정보를 보지 못하게 함) ---
        self.observations.policy.height_scan = None
        self.observations.policy.contact_forces = None # 명시적 차단

        # --- 관련 보상 비활성화 ---
        # [Restore] Blind Policy도 물리 엔진의 Privileged Info를 통해 학습 가능
        # self.rewards.feet_air_time = None
        # self.rewards.undesired_contacts = None
        
        # setattr로 추가된 보상 제거 (feet_contact_forces)
        if hasattr(self.rewards, "feet_contact_forces"):
            delattr(self.rewards, "feet_contact_forces")

        # --- 종료 조건 설정 ---
        # [NEW] [Fix] PhysX Error: Patch buffer overflow 해결
        # 에러 메시지에서 요구한 358714보다 여유 있게 설정
        self.sim.physx.gpu_max_rigid_patch_count = 12 * 10**5 

@configclass
class SpotMicroRoughNoSensorEnvCfg_PLAY(SpotMicroRoughNoSensorEnvCfg):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False
        self.events.base_external_force_torque = None
        self.events.push_robot = None
