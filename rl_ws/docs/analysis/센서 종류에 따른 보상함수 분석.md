# SpotMicro 보상 함수 및 센서 구성 분석 보고서

이 보고서는 SpotMicro 로봇의 강화학습 환경(`Isaac-Velocity-Flat-Custom-Quad-v0`)에서 사용되는 **센서 구성**과 **보상 함수(Reward Functions)**의 상세 내용을 분석한 결과입니다.

## 1. 분석 대상 파일 (Analyzed Files)
이 보고서의 내용은 다음 설정 파일들을 기반으로 작성되었습니다.

*   **로봇 및 물리 설정:**  
    [`data/train_myrobot/config/spot_micro/spotmicro_quad.py`](../../data/train_myrobot/config/spot_micro/spotmicro_quad.py)
*   **평지(Flat) 환경 설정:**  
    [`data/train_myrobot/config/spot_micro/flat_env_cfg.py`](../../data/train_myrobot/config/spot_micro/flat_env_cfg.py)
*   **거친 지형(Rough) 환경 설정:**  
    [`data/train_myrobot/config/spot_micro/rough_env_cfg.py`](../../data/train_myrobot/config/spot_micro/rough_env_cfg.py)

---

## 2. 활성화된 센서 (Active Sensors)

강화학습 에이전트가 관측(Observation)을 위해 사용하는 센서들입니다.

### 2.1. 접촉 센서 (Contact Sensors)
*   **센서 이름:** `contact_forces`
*   **정의 위치:** `flat_env_cfg.py` (Line 16), `spotmicro_quad.py` (Line 12)
*   **활성화 여부:** **Active** (`spotmicro_quad.py`에서 `activate_contact_sensors=True`로 물리적 활성화됨)
*   **대상:** 로봇의 모든 링크 (`{ENV_REGEX_NS}/Robot/.*`)
*   **기능:** 로봇 신체 부위가 지형과 충돌할 때 발생하는 힘을 감지합니다.
*   **사용 목적:**
    *   **Feet Air Time:** 발이 공중에 떠 있는 시간 계산 (보상 함수)
    *   **Undesired Contacts:** 허벅지, 어깨 등 발 이외의 부위가 땅에 닿는지 감지 (패널티)

### 2.2. 내부 상태 센서 (Intrinsic Sensors)
별도의 센서 클래스가 아닌, 로봇 에셋(`robot`) 자체에서 오는 데이터입니다.
*   **관절 위치/속도 (Joint Position/Velocity):** 12개 모터의 각도 및 회전 속도.
*   **베이스 상태 (Base State):** 몸체의 선속도(Linear Velocity), 각속도(Angular Velocity).
*   **중력 벡터 (Projected Gravity):** 로봇이 기울어진 정도를 파악하기 위한 중력 투영 벡터.

### 2.3. 지형 높이 스캐너 (Height Scanner)
*   **센서 이름:** `height_scanner`
*   **정의 위치:** `flat_env_cfg.py` (Line 25), `rough_env_cfg.py` (Line 55)
*   **상태:**
    *   **Flat 환경:** **Disabled** (`None`으로 설정됨). 평지이므로 높이 정보가 불필요합니다.
    *   **Rough 환경:** **Active**. 로봇 주변의 지형 높이 맵을 레이캐스팅(Ray-casting)으로 스캔하여 관측값에 포함합니다.

---

## 3. 보상 함수 (Reward Functions)

에이전트가 어떤 행동을 해야 하는지(또는 하지 말아야 하는지)를 정의합니다.  
**파일 위치:** `flat_env_cfg.py` (Line 44~)

### 3.1. 주요 보상 (성능 향상)

| 보상 이름 (Term Name) | 가중치 (Weight) | 설명 (Description) |
| :--- | :--- | :--- |
| **track_lin_vel_xy_exp** | `5.0` | 목표 **선속도(전진/횡이동)**를 얼마나 잘 따르는지 평가합니다. (지수 함수 형태) |
| **track_ang_vel_z_exp** | `2.5` | 목표 **각속도(회전)**를 얼마나 잘 따르는지 평가합니다. |
| **feet_air_time** | `2.0` | **발이 공중에 떠 있는 시간**을 늘려, 로봇이 발을 질질 끌지 않고 걷도록 유도합니다. |

### 3.2. 규제 및 패널티 (안정성 확보)

| 보상 이름 (Term Name) | 가중치 (Weight) | 설명 (Description) |
| :--- | :--- | :--- |
| **undesired_contacts** | `-5.0` | **부적절한 접촉:** 발바닥 외에 몸체나 허벅지가 땅에 닿으면 큰 감점을 줍니다. |
| **lin_vel_z_l2** | `-0.5` | **수직 진동 억제:** 몸체가 위아래로 심하게 흔들리는 것을 방지합니다 (z축 속도 최소화). |
| **ang_vel_xy_l2** | `-0.05` | **기울임 방지:** 몸체가 앞뒤(Pitch)나 좌우(Roll)로 흔들리는 것을 억제합니다. |
| **flat_orientation_l2** | `-1.0` | **수평 유지:** 몸체가 평평하게 유지되지 않으면 감점을 줍니다. |
| **base_height_l2** | `-2.0` | **높이 유지:** 목표 높이(`0.18m`)에서 벗어나면 감점을 줍니다. (너무 낮게 주저앉거나 너무 높게 서지 않도록 함) |
| **dof_torques_l2** | `-0.00005` | **에너지 효율:** 모터 토크 사용량을 최소화하여 부드럽고 효율적인 움직임을 유도합니다. |
| **dof_acc_l2** | `-1.0e-7` | **진동 억제:** 관절 가속도를 줄여 급격하고 떨리는 움직임을 방지합니다. |
| **action_rate_l2** | `-0.01` | **명령 변화율 억제:** 이전 행동과 급격하게 다른 행동 명령을 내리는 것을 방지합니다. |
| **feet_contact_forces** | `-0.001` | **충격 완화:** 발이 땅에 닿을 때(Landing) 너무 강하게 쿵 찍지 않도록 힘을 제한합니다. (`threshold=10.0`) |

### 3.3. Rough 환경과의 주요 차이점 (`rough_env_cfg.py`)
*   **track_lin_vel_xy_exp:** 가중치가 `7.0`으로 더 높음 (거친 지형에서 속도 유지가 더 중요해서 강화).
*   **feet_air_time:** 가중치가 `5.0`으로 더 높음 (장애물을 넘기 위해).
*   **base_height_l2:** 목표 높이가 `0.19m`로 다소 높고, 가중치도 `-5.0`으로 더 강력하게 높이 유지를 요구함.
*   **feet_contact_forces:** 가중치가 `-0.005`로 Flat보다 더 엄격하게 충격을 관리함.
