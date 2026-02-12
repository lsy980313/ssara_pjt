![physics inspector](docs/imgs/physics_inspector.png)
- 모터 관절의 회전 범위는 잘 설정되어 있음을 확인 가능하다.
- 어깨 관절 -31.398 ~ 31.398은 안정성 때문에 이렇게 했나? 

모터 강성 설정에 대해서는 조금 더 조사해봐야 할 것 같다.

astra는 무게 속성을 제거하고 visual로 부착하였다. 추후에 body에 무게를 추가하는 작업을 진행해야 한다.
카메라는 형상만 부착, 센서 값 받아오는 건 추후에 여유가 되면 할 예정
measure tool

## Stiffness and Damping
>이론값 설정, 게인 튜너를 활용한 미세 조정 과정

>[!info] 주요 참조 링크
>1. [이론값 설정 - omniphysics Articulations](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/rigid_bodies_articulations/articulations.html)
>2. [Tuning Joint Drive Gains](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/robot_setup_tutorials/joint_tuning.html)
### 이론값 설정

### 알아야 할 값들
> `docs/drivePerformanceEnvelope.pdf` 참고해서, 모터 데이터시트를 기반으로 값 계산해 보자
- `max_effort`: 회전 관절의 경우 `최대 토크`
- `velocityDependentResistance`이는 속도에 비례하는 저항을 나타냅니다.
- `speedEffortGradient`작동력에 따라 액추에이터의 속도 성능이 어떻게 감소하는지를 나타냅니다.
- `maxActuatorVelocity`이는 구동 관절에서 달성할 수 있는 최대 속도입니다.

회전 관절에 대해서는 아래와 같이 계산한다
- **각형 관절:**
    - `maxForce`: 토크 Nm
        
    - `velocityDependentResistance`: 토크 × 초 / 도
        
    - `speedEffortGradient`: 도/초/토크
        
    - `maxActuatorVelocity`: 도/초

### 관절 마찰


## 마찰계수, 반발력
> toe_link 4개, groundplane에 material 하나 씩 넣어두었다. 실제 사용하는 재료가 결정되면 `정적 마찰계수`. `동적 마찰계수`입력하기.

현재는 임의로 아래와 같이 설정해 두었다.
### 1. Rubber (고무, 로봇 바퀴 등)

일반적으로 고무는 마찰력이 매우 높게 설정됩니다.

- **Static Friction (정지 마찰):** `0.9` ~ `1.1`
- **Dynamic Friction (운동 마찰):** `0.7` ~ `0.9`
    - _팁: 로봇 바퀴의 경우 미끄러짐을 방지하기 위해 1.0 이상으로 높게 잡기도 합니다._

### 2. Carpet (카펫)

카펫은 고무보다는 마찰이 낮지만, 일반 바닥보다는 약간의 저항이 있습니다.

- **Static Friction (정지 마찰):** `0.5` ~ `0.7`
- **Dynamic Friction (운동 마찰):** `0.4` ~ `0.6`


마찰계수 생성하는 법
메뉴 모음으로 이동하여 생성 > 물리 > 물리 재질을 클릭합니다 .
팝업 상자에서 '강체 재질'을 선택하세요 . PhysicsMaterial스테이지 트리에 새 항목이 나타납니다.
속성 탭에서 마찰 계수 및 반발력과 같은 매개변수를 조정하십시오.

조인트 보는 법
좌상단 눈깔아이콘 클릭하고 조인트 활성화

센서 부착 위치는 `링크의 원점`이다.

카메라 삽입 시  usd로 변환 후 prim에 끌어 놓으면 이동 잘 된다.

# Assets configuration
마운트 복사해서 맞춰 놓고,
Asset 디렉토리
`~/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config` 여기에 `custom_quadruped` 폴더 구조 참조해서 사용할 로봇에 맞춘 폴더 추가하기
실행 명령어
> 학습을 시작하지.
```bash
cd ~/IsaacLab
./isaaclab.sh ~/IsaacLab/scripts/reinforcement_learning/rsl_rl/train.py
```

https://www.youtube.com/watch?v=z62oU4hM1xM&list=PL0-Gs4T6GAt1LoTibdw-0e3Vaeq9g7-oD&index=2
11:13 학습 방법 시작~!
12:11 부터 이어서 정리 
