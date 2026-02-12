# No Sensor 환경 코드 상세 분석 (No Sensor Environment Code Analysis)

센서 데이터를 사용하지 않는(Blind) 환경 설정인 `flat_env_cfg_no_sensor.py`, `rough_env_cfg_no_sensor.py`에 대한 상세 분석입니다.
부모 클래스(`spotmicro_quad.py`, `flat_env_cfg.py`, `rough_env_cfg.py`)와의 차이점을 중점으로 기술합니다.

---

## 1. Flat Environment No Sensor (`flat_env_cfg_no_sensor.py`)
평지 환경에서 외부 센서 없이 **Proprioception(고유 수용성 감각)** 만으로 주행을 학습하기 위한 설정입니다.

### 1.1 로봇 설정 (Robot Settings)
*   **Robot Path**: `SPOTMICRO_QUAD_CFG`를 사용하되, `prim_path`를 `"{ENV_REGEX_NS}/Robot"`으로 변경하여 네임스페이스 충돌을 방지합니다.

### 1.2 센서 및 관측 비활성화 (Sensors & Observations)
**부모 코드(Flat)와의 주요 차이점**입니다.
*   **Contact Sensor**: `self.scene.contact_forces = None` (주석 처리됨, 실제로는 제거된 상태로 간주)
    *   발바닥 접촉 여부를 알 수 없습니다.
*   **Height Scanner**: 부모 클래스(Flat)와 동일하게 `None`입니다.

### 1.3 보상 설정 (Reward Settings)
센서 정보 부재로 인해 계산할 수 없는 보상이 제거되고, 학습 성향을 강화하기 위해 가중치가 조정되었습니다.

#### **제거된 보상 (Removed Rewards)**
센서 데이터가 없어 계산이 불가능한 항목들입니다.
*   **`feet_air_time`**: 발이 공중에 떠있는 시간 측정 불가 (Contact Sensor 부재).
*   **`undesired_contacts`**: 발 이외의 부위 충돌 감지 불가.
*   **`feet_contact_forces`**: 발바닥 충격력 측정 불가.

#### **가중치 조정 (Weight Adjustments)**
2026-02-01 Phase 1 튜닝 내용이 반영되어 있습니다.

| 보상 이름 | 변경 전 (Flat) | **변경 후 (No Sensor)** | 의도 |
| :--- | :--- | :--- | :--- |
| **`track_lin_vel_xy_exp`** | 5.0 | **7.0** | 속도 추종 성능 강화 (error_vel_xy 정체 해소). |
| **`flat_orientation_l2`** | -1.0 | **-0.5** | 자세 제어 페널티 완화. |
| **`action_rate_l2`** | -0.01 | **-0.005** | 급격한 액션 변화에 대한 제약 완화 (유연성 확보). |

### 1.4 이벤트 설정 (Event Settings)
*   **PLAY 모드**:
    *   `enable_corruption = False`: 관측 데이터에 노이즈를 추가하지 않음.
    *   `base_external_force_torque = None`: 외란 제거.
    *   `push_robot = None`: 밀기 이벤트 제거.

---

## 2. Rough Environment No Sensor (`rough_env_cfg_no_sensor.py`)
불규칙한 지형에서 **지형 높이 정보(Height Scan) 없이** 주행을 학습하는 설정입니다. 일명 "Blind Locomotion" 입니다.

### 2.1 로봇 설정 (Robot Settings)
*   **Robot Path**: Flat과 동일하게 `prim_path` 재설정.

### 2.2 센서 및 관측 비활성화 (Sensors & Observations)
**부모 코드(Rough)와의 가장 큰 차이점**으로, 로봇이 "눈을 감고" 걷는 것과 같습니다.
*   **Height Scanner**: `self.scene.height_scanner = None`
    *   로봇 주변의 지형 높이 맵을 생성하지 않습니다.
    *   **Policy Observation**: `self.observations.policy.height_scan = None`으로 정책 신경망 입력에서도 제거됩니다.
*   **Contact Sensor**: `feet_air_time` 등의 보상을 위해 유지될 수 있으나, 여기서는 보상 제거와 함께 비활성화 되는 흐름입니다.

### 2.3 보상 설정 (Reward Settings)
지형지물을 볼 수 없으므로, 더욱 강력한 추종 능력과 유연성이 필요합니다.

#### **제거된 보상 (Removed Rewards)**
*   **`feet_air_time`**: 체공 시간 보상 제거.
*   **`undesired_contacts`**: 충돌 페널티 제거.
*   **`feet_contact_forces`**: 충격력 페널티 제거.

#### **가중치 조정 (Weight Adjustments)**
Flat No Sensor와 유사하게 추종성은 높이고 규제는 낮췄습니다.

| 보상 이름 | 변경 전 (Rough) | **변경 후 (No Sensor)** | 의도 |
| :--- | :--- | :--- | :--- |
| **`track_lin_vel_xy_exp`** | - | **7.0** | 강력한 속도 추종 요구. |
| **`track_ang_vel_z_exp`** | - | **3.5** | 회전 추종 강화. |
| **`flat_orientation_l2`** | - | **-0.5** | 기울어짐에 대한 페널티 완화. |
| **`action_rate_l2`** | -0.01 | **-0.005** | 액션 변화 허용폭 증대. |

### 2.4 종료 조건 (Terminations)
*   **Base Contact**: `self.terminations.base_contact = None` (코드 주석 상황에 따라 다를 수 있으나, 일반적으로 Blind 환경에서는 몸체가 닿아도 계속 가보게 할 수도 있음, 현재 코드는 주석 처리되어 있어 `RoughEnvCfg`의 설정을 따르거나 비활성화됨).

### 2.5 이벤트 설정 (Event Settings)
*   **PLAY 모드**: Flat과 동일하게 노이즈 및 외란 제거로 시각화 및 검증 용이성 확보.
