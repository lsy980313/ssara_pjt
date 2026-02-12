# setup USD file
## Edit components name
> 예제 코드에서 사용되는 정책에 맞게 각 부품의 이름을 변경해줘야 한다.
- shoulder -> hip
- leg -> thigh
- foot -> calf
- toe -> foot
- front_left -> FL
- front_right -> RL
- rear_left -> RL
- rear_right -> RR

## Troubleshooting

**질문**
@[data/usd/leg_finished.usd] 이 환경에서 시뮬레이션이 시작되면 로봇이 앞으로 넘어져 버려. 원인만 파악해 줘
**답변**
USD 파일 분석 결과, 크게 세 가지 치명적인 원인이 발견되었습니다:
1. **조인트 연결 끊김 (Critical)**: 모든 관절(Joint)의 `physics:body0`, `physics:body1` 관계가 비어 있습니다(None). 이로 인해 링크들이 서로 연결되지 않아 로봇 형상을 유지하지 못하고 무너집니다.
2. **Articulation Root 누락**: 로봇의 루트나 상위 프림에 `Articulation Root API`가 적용되지 않았습니다. Isaac Sim이 이를 로봇(관절체)으로 인식하지 못하고 개별 강체로 처리합니다.
3. **질량 중심(CoM) 데이터 오류**: 대부분의 링크에서 Center of Mass(CoM) 값이 `(-inf, -inf, -inf)`로 비정상적입니다. 이는 물리 엔진 계산 오류를 유발하여 로봇이 튕겨 나가거나 비정상적으로 쓰러지는 원인이 됩니다.

## configure settings
`/isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/custom_quadruped` 경로에 시뮬레이션에 필요한 설정 파일들이 저장되어 있다.

## run example scripts
**질문**
isaac-sim@actuatin:~/IsaacLab/scripts/reinforcement_learning/rsl_rl$ train.py
이 파일도 @[scripts]로 옮겨 줘. 추가로 옮기기 이전 경로에서 실행하는 방법만 알려줘
**답변**
 파일을 로컬  폴더로 복사 완료했습니다.

**옮기기 이전 경로(컨테이너 원본)에서 실행하는 방법:**
컨테이너의  루트에서 다음 명령어로 실행합니다.

```bash
# 컨테이너 내부 (IsaacLab 폴더에서)
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task <TASK_NAME> --num_envs <NUM>
```
- 예시: 기본 예제 실행하기
`./isaaclab.sh -p c --task Isaac-Velocity-Flat-Unitree-A1-v0 --num_envs 128 `

- 예시: **우리 모델링 반영 예제 실행하기**
`./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Flat-Custom-Quad-v0 --num_envs=512`

또는 절대 경로를 사용해도 됩니다:
```bash
./isaaclab.sh -p /isaac-sim/IsaacLab/scripts/reinforcement_learning/rsl_rl/train.py ...
```
## custom quadraped 경로
`/isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/custom_quadruped`

## 예제에서 수정사항
  1. USD 모델 파일 수정 (robot.usd)
  fix_usd.py 스크립트를 작성 및 실행하여 모델의 물리 설정을 다음과 같이 교정했습니다.

   * 중첩 Articulation Root 제거: /SpotMicroAI와 /SpotMicroAI/base에 중복으로 설정되어 있던 ArticulationRootAPI 중 하위 노드의 것을 제거하여 Isaac Lab의 단일 루트 제약 조건을
     충족시켰습니다.
   * Base 연결성 수정: 로봇의 루트인 base prim에 RigidBodyAPI와 MassAPI가 누락되어 관절들이 분리된 별개의 로봇으로 인식되는 문제를 해결했습니다.
   * 실제  관절 가동 범위(Joint Limits) 수정: calf_joint의 가동 범위가 약 [-86, 86]도(1.5 rad)로 제한되어 있어, 학습 설정값인 100도(1.745 rad)를 수용하지 못해 발생하는 에러를 해결하기 위해범위를 [-150, 150]도로 확장했습니다.
     * 아래와 같은 방법으로 문제를 해결한다
     * 어떤 코드에 모터에 관한 정보가 있는지 확인
     * 어떤 모터 스펙을 기입해야 되는지 확인
     * 해당되는 곳에 모터 스펙을 기입한다
     * 학습 설정값도 -90 ~ 90도로 수정한다.
   * 충돌 및 접촉 감지 설정: trunk 및 발(FL_foot 등) prim에 CollisionAPI와 PhysxContactReportAPI를 추가하여 접촉 센서(Contact Sensor)가 데이터를 정상적으로 읽을 수 있도록 수정했습니다.
     * 무슨 말인지 확인해 보기. IMU만 쓰는 것이 아닌가?

  1. 학습 환경 설정 파일 수정 (IsaacLab 내부 소스)
  컨테이너 내부의 IsaacLab 소스 코드를 패치하여 센서 관련 런타임 에러를 방지했습니다.

   * `rough_env_cfg.py` 패치: 접촉 센서가 물리 엔진에서 바디를 찾지 못해 발생하는 RuntimeError를 일시적으로 우회하기 위해, 문제가 되는 contact_forces 설정과 이를 사용하는 feet_air_time 보상, base_contact 종료 조건을 None으로 비활성화했습니다.
     * IMU 값과 모터 각도 데이터로만 가능하도록 수정하기
   * `flat_env_cfg.py` 패치: 상위 클래스(RoughEnvCfg)에서 보상이 비활성화됨에 따라, None 객체의 weight 속성에 접근하려다 발생하는 AttributeError를 방지하기 위해 해당 가중치 설정
     코드를 주석 처리했습니다.

  1. 신규 디버깅 도구 생성
   * `inspect_structure.py`: USD 파일의 계층 구조, Rigid Body 상태, Joint 연결 관계 및 적용된 API들을 상세히 출력하여 문제 원인을 파악하는 데 사용했습니다.
   * `patch_cfg.py`, `patch_flat_cfg.py`: 컨테이너 내부의 읽기 전용 권한이 걸린 설정 파일들을 root 권한으로 안전하게 수정하기 위한 패치 스크립트입니다.

  현재 모델의 물리적 구조와 관절 제한 문제는 모두 해결되었으며, 센서 비활성화를 통해 학습 스크립트가 중단 없이 실행될 수 있는 상태입니다. 학습을 다시 시작하려면 다음 명령을
  사용하세요. `cd /isaac-sim/IsaacLab && ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task=Isaac-Velocity-Flat-Custom-Quad-v0
     --num_envs=512`

## rename
> cannot move/rename ancestral... 에러가 발생할 때,
`save as flattend...`로 저장하면 rename 가능해 진다.

## essetial tips
- usd에서는 geometry, physics까지만 설정하는 듯 하다