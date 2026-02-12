# Isaac Lab & RSL RL 학습 터미널 출력 변수 분석 보고서

이 문서는 사용자가 `./isaaclab.sh -p ... train.py` 명령어를 통해 강화학습(Reinforcement Learning)을 수행할 때, 터미널에 실시간으로 출력되는 변수들의 의미를 상세히 설명합니다.

분석 대상 명령:
`./isaaclab.sh -p ~/IsaacLab/scripts/reinforcement_learning/rsl_rl/train.py --task=Isaac-Velocity-Flat-Custom-Quad-v0 --num_envs=6000`

## 1. 개요
RSL RL(Robotic Systems Lab RL) 라이브러리는 PPO(Proximal Policy Optimization) 알고리즘을 기반으로 하며, 학습 진행 상황을 터미널에 표 형태로 주기적으로 출력합니다. 이 출력은 학습 속도, 에이전트의 성능, 정책 신경망의 상태를 모니터링하는 데 필수적입니다.

## 2. 주요 출력 변수 설명

터미널 출력은 크게 **Performance(성능/속도)**, **Train(학습 결과)**, **Policy(정책 네트워크 상태)** 카테고리로 나뉩니다.

### A. Performance (학습 속도 관련)
시스템의 데이터 수집 및 학습 효율성을 나타냅니다.

| 변수명 | 의미 | 해석 가이드 |
| :--- | :--- | :--- |
| **`Perf/total_fps`** | 초당 처리 프레임 수 (전체) | 데이터 수집 + 학습 업데이트를 포함한 전체 처리 속도입니다. 이 값이 높을수록 학습이 빠르게 진행됩니다. |
| **`Perf/collection_fps`** | 초당 수집 프레임 수 | 시뮬레이션 환경에서 데이터를 수집하는 속도입니다. |
| **`Perf/learning_fps`** | 초당 학습 프레임 수 | GPU에서 신경망을 업데이트하는 속도입니다. |
| **`Time/iter`** | 반복(Iteration) 당 소요 시간 | 한 번의 정책 업데이트(수천 스텝의 데이터 수집 포함)에 걸리는 시간입니다. |

### B. Train / Environment (에이전트 성능 관련)
로봇이 환경에서 얼마나 잘 작동하고 있는지를 보여주는 가장 중요한 지표입니다.

| 변수명 | 의미 | 해석 가이드 |
| :--- | :--- | :--- |
| **`Train/mean_reward`** | **평균 보상 (Mean Reward)** | **가장 중요한 지표**입니다. 에이전트가 한 에피소드 동안 받은 총 보상의 평균입니다. 학습이 잘 진행되면 이 그래프는 **우상향**해야 합니다. |
| **`Train/mean_episode_length`** | 평균 에피소드 길이 | 에이전트가 넘어지지 않고 버틴 평균 시간(스텝 수)입니다. 초반에는 넘어지기 쉬워 짧지만, 학습이 될수록 **최대값(설정된 max_episode_length)에 수렴**해야 합니다. |

### C. Policy (PPO 알고리즘 내부 상태)
PPO 알고리즘의 안정성과 탐험(Exploration) 수준을 나타냅니다.

| 변수명 | 의미 | 해석 가이드 |
| :--- | :--- | :--- |
| **`Policy/mean_noise_std`** | 행동 노이즈 표준편차 | 에이전트의 탐험(Exploration) 정도입니다. 초기에는 높았다가, 최적의 행동을 찾으면서 점차 **감소**해야 합니다. 너무 빨리 0에 가까워지면 지역 최적해(Local Optima)에 빠진 것일 수 있습니다. |
| **`Policy/entropy`** | 엔트로피 (불확실성) | 에이전트 행동의 무작위성입니다. 학습이 진행됨에 따라 점차 **감소**합니다. |
| **`Policy/kl`** | KL 발산 (Divergence) | 이전 정책과 업데이트된 정책 간의 차이입니다. 이 값이 너무 크면 학습이 불안정하다는 뜻이며, 너무 작으면 학습이 너무 느리다는 뜻입니다. |
| **`Policy/clip_fraction`** | 클리핑 비율 (Clip Fraction) | PPO에서 정책 업데이트가 너무 크게 일어나는 것을 방지하기 위해 사용된 데이터의 비율입니다. 일반적으로 0.2 이하가 이상적입니다. |
| **`Loss/value_function`** | 가치 함수 손실 (Value Loss) | 현재 상태의 가치를 예측하는 Critic 네트워크의 오차입니다. 일반적으로 **감소**하는 경향을 보여야 합니다. |
| **`Loss/surrogate`** | 정책 손실 (Surrogate Loss) | Actor 네트워크의 손실값입니다. PPO에서는 이 값이 음수이거나 변동이 클 수 있으므로, 경향성을 파악하기 어렵습니다. (보상 증가가 더 중요) |

---

## 3. 세부 보상 구성 (Reward Composition)
`Train/mean_reward`는 `flat_env_cfg.py`에 정의된 여러 개별 보상 항목들의 총합입니다. 터미널에는 합계만 나오지만, 내부적으로는 아래 항목들이 더해져서 점수가 결정됩니다. 학습이 잘 안된다면 아래 가중치(weight)를 조정해야 할 수 있습니다.

**현재 `flat_env_cfg.py`에 설정된 주요 보상 항목:**

1.  **목표 추적 보상 (Tracking)**
    *   `track_lin_vel_xy_exp`: 목표한 x, y 속도를 잘 따라가면 +점수 (가중치: 5.0)
    *   `track_ang_vel_z_exp`: 목표한 회전 속도를 잘 따라가면 +점수 (가중치: 2.5)
    
2.  **안정성 및 자세 제어 (Stability & Regulation)**
    *   `lin_vel_z_l2`: 통통 튀지 않도록 z축 속도 억제 (-페널티)
    *   `ang_vel_xy_l2`: 기울어짐(roll/pitch) 방지 (-페널티)
    *   `flat_orientation_l2`: 몸체가 평평하게 유지되도록 유도 (-페널티)
    *   `base_height_l2`: 로봇 높이를 0.18m로 유지 (-페널티, 가중치 -2.0)

3.  **동작 품질 (Quality of Motion)**
    *   `feet_air_time`: 발이 공중에 떠 있는 시간을 길게 하여 걷는 동작 유도 (+점수, 가중치 2.0)
    *   `undesired_contacts`: 발 이외의 부위(허벅지, 어깨 등)가 땅에 닿으면 큰 감점 (-5.0) -> 넘어지는 것을 방지하는 핵심 항목
    *   `dof_torques_l2`, `dof_acc_l2`: 부드러운 움직임과 에너지 효율을 위해 힘과 가속도 억제

## 4. 요약
*   **지속적으로 확인해야 할 것**: `Train/mean_reward` (상승해야 함), `Train/mean_episode_length` (최대로 유지되어야 함).
*   **초반**: `mean_episode_length`가 늘어나는지 확인하세요 (안 넘어지고 걷기 시작).
*   **중반**: `mean_reward`가 꾸준히 오르는지 확인하세요 (목표 속도 추적).
*   **후반**: `Policy/mean_noise_std`가 줄어들며 동작이 정교해지는지 확인하세요.
