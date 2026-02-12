import isaaclab.sim as sim_utils
from isaaclab.actuators import ActuatorNetMLPCfg, DCMotorCfg, ImplicitActuatorCfg, IdealPDActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
import os
from math import pi

SPOTMICRO_QUAD_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=os.environ['HOME'] + "/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/spotmicro_quadruped/spot_micro/spot_micro.usd",
        activate_contact_sensors=True,

        # 강체 관련 물리 속성
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            rigid_body_enabled=True, # added this line
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.5,
            angular_damping=0.5,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
        
        # 관절 관련 물리 속성
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=4,
            solver_velocity_iteration_count=0,
            fix_foot_link=False,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        # 초기 소환 위치 0.27로 변경
        pos=(0.0, 0.0, 0.27),
        joint_pos={
            ".*_shoulder": 0.0,
            ".*_leg": -pi/6,
            ".*_foot": pi/3,
        },
        joint_vel={".*": 0.0},
    ),
    soft_joint_pos_limit_factor=0.9,
    actuators={
        "base_legs": IdealPDActuatorCfg(
            joint_names_expr=[".*_leg", ".*_foot", ".*_shoulder"],
            stiffness    = 40.0,        # P게인 (강성, N·m/rad): 관절 복원력 (무거운 로봇은 ~40까지 증가)
            damping      = 5.0,         # D게인 (감쇠, N·m·s/rad): 진동 억제 (P게인의 약 5% 수준 권장)
            effort_limit = 2.0,         # 최대 토크 (N·m): 모터가 낼 수 있는 최대 힘
            velocity_limit = 7.0        # 최대 속도 (rad/s): 관절 회전 속도 한계
        ),
        # "base_legs": ImplicitActuatorCfg(
        #     joint_names_expr=[".*_leg", ".*_foot", ".*_shoulder"],   # regex khớp tên hinge
        #     stiffness=20.0,                    # k_p  (N·m/rad)
        #     damping=0.5,                       # k_d  (N·m·s/rad)
        #     effort_limit=3.4,                  # τ_max
        #     velocity_limit=8.0,                # |ω|
        #     armature=0.0,                      # giữ mặc định
        # )
    },
)