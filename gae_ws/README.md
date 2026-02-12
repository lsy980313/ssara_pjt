# 🐕 GAE 4족 보행 로봇 통합 개발 환경 가이드 (v2.6)

> Docker 기반의 All-in-One 개발 환경입니다.
로컬에 복잡하게 라이브러리 설치할 필요 없이, 스크립트 하나로 개발을 시작하세요.
> 

---

## 🚀 빠른 시작 (Quick Start)

팀원들은 본인에게 할당된 폴더에서 아래 절차를 따라주세요. (이미 환경은 관리자가 구성해 두었습니다.)

## 💻 개발자별 할당 정보

| 이름 | 컨테이너 이름 | 호스트 작업 경로 | ROS_DOMAIN_ID |
| --- | --- | --- | --- |
| **정지용** | `jjy092801` | `~/S14P11C101/gae_ws` | 101 |
| **김태연** | `taeyeon` | `~/workspaces/taeyeon/S14P11C101/gae_ws` | 101 |
| **이수영** | `sooyoung` | `~/workspaces/sooyoung/S14P11C101/gae_ws` | 101 |
| **김경한** | `kyunghan` | `~/workspaces/kyunghan/S14P11C101/gae_ws` | 101 |
| **오충민** | `chungmin` | `~/workspaces/chungmin/S14P11C101/gae_ws` | 101 |

### 1. 컨테이너 접속

- 본인의 이름으로 된 폴더로 이동하여 접속 스크립트를 실행합니다.
- 이 스크립트를 통해 본인만의 독립된 도커 환경(GPU, 카메라 권한 포함)으로 입장합니다.
- 본 프로젝트는 Jetson Orin Nano의 자원을 효율적으로 사용하고, 개발자 간의 **Git 충돌 및 ROS2 토픽 간섭을 방지**하기 위해 **1인 1컨테이너/1인 1저장소** 체제로 운영됩니다.

```bash
# 1. 본인 작업 폴더로 이동 (예: taeyeon, sooyoung 등)
cd ~/workspaces/[본인이름]

# 2. 컨테이너 접속 스크립트 실행
# chmod +x connect.sh << 권한 거부시 실행
./connect.sh
```

### 2. 워크스페이스 빌드 (Container 내부)

- 도커 터미널(`root@ubuntu:/root/gae_ws#`)이 열리면 아래 명령어를 입력합니다.
- **주의:** Jetson 메모리 보호를 위해 빌드는 **한 명씩 차례대로** 진행해 주세요.

```bash
# 1. 워크스페이스 이동
cd ~/gae_ws

# 2. 전체 패키지 빌드
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

# 만약 빌드 에러(충돌) 발생 시 기존 내역 삭제 후 재빌드
# rm -rf build install log
# colcon build --symlink-install

# 3. 환경 변수 적용 (새 터미널을 열 때마다 실행하거나 .bashrc에 등록)
source install/setup.bash
```

## 🛠️ 관리자용 가이드 (Jetson 재부팅 시)

만약 Jetson이 재부팅되었거나 컨테이너가 멈춘 경우, 관리자(`ssafy`)가 아래 명령어를 한 번 실행해줘야 합니다.

```bash
# Jetson 터미널
cd ~/workspaces

# xhost +local:root

# docker commit (container_id) jjy092801/gae-system:vn.n
# docker push jjy092801/gae-system:vn.n

docker compose start
# docker compose start (특정 인원 ID)

# VSCode 접속 후
cd ~/S14P11C101/gae_ws

./connect.sh
```

- **도커 이미지 업데이트 시 가이드**

```python
# 1. 워크스페이스 이동
cd ~/workspaces

# 2. X11 시각화 권한 부여 (재부팅 시 필수)
# xhost +local:root

# 3. 기존 컨테이너 중지 및 제거 (소스 코드는 안전합니다)
docker compose down

# 4. 새 이미지 기반 컨테이너 생성 및 자동 실행
# (이 명령어 한 번으로 생성 + 실행(Start)이 동시에 완료됩니다)
docker compose up -d

# 5. 실행 상태 최종 확인
docker ps
```

- **Ros2 Humble 코드 개발 후 빌드 진행 가이드**

```python
# 1. 워크스페이스로 이동
cd ~/gae_ws

# 2. 코드 수정 후 빌드 (특정 패키지만 빌드하는 습관을 들이면 좋습니다)
colcon build --symlink-install --packages-select gae_control  <-- 예: gae_control 수정 시

# 3. 환경 설정 적용
source install/setup.bash

# 4. 실행
ros2 launch gae_control control.launch.py
```

- **도커 이미지 업데이트 (관리자용)**

```python
# 컨테이너 → 새 버전 이미지로 commit
docker commit 115834c5ce60 jjy092801/gae-system:v2.6

# Docker Hub 로그인 (이미 돼 있으면 스킵)
# docker login

# 새 버전 이미지 push
docker push jjy092801/gae-system:v2.6

# docker-compose.yml 수정
services:
  gae-system:
    image: jjy092801/gae-system:vn.n
    
# 기존 컨테이너 내리기
docker compose down

# 새 이미지 pull
docker compose pull

# 재배포
docker compose up -d
```

### 3. Git 협업 규칙

- **개인 설정**: 컨테이너 접속 후 **딱 한 번만** 실행하세요. 이후에는 컨테이너를 껐다 켜도 유지됩니다.

```bash
git config --local user.name "Your Name"
git config --local user.email "your_email@example.com"
```

- **브랜치 관리**: `main` 브랜치에 직접 Push하지 말고, 반드시 본인 브랜치에서 작업 후 PR(Pull Request)을 생성하세요.
- **최신화**: 작업 시작 전 항상 `git pull`을 받아 팀원들의 변경 사항을 반영하세요.

---

### 💡 팁: 실행이 안 된다면?

만약 `./connect.sh` 실행 시 컨테이너가 꺼져 있다는 메시지가 나오면, 관리자(@jjy092801)에게 **"컨테이너 올려달라"**고 요청하세요!

### 🛠️ 빌드(colcon build)는 언제 다시 하나요?

1. **최초 1회**: 컨테이너를 처음 만들고 접속했을 때 (필수)
2. **새로운 패키지 추가**: `git pull`을 받았는데 새로운 ROS2 패키지가 생겼을 때
3. **C++/Msg 수정**: 소스 코드(`.cpp`, `.hpp`)나 커스텀 메시지 파일을 수정했을 때
4. **빌드 에러 발생**: 원인 모를 빌드 오류가 날 때는 `rm -rf build install log` 후 다시 빌드

> ⚠️ **주의 (Jetson Orin Nano 공통)**
파이썬(.py) 코드만 수정했다면 colcon build를 다시 할 필요가 없습니다! (단, --symlink-install 옵션으로 빌드했을 경우에만 해당)
> 

## 3. 소프트웨어 환경 요약 (v2.6)

이미지(`gae-system:v2.6`) 안에 아래 의존성들이 모두 세팅되어 있습니다. **따로 설치하지 마세요!**

- **시스템 및 코어 (System & Core)**

| **구분** | **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- | --- |
| **OS** | Ubuntu | **22.04.3 LTS** | Jammy Jellyfish (Jetson Orin Nano 표준) |
| **JetPack** | **JetPack SDK** | **6.x** | **L4T R36 Driver.** Orin Nano용 최신 펌웨어/BSP. |
| **ROS** | ROS 2 | **Humble** | Hawksbill (LTS 버전) |
| **CUDA** | CUDA Toolkit | **12.2** | V12.2.140 (GPU 가속을 위한 핵심 코어) |
| **Python** | Python | **3.10.12** | Ubuntu 22.04 기본 파이썬 환경 |
| **Monitor** | **jetson-stats** | **4.2.x** | **jtop** 시스템 모니터링 도구 (CPU/GPU/Fan 상태 확인) |
| **Dependency** | **Click** | **8.1.7** | **⚠️ 버전 고정:** Flask와 gTTS 간의 호환성 유지를 위해 8.1.7로 고정됨. |
| **Dependency** | **Blinker** | **1.9.0** | **⚠️ 강제 업데이트:** Flask 최신 버전 구동을 위해 시스템 기본값(1.4) 대신 업데이트됨. |

- **인공지능 및 딥러닝 (AI & Deep Learning)**
    - Jetson의 NPU/GPU를 최대한 활용하도록 **최적화된 버전**이 설치되어 있습니다.
    (⚠️ `pip install`로 함부로 덮어쓰지 마세요. GPU 가속이 풀릴 수 있습니다.)

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **PyTorch** | **2.2.0** | **GPU 가속(CUDA) 활성화됨.** 모델 학습/추론의 핵심. |
| **TorchVision** | 0.17.2 | 이미지 처리용 라이브러리 (PyTorch 연동) |
| **Torch2TRT** | 0.5.0 | **⭐ 중요:** PyTorch 모델을 TensorRT로 변환해주는 툴. (추론 속도 3~5배 향상 가능) |
| **Ultralytics** | **8.4.9** | **YOLOv8** 공식 라이브러리. (객체 인식 구현 시 사용) |
| **faster-whisper** | **1.2.1** | **OpenAI Whisper**의 고속 추론 버전. (CTranslate2 기반 최적화) |
| **NumPy** | **1.26.4** | **⚠️ 중요:** PyTorch/OpenCV 호환성을 위해 **2.0 미만**으로 고정됨. |
| **openai** | **2.16.0** | **LLM Interface.** AI 비서 구현용. |

- **비전 및 센서 (Vision & Sensors)**

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **OpenCV** | **4.9.0** | **⭐ CUDA(GPU) 가속 빌드.** (`WITH_CUDA=ON`, `cuDNN` 포함). 시스템 전역 설치됨. |
| **astra_camera** | (Source) | **Orbbec Astra Pro 드라이버.** (`libuvc` 패치 적용하여 소스 빌드됨) |
| **camera_info_manager** | (Binary) | 카메라 캘리브레이션(.yaml) 로더. **해상도 변경 시 필수.** |
| **rtabmap_ros** | (Binary) | RGB-D 카메라 기반 **VSLAM** 패키지 |
| **astra_camera_msgs** | (Source) | Astra 카메라 전용 메시지 타입 정의 |

- **음성 및 오디오 (Voice & Audio)**

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **pulseaudio-utils** | (System) | **🆕 핵심 연결 도구.** Host(Jetson)의 오디오 서버와 **Socket** 통신 및 `pactl` 제어용. |
| **alsa-utils** | **1.2.6** | **오디오 제어.** `aplay`, `amixer` 포함. (PulseAudio 플러그인을 통해 블루투스/HDMI 출력). |
| **SoX** | **14.4.2** | **🆕 오디오 플레이어.** `play`, `rec` 명령어 포함. (딜레이 없는 재생 담당). |
| **libsox-fmt-all** | (System) | **🆕 코덱 확장팩.** MP3, FLAC, OGG 등 다양한 포맷 재생 지원 라이브러리. |
| **gTTS** | **2.5.4** | **Google Text-to-Speech.** 텍스트를 음성(mp3)으로 변환하는 라이브러리. |
| **SpeechRecognition** | **3.14.5** | 오디오 입력 및 음성 인식 전처리 라이브러리 |
| **PyAudio** | **0.2.14** | 마이크 하드웨어 제어 및 입출력 담당 (PortAudio 기반) |
| **libasound2-plugins** | (latest) | **ALSA 플러그인.** PulseAudio와의 호환성 브리지 역할. |

- **하드웨어 제어 (Hardware Control)**

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **adafruit-circuitpython-servokit** | 1.3.22 | **PCA9685** (서보모터) 제어용. **DS3218MG** 구동 핵심 라이브러리. |
| **adafruit-extended-bus** | **(Latest / 0.0.0-auto)** | **🆕 I2C Bus Helper.** Jetson의 특정 I2C 포트(Bus 7 등)를 강제로 지정하여 제어하기 위한 리눅스 전용 도구. |
| **setuptools_scm** | **(Latest)** | **🔧 빌드 의존성.** `adafruit-extended-bus` 설치 시 패키지 메타데이터 생성을 위해 필수적으로 요구되는 도구. |
| **adafruit-circuitpython-mpu6050** | 1.3.5 | **MPU-6050** IMU 센서 데이터 수신용. Blinka 위에서 동작. |
| **libgpiod / python3-libgpiod** | (System) | **⭐ 최신 표준:** **HC-SR04P(초음파)** 제어를 위한 리눅스 표준 GPIO 도구. |
| **adafruit-blinka** | 8.23.0 | CircuitPython 라이브러리를 리눅스에서 쓰게 해주는 미들웨어. |
| **Jetson.GPIO** | **2.1.12** | **(내부 의존성)** Blinka 구동을 위한 필수 패키지. **직접 사용 안 함.** |
| **smbus2** | 0.6.0 | 저수준 I2C 통신 라이브러리. IMU 및 기타 I2C 장치 디버깅용. |

- **통신 및 인터페이스 (Communication & Interface)**

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **paho-mqtt** | **2.1.0** | **MQTT 프로토콜** 클라이언트. 로봇(Pub)과 웹 서버(Sub) 간의 실시간 데이터 송수신 담당. |
| **Flask** | **3.1.2** | **🆕 웹 서버 프레임워크.** 로봇 제어 API 및 대시보드 백엔드 구동. |
| **Flask-Cors** | **6.0.2** | **🆕 보안 설정.** 외부 웹 페이지(React/Vue 등)에서 로봇 API 호출 시 CORS 에러 방지. |
| **mosquitto-clients** | (System) | **🆕 터미널 디버깅 툴.** `mosquitto_pub/sub` 명령어로 통신 상태 즉시 확인 가능. |
| **web_video_server** | (Binary) | **웹 비디오 스트리밍.** ROS 이미지 토픽을 웹 브라우저 호환(MJPEG) 포맷으로 변환하여 실시간 송출. |

- **개발 및 디버깅 도구 (Development & Debugging Tools)**

| **패키지명** | **버전** | **설명 및 특이사항** |
| --- | --- | --- |
| **ros-humble-plotjuggler-ros** | (System) | **⭐ 데이터 시각화 도구.** ROS 2 토픽 및 rosbag 데이터를 실시간 그래프로 분석. |
| **rosbag2** | (System) | **데이터 녹화 도구.** ROS 2 표준 기록 장치 (.mcap 형식 지원). |

## 4. 하드웨어 환경 요약 (v2.6)

- **컴퓨팅 및 제어 (Computing & Control)**

| **구분** | **모델명** | **수량** | **설명 및 역할** |
| --- | --- | --- | --- |
| **Main Board** | **Jetson Orin Nano 8GB** | 1 | **Robot Brain.** 6-core ARM CPU / 1024-core Ampere GPU. RAM 8GB(Shared). |
| **Storage** | **Samsung PM9B1 (256GB)** | 1 | **Main Storage (NVMe M.2).** PCIe 4.0 지원. OS, 라이브러리, 데이터셋 저장용 고속 I/O. |
| **Swap Memory** | **19.7GB (Total)** | 1 | **ZRAM + 16GB NVMe File.** 8GB RAM의 한계를 극복하기 위한 대용량 가상 메모리 구성 완료. (OOM 방지) |
| **PWM Driver** | **PCA9685** (16-ch) | 2 | **Servo Controller.** I2C 통신. **0x40(후방), 0x41(전방)** 분산 연결.
※ *상세 채널 매핑은 4.4 참조.* |
| **Camera** | **Stereo Camera** | 1 | **Visual Perception.** Depth 정보 취득 및 RTAB-Map 기반 VSLAM 수행. |

- **구동부 (Actuation - Legs)**

| **구분** | **모델명** | **수량** | **설명 및 역할** |
| --- | --- | --- | --- |
| **Servo Motor** | **DS3218MG** | 12 | **Joint Actuators.** 20kg·cm 고토크 메탈 기어. **3 DoF x 4 Legs.** (Hip, Upper Leg, Lower Leg). |
| **Motion Range** | - | - | **180도 (0~180).** Isaac Sim의 DOF Limit 설정 시 이 물리적 한계를 반영해야 함. |

- **센서 (Sensors - Proprioceptive & Exteroceptive)**

| **구분** | **모델명** | **수량** | **설명 및 역할** |
| --- | --- | --- | --- |
| **IMU** | **MPU-6050** (6-axis) | 1 | **Body State Estimation.** 가속도/자이로 측정. (Roll/Pitch 추정 및 RL 관측 데이터). |
| **Ultrasonic** | **HC-SR04P** | 2 | **Obstacle Detection.** 전방 장애물 거리 측정. 3.3V 호환 모델(P) 사용. |

- **전원부 (Power System)**

| **구분** | **모델명** | **수량** | **설명 및 역할** |
| --- | --- | --- | --- |
| **Battery** | **Tenanty 2S LiPo** | 2 | **7.4V 5200mAh.** 1개 장착(교체형). 순간 고전류(서보 12개) 방전 대응. (하나는 예비용) |
| **Step-Down** | **HW-083** (DC-DC) | 2 | **Voltage Regulator.** 배터리 전압(7.4~8.4V)을 서보 적정 전압(6V) 및 로직 전압(5V)으로 강하하여 공급. |

- **서보 모터 상세 핀맵 (Servo Pin Mapping) [중요]**
    - *코드 생성(Python/C++) 및 제어 로직 작성 시 아래 매핑 테이블을 기준으로 합니다.*
    - **Joint Index:** [0: Knee, 1: Shoulder, 2: Hip] 순서 (또는 [15: Knee, 14: Shoulder, 13: Hip]).

| **PCA9685 주소** | **다리 위치 (Leg)** | **관절 (Joint) 및 핀 번호 (Pin Channel)** | **비고** |
| --- | --- | --- | --- |
| **0x40 (Rear)** | **오른쪽 뒷다리 (RR)** | **무릎(0)**, **어깨(1)**, **골반(2)** | Rear Right |
| **0x40 (Rear)** | **왼쪽 뒷다리 (RL)** | **무릎(15)**, **어깨(14)**, **골반(13)** | Rear Left |
| **0x41 (Front)** | **오른쪽 앞다리 (FR)** | **무릎(0)**, **어깨(1)**, **골반(2)** | Front Right |
| **0x41 (Front)** | **왼쪽 앞다리 (FL)** | **무릎(15)**, **어깨(14)**, **골반(13)** | Front Left |

## 5. 프로젝트 폴더 구조

```python
~/gae_ws/
│
├── 📂 docs/               # 회의록, 아키텍처 다이어그램, 이미지 등
├── 📄 README.md           # [메인] 프로젝트 설명서
├── 📄 requirements.txt    # [설정] 파이썬 패키지 명세서 (pip)
├── 📜 run_gae.sh          # [실행] 도커 컨테이너 시동 스크립트
├── 📜 update_env.sh       # [관리] 환경 동기화 스크립트
├── 🚫 .gitignore          # [Git] 불필요한 파일 무시 설정
│
└── 📂 src/                # [개발] 소스 코드 메인 디렉토리
    │
    ├── 🟢 [Team GAE 패키지] ----------------------------------
    │   │
    │   │
    │   ├── 📦 gae_bringup/      # [통합] 로봇 전체 실행 (.launch.py)
    │   │└── 📂 tools/                   # 기타 툴
		│   │    ├── 📄 check_env.py         # 환경 점검 스크립트
		│   │    └── 📄 check_cuda_opencv.py # CUDA 사용 여부 확인용 코드
    │   │
    │   ├── 📦 gae_control/     # [제어] 강화학습(RL) 및 보행 알고리즘
    │   │   ├── 📂 config/      # 제어 파라미터 (.yaml)
    │   │   └── 📂 models/      # Isaac Sim 학습된 RL 정책 파일 (.onnx/.pt)
    │   │
    │   ├── 📦 gae_hardware/    # [하드웨어] PCA9685(서보), IMU 센서 드라이버
    │   │   └── 📂 config/      # 핀맵 및 캘리브레이션 설정
    │   │
    │   ├── 📦 gae_interface/   # [통신] 웹 서버 / 음성 인식(STT) / gTTS
    │   │
    │   ├── 📦 gae_msgs/        # [메시지] 커스텀 msg/srv 인터페이스 정의
    │   │
    │   └── 📦 gae_perception/  # [인식] YOLOv8, SLAM, OpenCV
    │       ├── 📂 maps/        # vslam 맵 저장
    │       ├── 📂 config/      # 카메라/SLAM 설정 파일
    │       ├── 📂 launch/      # 인식 모듈 개별 실행 파일
    │       └── 📂 weights/     # YOLOv8 학습 가중치 파일 (.pt)
    │
    │
    └── 🔴 [외부 라이브러리 - 수정 주의] ------------------------
        │
        └── 📦 ros2_astra_camera/ # Orbbec Astra Pro 카메라 드라이버
            ├── astra_camera/
            └── astra_camera_msgs/
```

- **`ros2_astra_camera` (외부 드라이버)**
    - Orbbec 제조사에서 제공한 C++ 기반 드라이버를 Jetson 환경에 맞게 빌드해둔 것입니다.
    - 개발 중 **"카메라 실행 파일이 어딨지?"** 찾을 때만 아래 구조를 참고하세요.
    
    | **폴더명** | **설명 및 특이사항** |
    | --- | --- |
    | **`launch/`** | **[실행 파일 위치]** 
     ⚠️ **주의:** 여기는 Python(`.py`)이 아니라 **XML(`.xml`)** 형식을 씁니다.
     • **`astra_pro.launch.xml`** : ★ 우리가 사용할 유력한 실행 파일
     • `multi_astra.launch.xml` : 카메라 여러 대 쓸 때 참조 |
    | **`src/`** | **[소스 코드 (C++)]** 
     • `uvc_camera_driver.cpp` : RGB 카메라 제어 (libuvc 사용)
     • `ob_camera_node.cpp` : ROS 2 노드 메인
     *(건드리지 마세요. 빌드 꼬입니다.)* |
    | **`scripts/`** | **[설정 스크립트]** 
     • `56-orbbec-usb.rules` : USB 권한 설정 파일 (이미 적용됨) |
    - **카메라 실행 방법 (참고용)**
    
    ```python
    # 1. 패키지 이름: astra_camera
    # 2. 실행 파일: astra_pro.launch.xml (뒤에 .xml 꼭 붙이는 것 권장)
    
    # 도커 터미널1 에서 카메라 실행
    ros2 launch astra_camera astra_pro.launch.xml
    
    # 도커 터미널2 에서 토픽 발행 확인
    ros2 topic list
    /camera/color/camera_info
    /camera/color/image_raw
    /camera/depth/camera_info
    /camera/depth/image_raw
    /camera/depth/points
    /camera/ir/camera_info
    /camera/ir/image_raw
    /parameter_events
    /rosout
    /tf
    /tf_static
    
    # 도커 터미널2 에서 데이터가 진짜 들어오는지 주파수(Hz) 체크
    ros2 topic hz /camera/color/image_raw
    average rate: 28.068
            min: 0.031s max: 0.100s std dev: 0.01239s window: 29
    ```
    

- **💡OpenCV CUDA 개발 가이드**
    - 우리는 **OpenCV 4.9.0 (CUDA 포함)** 버전을 사용합니다.
    - 일반적인 CPU 코드(`cv2.imread` 등)도 잘 돌아가지만, **vSLAM이나 객체 인식 전처리**를 할 때는 아래 규칙을 따라야 성능 이득을 볼 수 있습니다.
1. **핵심 개념: `GpuMat` (GPU 메모리)**
    1. CPU의 이미지를 GPU로 옮겨야 연산이 가능합니다. 이 과정(Upload/Download)이 비용이 크므로, **한 번 GPU로 올렸으면 최대한 GPU 안에서 모든 지지고 볶는 작업(Resize, Color Convert, Threshold 등)을 끝내고** 결과만 내려받는 것이 핵심입니다.
2. **기본 사용 패턴 (Python Code)**

```python
import cv2
import numpy as np

def process_image_with_cuda(cpu_image):
    # 1. GPU 메모리 할당 (GpuMat 생성)
    gpu_frame = cv2.cuda_GpuMat()

    # 2. Upload: CPU(RAM) -> GPU(VRAM) [비용 발생 구간 ⚠️]
    gpu_frame.upload(cpu_image)

    # 3. Process: GPU 안에서 고속 연산 (여기서 뽕을 뽑아야 함)
    # 예: 리사이즈
    gpu_frame = cv2.cuda.resize(gpu_frame, (640, 480))
    
    # 예: 흑백 변환 (cvtColor가 아니라 cuda.cvtColor 사용)
    gpu_frame = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2GRAY)
    
    # 예: 가우시안 블러
    # 필터 생성 후 적용 (CPU 방식과 다름)
    gaussian_filter = cv2.cuda.createGaussianFilter(cv2.CV_8UC1, cv2.CV_8UC1, (5, 5), 0)
    gpu_frame = gaussian_filter.apply(gpu_frame)

    # 4. Download: GPU(VRAM) -> CPU(RAM) [비용 발생 구간 ⚠️]
    result_image = gpu_frame.download()

    return result_image
```

## 6. 시스템 리소스 모니터링 (jtop)

- Jetson Orin Nano의 VRAM(8GB) 상태를 확인하고 싶다면 **호스트 터미널**에서 아래 명령어를 쓰세요.

```python
jtop
```

- **MEM:** 시스템 메모리 및 Swap 사용량 체크
- **GPU:** AI 모델 돌릴 때 부하 체크

## 7. 트러블슈팅

- 혹시 Orbbec 카메라가 인식이 안 된다면, USB를 뺐다 꽂은 후 **호스트**에서 아래 명령어를 한 번 입력해 주세요. (Udev 규칙 리로드)

```python
sudo udevadm control --reload-rules && sudo udevadm trigger
```

- 도커 컨테이너는 관리자만이 파일을 편집할 수 있도록 권한을 뺏음. 해당 명령어로 ~/gae_ws/src 아래 폴더 대한 권한 가져오기

```python
ssafy@ubuntu:~/gae_ws/src$ sudo chown -R ssafy:ssafy ~/gae_ws/src
```

- **Jetson Orin Nano I2C 관련**

![Screenshot from 2026-02-04 11-32-31.png](attachment:fe28bd06-8f1f-4608-828d-ff30260ced32:Screenshot_from_2026-02-04_11-32-31.png)

- **NVIDIA Orin Nano의 내부 I2C 인터페이스 매핑**

| 물리 핀 | Jetson pinmux 이름 | SoC I2C 컨트롤러 | Linux 디바이스 |
| --- | --- | --- | --- |
| 27 / 28 | i2c2 | **c240000.i2c** | **/dev/i2c-1** |
| 3 / 5 | i2c8 | c250000.i2c | /dev/i2c-7 |
- **명령어 예시**

```python
ssafy@ubuntu:~$ sudo i2cdetect -y -r 7
[sudo] password for ssafy: 
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: 40 41 -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: 70 -- -- -- -- -- -- --                         
ssafy@ubuntu:~$ sudo i2cdetect -y -r 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- UU -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: UU -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --                         
ssafy@ubuntu:~$ i2cdetect -l
i2c-0   i2c             3160000.i2c                             I2C adapter
i2c-1   i2c             c240000.i2c                             I2C adapter
i2c-2   i2c             3180000.i2c                             I2C adapter
i2c-4   i2c             Tegra BPMP I2C adapter                  I2C adapter
i2c-5   i2c             31b0000.i2c                             I2C adapter
i2c-7   i2c             c250000.i2c                             I2C adapter
i2c-9   i2c             NVIDIA SOC i2c adapter 0                I2C adapter
ssafy@ubuntu:~$ 
```

## 8. 협업 컨벤션(규칙)

### 📢 ROS 2 통신 규칙 (Communication)

모든 노드는 **"서로 코드를 안 봐도 통신이 가능하게"** 설계해야 합니다.

- **토픽(Topic) 명명 규칙**
    - **형태:** `/(상위 패키지)/(장비)/(기능)`
    - **원칙:** 누가(Package), 무엇을(Device), 어떻게(Function) 하는지 토픽 이름만 보고 알 수 있어야 함.

| **구분** | **규칙** | **예시 (Good ✅)** |
| --- | --- | --- |
| **노드 이름** | 기능_node | `lane_detector_node`, `motor_control_node` |
| **토픽 이름** | **/(패키지)/(장비)/(기능)** | `/gae_perception/camera/image_raw`
`/gae_control/motor/cmd_vel` |
| **서비스 이름** | /(패키지)/(장비)/(동사) | `/gae_system/power/reset` |
- **메시지 타입 (Message Type)**
    - **원칙:** **ROS 2 표준 메시지 타입만 사용**합니다. (Custom Msg 지양 🚫)
    - 이유: 커스텀 메시지를 남발하면, 다른 팀원이 내 코드를 실행할 때마다 빌드 에러가 터집니다.
    - **권장 타입:**
        - 기본 데이터: `std_msgs` (String, Int32, Float32...)
        - 센서/이미지: `sensor_msgs` (Image, LaserScan, Imu...)
        - 위치/속도: `geometry_msgs` (Twist, PoseStamped...)

### 🚀 실행 및 데이터 관리 (Workflow)

- **실행 파일 (Launch File) 필수**
    - **규칙:** "내 기능은 명령어 한 줄로 켜진다."
    - 복잡하게 "python3 뭐 실행하고, 파라미터 뭐 넣고..." 하지 마세요. 무조건 `launch` 파일 하나로 끝내야 합니다.
    - 
    
    ```python
    # 예시: 이거 한 줄이면 내 파트는 알아서 다 돌아감
    ros2 launch gae_perception lane_detection.launch.py
    ```
    
- **데이터 녹화 (Rosbag)**
    - **규칙:** 주행 테스트 시, 결과물이나 센서 데이터는 `rosbag`으로 녹화해서 공유합니다.
    - 이를 통해 로봇이 없어도 사무실에서 시뮬레이션 및 디버깅이 가능합니다.
    
    ```
    # 예시: 카메라랑 제어 명령 녹화
    ros2 bag record -o test_data_01 /gae_perception/camera/image_raw /gae_control/motor/cmd_vel
    ```
    

### 📂 파일 및 폴더 위치 규칙

- **파일 위치**
    - **실행 파일(.launch.py):** 각 패키지의 `launch/` 폴더.
    - **설정 값(.yaml):** 각 패키지의 `config/` 폴더. (코드 안에 하드코딩 금지 🚫)
    - **모델 파일(.pt, .onnx):**
        - `gae_perception/weights/`
        - `gae_control/models/`
- **절대 경로 금지 (`/home/ssafy/...` ❌)**
    - 팀원 컴퓨터마다 경로가 다를 수 있습니다. 무조건 **ROS 2 패키지 상대 경로**를 사용하세요.

```python
# Good ✅
from ament_index_python.packages import get_package_share_directory
pkg_path = get_package_share_directory('gae_perception')
model_path = os.path.join(pkg_path, 'weights', 'yolov8n.pt')
```

- **의존성 관리 (`package.xml`, `setup.py`)**
    - 새로운 라이브러리(`cv_bridge` 등)나 설정 파일(`launch`, `config`)을 추가했다면, 반드시 `package.xml`과 `setup.py`에 등록해야 빌드됩니다.
    

### 🐍 코딩 스타일 (Python)

- **클래스명:** `PascalCase` (예: `GaePerceptionNode`)
- **함수/변수명:** `snake_case` (예: `detect_object`, `image_raw`)

### 🐙 Git 규칙

- 현재 `~/gae_ws/src` 폴더는 **Jetson(호스트)과 Docker(컨테이너)가 서로 "공유"**하고 있습니다.
    - 도커 안에서 파일을 수정해도 → 바깥(Jetson)에 저장됩니다.
    - 바깥(Jetson)에서 파일을 수정해도 → 안(Docker)에 반영됩니다
- **Git 명령(add, commit, push)은** 굳이 도커 안에서 할 필요 없이, **바깥(Jetson 호스트 터미널)에서 하는 게 훨씬 편하고 안전**
- **~/gae_ws/src 에서 git 저장소 연결 후 commit - push 진행하면 됩니다.**