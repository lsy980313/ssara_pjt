# reference 코드 분석

# 제미니와의 즐거운 피드백 시간
@rough_env_cfg_no_sensor.py로 수행한 학습 play 결과, 아래와 같은 문제점이 파악되었다
1. 대부분의 로봇이 한 다리를 들고 있음
2. 머리 위에 표시되는 방향벡터의 길이가 매우 짧고, 회전하고 있음
3. 자리에 가만히 서서 거의 움직이지 않음.

## 문제 해결 계획 (2026-02-04)

### 목표
1. **Leg Holding (다리 들기)**: `feet_air_time` 보상 부재로 인한 현상 추정. 보상 복원.
2. **Short/Rotating Direction Vector (방향 벡터 문제)**: 관측 혹은 명령의 문제일 수 있음. 확인 필요.
3. **Standing Still (움직임 없음)**: 목표 속도 범위가 너무 낮거나 에너지 페널티가 높음. 명령 범위 확대.

### 변경 사항
#### [rough_env_cfg_no_sensor.py]
1. **보상 복원**:
> observation은 비활성화, reward는 활성화 하면 blind policy를 구현 가능하다.
    - `feet_air_time`: 물리 상태 기반으로 계산하여 보행 리듬 학습 유도.
    - `undesired_contacts`: 넘어짐 방지 및 자세 안정성 확보.
2. **명령 범위 확대 (속도 현실화)**:
    - 선형 속도 X: `(-1.0, 1.0)` -> `(-0.6, 0.6)` m/s (약 2km/h)
    - 선형 속도 Y: `(-0.5, 0.5)` -> `(-0.3, 0.3)` m/s
    - 각속도 Z: `(-1.0, 1.0)` -> `(-0.6, 0.6)` rad/s
    - *이유*: 너무 낮은 목표는 제자리 정지를 유발하며, 약간 높은 목표가 탐색(Exploration)을 돕습니다.

### 메모
- **Blind Policy**: 센서 없이도 시뮬레이터의 privileged information을 이용해 보상을 줄 수 있음.

feet_air_time 보상이 과도하거나, threshold가 너무 길 경우 한 다리를 들고 있으려 할 수 있다.
self.rewards.feet_air_time.weight = 5.0 -> 1.0으로 너프
## robot_mania youtube reference 분석
>`rough_env_cfg.py` 파일과 내 `rough_env_cfg.py`, `rough_env_cfg_no_sensor.py`를 비교/분석한 내용이다.

차이점
1. **Action Scale (동작 배율) 차이**:
    - `robotmania`: `self.actions.joint_pos.scale = 0.25`
    - `myrobot`: `self.actions.joint_pos.scale = 1.0`
    - **분석**:
        - `1.0`: 신경망의 출력이 1:1로 관절 각도에 반영됨. 로봇이 매우 민감하게 반응할 수 있음.
        - `0.25`: 신경망 출력의 25%만 반영됨. 더 세밀하고 안정적인 제어가 가능하며, 학습 초기 진동을 줄여줌.
        - **결론**: 초기에 `1.0`은 너무 과격할 수 있으므로, 학습이 불안정하다면 `0.25`로 낮추는 것을 고려해야 함.

2. **Reset Conditions (초기화 조건)**:
    - `robotmania` 설정:
      ```python
      self.events.reset_base.params = {
          "pose_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5), "yaw": (-3.14, 3.14)},
          "velocity_range": {
              "x": (0.0, 0.0), "y": (0.0, 0.0), "z": (0.0, 0.0),
              "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0),
          },
      }
      ```
    - **분석**:
        - **Pose Range**: 제자리 반경 0.5m 내에서 무작위 위치, 방향은 360도 전방위 무작위로 시작. 이는 다양한 초기 자세에 대한 적응력을 키워줌.
        - **Velocity Range**: 모든 속도를 `0.0`으로 설정하여 **완전 정지 상태**에서 시작.
        - **의미**: 로봇을 공중에 던지거나 움직이는 상태로 시작하지 않고, 바닥에 얌전히 놓인 상태에서 출발하도록 하여 학습 초기 난이도를 조절함.

언젠가는 종료조건에서 다리는 제거해야 할 것 같다. 아니면 학습 초기에는 넣다가, 학습이 진행되면 코드에서 빼버리기?!