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
    --task=Isaac-Velocity-Flat-NoSensor-Quad-v0 \
    --num_envs=4096 \
    --headless
```

*   **`--task`**: 실행할 Task ID (예: `Isaac-Velocity-Flat-NoSensor-Quad-v0`). `gym.register`로 등록된 ID여야 합니다.
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
    --task=Isaac-Velocity-Flat-NoSensor-Quad-v0 \
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
    --task=Isaac-Velocity-Flat-NoSensor-Quad-v0 \
    --num_envs=4096 \
    --resume

# 특정 날짜의 기록 로드 (logs/rsl_rl/[experiment_name]/[date_folder])
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task=Isaac-Velocity-Flat-NoSensor-Quad-v0 \
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

# Tensorboard 실행
tensorboard --logdir /isaac-sim/IsaacLab/logs/rsl_rl --port 6006 --bind_all
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

학습된 모델을 로드하여 시각화하는 방법은 두 가지가 있습니다.

**방법 1: 실행 이름으로 로드 (`--load_run`)**
특정 날짜/시간의 학습 기록 폴더명을 지정합니다.

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task=Isaac-Velocity-Flat-NoSensor-Quad-Play-v0 \
    --num_envs=50 \
    --load_run 2024-01-31_12-00-00
```

*   **`--load_run`**: 생략 시 가장 최신(last) 모델을 불러옵니다.

**방법 2: 모델 파일 직접 지정 (`--checkpoint`)**
>ps. 마운트 된 원본 폴더의 경로는 `/isaac-sim/IsaacLab/logs/rsl_rl/`이다.

특정 `.pt` 파일의 경로를 직접 지정합니다. 절대 경로 또는 컨테이너 내부 경로를 사용하세요.

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task=Isaac-Velocity-Flat-NoSensor-Quad-Play-v0 \
    --num_envs=50 \
    --checkpoint /isaac-sim/IsaacLab/logs/rsl_rl/quad_locomotion/2024-01-31_12-00-00/model_2000.pt
```

*   **`--task`**: 시각화용 Task (예: `...-Play-v0`) 사용 권장.
*   **`--num_envs`**: 시각화할 로봇 수 (GUI 부하 고려 50~100 권장).

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
    --task=Isaac-Velocity-Flat-NoSensor-Quad-v0 \
    --load_run ...
```
*   변환된 `.onnx` 파일은 inference 속도가 빠르고 의존성이 적어 배포에 유리합니다.
