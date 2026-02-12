# Isaac Lab 강화학습 (RL) 실전 가이드

이 문서는 **Isaac Lab** 환경에서 강화학습을 수행하는 전반적인 절차를 설명합니다. 프로젝트 설정(Config), 학습(Training), 모니터링(Monitoring), 그리고 결과 검증(Play)까지의 전체 워크플로우를 다룹니다.

본 가이드는 **SpotMicro** 프로젝트를 예시로 사용하지만, 내용은 Isaac Lab을 사용하는 모든 프로젝트에 범용적으로 적용될 수 있습니다.

---

## 1. 강화학습 워크플로우 (Workflow Overview)

Isaac Lab의 강화학습 프로세스는 크게 4단계로 나뉩니다.

1.  **환경 설정 (Configuration):** 로봇, 지형, 센서, 보상 함수 등을 정의 (`env_cfg.py`, `rsl_rl_ppo_cfg.py`).
2.  **학습 (Training):** 정의된 환경에서 에이전트(로봇)를 학습시킴 (`train.py`).
3.  **모니터링 (Monitoring):** 학습 진행 상황을 그래프로 분석 (`Tensorboard`).
4.  **검증 및 시각화 (Play/Vis):** 학습된 정책(Policy)을 시뮬레이터에서 시각적으로 확인 (`play.py`).

---

## 2. 학습 수행 (Training)

학습은 `scripts/reinforcement_learning/rsl_rl/train.py` 스크립트를 통해 실행됩니다.

### 2.1 기본 실행 명령어
가장 기본적인 학습 실행 방법입니다.

```bash
# Isaac Lab 디렉토리로 이동 (컨테이너 내부)
cd ~/IsaacLab

# 학습 실행
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task=Isaac-Velocity-Flat-NoSensor-Spot-Micro-v0 \
    --num_envs=4096 \
    --headless
```

*   **`--task`**: 실행할 Task ID (예: `Isaac-Velocity-Flat-NoSensor-Spot-Micro-v0`). `gym.register`로 등록된 ID여야 합니다.
*   **`--num_envs`**: 병렬로 실행할 환경의 개수입니다. GPU 메모리에 따라 조절합니다 (예: 2048, 4096).
*   **`--headless`**: GUI 없이 백그라운드에서 실행합니다. 학습 속도가 훨씬 빠르므로 **학습 시에는 필수 권장**됩니다.

### 2.2 쉘 스크립트 활용
매번 긴 명령어를 입력하는 대신, 미리 정의된 쉘 스크립트를 사용하면 편리합니다.

**예시: `scripts/train_unsensored_flat.sh`**
```bash
#!/bin/bash
docker exec -it isaac-sim bash -c 'cd ~/IsaacLab && \
    ./isaaclab.sh \
    -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task=Isaac-Velocity-Flat-NoSensor-Spot-Micro-v0 \
    --num_envs=30000 \
    --headless'
```
*   호스트에서 이 스크립트를 실행하면 즉시 컨테이너 내부에서 학습이 시작됩니다.

### 2.3 학습 재개 (Resuming Training)
중단된 학습을 이어서 하거나, 특정 체크포인트에서 다시 시작하려면 다음 옵션을 사용합니다.

*   **`--resume`**: 가장 최근(last) 로그 폴더의 모델을 불러와서 이어서 학습합니다.
*   **`--load_run [폴더명]`**: 특정 날짜/시간의 학습 기록을 지정하여 불러옵니다.

```bash
# 최신 기록에서 이어서 학습
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task=Isaac-Velocity-Flat-NoSensor-Spot-Micro-v0 \
    --num_envs=4096 \
    --resume

# 특정 날짜의 기록 로드 (logs/rsl_rl/[experiment_name]/[date_folder])
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task=Isaac-Velocity-Flat-NoSensor-Spot-Micro-v0 \
    --num_envs=4096 \
    --resume \
    --load_run 2024-01-31_12-00-00
```

---

## 3. 모니터링 (Monitoring)

학습이 잘 되고 있는지 확인하기 위해 **Tensorboard**를 사용합니다.

### 3.1 로그 위치 확인
로그는 기본적으로 다음 경로에 저장됩니다. (호스트와 마운트된 경로 확인 필요)

*   **컨테이너 내부:** `/isaac-sim/IsaacLab/logs/rsl_rl/[Experiment_Name]/[Date_Time]`
*   **호스트 (SpotMicro 예시):** `~/workspaces/spotmicro/logs/rsl_rl/[Experiment_Name]/[Date_Time]`

### 3.2 Tensorboard 실행
컨테이너 내부에서 실행하는 것을 권장합니다.

```bash
# 컨테이너 접속
docker exec -it isaac-sim bash

# Isaac Lab 디렉토리로 이동
cd ~/IsaacLab

# Tensorboard 실행
./isaaclab.sh -p -m tensorboard.main --logdir logs/rsl_rl --port 6006 --bind_all
```

*   **접속 주소:** 웹 브라우저에서 `http://localhost:6006` 접속.
*   **주요 지표:**
    *   `Episode/reward`: 에피소드 당 총 보상 (우상향해야 함).
    *   `Episode/length`: 에피소드 길이 (오래 버틸수록 증가).
    *   `Loss/value_function`: Critic Loss (0으로 수렴하면 좋음).

---

## 4. 검증 및 시각화 (Play / Visualization)

Headless로 학습된 모델이 실제로 어떻게 행동하는지 눈으로 확인하는 단계입니다.

### 4.1 기본 시각화 실행 (`play.py`)

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task=Isaac-Velocity-Flat-NoSensor-Spot-Micro-Play-v0 \
    --num_envs=50 \
    --load_run 2024-01-31_12-00-00
```

*   **`--task`**: 보통 시각화용 Task (예: `...-Play-v0`)를 따로 둡니다. 이는 환경 리셋 조건을 완화하거나 로봇 개수를 줄인 버전입니다.
*   **`--num_envs`**: 시각화할 로봇의 마리 수 (GUI 부하를 줄이기 위해 50~100 정도 권장).
*   **`--load_run`**: 생략 시 가장 최신(last) 모델을 불러옵니다.

### 4.2 영상 녹화 (Recording)
결과 영상을 저장하려면 `--video` 옵션을 사용합니다.

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task=... \
    --video \
    --video_length 200
```
*   영상은 `logs/rsl_rl/.../videos` 폴더에 `.mp4` 형식으로 저장됩니다.

### 4.3 키보드 조작 (Keyboard Interaction)
시뮬레이터 창이 활성화된 상태에서 키보드로 로봇에게 명령을 내리거나 방해를 줄 수 있습니다. (설정에 따라 다름)
*   일반적으로 `play.py` 실행 시 터미널에 조작 키 가이드가 출력됩니다.
*   예: 화살표 키(이동), `R`(리셋) 등.

---

## 5. 고급 설정 (Advanced Configuration)

더 나은 성능을 위해 환경과 알고리즘을 튜닝합니다.

### 5.1 환경 설정 (`env_cfg.py`)
*   **Reward (보상):** 로봇이 무엇을 잘했을 때 점수를 줄지 정의합니다.
    *   `lin_vel_z`: 수직 움직임 최소화 (떨림 방지).
    *   `ang_vel_xy`: 몸체 기울기 최소화.
    *   `feet_air_time`: 발이 공중에 떠있는 시간 (자연스러운 보행 유도).
*   **Observations (관측):** 로봇이 센서를 통해 무엇을 "보는지" 결정합니다.
    *   `base_lin_vel`, `base_ang_vel`, `projected_gravity`, `joint_pos`, `joint_vel` 등.
*   **Actions (행동):** 로봇 제어 방식 (위치 제어, 토크 제어 등).

### 5.2 알고리즘 설정 (`rsl_rl_ppo_cfg.py`)
`rsl_rl` 라이브러리의 PPO 알고리즘 하이퍼파라미터를 수정합니다.
*   `num_steps_per_env`: 한 번의 업데이트에 사용할 데이터 길이 (Step 수).
*   `learning_rate`: 학습률.
*   `max_iterations`: 총 학습 반복 횟수.
*   `actor_hidden_dims` / `critic_hidden_dims`: 신경망 크기 (예: [512, 256, 128]).

### 5.3 커리큘럼 학습 (Curriculum Learning)
처음에는 쉬운 환경에서 시작해서 점차 어려운 환경으로 난이도를 올립니다.
*   **Terrain Curriculum:** 평지 -> 약간 거친 지형 -> 매우 거친 지형.
*   `terrain.curvature`나 `terrain.difficulty` 파라미터를 조절하여 설정합니다.

---

## 6. 모델 내보내기 (Exporting)

학습된 정책(`model_*.pt`)은 Isaac Lab 내부에서만 쓰이는 PyTorch 모델입니다. 이를 실제 로봇이나 다른 시뮬레이터에서 쓰기 위해 ONNX로 변환할 수 있습니다.

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/export.py \
    --task=Isaac-Velocity-Flat-NoSensor-Spot-Micro-v0 \
    --load_run ...
```
*   변환된 `.onnx` 파일은 inference 속도가 빠르고 의존성이 적어 배포에 유리합니다.

---

## 7. 튜닝 히스토리 (Tuning History)

학습 성능 개선을 위한 하이퍼파라미터 및 보상 조정 기록입니다.

### 2026-02-01: Phase 1 보상 가중치 조정

**대상 파일:** `config/spot_micro/flat_env_cfg_no_sensor.py`

**분석 근거 (TensorBoard):**
- `error_vel_xy`: 0.71 수준에서 정체 → 속도 추종 개선 필요
- `action_rate_l2`: 4k 스텝 이후 고착화 → 유연성 부족
- `Time_out`: 1.0 (에피소드 완주는 성공)

**변경 사항:**

| 보상 항목                  | 변경 전  | 변경 후   | 목적           |
| ---------------------- | ----- | ------ | ------------ |
| `track_lin_vel_xy_exp` | 5.0   | 7.0    | 속도 추종 강화     |
| `flat_orientation_l2`  | -1.0  | -0.5   | 자세 페널티 완화    |
| `action_rate_l2`       | -0.01 | -0.005 | 액션 변화 페널티 완화 |

**백업:** `flat_env_cfg_no_sensor_backup.py`

**다음 단계:**
- 10k 스텝 학습 후 TensorBoard 재분석
- 개선 없을 시 Phase 2 (PPO 하이퍼파라미터) 적용 예정

### 2026-02-01: Base Contact Termination 활성화 (Blind Reset)

**목적:**
로봇이 "넘어짐(Falling)"을 인식하여 에피소드를 리셋함으로써, 비정상적인 자세(기어다니기 등)로 보상을 받는 것을 방지합니다.
단, "센서 없는(No Sensor)" 컨셉을 유지하기 위해 Contact 정보는 정책(Policy)에는 입력되지 않습니다.

**구현 내용:**
- **File:** `config/spot_micro/flat_env_cfg_no_sensor.py`
- `scene.contact_forces`: 물리 엔진의 접촉 계산 활성화 (Policy Obs에는 미포함).
- `terminations.base_contact`: 몸체가 닿으면 에피소드 종료 조건 활성화.

**기대 효과:**
- 잘못된 자세로 버티기(Survival hacking) 방지.
- 올바른 보행 자세(발로만 지지) 유도.

### 2026-02-01: 속도 목표치 하향
> 실제 스팟마이크로 동작 동영상을 보고 어림잡아 너프함. 기존 수치는 눈대중으로 봤을때 안되는 수치임. 물론 시뮬레이션 환경의 모터 동작 속도 등의 변수를 추후에 확인해 봐야 한다.

20260203 flat_env에서는 다시 상향(너무 느려서 가만히 서있는 env 다수 발생)

self.commands.base_velocity.ranges.lin_vel_x = (-0.4, 0.4) -> (0.2, 0,2) -> (-0.4, 0.4) 

self.commands.base_velocity.ranges.lin_vel_y = (-0.2, 0.2) -> (-0.05, 0.05) -> (0.1, 0.1)

self.commands.base_velocity.ranges.ang_vel_z = (-0.6, 0.6) -> (-0.1, 0.1) -> (-0.4, 0.4)


20260203  rough_env에서도 소폭 상향(너무 느려서 가만히 서있는 env 다수 발생)
elf.commands.base_velocity.ranges.lin_vel_x = (-0.3, 0.3)

self.commands.base_velocity.ranges.lin_vel_y = (-0.1, 0.1)

self.commands.base_velocity.ranges.ang_vel_z = (-0.3, 0.3)

### 2026-02-01: `velocity_limit`, `effort_limit` 타당성 평가
> 모터 구매처의 데이터를 참조해, 모터 최대 속도를 제한하는 `velocity_limit` 변수의 타당성을 평가해 보았다.


- velocity_limit
datasheet
모터 Operating speed (at no load): 0.16 sec/60°(5v) ~ 0.14sec/60°(6.4v) -> 0.146sec/60°
= 60°

#### 1단계: 60도를 라디안(rad)으로 변환

각도(Degree)를 라디안(Radian)으로 바꾸기 위해 $\frac{\pi}{180}$를 곱합니다.

$$60^\circ \times \frac{\pi}{180} = \frac{60\pi}{180} = \frac{\pi}{3} \text{ rad}$$ $$(\text{약 } 1.0472 \text{ rad})$$

#### 2단계: 각속도(rad/s) 계산

속도는 **이동 거리(각도) ÷ 걸린 시간**입니다.

$$\text{속도 } (\omega) = \frac{\text{이동 각도}}{\text{걸린 시간}}$$ $$\omega = \frac{\frac{\pi}{3} \text{ rad}}{0.146 \text{ sec}}$$ $$\omega = \frac{\pi}{3 \times 0.146}$$ $$\omega = \frac{\pi}{0.438}$$

#### 3단계: 최종 수치 계산

$\pi \approx 3.14159$를 대입하여 계산합니다.

$$\omega \approx \frac{3.14159265}{0.438}$$ $$\omega \approx 7.17258...$$
**7.17rad/s**

- effort_limit
datasheet
Stall torque (at locked): 18 kg*cm(5v) ~ 21.5 kg*cm(6.4v) -> 20.5kg*cm(6v)
**2.01N/m**


### 0203 loosen 도메인 랜덤화
`flat_env_cfg.py`, `rough_env_cfg.py`에서 질량 관련 도메인 랜덤화 완화
self.events.add_base_mass.params["mass_distribution_params"] = (-0.2, 0.4)

0203 지형 높낮이 낮춤
self.scene.terrain.terrain_generator.sub_terrains["boxes"].grid_height_range = (0.005, 0.03)

self.scene.terrain.terrain_generator.sub_terrains["random_rough"].noise_range = (0.003, 0.15)

self.scene.terrain.terrain_generator.sub_terrains["random_rough"].noise_step = 0.01


0203 rough 목표속도 전진 쪽에 높여줌

self.actions.joint_pos.scale = 1.0

self.commands.base_velocity.ranges.lin_vel_x = (-0.2, 0.4)

self.commands.base_velocity.ranges.lin_vel_y = (-0.1, 0.1)

self.commands.base_velocity.ranges.ang_vel_z = (-0.3, 0.3)


외란 추가
추후에 학습이 잘 된 rough no sensor 모델이 생성된다면, 
self.events.base_external_force_torque.params["force_range"] = (-0.5, 0.5)

self.events.base_external_force_torque.params["torque_range"] = (-0.05, 0.05)
이 코드로 외란 추가(모터 틀어짐, 약한 바람 등도 외란으로 칠 수 있다.)

종료 조건 추가
"front_link", "rear_link"의 contact도 종료 조건으로 추가하였다.(no_sensor 버전에만)
self.terminations.base_contact.params["sensor_cfg"].body_names =

["base_link", "front_link", "rear_link",

"front_right_leg_link", "front_left_leg_link",

"rear_right_leg_link", "rear_left_leg_link"]
걍 몸통 + 윗다리 다 추가함 ㅋㅋ

---
>아이작랩 예제 코드 기반의 `spotmicroIsaacLab_github`코드 기반으로, 위에 수정한 값들만 바꿔서 환경 엎기

### 1. __init__.py
> 얘는 그냥 기존 거 들고와서 쓰고, 젬미니한테 이거에 맞게 코드 리팩터링을 맡기는 게 나을 듯

### 2. `rough_env.py`

---

## 8. 학습 시 로봇이 움직이지 않는 원인 분석 (2026-02-06)

`scripts/train_unsensored_rough.sh` 스크립트 (태스크: `Isaac-Velocity-Rough-NoSensor-Spot-Micro-v0`) 실행 시 로봇이 제자리에서 거의 움직이지 않는 문제에 대한 종합 분석입니다.

### 8.1 rough_env_cfg_no_sensor.py

**파일:** `data/train_myrobot/config/spot_micro/rough_env_cfg_no_sensor.py`

| 항목 | 원인 | 심각도 |
|------|------|--------|
| 센서 제거 | `height_scan = None`, `contact_forces = None`으로 설정되어 로봇이 환경 인식 불가. "blind policy" 학습 난이도 매우 높음 | ⚠️ 중간 |

> [!IMPORTANT]
> NoSensor 환경은 학습 난이도가 매우 높습니다. 센서 있는 환경(`Isaac-Velocity-Rough-Spot-Micro-v0`)에서 먼저 학습 후 전이학습을 권장합니다.

### 8.2 rough_env_cfg.py (핵심)

**파일:** `data/train_myrobot/config/spot_micro/rough_env_cfg.py`

| 항목 | 현재 설정 | 권장 설정 | 원인 |
|------|----------|----------|------|
| **lin_vel_x** | `(-0.2, 0.4)` | `(-0.4, 0.4)` | 속도 범위가 너무 좁아 정적 정책 유도 |
| **lin_vel_y** | `(-0.1, 0.1)` | `(-0.2, 0.2)` | 측면 이동 범위 부족 |
| **ang_vel_z** | `(-0.3, 0.3)` | `(-0.6, 0.6)` | 회전 속도 범위 부족 |
| **action scale** | `0.25` | `0.5~1.0` | 너무 작아 관절 움직임이 미미함 |
| **push_robot** | `None` | 활성화 권장 | 외력 이벤트 비활성화로 다양한 상황 학습 불가 |
| **track_lin_vel_xy_exp.weight** | `3.0` | `5.0~7.0` | 속도 추종 보상 가중치가 낮음 |
| **feet_air_time.weight** | `0.01` | `0.5~5.0` | ⚡ **핵심**: 발 공중 시간 보상이 너무 낮아 걷기 동작 학습 X |
| **undesired_contacts** | `None` | 활성화 권장 | 원치 않는 접촉 페널티 없음 |

> [!CAUTION]
> `feet_air_time.weight = 0.01`은 **매우 낮은 값**입니다. 참조 환경(ohchungmin_ssafy)은 `5.0`을 사용합니다.

### 8.3 spotmicro_quad.py (로봇 모델)

**파일:** `data/train_myrobot/config/spot_micro/spotmicro_quad.py`

| 항목 | 현재 설정 | 권장 설정 | 원인 |
|------|----------|----------|------|
| **stiffness** | `40.0` | `20.0~30.0` | P게인이 너무 높아 관절이 뻣뻣함 |
| **damping** | `5.0` | `0.5~2.0` | D게인이 너무 높아 움직임 억제 |
| **effort_limit** | `2.2 N·m` | `3.0~5.0 N·m` | 토크 한계가 낮아 강한 움직임 불가 |
| **velocity_limit** | `7.0 rad/s` | `8.0~10.0 rad/s` | 속도 제한이 낮음 |
| **linear_damping** | `0.5` | `0.0~0.1` | 강체 선형 감쇠가 너무 높음 |
| **angular_damping** | `0.5` | `0.0~0.1` | 강체 각속도 감쇠가 너무 높음 |

> [!WARNING]
> **stiffness=40, damping=5** 조합은 로봇 관절을 매우 뻣뻣하게 만들어 정책이 관절을 움직이기 어렵게 합니다.

### 8.4 rsl_rl_ppo_cfg.py (PPO 설정)

**파일:** `data/train_myrobot/config/spot_micro/agents/rsl_rl_ppo_cfg.py`

| 항목 | 현재 설정 | 권장 설정 | 원인 |
|------|----------|----------|------|
| **init_noise_std** | `1.0` | `0.5~1.0` | 초기 노이즈가 높으면 학습 불안정 |
| **entropy_coef** | `0.0025` | `0.005~0.01` | 엔트로피 계수가 낮아 탐색 부족 |
| **learning_rate** | `1.0e-3` | `1.0e-4` | 학습률이 높아 불안정할 수 있음 |

### 8.5 robot.usd (USD 모델)

**파일:** `data/train_myrobot/config/spot_micro/robot.usd`

| 항목 | 현재 상태 | 원인 |
|------|----------|------|
| **toe 링크 존재** | `*_toe_link` 존재 | `feet_air_time`에서 `.*_foot_link`만 추적하므로 실제 접지점과 불일치 |
| **관절 구조** | shoulder → leg → foot → toe | 제어 관절과 접촉 센서 바디명 불일치 가능 |

### 8.6 spotmicroai_gen_ros.urdf

**파일:** `data/train_myrobot/config/spot_micro/spotmicroai_gen_ros.urdf`

| 항목 | 값 | 원인 |
|------|------|------|
| **shoulder 관절 제한** | `[-0.548, 0.548]` rad (±31°) | 관절 가동 범위가 제한적 |
| **관절 damping** | 모두 0.05 | Python 설정(5.0)이 덮어써서 100배 차이 |

### 8.7 참조 환경과의 비교 (ohchungmin_ssafy)

**파일:** `references/ohchungmin_ssafy/rough_env_cfg.py`

| 설정 항목 | 현재 환경 | 참조 환경 | 영향 |
|-----------|----------|----------|------|
| `track_lin_vel_xy_exp.weight` | 3.0 | **7.0** | 속도 추종 동기 부족 |
| `track_ang_vel_z_exp.weight` | 0.75 | **2.5** | 회전 동기 부족 |
| `feet_air_time.weight` | 0.01 | **5.0** | ⚡ **핵심 차이**: 걷기 동작 학습 X |
| `lin_vel_z_l2` | 없음 | **-0.5** | 수직 속도 페널티 없음 |
| `ang_vel_xy_l2` | 없음 | **-0.05** | 롤/피치 각속도 페널티 없음 |
| `base_height_l2` | 없음 | **-5.0** | 높이 유지 보상 없음 |
| `joint_deviation_l1` | 없음 | **-0.25** | 기본 자세 유지 보상 없음 |
| `undesired_contacts` | None | **-5.0** | 원치 않는 접촉 페널티 없음 |

### 8.8 권장 수정 사항

**1순위 (필수)**
1. `rough_env_cfg.py`: `feet_air_time.weight` → `0.01` → `5.0`
2. `spotmicro_quad.py`: `stiffness` → `40.0` → `25.0`, `damping` → `5.0` → `1.0`
3. `rough_env_cfg.py`: `action_scale` → `0.25` → `0.5`

**2순위 (권장)**
4. `rough_env_cfg.py`: `track_lin_vel_xy_exp.weight` → `3.0` → `5.0`
5. `rough_env_cfg.py`: 안정성 보상 추가 (`base_height_l2`, `lin_vel_z_l2` 등)
6. `rough_env_cfg.py`: 속도 범위 확대

**3순위 (테스트 필요)**
7. 센서 있는 환경(`Isaac-Velocity-Rough-Spot-Micro-v0`)으로 먼저 학습
8. `feet_air_time`의 body_names를 `.*_toe_link`로 변경 (실제 접지점)
