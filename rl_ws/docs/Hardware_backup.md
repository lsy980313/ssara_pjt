
# Validity
> 데이터 시트 기반으로, 로봇의 구동에 무리가 없을 지 판단한다.
## 1. Battery
## Connected devices
> 배터리는 아래 장치들에 전력을 공급한다.
- jetson orin nano
- sensors: HC-SR04, MPU-6050, PCA9685
- DS3218MG pro * 12
- Orbbec Astra Pro 3D 카메라

| 구분        | 요구사항                                                                                    |
| --------- | --------------------------------------------------------------------------------------- |
| 전압        | 배터리(예: 2S~3S LiPo)를 DC-DC로 분리해 서보 레일 6V, Jetson/센서/카메라 5V 안정화                           |
| 전류 - 서보   | DS3218MG pro 12개 스톨 가정 2~2.5A/ea -> 피크 약 24~30A @6V. 서보용 벅컨 연속 15A+, 피크 30A+ 권장         |
| 전류 - 시스템  | Jetson Orin Nano + Orbbec Astra Pro + 센서: 약 20~25W -> 5V 기준 4~5A (배터리 측 3S 기준 약 2~2.5A) |
| 전류 - 총 피크 | 서보 30A + 논서보 여유 3A -> 순간 33A 이상 공급 가능한 배터리/배선/BMS 필요                                    |
| 배터리 연속 방전 | 서보 평균 0.5A/ea 가정 시 6A + 시스템 3A ~ 9A -> 여유 포함 15A급 이상 권장                                 |
| 배터리 피크 방전 | 33A 이상 (3S 5600mAh 100C는 여유 충분, 병목은 DC-DC·커넥터·배선)                                       |
| BMS 조건    | 차단 전류가 피크보다 높고, 저전압 컷오프가 2S/3S에 맞는 팩 사용할 것                                              |
| 예상 구동 시간  | 3S 5600mAh(약 62Wh) 기준, 평균 10A@11.1V 소비 시 `t ~ 0.56h`(약 34분). 부하 증가 시 비례 단축              |


## 2. Isaac Sim Simulation Parameters & Hardware Validity Analysis

## 3. Enhance camera mount
기존 카메라 마운트가 나사 1개로 지지되어 회전에 취약한 점을 해결하기 위해, 좌우 지지하는 마운트를 모델링 후 3D프린팅하여 보강.

## 4. TroubleShooting
### 어깨 관절 보강하기
> 어깨 관절에서, 다리 전체가 `서보 모터 혼`에 의해서만 지지되어 불안정한 문제를 해결하기 위한 방법이다.

### 모터드라이버, 스텝다운 모듈 전원 공급선 쇼트 발생
글루건 작업으로 해결

# 참고자료
## datasheets
- Jetson Orin Nano Developer Kit: https://d29g4g2dyqv443.cloudfront.net/sites/default/files/Jetson_Orin_Nano_Developer_Kit_RG_0.pdf
- HC-SR04 초음파 센서: https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf
- MPU-6050 IMU: https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf
- Rocker 스위치 RL2-321: https://www.edcon-components.com/Webside/PDFEA/RL2_3.pdf
- XL4016 DC-DC 컨버터: https://datasheet.lcsc.com/szlcsc/1811021511_XI-LAN-DCSHANGHAI-XI-LIAN-XL4016_C105450.pdf
- LM2596 DC-DC 컨버터: https://www.ti.com/lit/ds/symlink/lm2596.pdf
- PCA9685 PWM 서보 드라이버: https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf
- DS3218MG 서보 모터: https://www.dsservo.com/d_file/DS3218%20datasheet.pdf
- Orbbec Astra Pro 3D 카메라: https://www.mybotshop.de/Datasheet/Orbbec_Astra_Pro_Final.pdf
- 커넥터류, 점퍼케이블, 수축튜브는 충민이 꺼 사용
- 서포트는 SSAFY 제공 키트에 포함

# Electronics
전원 및 신호선 배선은 아래와 같다.
컴퓨터: Jetson orin nano developer kit
- PCA9685: 2개
- MPU6050: 1개