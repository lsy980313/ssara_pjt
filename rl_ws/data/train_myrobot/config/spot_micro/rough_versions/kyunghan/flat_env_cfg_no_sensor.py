from isaaclab.utils import configclass
from .flat_env_cfg import SpotMicroFlatEnvCfg
from .spotmicro_quad import SPOTMICRO_QUAD_CFG
@configclass
class SpotMicroFlatNoSensorEnvCfg(SpotMicroFlatEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # [추가] 로봇 설정 덮어쓰기
        self.scene.robot = SPOTMICRO_QUAD_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

        # --- 센서 비활성화 ---
        # Contact Sensor 제거
        # self.scene.contact_forces = None
        # Height Scanner는 이미 부모 클래스(Flat)에서 None임

        # --- 관련 보상 비활성화 ---
        # 센서 의존 보상 제거
        self.rewards.feet_air_time = None
        self.rewards.undesired_contacts = None
        
        # setattr로 추가된 보상 제거 (feet_contact_forces)
        if hasattr(self.rewards, "feet_contact_forces"):
            delattr(self.rewards, "feet_contact_forces")

        # --- 종료 조건 비활성화 ---
        # 몸체 접촉 종료 조건 제거 (Contact Sensor 의존)
        # self.terminations.base_contact = None

        # --- [Phase 1] 보상 가중치 조정 (2026-02-01) ---
        # TensorBoard 분석 결과:
        # - error_vel_xy 정체 (0.71) → 속도 추종 강화 필요
        # - action_rate 페널티 고착 → 유연성 확보
        self.rewards.track_lin_vel_xy_exp.weight = 7.0   # 기존: 5.0 → 속도 추종 강화
        self.rewards.flat_orientation_l2.weight = -0.5   # 기존: -1.0 → 자세 페널티 완화
        # action_rate_l2는 setattr로 추가됨, 다시 설정
        if hasattr(self.rewards, "action_rate_l2"):
            self.rewards.action_rate_l2.weight = -0.005  # 기존: -0.01 → 액션 변화 페널티 완화

@configclass
class SpotMicroFlatNoSensorEnvCfg_PLAY(SpotMicroFlatNoSensorEnvCfg):
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
