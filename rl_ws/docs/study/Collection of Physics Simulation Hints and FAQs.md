> omni physics 109.0 문서를 보고 공부한 내용이다

## [Articulation and Robot Simulation Stability Guide](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/guides/articulation_stability_guide.html#id1)
usd view
usdview는 픽사 애니메이션 스튜디오에서 개발한 경량 애플리케이션으로, USD 스테이지를 보고, 탐색하고, 분석하는 데 사용됩니다. usdview의 분석 기능은 사용자가 프리미티브 구성과 속성 값의 변환 과정을 이해하는 데 도움을 줍니다. USD 스테이지 디버깅에 필수적인 도구입니다.

simulation time step

가속 드라이브
stiffness = naturalFrequency * naturalFrequency
damping = 2 * dampingRatio * sqrt(stiffness)
이 공식으로 강성과 감쇠를 계산할 수 있다

강성을 무작정 높이면 이론적인(동역학) 움직임에 가까워지지만, 매우 큰 힘을 발생시켜서 불안정성을 초래할 수 있다.
1. 중력 보정, 가속도 보정, 코리올리스 보정과 같은 피드포워드 제어 노력을 추가하여 적절한 강성 값으로 추적 성능을 향상시키십시오. Tensor API 문서의 역동역학 도우미를 참조하십시오(예: ) [`get_gravity_compensation_forces`](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/extensions/runtime/source/omni.physics.tensors/docs/api/python.html#omni.physics.tensors.impl.api.ArticulationView.get_gravity_compensation_forces "omni.physics.tensors.impl.api.ArticulationView.get_gravity_compensation_forces").
    
2. 관절의 현재 상태에서 크게 벗어난 위치 및 속도 구동 목표값을 설정하면 큰 힘이 발생할 수 있습니다. 적절한 구동력 제한을 설정하거나 구동 목표값에 속도 제한기와 같은 기능을 구현하는 것을 고려해 보십시오.

질량비 (Mass Ratios)와 불안정성
"An impulse applied to a large mass can produce very large velocities when propagated to a body with small mass." (큰 질량에 가해진 충격량이 작은 질량으로 전달될 때, 매우 큰 속도를 유발할 수 있다.)

이 문장은 물리 엔진(PhysX)의 **솔버(Solver)**가 작동하는 방식 때문에 발생하는 문제입니다.

상황 예시:
몸통(Base): 10kg
발끝(Foot): 0.01kg (10g)
질량비: 10 : 0.01 = 1000 : 1
문제 현상: 로봇이 걷다가 발(0.01kg)이 땅에 닿거나 관절이 움직일 때, 몸통(10kg)에서 발생한 힘이 관절을 통해 발로 전달됩니다. 물리 공식 $F = ma$ (힘 = 질량 $\times$ 가속도)에 의해, 같은 힘이라도 질량이 매우 작은 물체는 **어마어마한 가속도(속도 변화)**를 겪게 됩니다.
결과: 시뮬레이션의 한 스텝(Time Step) 동안 발의 속도가 비현실적으로 빨라지면서, 다음 스텝에서 발이 엉뚱한 위치로 튀어 나가게 됩니다. 이로 인해 로봇 전체가 진동하거나 폭발하는 현상이 발생합니다.
권장 사항:

서로 연결된 링크(Link) 간의 질량비는 가능한 한 10:1 이내, 최대 100:1을 넘지 않도록 하는 것이 좋습니다.
만약 발(Foot)이 너무 가볍다면, 물리적으로 정확하지 않더라도 시뮬레이션 안정성을 위해 질량을 인위적으로 조금 늘려주는 튜닝이 필요할 수 있습니다.

Time step 관련 설정들
강화학습 시뮬레이션에서 **Time Step** 관련 설정들은 **"물리 세계의 시간"**과 **"로봇 뇌(정책)의 시간"**을 동기화하는 핵심 개념입니다.

이 값들이 왜 이렇게 설정되어 있는지, 그리고 실제 로봇 학습에서 어떤 의미를 가지는지 자세히 설명해 드리겠습니다.

---

### **1. 🌍 `sim.dt`: 물리 엔진의 최소 단위 (0.005초 = 200Hz)**

- **의미:** 시뮬레이터(Isaac Sim/PhysX)가 세상을 "새로고침" 하는 간격입니다.
- **작동:** 0.005초마다 중력, 마찰력, 충돌, 관절의 움직임을 계산합니다.
- **왜 200Hz인가?**
    - 너무 느리면(예: 0.05초): 로봇 발이 땅을 뚫고 지나가거나(Tunneling effect), 충돌 계산이 불안정해져 로봇이 폭발하듯 튕겨 나갈 수 있습니다.
    - 너무 빠르면(예: 0.0001초): 계산량이 너무 많아져 학습 속도가 매우 느려집니다.
    - **200Hz~400Hz**는 로봇의 "접촉(Contact)"을 안정적으로 시뮬레이션하기 위한 타협점입니다.

### **2. 🧠 `decimation`: 생각의 주기 (4)**

- **의미:** 물리 엔진이 여러 번 돌아갈 때, 로봇의 뇌(Neural Network)는 몇 번에 한 번씩 개입할지를 정하는 "비율"입니다.
- **Decimation = 4**의 뜻:
    
    > _"물리 엔진이 4번 계산하는 동안(0.005s × 4), 로봇은 **이전 명령을 유지**하며 아무것도 하지 않고 기다린다."_
    
- **왜 필요한가?**
    - **Sim-to-Real Gap 줄이기:** 실제 로봇 하드웨어(Raspberry Pi, Jetson 등)와 통신 라인은 물리 현상만큼 빠르지 않습니다. 센서 데이터를 읽고, 신경망을 태우고, 모터에 명령을 보내는 데 시간이 걸립니다.
    - **학습 효율성:** AI가 너무 짧은 간격(0.005초)마다 판단을 내리면, 행동의 변화가 거의 없어 학습이 비효율적입니다(데이터 간의 상관관계가 너무 높음).

### **3. 🎮 `Contact Policy DT`: 실제 제어 주기 (0.02초 = 50Hz)**

- **공식:** `sim.dt` (0.005) × `decimation` (4) = **0.02초**
- **의미:** AI(정책)가 한 번 행동(Action)을 결정하는 주기입니다.
    - 1초에 **50번** 새로운 명령을 내립니다.
- **SpotMicro에서의 의미:**
    - 일반적인 4족 보행 로봇(Unitree Go1 등)은 보통 **50Hz** 혹은 **100Hz**로 제어합니다.
    - **50Hz (0.02s)**: 로봇이 발을 내딛거나 균형을 잡기에 충분히 빠르면서, 실제 엣지 디바이스(작은 컴퓨터)에서도 부하 없이 돌릴 수 있는 속도입니다.

# [Joint Parameter Tuning Example: Robotiq 2F-85](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/guides/gripper_tuning_example.html)
