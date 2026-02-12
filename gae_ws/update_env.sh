#!/bin/bash
echo "🚧 환경 동기화 중..."

# 1. 시스템 패키지 설치
# - portaudio19-dev: PyAudio 빌드 의존성
# - ros-humble-camera-info-manager: 카메라 캘리브레이션
# - pulseaudio-utils: 마이크 장치 확인 (pactl)
# - sox, libsox-fmt-all: 오디오 재생 및 포맷 변환
echo "Installing system dependencies..."
apt-get update && apt-get install -y \
    portaudio19-dev \
    ros-humble-camera-info-manager \
    pulseaudio-utils \
    sox \
    libsox-fmt-all \
    libasound2-plugins

# 2. 파이썬 의존성 설치
echo "Installing Python libraries..."
pip install -r "$(dirname "$0")/requirements.txt" --index-url https://pypi.org/simple

echo "✅ 환경 설정 완료! (카메라, 음성, 오디오 도구 설치됨)"