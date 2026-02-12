# 베이스 환경 코드 상세 분석 (Base Environment Code Analysis)

실전 코드에서 상속해서 쓰는 `flat_env_cfg.py`, `rough_env_cfg.py`에 대한 상세 분석입니다.

---

## 1. Flat Environment (`flat_env_cfg.py`)
평지 환경에서의 학습 및 디버깅을 위한 설정입니다.

### 1.1 로봇 설정 (Robot Settings)
*   **기본 정의**: `spotmicro_quad.py`의 설정을 불러옵니다.
*   **Sensor**: `ContactSensorCfg`가 활성화되어 발바닥 접촉을 감지합니다. (`track_air_time=True`)

### 1.2 지형 설정 (Terrain Settings)
*   **Type**: `plane` (평지)
*   **특징**: 무한한 평면 바닥이며, 장애물이 없습니다.
*   **Curriculum**: 지형 난이도 조절이 없으므로 `None`으로 설정됩니다.

### 1.3 보상 설정 (Reward Settings)
초기 보행 패턴 형성을 위해 안정성 위주로 설정되어 있습니다.

| 보상 이름 | 가중치 | 설명 |
| :--- | :--- | :--- |
| **`track_lin_vel_xy_exp`** | **5.0** | 목표 속도 추종. Rough 보다 낮게 설정됨. |
| **`track_ang_vel_z_exp`** | **2.5** | 회전 속도 추종. |
| **`feet_air_time`** | **2.0** | 발이 공중에 떠있는 시간 보상. |
| **`undesired_contacts`** | -5.0 | 발 이외의 부위 접촉 페널티. |
| `base_height_l2` | -2.0 | 목표 높이(0.18m) 유지. |
| `lin_vel_z_l2` | -0.5 | 상하 진동 억제. |
| `feet_contact_forces` | -0.001 | 발바닥 충격력 최소화. |

### 1.4 이벤트 설정 (Event Settings)
*   **Push Robot**: `None` (로봇을 미는 외란 없음)
*   **Base Mass**: `base_link`의 질량을 `(-0.2, 1.0)` 범위에서 랜덤화.
*   **Reset**: 관절 위치를 랜덤화하지 않고 고정된 범위 `(1.0, 1.0)`로 초기화.

---

## 2. Rough Environment (`rough_env_cfg.py`)
불규칙한 지형에서의 강건한 보행 학습을 위한 설정입니다.

### 2.1 로봇 설정 (Robot Settings)
*   **높이 조정**: 초기 시작 높이가 `0.28m`로 설정되어 평지보다 약간 높게 시작합니다. (지형 높이 고려)
*   **Joint Scale**: `1.0` (Flat은 0.5로 되어있으나 Rough는 원본 스케일 사용)

### 2.2 지형 설정 (Terrain Settings)
*   **Generator**: 박스와 랜덤 노이즈 지형이 혼합되어 생성됩니다.
    *   **Boxes**: 높이 `0.005 ~ 0.03m` (0.5cm ~ 3cm)
    *   **Roughness**: 노이즈 범위 `0.003 ~ 0.15m`(0.3cm ~ 1.5cm)
*   **Curriculum (승급 시스템)**:
    *   **승급**: 목표 속도의 50% 이상 속도로 주행 시 난이도 상승.
    *   **강등**: 목표 속도의 10% 미만 속도 시 난이도 하락.
    *   **함수**: `spotmicro_velocity_curriculum`을 통해 완화된 기준 적용.

### 2.3 보상 설정 (Reward Settings)
다양한 지형 극복을 위해 추종 보상이 강화되고, 안정성 규제가 세분화되었습니다.

| 보상 이름 | 가중치 | 설명 |
| :--- | :--- | :--- |
| **`track_lin_vel_xy_exp`** | **7.0** | 목표 추종 성향을 강하게 설정. (Flat 대비 +2.0) |
| **`track_ang_vel_z_exp`** | **3.5** | 회전 추종 강화. |
| **`feet_air_time`** | **5.0** | 장애물을 넘기 위해 발을 더 확실히 들도록 유도. (임계값 0.15s) |
| **`base_height_l2`** | **-5.0** | 높이 유지 규제 강화. (목표 높이 0.19m) |
| `feet_contact_forces` | **-0.005** | 충격력 규제 (최근 대폭 하향 조정됨). |
| `action_rate_l2` | -0.05 | 급격한 제어 떨림 방지. |

### 2.4 이벤트 설정 (Event Settings)
*   **External Force**: `base_link`에 외란(밀기/토크)을 가하여 넘어지지 않도록 학습.
*   **Base Mass**: `add_base_mass`를 통해 무게 중심/질량 변화에 대응. (`base_link` 타겟 지정 확인됨)
