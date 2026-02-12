# MPU-6050 Configuration for Jetson Orin Nano

Jetson Orin Nano와 같은 Linux 기반 시스템에서는 I2C 인터페이스를 통해 MPU-6050의 레지스터를 직접 설정하여 `DLPF_CFG`와 `SMPLRT_DIV` 값을 변경합니다.

## 1. 하드웨어 연결 및 인식 확인
MPU-6050은 Jetson의 GPIO 헤더(I2C pins)에 연결됩니다.
터미널에서 다음 명령어로 연결된 주소를 확인합니다 (보통 `0x68`).

```bash
# i2c-tools 설치 (없을 경우)
sudo apt-get install -y i2c-tools python3-smbus2

# 장치 스캔 (Bus 1번 예시)
sudo i2cdetect -y -r 1
```

## 2. Python 설정 예시 (smbus2 사용)

Python 코드 내에서 직접 레지스터 주소에 값을 써서 필터와 주기를 설정하는 방법입니다.

```python
import smbus2
import time

# --- MPU-6050 레지스터 주소 ---
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A  # DLPF_CFG

# --- 설정 값 ---
# I2C 버스 번호 (Jetson Orin Nano 40-pin header의 3,5번 핀은 보통 Bus 1)
BUS_NUM = 1
DEVICE_ADDR = 0x68

# 초기화 함수
def configure_mpu6050():
    try:
        bus = smbus2.SMBus(BUS_NUM)
        
        # 1. 센서 깨우기 (Wake Up)
        # PWR_MGMT_1 레지스터에 0을 기록하여 Sleep 모드 해제
        bus.write_byte_data(DEVICE_ADDR, PWR_MGMT_1, 0)
        time.sleep(0.1)

        # 2. DLPF (Digital Low Pass Filter) 설정 - 레지스터 0x1A
        # 설정값에 따른 대역폭(Bandwidth) 및 지연(Delay):
        # 0x00: 260Hz (0ms)
        # 0x01: 184Hz (2.0ms)
        # 0x02: 94Hz  (3.0ms)
        # 0x03: 44Hz  (4.9ms)
        # 0x04: 21Hz  (8.5ms)
        # 0x05: 10Hz  (13.8ms)
        # 0x06: 5Hz   (19.0ms)
        
        dlpf_config = 0x01  # 예: 184Hz 대역폭 설정
        bus.write_byte_data(DEVICE_ADDR, CONFIG, dlpf_config)
        print(f"DLPF Configured to: {dlpf_config}")

        # 3. Sample Rate 설정 - 레지스터 0x19
        # 공식: Sample Rate = Gyroscope Output Rate / (1 + SMPLRT_DIV)
        # DLPF가 켜져있으면(0x01 ~ 0x06) Gyro Rate는 1kHz (1000Hz)
        # 목표 Sample Rate가 100Hz라면:
        # 100 = 1000 / (1 + DIV) -> 1 + DIV = 10 -> DIV = 9
        
        sample_rate_div = 9
        bus.write_byte_data(DEVICE_ADDR, SMPLRT_DIV, sample_rate_div)
        print(f"Sample Rate Divider set to: {sample_rate_div} (Approx 100Hz)")

    except Exception as e:
        print(f"Error configuring MPU6050: {e}")

if __name__ == "__main__":
    configure_mpu6050()
```

## 3. 요약
- **DLPF_CFG (0x1A)**: 노이즈 필터링 강도 조절. 1~2 정도가 무난함.
- **SMPLRT_DIV (0x19)**: 데이터 출력 주기 조절. `1000 / (1 + 값)` 공식 사용.

## 4. "최고의 성능"을 위한 설정 가이드 (Q&A)

**Q. 무조건 DLPF_CFG=0, SMPLRT_DIV=1로 설정하면 성능이 제일 좋은가요?**

**A. 아닙니다. (특히 보행 로봇에서는 비추천)**

단순히 "통신 속도"와 "지연 시간 최소화" 관점에서는 빠를 수 있지만, **실제 제어 성능(Control Performance)**은 오히려 떨어질 수 있습니다.

### 이유 1: 진동 노이즈 (Mechanical Noise)
- **DLPF_CFG = 0 (260Hz 대역폭)**: 모터가 돌아갈 때 발생하는 고주파 진동이 그대로 센서값에 들어옵니다.
- 가속도계 데이터가 심하게 흔들려서, 로봇이 서 있는데도 기울어졌다고 착각하거나 자세 제어가 발산할 수 있습니다.
- **추천**: SpotMicro와 같은 보행 로봇은 **DLPF_CFG = 3 (44Hz) ~ 4 (21Hz)** 정도를 사용하여 기구적 진동을 걸러내는 것이 훨씬 안정적입니다. 약간의 지연(4~8ms)이 생기지만, 깨끗한 데이터가 더 중요합니다.

### 이유 2: 통신 부하 (I2C Bus Load)
- **DLPF_CFG = 0**일 때는 내부 Gyro Rate가 **8kHz**가 됩니다.
- 이때 **SMPLRT_DIV = 1**로 설정하면 샘플 레이트는 **4kHz ($8000 / (1+1)$)**가 됩니다.
- Jetson Nano에서 Python(`smbus2`)으로 4kHz 데이터를 끊김 없이 읽는 것은 불가능에 가깝습니다 (OS 스케줄링, I2C 속도 한계).
- 읽지 못한 데이터가 버려지거나(Alias), 통신 병목으로 전체 루프가 느려질 수 있습니다.

### ✅ 추천 설정 (Best Practice)
- **DLPF_CFG**: `0x03` (44Hz) 또는 `0x02` (94Hz)
    - 진동을 적절히 잡으면서도 비교적 빠른 반응 속도.
- **SMPLRT_DIV**: `0x09` (100Hz) ~ `0x04` (200Hz)
    - Python 제어 루프 주기(보통 50~100Hz)보다 2~4배 빠르게 설정하여 앨리어싱 방지.