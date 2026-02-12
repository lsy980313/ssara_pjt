# Sim2Real 컨트롤러 가이드라인

`controlled_by_model.py`를 사용하여 학습된 모델로 SpotMicro 로봇을 구동하는 방법입니다.

---

## 파일 구조

| 파일 | 역할 |
|------|------|
| `controlled_by_model.py` | 메인 컨트롤러 (모델 추론 + 하드웨어 제어) |
| `hardware_config.py` | 핀맵, I2C 주소, IMU 좌표계 설정 |
| `servo_control.py` | 개별 서보 수동 제어 (디버깅용) |
| `imu_control.py` | IMU ROS2 노드 (참고용) |

---

## 사용 방법

### 1. 모델 준비
학습된 JIT 모델 파일(`.pt`)을 준비합니다:
```python
# 학습 코드에서 export
torch.jit.save(actor_critic.actor, 'policy.pt')
```

### 2. 실행
```bash
cd /home/actuating/workspaces/spotmicro/scripts/sim2real

# 기본 실행
python3 controlled_by_model.py --model policy.pt

# 다른 모델 파일 사용
python3 controlled_by_model.py --model /path/to/your_model.pt
```

### 3. DRY-RUN 모드
하드웨어 라이브러리가 없으면 자동으로 시뮬레이션 모드로 동작합니다:
- 서보 명령은 무시됨
- IMU는 더미 데이터 반환 (정지 상태)

---

## 하드웨어 설정

### I2C 연결
| 장치 | 버스 | 주소 |
|------|------|------|
| PCA9685 (Front) | 7 | 0x40 |
| PCA9685 (Rear) | 7 | 0x41 |
| MPU6050 (IMU) | 1 | 0x68 |

### 관절 매핑
모델 출력 순서와 하드웨어 핀 매핑:

| Index | 관절 | hardware_config 키 |
|-------|------|-------------------|
| 0 | FL_Shoulder | `front-left`, index 2 |
| 1 | FL_Leg | `front-left`, index 1 |
| 2 | FL_Foot | `front-left`, index 0 |
| 3-5 | FR_* | `front-right` |
| 6-8 | RL_* | `rear-left` |
| 9-11 | RR_* | `rear-right` |

---

## 주의사항

> ⚠️ **안전 경고**
> - 반드시 로봇을 공중에 들어올린 상태에서 처음 테스트하세요!
> - `Ctrl+C`로 언제든 종료할 수 있습니다.

---

## 문제 해결

### 하드웨어 초기화 실패
```
❌ Hardware initialization failed
```
- I2C 연결 확인: `i2cdetect -y 7` (서보), `i2cdetect -y 1` (IMU)
- 전원 공급 확인

### 모델 로드 실패
```
❌ Error loading model
```
- JIT export 여부 확인
- PyTorch 버전 호환성 확인
