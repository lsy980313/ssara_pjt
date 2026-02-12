# Isaac Lab & Sim Video Analysis Notes

## 1. Isaac Lab: Custom Environment Training. A Step-by-Step Guide
**원본 링크**: [https://www.youtube.com/watch?v=o9Bym5mOl2k](https://www.youtube.com/watch?v=o9Bym5mOl2k)

### 영상 개요
이 영상은 Isaac Lab에서 커스텀 강화학습 환경을 구축하고 훈련하는 방법을 단계별로 설명하는 튜토리얼입니다. 바퀴 달린 4족 보행 로봇(Wheeled Quadruped Robot)이 뒷다리로 균형을 잡고 서 있는 과제를 예제로 사용합니다.

#### 주요 내용
*   **Isaac Lab 설치**: 필수 패키지 및 시뮬레이터 설치 과정
*   **문제 정의 (Problem Definition)**: 로봇의 목표(서 있기), 관측값(Observation), 행동(Action), 보상(Reward) 설계
*   **로봇 자산 준비**: Xacro 파일을 URDF로 변환하고 Isaac Sim에서 USD 파일로 변환하는 과정
*   **환경 구축 코드**: Python 스크립트를 통한 환경 설정 (센서, 관절 제어, 보상 함수, 종료 조건 등)
*   **강화학습 훈련**: Stable Baselines 3를 이용한 PPO 알고리즘 훈련 실행
*   **추론 (Inference)**: 훈련된 모델을 로드하여 시뮬레이션 실행

### 타임라인 및 상세 요약

#### [0:00] 서론 (Introduction)
*   **목표**: 바퀴 달린 4족 보행 로봇이 뒷다리로 균형을 잡고 서 있도록 훈련시키는 것.
*   Isaac Lab을 사용하면 잘 알려진 머신러닝 알고리즘을 자신의 환경에 빠르게 적용해 볼 수 있음을 강조.

#### [0:29] 설치 (Installation)
*   Isaac Lab 리포지토리 클론 및 설치 과정 안내.
*   `cmake`, `build-essential` 등 의존성 패키지 설치.
*   Isaac Lab 설치 스크립트(`install_deps.sh`) 실행 전 `python`을 `python3`로 수정하는 팁 공유.
*   설치 확인을 위해 빈 Isaac Sim 창을 띄워보는 `create_empty.py` 예제 실행.

#### [2:41] 문제 정의 (Problem Definition)
*   **목표**: 로봇이 직립 상태를 유지하는 것.
*   **관측 (Observations)**: 선속도(Linear Velocity), 각속도(Angular Velocity), 이전 행동(Previous Actions).
*   **행동 (Actions)**: 뒷다리 바퀴 회전, 앞다리를 초기 위치 기준 전후 45도 이동.
*   **보상 (Reward)**: 넘어지지 않고 직립하면 매 스텝 보상 부여. 특정 각도 이상 기울어지거나 넘어지면 페널티. 목표 높이와 무게중심 간의 차이에 비례하여 페널티 부여.

#### [3:37] USD 파일 생성 (Creating USD File)
*   Google Drive에서 제공된 로봇 파일 다운로드 및 압축 해제.
*   **Xacro -> URDF 변환**: `xacro` 명령어를 사용하여 로봇 모델 변환.
*   **URDF -> USD 변환**: Isaac Sim의 'URDF Importer' 워크플로우 사용.
    *   `Merge Fixed Joints` 옵션 체크 (불필요한 관절 제거 및 모델 단순화).
    *   **Joint 속성 수정**: 위치 제어(Position Controlled) 관절은 그대로 두되, 속도 제어(Velocity Controlled) 관절은 Damping=1.0, Stiffness=0.0으로 설정하여 부드러운 회전 유도.

#### [6:01] 환경 구축 코드 분석 (Launching Environment Code)
*   `create_wheeled_quadruped.py` 스크립트 분석.
*   **USD 경로 설정**: 변환한 로봇 모델(USD) 로드.
*   **초기 상태 설정**: 로봇이 바퀴가 바닥에 닿도록 초기 위치 지정.
*   **액추에이터 설정**: 위치 제어 및 속도 제어 관절에 대한 각각의 설정 적용.
*   **Scene 설정**: 지면(Ground Plane), 조명(Light) 등 설정.
*   **관측 및 보상 설정**: 문제 정의에서 설계한 대로 관측값과 보상 함수 구현.
    *   `rewards.py`의 기본 페널티 함수 사용 가능, 커스텀 함수 작성 가능.
*   **종료 조건 (Termination)**: 일정 시간 경과 또는 로봇이 넘어짐(60도 이상 기울어짐) 감지 시 에피소드 종료.

#### [10:02] 훈련 (Training)
*   **프레임워크**: Stable Baselines 3 사용.
*   **환경 등록**: Gymnasium 환경으로 등록하기 위해 `sb3` 디렉토리 내에 환경 설정 파일 구성.
    *   기존 예제 폴더 구조를 복사하여 자신의 로봇 환경에 맞게 수정.
    *   `train.py` 스크립트 실행 시 등록된 task 이름 사용.
*   훈련 실행: `python train.py --task=...`

#### [13:01] 실행 및 테스트 (Running/Play)
*   **Play 스크립트**: `play.py`를 실행하여 훈련된 모델 테스트.
*   `--checkpoint` 옵션 등을 사용하여 최신 훈련 모델 로드 가능.

---

## 2. Design & Train your own Robots | From CAD (Onshape) to URDF to Isaac Sim to Isaac Lab
**원본 링크**: [https://www.youtube.com/watch?v=7bPfUcXKaQk](https://www.youtube.com/watch?v=7bPfUcXKaQk)

### 영상 개요
이 영상은 Onshape(CAD)에서 로봇을 설계하고, URDF로 변환한 후 Isaac Sim을 거쳐 Isaac Lab에서 강화학습을 수행하는 전체 파이프라인을 설명합니다.

#### 주요 내용
*   **Onshape 설계**: 클라우드 기반 CAD 툴인 Onshape를 사용하여 로봇 모델링.
*   **URDF 변환**: `onshape-to-robot` 툴을 사용해 CAD 모델을 URDF로 변환.
*   **Isaac Sim 포팅**: URDF를 Isaac Sim으로 불러와 USD(Universal Scene Description) 포맷으로 변환 및 검증.
*   **Isaac Lab 훈련**: 변환된 모델을 Isaac Lab 환경에 로드하여 강화학습(RL) 훈련 수행.

### 타임라인 및 상세 요약

#### [0:00] 서론 (Introduction)
*   **목표**: CAD 설계부터 강화학습 훈련까지의 전체 프로세스 안내 (Onshape -> URDF -> Isaac Sim -> Isaac Lab).

#### [0:28] Onshape 선택 이유
*   무료, 웹 기반, 리눅스 지원, 강력한 문서화.

#### [1:12] URDF와 OpenUSD
*   **URDF**: 로봇의 물리적 표준 포맷 (링크, 관절).
*   **OpenUSD**: NVIDIA Omniverse의 3D 장면 표준 포맷.

#### [3:23] Onshape 로봇 설계
*   Part Studio에서 부품 설계 및 조인트 연결 지점(Mate Connector) 정의.
*   Assembly에서 관절 조립 및 제한(Limits) 설정.

#### [6:34] URDF 내보내기 (Exporting)
*   `onshape-to-robot` 툴 사용.
*   API 키 연동 후 커맨드로 URDF 및 메쉬 파일 생성.

#### [7:32] Isaac Sim으로 가져오기 (Importing)
*   Isaac Sim의 **URDF Importer** 익스텐션 사용.
*   Import 옵션: `Merge Fixed Joints` (고정 관절 병합), `Fix Base Link` (베이스 고정 여부) 등 설정.
*   결과물을 USD 파일로 저장.

#### [9:02] 물리 검증 (Physics Verification)
*   Isaac Sim 재생 후 로봇이 폭발(발산)하지 않는지 확인.
*   **Gain Tuner**: 관절의 Stiffness/Damping 값을 조절하여 안정적인 동작 확보.

#### [10:52] Isaac Lab 훈련 (Training)
*   Isaac Lab의 템플릿 코드에서 USD 경로를 내 로봇으로 변경.
*   Action/Observation 스페이스에 맞춰 관절 인덱스 등 수정.
*   `python train.py` 실행하여 병렬 강화학습 시작.

---

## 3. How to Train a Custom Quadruped Robot to Walk Using Isaac Lab
**원본 링크**: [https://www.youtube.com/watch?v=z62oU4hM1xM](https://www.youtube.com/watch?v=z62oU4hM1xM)

### 영상 개요
이 영상은 Isaac Lab(NVIDIA Omniverse)을 사용하여 커스텀 4족 보행 로봇(예: SpotMicro)을 훈련시키는 전체 과정을 다룹니다. 로봇의 Xacro/URDF 설정부터 시뮬레이션 환경 구축, 그리고 **RSL RL** 라이브러리를 이용한 GPU 가속 강화학습까지 단계별로 설명합니다.

#### 주요 내용
*   **로봇 구성 (Configuration)**: Isaac Lab의 기본 템플릿을 활용하여 커스텀 로봇 설정 파일 작성.
*   **초기 상태 설정 (Initial State)**: 안정적인 학습 시작을 위한 로봇의 초기 관절 각도 및 높이 설정.
*   **Sim-to-Real 튜닝**: 시뮬레이션 안정성을 위한 강성(Stiffness) 및 감쇠(Damping) 값 조절.
*   **보상 설계 (Rewards)**: 발이 걸리지 않고 몸통 높이를 유지하도록 보상 함수 정의.
*   **RSL RL 훈련**: 고속 병렬 학습을 위한 RSL RL 프레임워크 사용 및 TensorBoard 모니터링.

### 타임라인 및 상세 요약

#### [0:02] 서론 (Introduction)
*   **목표**: 커스텀 4족 보행 로봇이 평지에서 걷도록 훈련.
*   Isaac Lab의 강력한 시뮬레이션 기능 활용.

#### [0:41] 환경 구성 (Configuration)
*   Isaac Lab에서 제공하는 기본 Locomotion 설정을 템플릿으로 사용하여 커스텀 설정을 생성.

#### [1:54] 로봇 셋업 (Robot Setup)
*   로봇의 링크(Trunk, Hip, Thigh, Calf)와 관절을 정의하는 Xacro 파일 구조 설명.
*   커스텀 에셋 폴더 구조 생성.

#### [3:45] Isaac Sim 가져오기 (Importing)
*   생성된 URDF/USD 파일을 Isaac Sim으로 로드.
*   시뮬레이션 환경(지면 등) 설정.

#### [4:11] 초기 상태 설정 (Initial States)
*   학습 시작 시 로봇이 넘어지지 않도록 초기 높이와 관절 각도 지정.
*   예: 허벅지(Thigh) -50도, 종아리(Calf) 100도 등으로 설정하여 안정적인 자세 유도.

#### [5:14] 불안정성 해결 및 튜닝 (Stability Tuning)
*   초기 시뮬레이션 시 로봇이 주저앉는 문제 해결.
*   **Stiffness(강성)**: 60, **Damping(감쇠)**: 1.5 정도로 설정하여 관절이 버틸 수 있게 튜닝.

#### [7:21] 보상 함수 설정 (Reward Weights)
*   로봇이 발을 질질 끌지 않고(Feet clearance), 몸통을 일정 높이로 유지하도록 보상 가중칠 설정.
*   불필요한 동작을 줄이기 위한 페널티 부여.

#### [9:06] RSL RL 프레임워크
*   NVIDIA의 GPU 가속 강화학습 라이브러리인 **RSL RL** 소개.
*   빠른 학습 속도와 효율적인 자원 사용.
*   **Actor & Critic 네트워크**: 행동을 결정하는 Actor와 상태를 평가하는 Critic 네트워크 구조 설명.

#### [11:11] 훈련 실행 (Training Process)
*   훈련 스크립트 실행 및 로그 확인.
*   **TensorBoard**를 사용하여 보상(Reward) 그래프와 학습 진행 상황 모니터링.

#### [12:32] 결과 확인 (Results & Playback)
*   `play.py`를 실행하여 훈련된 정책(Policy)으로 로봇이 걷는 모습 확인.

---

## 4. Import ANY Robot (URDF): From CAD to Isaac Sim
**원본 링크**: [https://www.youtube.com/watch?v=KCHmYvYF_6c](https://www.youtube.com/watch?v=KCHmYvYF_6c)

### 영상 개요
이 영상은 복잡한 CAD 모델(Onshape)을 Isaac Sim에서 시뮬레이션 가능한 URDF 포맷으로 변환하는 효율적인 워크플로우를 소개합니다. **Onshape-Robotics-Toolkit**을 활용하여 관절(Joint) 설정과 URDF 생성을 자동화하는 방법을 다룹니다.

#### 주요 내용
*   **Onshape 활용**: 웹 기반 CAD인 Onshape에서 로봇 모델(Step 파일 등)을 불러오고 관절을 정의.
*   **Onshape-Robotics-Toolkit**: Python 기반 툴킷을 사용하여 메시 추출 및 URDF 생성 자동화.
*   **Isaac Sim Import**: 생성된 URDF를 시뮬레이터로 가져와 물리 속성(Stiffness, Damping) 튜닝.

### 타임라인 및 상세 요약

#### [1:23] 서론 (Intro)
*   **배경**: 로봇 시뮬레이션을 위해서는 CAD 모델을 URDF(Unified Robot Description Format)로 변환해야 함.
*   **문제점**: 수동 변환은 어렵고 오류가 발생하기 쉬움.
*   **해결책**: Onshape와 전용 툴킷을 이용한 "Pain-free" 워크플로우 소개.

#### [1:58] CAD 모델 가져오기 (Import .step File)
*   로봇 제조사나 소스에서 제공하는 `.step` 파일을 Onshape에 업로드.
*   업로드된 모델의 파트(Links)와 계층 구조 확인.

#### [3:00] 관절 정의 (Define Joints)
*   **Mate vs Relation**: 단순한 조립(Mate)을 넘어 물리적 움직임을 정의하는 관계(Relation) 설정.u
*   **Revolute Joint**: 회전 관절 설정, 회전축(Axis) 및 가동 범위(Limits) 지정.
*   **Fixed Base**: 로봇의 베이스 링크를 고정(Fixed)하여 시뮬레이션 시 움직이지 않도록 설정.

#### [5:41] URDF 생성 (Generate URDF)
*   **도구**: Onshape-Robotics-Toolkit (영상에서 언급된 툴).
*   **설정**: API Key 설정 및 Python 환경 구성.
*   **실행**: 스크립트를 실행하면 자동으로 각 링크의 메시(.stl/.obj)를 다운로드하고 `robot.urdf` 파일을 생성함.
*   이 과정에서 질량(Mass) 및 관성(Inertia) 정보도 함께 처리됨.

#### [9:40] Isaac Sim으로 가져오기 (Isaac Sim Import)
*   **Import**: Isaac Sim의 URDF Importer를 사용하여 생성된 `.urdf` 파일 로드.
*   **Physics Tuning**:
    *   **Stiffness (강성)**: 0.0 (위치 제어가 아닌 경우) 또는 적절한 값.
    *   **Damping (댐핑)**: 진동을 줄이기 위해 적절한 값으로 튜닝.
*   **Test**: 시뮬레이션 재생(Play) 후 관절을 움직여보며 정상 동작 확인.

---

## 5. Import Your Robots From URDF to USD - Isaac Sim Tutorial
**원본 링크**: [https://www.youtube.com/watch?v=AMfEtZ4hyLY](https://www.youtube.com/watch?v=AMfEtZ4hyLY)

### 영상 개요
이 영상은 LycheeAI가 제공하는 튜토리얼로, URDF 파일로 된 로봇(예: SO-ARM 100)을 Isaac Sim으로 가져와 USD 포맷으로 변환하는 과정을 상세히 다룹니다. 특히 시뮬레이션과 현실 간의 격차를 줄이기 위한 관절 물리학(Stiffness, Damping) 설정과 Articulation Root 수정 등 실무적인 팁을 강조합니다.

#### 주요 내용
*   **URDF 준비**: 호환성을 위해 관절 이름에 밑줄(underscore) 추가 등 사전 작업.
*   **Isaac Sim Import**: 'Robot as Default Prim', 'Static Base', 'Convex Hull' 등 최적의 Import 설정 안내.
*   **물리 설정 심화**: 가속도 구동(Acceleration Drive) 대신 힘 구동(Force Drive)을 권장하며, 고유 진동수(Natural Frequency)와 감쇠비(Damping Ratio)를 기반으로 Stiffness와 Damping 값을 계산하는 방법 설명.
*   **Sim-to-Real**: 도메인 랜덤화(Domain Randomization)의 중요성 언급.
*   **Articulation Root 수정**: ROS 및 Isaac Lab과의 호환성을 위해 Articulation Root를 올바른 위치(Xform)로 설정하는 방법.

### 타임라인 및 상세 요약

#### [0:00] 서론 (Introduction)
*   URDF에서 Isaac Sim으로 로봇을 가져오는 과정 개요.
*   예제 로봇으로 오픈소스 로봇 팔인 SO-ARM 100 사용.

#### [1:13] URDF 및 USD 이해
*   URDF와 USD 포맷의 차이 설명.
*   GitHub 등에서 다운로드한 URDF 파일의 오류(이름 규칙 등) 수정 필요성.

#### [2:32] Import 설정 (Import Settings)
*   **Import Config**: `Robot as Default Prim` 체크 (로봇을 최상위 prim으로), `Fix Base Link` (로봇 팔 등 고정형인 경우).
*   **Colliders**: `Convex Decomposition` 대신 `Convex Hull` 사용 권장 (자가 충돌 허용 및 효율성).

#### [4:18] 관절 물리학 (Joint Physics)
*   **Stiffness & Damping**: 시뮬레이션의 안정성과 현실성을 결정하는 핵심 변수.
*   **Joint Drive Type**: `Acceleration Drive`(이상적, 비현실적) 대신 `Force Drive`(스프링-댐퍼 시스템, 현실적) 사용 권장.
*   엔비디아 엔지니어들의 설명을 인용하여 물리 엔진 원리 해설.

#### [5:50] 게인 튜닝 (Tuning Gains)
*   **Stiffness(Kp)**와 **Damping(Kd)** 값을 임의로 찍는 것이 아니라, **Natural Frequency(고유 진동수)**와 **Damping Ratio(감쇠비)** 공식을 통해 계산하는 방법 소개.
*   예: Damping Ratio 0.7 (약간의 오버슈트 허용하며 빠른 수렴), Natural Frequency 10Hz 등.

#### [11:22] Articulation Root 및 USD 저장
*   **중요**: Import 직후 Articulation Root가 잘못된 링크에 설정되어 있을 수 있음.
*   ROS나 Isaac Lab에서 제어하기 위해서는 Articulation Root를 로봇의 최상위 Xform으로 이동시켜야 함.
*   설정 완료 후 USD 파일로 저장.

---

# 궁금한 점
- stiffness와 damping이 무엇인지, 어떻게 정의해야 하는지?