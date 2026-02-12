# 사용하고 싶은 기술 스택

> 글머리 번호 최상위 항목은 `사용하고 싶은 기술 스택의 이름`이고, 차상위 항목은 `실제 사용처`입니다. `태그` 양식은 `역할 분담 시 큰 카테고리`정도로 생각하면 될 것 같습니다. 태그가 없는 영역은 로봇 영역입니다.
>
> > `AD(Autonomous driving)` = 자율주행

1. NVIDIA Issac ROS, Issac Sim, Issac lab
   - `AD` Issac Sim을 통한 실제 시연 전 시뮬레이션
   - `AD` Isaac Sim + Issac lab을 통한 로봇 강화학습(RL) 데이터 확보
   - VLA, Physical AI
1. 객체인식 -> Action
2. VSLAM
   - `AD + AI` depth 카메라만 사용(Lidar 센서를 사용하지 않고), 장애물을 회피하며 목표물을 찾아가는 자율주행 구현
4. 하드웨어 모델링 및 제작(3D프린팅, 선반가공, 레이저가공 등)
   - `HW` 기본적인 뼈대는 SpotMicro(Opensource project에서 가져옴)
5. `Web`동일 네트워크 상이 아닌 외부 네트워크를 통한 로봇 IOT 제어
   - 담당자 기획 추가
   - 모니터링
6. 마이크를 활용한 음성인식 AI로 명령 전달
7. `HW` PCB 설계 및 최종본 인쇄
# 더 조사해 봐야 할 기술
1. Physical AI
2. VLA
3. CES 보고 아이디어 찾아보기
4. walk
5. object detection
6. vslam
   1. real world

앞부분은 제 생각에 포트폴리오에 작성 시 유용할 만한 기술 스택들을 정리한 내용이고, 뒷부분은 이 기술 스택들을 활용한 프로젝트 예시입니다.

# [BOM](https://docs.google.com/spreadsheets/d/18mxItY0H7ypNeKVTIqvK2lVw06e1zQXP21BfDEnFfvg/edit?gid=450530006#gid=450530006)

# References
[SpotMicro Lecture Notion](https://puzzling-cashew-c4c.notion.site/SpotMicro-for-G-Camp-c541934a4bad4ad48d1e37ab94c10de8)
[SpotMicroJetson BOM](https://docs.google.com/spreadsheets/d/1UIJ1a0tUQx4ky75Ovr97hnKy3tkcdXQCYJl6zFl0juA/edit?gid=450530006#gid=450530006)
[SpotMicroAI Docs](https://spotmicroai.readthedocs.io/en/latest/)
[spotMicro reddit](https://www.reddit.com/r/Spotmicro/)
[Mike's spotMicro github](https://github.com/mike4192/spotMicro)
[Florian Wilk's spotMicro gitlab](https://gitlab.com/public-open-source/spotmicroai)
[spotMicroJetson(Notion에 사용됨) github](https://github.com/Road-Balance/SpotMicroJetson)
[SpotMicro-IsaacLab](https://github.com/tonhathuy/SpotMicro-IsaacLab)

# 개발 환경 정의

## Simulation Enviroment Spec

✅ 데스크탑(Ubuntu 22.04 / RTX 5080 / 9800X3D)
✅ Laptop(Ubuntu 22.04 / RTX 4050 Laptop / Intel® Core™ Ultra 7 Processor 155H)

## sim2real Environment Spec

✅ Jetson Orin Nano(Jetpack 6.2.1)

> [!note] 최종 결정 버전
> Isaac Sim: 5.1.x (가능하면 5.1.0 이상)
>
> Isaac Lab: v2.3.x (또는 main 브랜치)
>
> Isaac ROS: 3.2.x
>
> ROS 2: Humble (Ubuntu 22.04 표준)

이 조합을 추천하는 이유

RTX 50 시리즈 이슈(렌더/OptiX 계열) 회피

RTX 50 시리즈에서 Isaac Sim 4.5 계열로 렌더링 품질/노이즈/블러 같은 문제가 보고되었고, NVIDIA 쪽에서 Isaac Sim 5.0에서 해결되었다는 언급이 있습니다.

Isaac Sim 5.1 요구사항 페이지에서도 권장 GPU 예시로 RTX 5080을 직접 제시하고, 리눅스 권장 드라이버 버전도 명시되어 있습니다.

# 임시 메모

Isaac 초기 + 학습 과정 전체적으로 보여주기 - 개발 과정을 스크린 샷, 스크린 레코드로 꾸준히 기록 해두기
jira 30 + git 30 + pjt 40, agile??, git flow vs github flow vs gitlab flow??

# Inspection of Isaac sim
## 1. About Isaac Sim & Lab

### Issac mobility (Isaac 모빌리티)

**Real-Time 3D Occupancy Grid (실시간 3D 점유 그리드)**
Enable robots to identify obstacles in 3D spaces up to five meters away and generate a 2D costmap using the NVIDIA nvblox CUDA-accelerated 3D reconstruction library. Get results 100x faster than with CPU-centric methods.

NVIDIA nvblox CUDA 가속 3D 재구성 라이브러리를 사용하여, 로봇이 최대 5미터 거리의 3D 공간에서 장애물을 식별하고 2D 비용 맵(costmap)을 생성합니다. CPU 중심 방식보다 **100배 빠른** 결과를 얻을 수 있습니다.

### Accelerated Stereo Visual Odometry and SLAM (가속화된 스테레오 시각 주행 거리 측정 및 SLAM)

Get sub-1% trajectory errors for real-time, CUDA-accelerated visual SLAM across diverse sensors and platforms using NVIDIA cuVSLAM. Seamlessly navigate environments with sparse visual features or repetitive patterns by fusing input from multiple viewpoints. Get started with pycuVSLAM.

NVIDIA cuVSLAM을 사용하여 다양한 센서와 플랫폼에서 실시간 CUDA 가속 비주얼 SLAM으로 **1% 미만의 궤적 오차**를 달성합니다. 여러 시점의 입력을 융합하여 시각적 특징이 부족하거나 반복적인 패턴이 있는 환경에서도 원활하게 탐색할 수 있습니다. pycuVSLAM으로 시작해 보세요.

- Generalizable End-to-End Mobility (범용 엔드투엔드 모빌리티)

Train vision-based mobility foundation models using NVIDIA COMPASS, enabling navigation across robot types and changing environments. The workflow includes synthetic data generation with NVIDIA Isaac Sim™ and Cosmos™ Transfer, model training and post-training in Isaac Lab, and deployment with **NVIDIA Jetson Orin™ or Thor™**.

NVIDIA COMPASS를 사용하여 비전 기반 모빌리티 파운데이션 모델을 훈련하고, 다양한 로봇 유형과 변화하는 환경에서 탐색을 가능하게 합니다. 워크플로우에는 NVIDIA Isaac Sim™ 및 Cosmos™ Transfer를 사용한 합성 데이터 생성, Isaac Lab에서의 모델 훈련 및 후처리 훈련, 그리고 **NVIDIA Jetson Orin™ 또는 Thor™**를 통한 배포가 포함됩니다.

## Reddit reactions (Reddit 반응)

- Yes I've tried sota valam (cuvslam) developed by Nvidia. If your task is vision based or cuda specific, I would definitely recommend you to try it out.
  - 네, 엔비디아가 개발한 최신 VSLAM(cuVSLAM)을 사용해 봤습니다. 비전 기반 작업이나 CUDA 관련 작업이라면 꼭 사용해 보시길 추천합니다.
- I did used it for my project and it made it very easy for me to setup a hardware accelerated image processing nodes and deploying neural networks, without me having to write a lot of this functionality myself. Therefore, it saved me a lot of time as well.
  - 제 프로젝트에 사용했는데, 하드웨어 가속 이미지 처리 노드를 설정하고 신경망을 배포하는 것이 매우 쉬웠습니다. 이런 기능을 직접 작성하지 않아도 되어서 시간을 많이 절약할 수 있었습니다.

# Questions

## isaac을 사용해야 할 이유?

- RL 관점에서의 강점
- 샘플 효율: 로봇 RL은 실제 로봇에서 데이터를 수집하기 어렵기 때문에 시뮬레이션에서 대량의 경험을 생성해야 함. Isaac Lab의 병렬 시뮬레이션이 이 지점을 해결.
- 안정적인 물리: 정책 학습은 물리엔진의 안정성에 크게 좌우됨. Isaac Sim의 고품질 물리 엔진이 장점.
- Sim-to-Real:
  - 도메인 랜덤화: 실제 환경 변동을 시뮬레이션에 반영해 정책이 일반화되도록 함.
  - 센서 노이즈 모델링: 카메라, LiDAR 등의 노이즈를 실제와 유사하게 설정.
  - 마찰/관성 변동: 물리 파라미터를 랜덤하게 바꿔 실환경 적응력 향상.
- 보상 설계: 로봇 RL의 가장 어려운 부분 중 하나. 목표 도달, 에너지 효율, 충돌 회피 등의 항을 적절히 균형 맞춰야 함.
- 탐색 안정성: 로봇 관절 제한, 충돌, 불안정한 자세를 회피하는 안전한 정책 설계가 필요.

아이작을 직접 사용해 본 사람으로서 말씀드리자면, 아이작은 개인이 운영하기보다는 기업에서 사용하는 데 더 적합합니다. 정말 부유하고 고성능 워크스테이션을 가지고 있거나 NVIDIA 클라우드를 이용할 계획이 아니라면 말이죠. NVIDIA 클라우드를 이용하는 것이 가장 좋은 방법일지도 모르겠습니다. 왜냐하면 아이작을 제대로 설정하는 과정이 매우 복잡하고, 앞으로 사용할 기업 수도 많지 않을 것이기 때문입니다. 아이작은 가제보와 거의 비슷한 기능을 제공하지만, 로봇 체육관 기능만 봐도 가제보보다 훨씬 더 많은 기능을 갖추고 있다는 것을 알 수 있습니다. 제 생각에는 아이작에 익숙해지는 것이 현명합니다. 아이작은 아직 초기 단계이고, NVIDIA의 향후 계획을 보면 5년, 10년 안에 업계 표준이 될 가능성이 충분히 있습니다. NVIDIA는 자사의 기능을 통합한 "ROS 3"를 출시할 예정이며, 이를 통해 로봇을 작동시키는 신경망 학습이 훨씬 더 쉽고 실용적인 용도로 활용될 수 있도록 만들 것입니다. 제 생각에는, 제가 다음에 할 말에 대해 반론을 제기할 수도 있겠지만, Isaac의 물리 엔진이 전기 시뮬레이션을 포함하여 힘과 토크로부터 MMC와 같은 것을 실제 전기적 응답으로 변환하는 방식을 보면, 제 생각에는 이것이 판도를 바꿀 만한 혁신이라고 생각합니다. (누구나 Gazebo에서 비슷한 기능을 구현할 수 있다면 자유롭게 의견을 제시할 수 있을 것입니다. 추가 코드를 실행하거나, ROS 프로젝트 내에서 로봇의 기계-전기 시스템 시뮬레이션 부분을 포함하는 런처를 만들 수도 있겠지만, Gazebo에서 이것이 가능한지는 잘 모르겠습니다. 제 주장에 반하는 의견을 제시하는 것일 뿐, 그런 기능이 있는지조차 확신할 수 없습니다.) 엔비디아는 여러분이 Isaac Sim과 그 패키지만 사용하도록 유도하려는 것 같습니다. 자사 독점 소프트웨어로 미개척 시장을 공략하려는 거죠. 로봇 개발 환경을 위한 독점 소프트웨어가 사실상 없다는 점에 주목하세요. 오토데스크에서 만든 로봇 공학용 소프트웨어가 있긴 한데, 이름은 기억나지 않지만 ANSYS for Robotics 같은 겁니다. 엔비디아는 공개적으로 소유하지 않는 로봇 공학 환경 전체를 만들려고 하는 것 같습니다. ROS는 오픈 소스 소프트웨어일 뿐만 아니라 업계에서도 널리 사용되지 않습니다. 그래서 엔비디아는 ROS를 팀에서 사용할 수 있는 시스템으로 만들어 클라우드를 임대하는 기업들이 활용할 수 있도록 하려는 것 같습니다. 다시 한번 강조하지만, 제 주장은 모두 추측일 뿐이니 참고만 하세요. 저도 설치해 봤는데, 리눅스에서 엔비디아 제품을 사용하는 건 언제나처럼 끔찍했고, 훨씬 더 고통스러웠습니다. 엔비디아는 엄청난 처리 능력을 요구하는데, 늘 그렇듯이 다루기가 너무 어렵습니다. 혹시 실제로 사용해 보신 분이 있다면 경험을 공유해 주시면 좋겠습니다. 수정: 제가 깜빡 잊고 언급하지 않았는데, 젯슨은 아이작이 만든 프로젝트와 호환성이 매우 높아 로봇 공학 분야의 하드웨어 및 소프트웨어 플랫폼 모두를 장악할 가능성이 높습니다.

## Jetson 또는 Nano나 유사한 SBC에서 실행될 수 있는 실외 UAV 애플리케이션용 시각 관성 주행 거리 측정 패키지에 대한 추천 사항?

- Isaac ROS 튜토리얼에서 지원하는 카메라 중 하나를 가지고 있다면, 해당 튜토리얼이 3년 전에 만들어졌고 상당히 탄탄한 디버깅 문서가 제공되므로 문제 해결에 어려움이 없을 거라고 생각합니다.

# issac + ros2 environment settings

- 저는 공식 ROS2 Jazzy 데스크톱 Docker 이미지를 사용하고 빌드 시 컨테이너 내에서 Isaac을 빌드하는 방식으로 잘 작동하도록 설정했습니다. I have it working well starting with the official ROS2 jazzy deskddtop Docker image and building Isaac in the container during build time. Make sure you use the Nvidia docker container runtime when starting the container.
- Fusion 360을 사용하여 모델을 만들고 Ubuntu 시스템으로 내보낼 수 있습니다. Ubuntu는 ROS, Gazebo 및 Isaac Sim을 사용하는 데에도 적합합니다. You can use fusion 360 and export your models to your ubuntu machine. You can use ubuntu for ros, gazebo and isaac sim.