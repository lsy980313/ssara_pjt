# GAE Server

AIoT 로봇 펫 관리 플랫폼의 Spring Boot 백엔드 서버

## 기술 스택

- Java 17
- Spring Boot 4.0.1
- Spring Security + JWT
- Spring Data JPA + PostgreSQL
- Spring Integration MQTT
- WebSocket (STOMP)

## 실행 방법

### 1. 데이터베이스 실행

```bash
docker-compose up -d
```

### 2. 서버 실행

```bash
./gradlew bootRun
```

서버: http://localhost:8080

## API 엔드포인트

### 인증 (Public)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/auth/signup` | 회원가입 |
| POST | `/api/auth/login` | 로그인 (JWT 토큰 발급) |

### 회원 (JWT 필요)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/members/me` | 내 정보 조회 |
| PATCH | `/api/members/me` | 내 정보 수정 |
| DELETE | `/api/members/me` | 회원 탈퇴 |

### 로봇 (JWT 필요)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/robots/me` | 내 로봇 조회 |
| PATCH | `/api/robots/me` | 내 로봇 정보 수정 |

### 로봇 제어 (MQTT 발행)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/robot/control` | 속도 제어 (조이스틱) |
| POST | `/api/robot/home` | 홈으로 이동 |
| POST | `/api/robot/stop` | 정지 |
| POST | `/api/robot/nav` | 좌표 이동 |

## 로봇 속도 제어 API

### POST /api/robot/control

프론트엔드 조이스틱/화살표 키로 로봇을 제어합니다.

**Request Body:**
```json
{
  "linearX": 0.5,
  "angularZ": 0.3
}
```

| 필드 | 타입 | 범위 | 설명 |
|------|------|------|------|
| linearX | Double | -1.0 ~ 1.0 | 전진(+) / 후진(-) 속도 |
| angularZ | Double | -1.0 ~ 1.0 | 좌회전(+) / 우회전(-) 각속도 |

**Response:**
```json
{
  "status": "success",
  "message": "Velocity command sent",
  "linearX": 0.5,
  "angularZ": 0.3
}
```

### MQTT 발행 메시지 (Rosbridge Protocol)

`robot/cmd/vel` 토픽으로 ROS 표준 규격 메시지가 발행됩니다:

```json
{
  "op": "publish",
  "topic": "/cmd_vel",
  "msg": {
    "linear": { "x": 0.5, "y": 0.0, "z": 0.0 },
    "angular": { "x": 0.0, "y": 0.0, "z": 0.3 }
  }
}
```

### 사용 예시

```bash
# 전진
curl -X POST http://localhost:8080/api/robot/control \
  -H "Content-Type: application/json" \
  -d '{"linearX": 0.5, "angularZ": 0.0}'

# 후진
curl -X POST http://localhost:8080/api/robot/control \
  -H "Content-Type: application/json" \
  -d '{"linearX": -0.5, "angularZ": 0.0}'

# 좌회전
curl -X POST http://localhost:8080/api/robot/control \
  -H "Content-Type: application/json" \
  -d '{"linearX": 0.0, "angularZ": 0.5}'

# 우회전
curl -X POST http://localhost:8080/api/robot/control \
  -H "Content-Type: application/json" \
  -d '{"linearX": 0.0, "angularZ": -0.5}'

# 정지
curl -X POST http://localhost:8080/api/robot/control \
  -H "Content-Type: application/json" \
  -d '{"linearX": 0.0, "angularZ": 0.0}'
```

## 프로젝트 구조

```
src/main/java/com/gae/server/
├── api/
│   ├── auth/           # 인증 (로그인, 회원가입)
│   ├── member/         # 회원 관리
│   ├── robot/          # 로봇 관리 & 제어
│   │   └── dto/
│   │       ├── ros/    # ROS 메시지 DTO
│   │       │   ├── Vector3.java
│   │       │   ├── Twist.java
│   │       │   └── RosMessage.java
│   │       ├── VelocityRequest.java
│   │       └── ...
│   └── mqtt/           # MQTT 통신
│       ├── MqttGateway.java
│       └── MqttService.java
├── domain/
│   ├── member/         # Member 엔티티
│   └── robot/          # Robot 엔티티
└── global/
    ├── config/         # 설정 (Security, MQTT, WebSocket)
    ├── jwt/            # JWT 토큰 처리
    └── auth/           # 인증 관련
```

## MQTT 토픽

### Subscribe (로봇 → 서버)

| 토픽 | 설명 |
|------|------|
| `robot/status` | 로봇 상태 |
| `robot/pose` | 로봇 위치 |
| `robot/map` | 지도 데이터 |

### Publish (서버 → 로봇)

| 토픽 | 설명 |
|------|------|
| `robot/cmd/vel` | 속도 제어 (Rosbridge) |
| `robot/cmd/move` | 이동 명령 (home, stop) |
| `robot/cmd/nav` | 좌표 이동 |

## 환경 설정

### application.yml

```yaml
mqtt:
  broker:
    url: tcp://localhost:1883
  client:
    id: spring-server
  qos: 1
```

### 프로필

- `dev`: 로컬 개발 환경
- `docker`: Docker 환경
- `prod`: 프로덕션 환경
