# GAE - AIoT 로봇 반려견 돌봄 플랫폼

> 로봇 반려견을 원격으로 모니터링하고 제어할 수 있는 AIoT 기반 반려견 돌봄 플랫폼

![ROS2](https://img.shields.io/badge/ROS2-Humble-22314E?logo=ros)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-4.0-6DB33F?logo=springboot)
![Vue.js](https://img.shields.io/badge/Vue.js-3.5-4FC08D?logo=vuedotjs)
![Docker](https://img.shields.io/badge/Docker-blue?logo=docker)
![Jetson](https://img.shields.io/badge/Jetson_Orin_Nano-8GB-76B900?logo=nvidia)

---

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | GAE (개) |
| **분류** | AIoT 풀스택 웹 + 로보틱스 |
| **기간** | 2026.01 ~ 2026.02 (6주) |
| **소속** | 삼성 청년 SW 아카데미 (SSAFY) 14기 |
| **팀 구성** | 6명 |

시각장애인이 실외 보행 시 **실시간 음성 안내, 장애물/신호등 감지, 보호자 연동, 원격 모니터링** 기능을 갖춘 4족 보행 로봇 + 웹 서비스입니다.

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────┐
│           User (Web Browser / PWA)               │
└────────────┬────────────────────────────────────┘
             │ HTTPS / WebSocket
             ▼
┌─────────────────────────────────────────────────┐
│        Nginx (Reverse Proxy + SSL)               │
│  / → Vue SPA    /api/ → Spring Boot   /ws/ → WS │
└────────────┬──────────────┬─────────────────────┘
             │              │ MQTT.js (9001)
             ▼              ▼
┌─────────────────────────────────────────────────┐
│           Backend (Spring Boot 4.0)              │
│  REST API / MQTT↔WebSocket / Firebase FCM        │
│  PostgreSQL 15 / Kakao Maps Proxy                │
└────────────┬────────────────────────────────────┘
             │ MQTT (1883)
             ▼
┌─────────────────────────────────────────────────┐
│      Mosquitto MQTT Broker (3포트)               │
│  1883 TCP / 1884 TCP (호환) / 9001 WebSocket     │
└───────┬──────────────────┬──────────────────────┘
        ▼                  ▼
┌─────────────────────────────────────────────────┐
│     Jetson Orin Nano (Docker + ROS2 Humble)      │
│                                                   │
│  [gae_control]    RL 보행 제어 (50Hz)             │
│  [gae_hardware]   서보 12축 / IMU / 초음파         │
│  [gae_perception] YOLOv8 + RTAB-Map SLAM          │
│  [gae_interface]  AI 음성 비서 + MQTT 브릿지       │
└─────────────────────────────────────────────────┘
```

---

## 핵심 기능

### 1. AI 음성 비서 "싸라"
- **Whisper tiny + INT8 양자화** → 0.4초 추론
- 긴급 정지 응답 3초 → **0.5초** (6배 개선)
- TTS 캐시 14개 (0.1초 재생) + espeak 오프라인 폴백
- GPT-4o-mini 구현 후 안전 기준 미충족으로 폐기 → 키워드 매칭 전환

### 2. YOLOv8 객체 인식
- 7번 반복 실험 → "강아지 시선(30cm) 데이터" 인사이트 도출
- 3클래스(빨간불/초록불/정지선) 집중 → **mAP 0.99**
- TensorRT FP16 양자화 → Jetson에서 **60~100 FPS**

### 3. MQTT 3포트 멀티 브로커
- TCP 1883 + 1884(호환) + WebSocket 9001 동시 운영
- 팀원 코드 수정 없이 인프라 설정으로 통신 호환 해결
- ROS2 ↔ MQTT ↔ WebSocket 3계층 통신 아키텍처

### 4. VSLAM 좌표 브릿지
- RTAB-Map → 4단계 필터링 → MQTT → 웹 지도
- (0,0) 리셋 / 점프 / 지터 / 전송 제한 필터

### 5. 실시간 로봇 제어
- 웹 조이스틱 → MQTT → ROS2 → 서보 제어
- 자율 주행 네비게이션, 긴급 정지, 홈 복귀

### 6. 강화학습 보행
- Isaac Sim + Isaac Lab, PPO, 4096 병렬 환경
- Sim2Real: 50Hz 제어 루프, 12축 서보 동시 제어

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| **Robot** | Jetson Orin Nano, ROS2 Humble, CUDA 12.2, Python 3.10 |
| **AI/ML** | faster-whisper (INT8), YOLOv8 (TensorRT FP16), PyTorch 2.2 |
| **RL** | NVIDIA Isaac Sim 5.1 + Isaac Lab 2.3, PPO |
| **Backend** | Spring Boot 4.0, Java 17, PostgreSQL 15, JWT, Firebase FCM |
| **Frontend** | Vue 3, Vite, Pinia, Tailwind CSS, Kakao Map API, PWA |
| **Communication** | MQTT (Mosquitto/Paho), WebSocket (STOMP), ROS2 DDS |
| **Infra** | Docker, Docker Compose, Nginx, AWS EC2 |
| **Hardware** | DS3218MG 서보 ×12, MPU-6050 IMU, Orbbec Astra Pro, HC-SR04P |

---

## 프로젝트 구조

```
S14P11C101/
├── backend/               # Spring Boot 백엔드
│   ├── src/main/java/com/gae/server/
│   │   ├── api/           # auth, member, robot, mqtt, activity, notification, proxy
│   │   ├── domain/        # JPA 엔티티
│   │   └── global/        # JWT, Security, MQTT, WebSocket 설정
│   └── docker-compose.yml
│
├── frontend/              # Vue 3 프론트엔드 (18개 라우트)
│   ├── src/views/         # 페이지 컴포넌트
│   ├── src/stores/        # Pinia 상태 관리
│   └── nginx.conf
│
├── gae_ws/src/            # ROS2 워크스페이스
│   ├── gae_bringup/       # 통합 런치
│   ├── gae_control/       # RL 보행 제어
│   ├── gae_hardware/      # 서보/IMU/초음파 드라이버
│   ├── gae_interface/     # 음성 비서, MQTT 브릿지
│   ├── gae_perception/    # YOLO, RTAB-Map SLAM
│   └── ros2_astra_camera/ # RGB-D 카메라 드라이버
│
├── rl_ws/                 # 강화학습 (Isaac Sim/Lab)
├── dummies_ros2/          # 더미 시뮬레이터
└── mosquitto/             # MQTT 브로커 설정
```

---

## 핵심 성과

| 항목 | 수치 |
|------|------|
| 긴급 정지 응답 | 3초 → **0.5초** |
| YOLO mAP | **≈ 0.99** (강아지 시선 데이터) |
| YOLO 추론 속도 | **60~100 FPS** (Jetson) |
| Whisper 메모리 | 140MB → **75MB** (46% 절감) |
| TTS 응답 | 0.5~1초 → **0.1초** (캐시) |
| 오프라인 TTS | **100%** 보장 (espeak 폴백) |
| RL 보행 제어 | **50Hz** 실시간 루프 |

---

## 하드웨어 구성

| 부품 | 사양 | 수량 | 역할 |
|------|------|:----:|------|
| Jetson Orin Nano | 8GB RAM, 1024코어 GPU | 1 | 메인 컴퓨팅 |
| DS3218MG 서보 | 20kg·cm, 180° | 12 | 4족 보행 (3 DoF × 4) |
| Orbbec Astra Pro | RGB-D 스테레오 | 1 | 영상 + 깊이 인식 |
| MPU-6050 | 6축 IMU | 1 | 자세 추정 |
| HC-SR04P | 초음파 거리 센서 | 2 | 장애물 감지 |
| PCA9685 | 16ch PWM 드라이버 | 2 | 서보 제어 (I2C) |

---

## 실행 방법

### Jetson Docker (로봇)
```bash
docker run -it \
    --privileged \
    --network host \
    --runtime nvidia \
    -v /dev:/dev \
    -v /tmp/pulseaudio.socket:/tmp/pulseaudio.socket \
    -e PULSE_SERVER=unix:/tmp/pulseaudio.socket \
    jjy092801/gae-system:v2.6
```

### 웹 서비스 (Docker Compose)
```bash
cd backend
docker-compose up -d
```

### ROS2 빌드 및 실행
```bash
cd ~/gae_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch gae_bringup gae_system.launch.py
```

---

## 팀 구성

| 담당 | 주요 작업 |
|------|----------|
| **AI/인프라** | AI 음성 비서, YOLO 연동, MQTT 통신, VSLAM 브릿지, Docker, Git 관리 |
| **웹** | Vue 3 프론트엔드, Spring Boot 백엔드, EC2 배포 |
| **하드웨어/RL** | 강화학습 보행, Sim2Real, 서보/IMU 제어, 기구부 설계 |

---

## 프로젝트 규모

| 항목 | 수량 |
|------|------|
| Backend Java 파일 | 70+ |
| Frontend Vue 컴포넌트 | 22 |
| Robot Python 모듈 | 75 |
| ROS2 패키지 | 8 |
| API 엔드포인트 | 30+ |
| DB 테이블 | 5 |

---

## 라이선스

이 프로젝트는 삼성 청년 SW 아카데미(SSAFY) 14기 특화 프로젝트로 개발되었습니다.
