# Isaac Sim Actuator Parameter Calculation Breakdown

이 문서는 DS3218MG 서보 모터의 사양을 기반으로 Isaac Sim 시뮬레이션에 필요한 강성(Stiffness) 및 댐핑(Damping) 관련 파라미터를 계산하는 과정을 상세히 기술합니다. 또한, PCA9685 모터 드라이버의 전류 제한이 성능에 미치는 영향도 분석합니다.

## 1. DS3218MG Servo Specifications

제조사 데이터시트 및 일반적인 사양(6.8V 기준)을 6V 구동 환경으로 보간(Interpolation)하여 사용합니다.

| Voltage | Stall Torque (kg·cm) | Speed (sec/60°) |
| :--- | :--- | :--- |
| 5.0V | 19.0 | 0.16 |
| 6.8V | 21.5 | 0.14 |

**6V 기준 추정값 (Linear Interpolation):**
*   **Stall Torque**: $19 + \frac{(21.5 - 19)}{(6.8 - 5.0)} \times (6.0 - 5.0) \approx \mathbf{22.11 \text{ kg}\cdot\text{cm}}$
*   **Speed**: $0.16 - \frac{(0.16 - 0.14)}{(6.8 - 5.0)} \times (6.0 - 5.0) \approx \mathbf{0.1489 \text{ sec/60}^\circ}$
    *   *(Note: 6.8V Speed가 Datasheet마다 0.14s로 표기되기도 하고 Pro 버전은 더 빠르기도 함. 여기서는 보수적으로 일반형 기준 0.1089s (Pro @ 6V) 또는 위 계산값 사용 가능. 앞선 문서에서는 DS3218 Pro Datasheet (0.12s @ 5V, 0.10s @ 6.8V)를 기반으로 하여 약 0.11s @ 6V를 사용했음)*
    *   **Pro Version (Re-evaluated):** 5V(0.12s), 6.8V(0.10s) -> **6V $\approx$ 0.1089s**

## 2. Unit Conversions for Isaac Sim

Isaac Sim은 SI 단위계(Meters, Kilograms, Seconds, Radians/Degrees)를 따르므로 변환이 필요합니다.

### 2.1 Torque (`maxForce`)
*   Value: $22.11 \text{ kg}\cdot\text{cm}$
*   Conversion: $1 \text{ kg}\cdot\text{cm} \approx 0.0980665 \text{ N}\cdot\text{m}$
*   Calculation: $22.11 \times 0.0980665 \approx \mathbf{2.168 \text{ N}\cdot\text{m}}$
*   **Result**: `maxForce` = **2.17 Nm**

### 2.2 Velocity (`maxActuatorVelocity`)
*   Value: $0.1089 \text{ sec } / \ 60^\circ$
*   Angular Velocity (deg/s): $\frac{60^\circ}{0.1089 \text{ s}} \approx \mathbf{550.96 \text{ deg/s}}$
*   **Result**: `maxActuatorVelocity` = **551 deg/s**

## 3. Derivative Parameters

Isaac Sim의 Actuator 모델(DC Motor approximation)에서 사용되는 파생 파라미터입니다.

### 3.1 `speedEffortGradient` (Inverse Damping Slope)
토크가 0일 때 최대 속도, 속도가 0일 때 최대 토크(Stall)라고 가정하고, 그 기울기를 구합니다.
*   Formula: $\frac{\text{Max Velocity}}{\text{Max Force}}$
*   Calculation: $\frac{551 \text{ deg/s}}{2.17 \text{ N}\cdot\text{m}} \approx \mathbf{253.9 \text{ (deg/s) / (N}\cdot\text{m)}}$
*   **Result**: `speedEffortGradient` = **254**

### 3.2 `velocityDependentResistance` (Damping Coefficient)
`speedEffortGradient`의 역수 개념으로, 속도에 따른 저항(댐핑)을 나타냅니다.
*   Formula: $\frac{\text{Max Force}}{\text{Max Velocity}}$
*   Calculation: $\frac{2.17 \text{ N}\cdot\text{m}}{551 \text{ deg/s}} \approx \mathbf{0.003938 \text{ (N}\cdot\text{m) / (deg/s)}}$
*   **Result**: `velocityDependentResistance` = **0.00394**

---

## 4. PCA9685 Breakout Board Constraints Analysis

### 4.1 Current Limitations
*   **Requirements**: 12개의 서보가 Stall 상태일 때 최대 전류 소모.
    *   Per Servo Stall Current: ~2.5A (Typical High Torque Servo)
    *   Total Peak Current: $12 \times 2.5\text{A} = \mathbf{30\text{A}}$
*   **Board Capability**: Adafruit 및 일반적인 PCA9685 브레이크아웃 보드.
    *   Trace Width Limit: V+ 및 GND 트레이스는 보통 3A continuous, 순간 최대 **10A** 정도가 한계.
    *   Terminal Block Rating: 보통 10A~15A 급 단자대 사용.

### 4.2 Impact Calculation (Bottleneck Scenario)
보드를 통해 전원을 공급할 경우, 전류 제한(30A 필요 vs 10A 공급)으로 인해 전압 강하(Voltage Drop)가 발생하고 서보가 낼 수 있는 토크가 비례하여 감소합니다.

*   **Current Availability**: $\frac{10\text{A (Limit)}}{30\text{A (Req)}} = \frac{1}{3} \approx 33\%$
*   **Effective Torque**: $2.17 \text{ N}\cdot\text{m} \times 0.33 \approx \mathbf{0.72 \text{ N}\cdot\text{m}}$
*   **Result**: 배선 잘못 시 최대 토크는 0.72 Nm로 제한되며, 이는 로봇이 일어서지 못하거나 매우 불안정한 원인이 됨.

## 5. Summary Table

| Parameter | Unit | Ideal (External Power) | Board Limited (PCA9685) | Note |
| :--- | :--- | :--- | :--- | :--- |
| **maxForce** | Nm | **2.17** | **0.72** | **Critical Difference** |
| **maxActuatorVelocity** | deg/s | **551** | 551 | No load speed unchanged |
| **speedEffortGradient** | deg/s/Nm | **254** | 765 | Steeper slope (weaker motor) |
| **velocityDependentResistance** | Nm·s/deg | **0.00394** | 0.0013 | Less damping force |

> **Conclusion**: 시뮬레이션에는 **Ideal** 값을, 실제 제작 시에는 반드시 **외부 전원 분배(Bus-bar/PDB)**를 적용해야 함.
