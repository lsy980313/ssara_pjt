# 포팅 매뉴얼 (Porting Manual)

> **프로젝트명:** GAE - AIoT 로봇 반려견 돌봄 플랫폼
> **최종 수정일:** 2025-02-08

---

## 1. 빌드 및 배포 가이드

### 1-1. 개발 환경 및 버전 정보

#### Backend

| 항목 | 버전 / 상세 |
|------|-------------|
| Language | Java 17 |
| Framework | Spring Boot 4.0.1 |
| Build Tool | Gradle 8.x (Gradle Wrapper 포함) |
| IDE | IntelliJ IDEA 2024.x 이상 권장 |
| JVM | Eclipse Temurin 17 (Docker: `eclipse-temurin:17-jdk-alpine`) |
| WAS | Spring Boot 내장 Tomcat |
| Database | PostgreSQL 15 |
| MQTT Broker | Eclipse Mosquitto (TCP 1883 + WebSocket 9001) |
| MQTT Client | Eclipse Paho 1.2.5 |
| Authentication | JWT (JJWT 0.13.0) |
| Firebase Admin SDK | 9.2.0 |

#### Frontend

| 항목 | 버전 / 상세 |
|------|-------------|
| Language | JavaScript (ES Module) |
| Framework | Vue.js 3.5.24 |
| Build Tool | Vite 7.2.4 |
| Runtime | Node.js 20 |
| IDE | VS Code 최신 권장 |
| Web Server | Nginx Alpine (배포 시) |
| State Management | Pinia 3.0.0 |
| HTTP Client | Axios 1.13.2 |
| CSS | Tailwind CSS 4.1.18 |
| MQTT Client | mqtt.js 5.15.0 |
| WebSocket | @stomp/stompjs 7.2.1 |
| PWA | vite-plugin-pwa 1.2.0 |

#### Robot (Jetson)

| 항목 | 버전 / 상세 |
|------|-------------|
| Board | NVIDIA Jetson (JetPack) |
| OS | Ubuntu 22.04 |
| ROS | ROS2 Humble |
| Docker Image | gae-system:v2.6 (torch, torchvision, opencv 내장) |
| Python | 3.10 |
| SLAM | RTAB-Map |
| Camera | Orbbec Astra Pro (RGB-D) |

---

### 1-2. 소스 클론 및 빌드

#### Step 1: 소스 클론

```bash
git clone https://lab.ssafy.com/s14-final/S14P11C101.git
cd S14P11C101
```

#### Step 2: Backend 빌드

```bash
cd backend

# 1) PostgreSQL 실행 (Docker)
docker-compose up -d

# 2) 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 DB 비밀번호, JWT 시크릿, Firebase 키 등 입력

# 3) Gradle 빌드
./gradlew bootJar -x test

# 4) 실행
java -jar build/libs/*.jar
# 또는
./gradlew bootRun
```

#### Step 3: Frontend 빌드

```bash
cd frontend

# 1) 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 API URL, MQTT IP, Firebase 키, Kakao API 키 등 입력

# 2) 의존성 설치
npm ci

# 3) 개발 서버 실행
npm run dev

# 4) 프로덕션 빌드
npm run build
# → dist/ 폴더에 정적 파일 생성
```

#### Step 4: Mosquitto 브로커 실행

```bash
# Docker로 실행
docker run -d \
  --name mosquitto \
  -p 1883:1883 \
  -p 9001:9001 \
  -v $(pwd)/mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf \
  eclipse-mosquitto

# 또는 로봇(Jetson)에서 직접 실행
mosquitto -c /etc/mosquitto/mosquitto.conf
```

---

### 1-3. 환경 변수 상세

#### Backend 환경 변수 (`backend/.env`)

| 변수명 | 설명 | 기본값 / 예시 |
|--------|------|---------------|
| `DB_HOST` | PostgreSQL 호스트 | `localhost` |
| `DB_PORT` | PostgreSQL 포트 | `5432` |
| `DB_NAME` | 데이터베이스명 | `dog_gaje_db` |
| `DB_USERNAME` | DB 계정 | `postgres` |
| `DB_PASSWORD` | DB 비밀번호 | (설정 필요) |
| `JWT_SECRET` | JWT 서명 키 (Base64, 256비트 이상) | `openssl rand -base64 64`로 생성 |
| `JWT_EXPIRATION` | 토큰 만료 시간 (ms) | `86400000` (24시간) |
| `SERVER_PORT` | 서버 포트 | `8080` |
| `SPRING_PROFILES_ACTIVE` | 프로파일 | `dev` / `prod` / `docker` |
| `FIREBASE_PROJECT_ID` | Firebase 프로젝트 ID | (Firebase Console에서 확인) |
| `FIREBASE_PRIVATE_KEY` | Firebase 비공개 키 | (서비스 계정 JSON에서 복사) |
| `FIREBASE_CLIENT_EMAIL` | Firebase 서비스 계정 이메일 | (서비스 계정 JSON에서 복사) |
| `FIREBASE_CLIENT_ID` | Firebase 클라이언트 ID | (서비스 계정 JSON에서 복사) |
| `ROSBRIDGE_HOST` | ROSBridge 호스트 | `localhost` |
| `ROSBRIDGE_PORT` | ROSBridge 포트 | `9090` |
| `CORS_ALLOWED_ORIGINS` | 허용 Origin (쉼표 구분) | `http://localhost:5173,http://localhost:3000` |
| `LOG_LEVEL` | 로그 레벨 | `INFO` |

#### Frontend 환경 변수 (`frontend/.env`)

| 변수명 | 설명 | 기본값 / 예시 |
|--------|------|---------------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8080/api` |
| `VITE_WS_URL` | WebSocket URL | `ws://localhost:8080/ws/websocket` |
| `VITE_MQTT_BROKER_IP` | Mosquitto 브로커 IP (Jetson) | `172.30.1.49` |
| `VITE_FIREBASE_API_KEY` | Firebase API 키 | (Firebase Console에서 확인) |
| `VITE_FIREBASE_AUTH_DOMAIN` | Firebase Auth 도메인 | `<project>.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | Firebase 프로젝트 ID | (Firebase Console에서 확인) |
| `VITE_FIREBASE_STORAGE_BUCKET` | Firebase Storage | `<project>.appspot.com` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | FCM Sender ID | (Firebase Console에서 확인) |
| `VITE_FIREBASE_APP_ID` | Firebase App ID | (Firebase Console에서 확인) |
| `VITE_FIREBASE_VAPID_KEY` | FCM VAPID 키 | (Cloud Messaging 탭에서 확인) |
| `VITE_KAKAO_MAP_API_KEY` | 카카오맵 JavaScript 키 | (Kakao Developers에서 발급) |
| `VITE_KAKAO_REST_API_KEY` | 카카오 REST API 키 | (Kakao Developers에서 발급) |
| `VITE_GMS_API_KEY` | GMS(SSAFY OpenAI Proxy) API 키 | (SSAFY에서 발급) |
| `VITE_APP_NAME` | 앱 이름 | `GAE` |
| `VITE_APP_VERSION` | 앱 버전 | `1.0.0` |

---

### 1-4. 배포 시 특이사항

#### Docker 배포

```bash
# Backend
cd backend
docker build -t gae-backend .
docker run -d -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=docker \
  -e SPRING_DATASOURCE_URL=jdbc:postgresql://host:5432/dog_gaje_db \
  -e SPRING_DATASOURCE_USERNAME=postgres \
  -e SPRING_DATASOURCE_PASSWORD=your_password \
  gae-backend

# Frontend
cd frontend
docker build -t gae-frontend .
docker run -d -p 80:80 gae-frontend
```

#### 배포 주의사항

| # | 항목 | 내용 |
|---|------|------|
| 1 | **MQTT 브로커 IP** | 프론트엔드 `.env`의 `VITE_MQTT_BROKER_IP`를 실제 로봇 IP로 변경 필요 |
| 2 | **STOMP WebSocket URL** | `robotStore.js`에 `ws://localhost:8080`이 하드코딩 → 배포 환경에서는 실제 서버 IP로 변경 필요 |
| 3 | **카메라 스트림 프록시** | `vite.config.js`의 `/robot-stream` 프록시 target을 실제 로봇 IP로 변경 |
| 4 | **JPA DDL 모드** | dev: `create` (매번 테이블 재생성), prod: `validate` (스키마 변경 금지) |
| 5 | **Nginx WebSocket** | 배포 시 Nginx에 `/ws/` 경로 WebSocket 프록시 설정 추가 필요 |
| 6 | **HTTPS 환경** | HTTPS 배포 시 `ws://` → `wss://` 변경 필요 (Mixed Content 차단 방지) |

---

### 1-5. 프로퍼티 파일 목록

| 파일 | 위치 | 주요 내용 |
|------|------|----------|
| `application.yml` | `backend/src/main/resources/` | MQTT 브로커 URL, 기본 프로파일 설정 |
| `application-dev.yml` | `backend/src/main/resources/` | 개발 DB 접속 정보, JPA ddl-auto: create, JWT 시크릿 |
| `application-docker.yml` | `backend/src/main/resources/` | Docker 환경 DB (환경변수 참조), JPA ddl-auto: update |
| `application-prod.yml` | `backend/src/main/resources/` | 운영 DB (환경변수 참조), JPA ddl-auto: validate |
| `.env` | `backend/` | DB 계정, JWT 시크릿, Firebase 키, CORS 설정 |
| `.env` | `frontend/` | API URL, MQTT IP, Firebase 키, Kakao API 키, GMS 키 |
| `mosquitto.conf` | `mosquitto/config/` | MQTT 리스너 포트 (1883, 9001), 인증 설정 |
| `vite.config.js` | `frontend/` | 프록시 설정 (API, 카메라 스트림, GMS) |
| `nginx.conf` | `frontend/` | 배포용 Nginx 프록시 및 SPA 라우팅 설정 |

---

## 2. 외부 서비스 정보

### 2-1. Firebase (FCM 푸시 알림)

| 항목 | 내용 |
|------|------|
| **서비스** | Firebase Cloud Messaging (FCM) |
| **용도** | 이상 감지 시 보호자에게 푸시 알림 전송 |
| **가입** | [Firebase Console](https://console.firebase.google.com/) |
| **설정 절차** | 1) 프로젝트 생성 → 2) 웹 앱 등록 → 3) 서비스 계정 > 새 비공개 키 생성(JSON) → 4) Cloud Messaging > VAPID 키 확인 |
| **Backend 필요 값** | `FIREBASE_PROJECT_ID`, `FIREBASE_PRIVATE_KEY`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_CLIENT_ID` |
| **Frontend 필요 값** | `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_STORAGE_BUCKET`, `VITE_FIREBASE_MESSAGING_SENDER_ID`, `VITE_FIREBASE_APP_ID`, `VITE_FIREBASE_VAPID_KEY` |

### 2-2. Kakao Map API

| 항목 | 내용 |
|------|------|
| **서비스** | Kakao Maps SDK / REST API |
| **용도** | 로봇 위치 카카오맵 표시, 역지오코딩 (좌표 → 주소 변환), 장소 검색 |
| **가입** | [Kakao Developers](https://developers.kakao.com/) |
| **설정 절차** | 1) 애플리케이션 생성 → 2) 플랫폼 > 웹 사이트 도메인 등록 (`http://localhost:5173`) → 3) 앱 키 확인 (JavaScript 키, REST API 키) |
| **Frontend 필요 값** | `VITE_KAKAO_MAP_API_KEY` (JavaScript 키), `VITE_KAKAO_REST_API_KEY` (REST API 키) |

### 2-3. GMS (SSAFY OpenAI Proxy)

| 항목 | 내용 |
|------|------|
| **서비스** | SSAFY GMS API (OpenAI GPT Proxy) |
| **용도** | AI 비서 자연어 처리 (보호자-로봇 간 대화) |
| **가입** | SSAFY 제공 (팀별 API 키 발급) |
| **엔드포인트** | `https://gms.ssafy.io/gmsapi` (Vite 프록시: `/gms-api`) |
| **Frontend 필요 값** | `VITE_GMS_API_KEY` |

### 2-4. Gmail SMTP

| 항목 | 내용 |
|------|------|
| **서비스** | Gmail SMTP |
| **용도** | 이메일 인증, 비밀번호 재설정 메일 발송 |
| **설정** | Gmail 계정 > 2단계 인증 > 앱 비밀번호 생성 |
| **Backend 설정 위치** | `application-dev.yml` > `spring.mail` |

---

## 3. DB 정보

### 3-1. DB 접속 정보

| 항목 | 개발 환경 | Docker 환경 | 운영 환경 |
|------|----------|-------------|----------|
| DBMS | PostgreSQL 15 | PostgreSQL 15 | PostgreSQL 15 |
| Host | localhost | (환경변수) | (환경변수) |
| Port | 5432 | 5432 | 5432 |
| Database | dog_gaje_db | dog_gaje_db | (환경변수) |
| Username | postgres | (환경변수) | (환경변수) |
| Password | your_password | (환경변수) | (환경변수) |
| JPA DDL | create | update | validate |

### 3-2. DB Docker 실행

```bash
cd backend
docker-compose up -d

# 확인
docker ps | grep gae_postgres
```

### 3-3. DB 덤프

```bash
# 덤프 생성
pg_dump -U postgres -d dog_gaje_db > exec/db_dump.sql

# 덤프 복원
psql -U postgres -d dog_gaje_db < exec/db_dump.sql
```

### 3-4. 주요 테이블

| 테이블 | 설명 |
|--------|------|
| `member` | 회원 정보 (보호자) |
| `robot` | 로봇 정보 (시리얼번호, 배터리, 상태, 위치) |
| `activity_log` | 이상 감지 활동 로그 (낙상, 장시간 부재 등) |

---

## 4. 시연 시나리오

### 4-1. 사전 준비

1. PostgreSQL 실행 (`docker-compose up -d`)
2. Backend 실행 (`./gradlew bootRun`)
3. Frontend 실행 (`npm run dev`)
4. Mosquitto 브로커 실행 (로봇 또는 로컬)
5. 로봇 전원 ON + ROS2 노드 실행 (`camera_start.sh`)

### 4-2. 시연 순서

#### Scene 1: 로그인

| 순서 | 화면 | 동작 |
|------|------|------|
| 1 | 로그인 화면 | 앱 접속 → 로그인 화면 표시 |
| 2 | 로그인 화면 | 이메일/비밀번호 입력 → [로그인] 버튼 클릭 |
| 3 | 홈 화면 | 로그인 성공 → 홈 화면 이동 |

#### Scene 2: 홈 화면 - 로봇 상태 확인

| 순서 | 화면 | 동작 |
|------|------|------|
| 1 | 홈 화면 | "SSARA" 로봇 이름 + 온라인 상태(초록 점) + 배터리 잔량 확인 |
| 2 | 홈 화면 | 배터리 상태 카드 클릭 → 배터리 상세 페이지 이동 |
| 3 | 홈 화면 | 카메라 스트림 실시간 표시 확인 |
| 4 | 홈 화면 | 지도 영역에서 VSLAM/카카오맵 토글 → 로봇 위치 마커 확인 |

#### Scene 3: 카메라 상세보기

| 순서 | 화면 | 동작 |
|------|------|------|
| 1 | 홈 화면 | [카메라 상세보기] 버튼 클릭 |
| 2 | 카메라 화면 | 전체화면 카메라 스트림 확인 (세로: 화면 꽉 채움 / 가로: 비율 유지) |
| 3 | 카메라 화면 | 화면 탭 → 컨트롤 표시 |
| 4 | 카메라 화면 | 우측 [가로] 버튼 클릭 → 가로 모드 전환 |
| 5 | 카메라 화면 | [사진] 버튼 클릭 → 플래시 효과 + "사진이 기록에 저장되었습니다" 토스트 |
| 6 | 카메라 화면 | [녹화] 버튼 클릭 → REC 표시 + 시간 카운트 → 다시 클릭하여 중지 |
| 7 | 카메라 화면 | 우측 상단 [맵] 아이콘 클릭 → 미니맵 오버레이 표시 |
| 8 | 카메라 화면 | 좌측 하단 [AI 비서] 버튼 클릭 → 채팅 오버레이 표시 |

#### Scene 4: 위치간 이동 (네비게이션)

| 순서 | 화면 | 동작 |
|------|------|------|
| 1 | 홈 화면 | [위치간 이동] 버튼 클릭 |
| 2 | 네비게이션 화면 | 이동할 좌표 입력 또는 지도에서 위치 선택 |
| 3 | 네비게이션 화면 | [이동] 버튼 클릭 → 로봇이 해당 위치로 이동 |
| 4 | 네비게이션 화면 | 실시간 지도에서 로봇 마커 이동 확인 |

#### Scene 5: 핵심기록 확인

| 순서 | 화면 | 동작 |
|------|------|------|
| 1 | 홈 화면 | [핵심기록 확인] 버튼 클릭 |
| 2 | 기록 화면 | 촬영한 사진/녹화 영상 목록 확인 |
| 3 | 기록 화면 | 사진 클릭 → 상세 보기 |
| 4 | 기록 화면 | 영상 클릭 → 재생 |

#### Scene 6: 기능 메뉴

| 순서 | 화면 | 동작 |
|------|------|------|
| 1 | 하단 네비게이션 | [기능] 탭 클릭 |
| 2 | 기능 화면 | 건강관리, 커뮤니티, 메모 등 부가 기능 확인 |

#### Scene 7: AI 비서 대화

| 순서 | 화면 | 동작 |
|------|------|------|
| 1 | 카메라 화면 또는 AI 비서 화면 | AI 비서 채팅 창 열기 |
| 2 | 채팅 화면 | 보호자 메시지 입력 → [전송] |
| 3 | 채팅 화면 | 로봇의 음성 대화 실시간 수신 확인 |
| 4 | 채팅 화면 | 위치 검색 요청/응답 확인 |

#### Scene 8: 이상 감지 알림

| 순서 | 화면 | 동작 |
|------|------|------|
| 1 | (로봇 동작 중) | 로봇 AI가 낙상/장시간 부재 등 이상 감지 |
| 2 | 홈 화면 | 실시간 활동 로그에 이상 감지 이벤트 표시 |
| 3 | 기록 화면 | 이상 감지 기록 확인 |

---

## 부록: 시스템 아키텍처

```
[로봇 (Jetson)]                [Mosquitto Broker]              [Spring Backend]              [Frontend (Vue)]
                                 172.30.1.49                     localhost:8080                localhost:5173

  ROS2 Node ──publish──> MQTT (tcp://1883) ──subscribe──> Spring Integration ──broadcast──> STOMP WebSocket
                           robot/pose                     MqttService.java                  /topic/robot/*
                           robot/status
                           robot/activity

                         MQTT (ws://9001) ──────────────────────────────────────────────> Frontend 직접 구독
                                                                                          robot/pose (저지연)
                                                                                          /gae/* (AI 비서)

  ROS2 Node <──subscribe── MQTT <──publish── MqttGateway <──REST API──────────────────── Frontend 명령 전송
                           robot/cmd/vel                                                  /api/robot/*
```
