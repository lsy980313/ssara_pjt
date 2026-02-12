# 로봇 설정 코드 상세 분석

이 문서는 `data/train_myrobot/config/spot_micro/spotmicro_quad.py` 파일에 정의된 Spot Micro 로봇의 설정 값을 상세히 분석합니다. 이 설정은 Isaac Lab 시뮬레이션 환경에서 로봇의 물리적 특성, 제어 파라미터, 초기 상태를 결정짓는 핵심적인 요소입니다.

## 1. 센서 활성화 (Sensor Activation)

발바닥의 접촉 여부(Contact)를 감지하기 위한 설정입니다.

```python
activate_contact_sensors=True
```

*   **[중요] `activate_contact_sensors`**:
    *   **값**: `True`
    *   **설명**: 이 값이 `True`여야 로봇의 발이 지면에 닿았는지 감지할 수 있습니다. 보행 로봇의 강화학습에서 발의 접촉 정보(Contact Force/Boolean)는 보상을 계산하거나 관측(Observation) 데이터로 사용하는 데 매우 필수적입니다.
    *   **참고**: `*_no_sensor.py`와 같은 환경 설정 파일에서 이 값을 무시하고 강제로 센서를 끌 수도 있지만, 기본 로봇 설정(Asset) 레벨에서는 켜두는 것이 일반적입니다.

---

## 2. 강체 속성 (Rigid Body Properties)

로봇의 각 링크(Link)들이 가지는 물리적 저항과 한계값을 정의합니다.

```python
rigid_props=sim_utils.RigidBodyPropertiesCfg(
    rigid_body_enabled=True,
    disable_gravity=False,
    linear_damping=0.5,
    angular_damping=0.5,
    max_linear_velocity=1000.0,
    max_angular_velocity=1000.0,
    max_depenetration_velocity=1.0,
),
```

*   **`linear_damping` / `angular_damping`**: (간단) 공기 저항이나 마찰로 인한 감쇠를 시뮬레이션합니다. 0.5는 약간의 저항이 있는 상태입니다.
*   **`max_linear/angular_velocity`**: (간단) 물리 시뮬레이션의 안정성을 위해 속도의 최대값을 제한합니다.

---

## 3. 관절 속성 (Articulation Properties)

로봇 전체 구조(Articulation)에 대한 물리 엔진 솔버(Solver) 설정입니다.

```python
articulation_props=sim_utils.ArticulationRootPropertiesCfg(
    enabled_self_collisions=False,
    solver_position_iteration_count=4,
    solver_velocity_iteration_count=0,
    fix_root_link=False,
),
```

*   **[중요] `fix_root_link`**:
    *   **값**: `False`
    *   **설명**: 로봇의 몸체(Root Link)를 공간에 고정할지 여부입니다. 이동하는 로봇(Mobile Robot)이므로 반드시 `False`여야 합니다. `True`로 설정하면 로봇이 공중에 매달린 것처럼 움직이지 못합니다.
*   **`enabled_self_collisions`**: (간단) 로봇의 다리끼리 부딪히는 것을 계산할지 여부입니다. `False`로 설정하여 연산 속도를 높입니다(다리가 서로 겹쳐도 물리적으로 밀어내지 않음).

---

## 4. 초기 상태 설정 (Initial State)

시뮬레이션이 시작되거나 리셋(Reset)될 때 로봇이 취할 자세와 위치입니다.

```python
init_state=ArticulationCfg.InitialStateCfg(
    pos=(0.0, 0.0, 0.27),
    joint_pos={
        ".*_shoulder": 0.0,
        ".*_leg": -pi/6,
        ".*_foot": pi/3,
    },
    joint_vel={".*": 0.0},
),
```

*   **[중요] `pos (0.0, 0.0, 0.27)`**:
    *   **설명**: 로봇의 초기 위치(x, y, z)입니다. 여기서 `z=0.27`은 **0.27m 높이**에서 스폰됨을 의미합니다. 이는 로봇이 다리를 펴고 섰을 때의 적정 높이로 설정되어야 하며, 너무 높으면 떨어지면서 충격을 받고, 너무 낮으면 바닥에 파묻힐 수 있습니다.
*   **`joint_pos` (관절 각도)**:
    *   **설명**: 초기 기립 자세를 정의합니다.
    *   `shoulder`: 0도 (좌우 벌림 없음)
    *   `leg`: -30도 (-pi/6, 앞/뒤 허벅지)
    *   `foot`: 60도 (pi/3, 종아리)
    *   이 설정은 SpotMicro의 일반적인 "Home" 자세입니다.

---

## 5. 액추에이터 설정 (Actuator Configuration)

모터의 제어 방식과 물리적 한계를 정의합니다. Sim-to-Real(시뮬레이션과 실제 로봇 간 격차 줄이기)에 가장 중요한 부분입니다.

```python
actuators={
    "base_legs": IdealPDActuatorCfg(
        joint_names_expr=[".*_leg", ".*_foot", ".*_shoulder"],
        stiffness=40.0,
        damping=5.0,
        effort_limit=2.0,
        velocity_limit=7.0,
    ),
},
```

*   **[중요] `stiffness` (P gain)**:
    *   **값**: `40.0`
    *   **설명**: 위치 제어의 "강성"입니다. 값이 클수록 목표 위치로 가려는 힘이 강해져 로봇이 딱딱하게 움직이고, 값이 작으면 부드럽거나 흐물거리게 움직입니다.
*   **[중요] `damping` (D gain)**:
    *   **값**: `5.0`
    *   **설명**: 속도에 대한 저항입니다. 진동을 잡아주는 역할을 합니다. P 게인과 D 게인의 조화가 중요합니다.
*   **[중요] `effort_limit`**:
    *   **값**: `2.0`
    *   **설명**: 모터가 낼 수 있는 **최대 토크(N·m)**입니다. 실제 모터 스펙을 반영해야 현실적인 동작이 나옵니다.
*   **[중요] `velocity_limit`**:
    *   **값**: `7.0`
    *   **설명**: 관절의 **최대 회전 속도(rad/s)**입니다. 너무 빠른 움직임을 물리적으로 제한합니다.

---

### 요약
> 이 설정 파일은 Spot Micro가 **0.27m 높이**에서 기본 기립 자세로 시작하며, **이동 가능(fix_root_link=False)**하고, **발바닥 센서가 켜진(activate_contact_sensors=True)** 상태임을 정의합니다. 또한 모터는 **최대 2.0Nm의 토크**를 낼 수 있는 PD 제어기로 구동됩니다.