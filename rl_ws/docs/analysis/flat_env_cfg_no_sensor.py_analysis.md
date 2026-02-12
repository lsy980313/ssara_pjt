# 분석: `flat_env_cfg_no_sensor.py` (`Isaac-Velocity-Flat-NoSensor-Quad-v0`)

## 1. 개요
*   **Task ID**: `Isaac-Velocity-Flat-NoSensor-Quad-v0`
*   **Config File**: `data/train_myrobot/config/spot_micro/flat_env_cfg_no_sensor.py`
*   **Class**: `SpotMicroFlatNoSensorEnvCfg`
*   **Parent Classes**: `SpotMicroFlatEnvCfg` -> `LocomotionVelocityRoughEnvCfg`

## 2. 환경 특징 (Environment Features)

### 2.1 Sensorless (Blind)
이 환경의 가장 큰 특징은 **외부 감지 센서가 모두 제거된 상태**라는 점입니다.
*   **Contact Sensor (`contact_forces`)**: `None`으로 설정되어 있습니다. 따라서 로봇은 발바닥이 지면에 닿았는지 직접적인 센서 데이터로 확인할 수 없습니다.
*   **Height Scanner (`height_scanner`)**: `None`으로 설정되어 있습니다. 로봇 전방의 지형 높낮이 정보를 전혀 받을 수 없는 **Blind Locomotion** 설정입니다.

### 2.2 Terrain (지형)
*   **Type**: `plane` (평지)
*   **Terrain Generator**: `None` (복잡한 지형 생성기 사용 안 함)

### 2.3 Robot Configuration
*   **초기 상태**: 높이 0.27m에서 시작.
*   **관절 설정**: `IdealPDActuatorCfg` 사용 (P: 40.0, D: 5.0).
*   **Dynamics**: 자가 충돌(Self-collision) 비활성화.

## 3. 보상 함수 (Reward Function) 변경 사항
센서가 제거됨에 따라, 센서 데이터(주로 Contact Force)에 의존하는 보상 항목들이 명시적으로 제거되었습니다.

### 3.1 제거된 보상 (`flat_env_cfg_no_sensor.py`에서 `None` 처리)
*   **`feet_air_time`**: 발이 공중에 떠 있는 시간을 늘리기 위한 보상. (Contact Sensor 필요)
*   **`undesired_contacts`**: 허벅지(Thigh)나 몸통(Base)이 지면에 닿았을 때 부여하는 페널티. (Contact Sensor 필요)
*   **`feet_contact_forces`**: 발바닥에 과도한 힘이 가해지는 것을 방지하는 페널티.

### 3.2 유지되는 보상 (부모 클래스 `SpotMicroFlatEnvCfg`로부터 계승)
로봇의 움직임 자체와 자세 유지에 관련된 보상은 그대로 유지됩니다.
*   **속도 추종**: `track_lin_vel_xy_exp` (xy 평면 속도), `track_ang_vel_z_exp` (z축 회전 속도)
*   **자세 유지**: `base_height_l2` (목표 높이 0.18m 유지), `flat_orientation_l2` (평평한 자세 유지)
*   **에너지/부드러움**: `dof_torques_l2` (토크 최소화), `dof_acc_l2` (가속도 최소화), `action_rate_l2` (급격한 동작 변화 최소화)

## 4. 종료 조건 (Termination Conditions)
*   **`base_contact` 제거**: 몸통이 바닥에 닿았을 때 에피소드를 종료시키는 조건이 제거되었습니다. 이는 Contact Sensor가 없기 때문입니다.
    *   *주의: 로봇이 넘어져도 이 조건으로는 종료되지 않으므로, 학습 시 이상 동작이 길어질 수 있는 가능성이 있습니다.*

## 5. 결론
이 환경은 로봇이 **시각 정보나 접촉 정보 없이**, 오직 **고유수용감각(Proprioception: 관절 위치, 관절 속도, 기저부 속도 등)**에만 의존하여 평지 보행을 학습해야 하는 환경입니다.

접촉 피드백(발이 땅에 닿았는지 여부)과 지형 정보가 없는 상태에서 안정적인 보행 패턴(Gait)을 생성해낼 수 있는지 검증하는 용도로 적합합니다.

## 6. 로그 저장 및 모니터링 분석 (Log & Monitoring)

### 6.1 실험 설정 (Experiment Config)
*   **실험 이름 (Experiment Name)**: `custom_quad_flat`
    *   설정 파일: `data/train_myrobot/config/spot_micro/agents/rsl_rl_ppo_cfg.py`
    *   `CustomQuadFlatPPORunnerCfg` 클래스에서 정의됨.
*   **저장 주기**: 50 iteration마다 체크포인트 저장.
*   **최대 Iteration**: 40,000.

### 6.2 로그 저장 위치 (Log Path)
*   **컨테이너 내부 경로**: `~/IsaacLab/logs/rsl_rl/custom_quad_flat/<YYYY-MM-DD_HH-MM-SS>`
*   **로그 형식**: 
    *   **Tensorboard**: 학습 곡선 및 지표 (`events.out.tfevents.*`)
    *   **Checkpoints**: 모델 가중치 파일 (`model_*.pt`)

### 6.3 주의사항: 로그 영속성 (Persistence Issue)
현재 `scripts/run_container.sh` 설정을 분석한 결과, **Isaac Lab의 로그 디렉토리(`~/IsaacLab/logs`)가 호스트(Host)와 공유(Mount)되어 있지 않습니다.**
*   **문제점**: 컨테이너를 종료하거나 삭제하면 학습 결과(로그 및 모델)가 **모두 사라집니다.**
*   **해결 방안**: `scripts/run_container.sh` 수정 필요.
    ```bash
    # 예시: 호스트의 logs 폴더를 컨테이너 로그 폴더에 마운트
    -v $(pwd)/logs:/isaac-sim/IsaacLab/logs:rw
    ```

### 6.4 모니터링 방법
*   **WandB**: 현재 설정상 비활성화 상태입니다.
*   **Tensorboard**: 컨테이너 내부에서 실행되므로, 호스트에서 보려면 추가 포트 포워딩이나 로그 마운트가 필요합니다.
