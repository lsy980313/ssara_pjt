# env_cfg.py 구조 및 내용 분석

이 문서는 `scripts/custom_quadruped_isaac/env_cfg.py` 파일의 구조와 주요 설정 내용을 분석한 결과입니다.

## 1. 파일 개요
이 파일은 IsaacLab의 `LocomotionVelocityRoughEnvCfg`를 상속받아 커스텀 4족 보행 로봇(SpotMicro 추정)의 강화학습 환경을 구성합니다. 지형(Rough/Flat)과 실행 모드(Train/Play)에 따라 4가지 클래스로 구분됩니다.

## 2. 클래스 계층 구조

*   **`LocomotionVelocityRoughEnvCfg`** (IsaacLab Base Class)
    *   **`CustomQuadRoughEnvCfg`**: 거친 지형(Rough Terrain) 학습용 기본 설정
        *   **`CustomQuadRoughEnvCfg_PLAY`**: 거친 지형 추론/테스트(Play)용 설정
        *   **`CustomQuadFlatEnvCfg`**: 평지(Flat Terrain) 학습용 설정
            *   **`CustomQuadFlatEnvCfg_PLAY`**: 평지 추론/테스트(Play)용 설정

## 3. 주요 설정 상세 (`CustomQuadRoughEnvCfg`)

가장 기본이 되는 `CustomQuadRoughEnvCfg` 클래스의 `__post_init__` 메서드에서 재정의된 주요 설정은 다음과 같습니다.

### 3.1 Scene (장면 설정)
*   **Robot**: `CUSTOM_QUAD_CFG`를 사용하며, Prim path는 `{ENV_REGEX_NS}/Robot`으로 설정됩니다.
*   **Height Scanner**: `{ENV_REGEX_NS}/Robot/trunk` 부착되어 지형 높이를 스캔합니다.
*   **Terrain (지형)**:
    *   로봇이 작기 때문에 지형의 스케일을 조정합니다.
    *   `grid_height_range`: (0.025, 0.1)
    *   `noise_range`: (0.01, 0.06)

### 3.2 Actions (액션)
*   **Joint Position Scale**: `0.25`로 설정하여 정책(Policy)의 출력이 관절 제어에 미치는 영향을 스케일링합니다.

### 3.3 Events (이벤트 및 랜덤화)
학습 시 환경의 다양성을 주기 위한 이벤트들입니다.
*   **`push_robot`**: `None`으로 설정되어 있어, 로봇을 미는 외력 이벤트는 **비활성화** 상태입니다.
*   **`add_base_mass`**: 로봇의 질량을 랜덤하게 변경 (분포 파라미터: -1.0 ~ 3.0). 대상 링크는 "trunk".
*   - trunk의 질량은 2.0으로 고정
*   **`base_external_force_torque`**: "trunk"에 외력/토크 적용.  **Body Names**: "trunk"
*   - 설명: 바람/외력 등 구현

*   **`reset_robot_joints`**: 리셋 시 관절 위치 범위. `(1.0, 1.0)`으로 설정되어 있는데, 이는 랜덤 범위가 아니라 고정된 값 일 수 있어 확인이 필요합니다 (보통 `(min, max)` 형태).
    - (1,1): 관절 위치 랜덤화를 끄고, 항상 정해진 기본 자세로 리셋하라
*   **`base_com`**: `None`으로 설정되어 무게 중심 변경 이벤트는 **비활성화** 상태입니다.

### 3.4 Rewards (보상 함수)
*   **`feet_air_time`**: 발이 공중에 떠 있는 시간 보상. 대상 링크는 `.*_calf` 정규식을 따릅니다. (가중치: 0.01)
*   **`undesired_contacts`**: 비활성화 (`None`).
*   **`dof_torques_l2`**: 토크 비용 (가중치: -0.0002).
*   **`track_lin_vel_xy_exp`**: XY 선속도 추종 (가중치: 1.5).
*   **`track_ang_vel_z_exp`**: Z 각속도 추종 (가중치: 0.75).
*   **`dof_acc_l2`**: 관절 가속도 비용 (가중치: -2.5e-7).

### 3.5 Terminations (종료 조건)
*   **`base_contact`**: "trunk"가 지면에 닿으면 에피소드 종료.

## 4. 파생 클래스 특징

### 4.1 `CustomQuadRoughEnvCfg_PLAY` (Play Mode)
*   학습된 정책을 테스트하거나 시각화할 때 사용합니다.
*   **환경 수**: 50개로 축소.
*   **지형**: 난이도(Curriculum) 없음, 5x5 그리드.
*   **랜덤화 비활성화**: `observation noise`, `push_robot`, `base_external_force_torque` 등이 꺼집니다.

### 4.2 `CustomQuadFlatEnvCfg` (Flat Terrain)
*   평평한 바닥에서 학습하기 위한 설정입니다.
*   **Terrain**: `terrain_type = "plane"`. Height Scanner 비활성화.
*   **Rewards**:
    *   `flat_orientation_l2`: 평지에서 자세 유지를 위한 보상 추가 (가중치: -2.5).
    *   `feet_air_time`: 가중치가 0.25로 Rough 환경(0.01)보다 높게 설정됨.

### 4.3 `CustomQuadFlatEnvCfg_PLAY`
*   평지 환경에서의 Play 모드 설정입니다.

## 5. 특이 사항 및 점검 포인트
*   **`reset_robot_joints`**: `position_range`가 `(1.0, 1.0)`으로 되어 있어, 리셋 시 관절 위치가 랜덤하지 않고 고정될 가능성이 있습니다. 의도된 것인지 확인 필요.
*   **비활성화된 항목들**: `push_robot`, `undesired_contacts`, `base_com` 등이 주석 처리되거나 `None`으로 설정되어 있습니다. 필요 시 활성화해야 합니다.
*   **Body Names**: "trunk", ".*_calf" 등의 이름이 실제 로봇 USD/URDF 파일의 링크 이름과 일치해야 합니다.

## 6. 초기화 (Reset) 기본 관절 위치
`scripts/custom_quadruped_isaac/custom_quad.py`의 `init_state`에 정의된 값입니다. `env_cfg.py`의 `reset_robot_joints` 설정 `(1.0, 1.0)`은 이 기본 위치를 100% 그대로 사용한다는 의미입니다.

| 관절 (Joint)                            | 설정값 (Radian) | 각도 (Degree, 약) |
| :-------------------------------------- | :-------------- | :---------------- |
| `L_hip_joint`, `R_hip_joint`            | `pi/45`         | **4도**           |
| `FL_thigh_joint`, `FR_thigh_joint`, ... | `-5*pi/18`      | **-50도**         |
| `FL_calf_joint`, `FR_calf_joint`, ...   | `5*pi/9`        | **100도**         |
