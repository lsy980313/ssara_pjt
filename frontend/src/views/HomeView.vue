<template>
  <div class="home-page">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-content">
        <div class="header-left">
          <span class="greeting">안녕하세요 👋</span>
          <h1 class="title">우리 가족 돌봄</h1>
        </div>
        <button class="profile-btn" @click="$router.push('/profile')" title="내정보">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- 메인 콘텐츠 -->
    <main class="content">
      <!-- 로봇 상태 카드 (컴팩트) -->
      <section class="status-card" :class="{ offline: !isOnline }" @click="$router.push('/battery')" style="cursor: pointer;">
        <div class="status-row">
          <div class="robot-avatar">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
              <line x1="9" y1="9" x2="9.01" y2="9"/>
              <line x1="15" y1="9" x2="15.01" y2="9"/>
            </svg>
          </div>
          <div class="robot-info">
            <span class="robot-name">SSARA</span>
            <span class="status-dot" :class="{ online: isOnline }"></span>
          </div>
          <div class="battery-value" :class="batteryClass">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="1" y="6" width="18" height="12" rx="2" ry="2"/>
              <line x1="23" y1="13" x2="23" y2="11"/>
            </svg>
            <span>{{ currentBattery }}%</span>
          </div>
          <svg class="battery-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </div>
        <div class="battery-bar">
          <div class="battery-fill" :class="batteryClass" :style="{ width: currentBattery + '%' }"></div>
        </div>
      </section>

      <!-- 퀵 액션 버튼 -->
      <section class="quick-actions">
        <button class="quick-action-btn" @click="$router.push('/screen')">
          <div class="action-icon camera">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
          </div>
          <span>카메라 상세보기</span>
        </button>
        <button class="quick-action-btn" @click="$router.push('/navigation')">
          <div class="action-icon location">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>
            </svg>
          </div>
          <span>위치간 이동</span>
        </button>
        <button class="quick-action-btn" @click="$router.push('/records')">
          <div class="action-icon history">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
          </div>
          <span>핵심기록 확인</span>
        </button>
      </section>

      <!-- 로봇 화면 스트리밍 -->
      <section class="screen-section">
        <div class="section-header">
          <div class="section-title-wrap">
            <h3 class="section-title">로봇 카메라</h3>
          </div>
        </div>
        <div class="stream-container">
          <img
            :src="streamUrl"
            alt="로봇 카메라 화면"
            class="stream-image"
            @error="handleStreamError"
          />
        </div>
      </section>

      <!-- 전체화면 스트리밍 오버레이 -->
      <Teleport to="body">
        <div v-if="isFullscreenOpen" class="fullscreen-overlay" @click="toggleFullscreenControls">
          <div class="fullscreen-stream">
            <img
              ref="fullscreenImageRef"
              :src="fullscreenStreamUrl"
              alt="로봇 카메라 전체화면"
              class="fullscreen-image"
              crossorigin="anonymous"
            />
          </div>

          <!-- 녹화 중 표시 -->
          <div v-if="isRecording" class="recording-indicator">
            <span class="rec-dot"></span>
            <span class="rec-text">REC</span>
            <span class="rec-time">{{ recordingTime }}</span>
          </div>

          <!-- 상단 컨트롤 -->
          <div class="fs-top-controls" :class="{ visible: showFsControls }" @click.stop>
            <button class="fs-close-btn" @click="closeFullscreenStream">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
            <div class="fs-live-badge">
              <span class="fs-live-dot"></span>
              LIVE
            </div>
            <div class="fs-battery" :class="batteryClass">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="1" y="6" width="18" height="12" rx="2" ry="2"/>
                <line x1="23" y1="13" x2="23" y2="11"/>
              </svg>
              <span>{{ currentBattery }}%</span>
            </div>
          </div>

          <!-- 하단 컨트롤 -->
          <div class="fs-bottom-controls" :class="{ visible: showFsControls }" @click.stop>
            <div class="fs-control-buttons">
              <!-- 사진 촬영 -->
              <button class="fs-control-btn" @click="capturePhoto">
                <div class="control-icon-wrap photo">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                    <circle cx="12" cy="13" r="4"/>
                  </svg>
                </div>
                <span>사진</span>
              </button>

              <!-- 동영상 녹화 -->
              <button class="fs-control-btn record-btn" :class="{ recording: isRecording }" @click="toggleRecording">
                <div class="control-icon-wrap video" :class="{ recording: isRecording }">
                  <svg v-if="!isRecording" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="23 7 16 12 23 17 23 7"/>
                    <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                  </svg>
                  <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="6" y="6" width="12" height="12" rx="2"/>
                  </svg>
                </div>
                <span>{{ isRecording ? '중지' : '녹화' }}</span>
              </button>

              <!-- 기록 보기 -->
              <button class="fs-control-btn" @click="goToRecords">
                <div class="control-icon-wrap gallery">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <polyline points="21 15 16 10 5 21"/>
                  </svg>
                </div>
                <span>기록</span>
              </button>
            </div>
            <p class="fs-hint-text">화면을 탭하여 컨트롤 표시/숨김</p>
          </div>

          <!-- 캡처 플래시 효과 -->
          <div v-if="showCaptureFlash" class="capture-flash"></div>

          <!-- 저장 완료 토스트 -->
          <div v-if="showSaveToast" class="save-toast">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span>{{ saveToastMessage }}</span>
          </div>
        </div>
      </Teleport>

      <!-- 지도 영역 -->
      <section class="map-section">
        <div class="section-header">
          <div class="section-title-wrap">
            <span class="section-badge location">GPS</span>
            <h3 class="section-title">현재 위치</h3>
          </div>
          <span class="location-text">{{ currentLocationText }}</span>
        </div>
        <div class="map-container" ref="mapContainer">
          <!-- VSLAM 그리드 맵 -->
          <div v-show="mapMode === 'vslam'" class="grid-map">
            <canvas ref="mapCanvas" class="map-canvas"></canvas>
            <div class="robot-marker" :style="robotMarkerStyle">
              <div class="robot-dot"></div>
              <div class="robot-direction" :style="robotDirectionStyle"></div>
            </div>
            <!-- VSLAM 연결 상태 표시 -->
            <div class="vslam-status" :class="{ connected: robotStore.vslamConnected }">
              <span class="vslam-dot"></span>
              <span>{{ robotStore.vslamConnected ? 'VSLAM 연결됨' : 'VSLAM 연결 중...' }}</span>
            </div>
            <!-- 좌표 표시 -->
            <div class="coord-display">
              X: {{ robotStore.robotPose.x.toFixed(2) }}m,
              Y: {{ robotStore.robotPose.y.toFixed(2) }}m,
              θ: {{ (robotStore.robotPose.theta * 180 / Math.PI).toFixed(0) }}°
            </div>
          </div>
          <!-- 카카오맵 -->
          <div v-show="mapMode === 'kakao'" ref="kakaoMapRef" class="kakao-map">
            <div v-if="!isKakaoMapReady" class="map-loading">
              <div class="loading-spinner"></div>
              <span>카카오맵 로딩중...</span>
            </div>
          </div>
          <!-- 맵 모드 토글 -->
          <div class="map-toggle">
            <button
              class="toggle-btn"
              :class="{ active: mapMode === 'vslam' }"
              @click="mapMode = 'vslam'"
            >
              VSLAM
            </button>
            <button
              class="toggle-btn"
              :class="{ active: mapMode === 'kakao' }"
              @click="switchToKakao"
            >
              카카오맵
            </button>
            <button class="sync-btn" @click="syncKakaoMapPosition" title="위치 동기화">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
            </button>
          </div>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 하단 네비게이션 -->
    <nav class="bottom-nav">
      <button class="nav-item active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>홈</span>
      </button>
      <button class="nav-item" @click="$router.push('/features')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <rect x="3" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="14" width="7" height="7" rx="1.5"/>
          <rect x="3" y="14" width="7" height="7" rx="1.5"/>
        </svg>
        <span>기능</span>
      </button>
      <button class="nav-item" @click="$router.push('/history')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        <span>기록</span>
      </button>
      <button class="nav-item" @click="$router.push('/help')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="12" cy="12" r="10"/>
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <span>도움말</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { robotState } from '../store.js';
import { useAuthStore } from '../stores/authStore';
import { useRobotStore } from '@/stores/robotStore';
import { useRecordsStore } from '@/stores/recordsStore';
import { activityApi } from '@/api';

const router = useRouter();
const authStore = useAuthStore();
const robotStore = useRobotStore();
const recordsStore = useRecordsStore();

// ==================== 로봇 화면 스트리밍 ====================
// 프록시를 통해 CORS 우회 (캡처 기능 지원)
const ROBOT_STREAM_URL = '/robot-stream/stream?topic=/camera/color/image_raw&type=mjpeg&width=560&height=315';
const ROBOT_STREAM_URL_HD = '/robot-stream/stream?topic=/camera/color/image_raw&type=mjpeg&width=1280&height=720';
const streamUrl = ref(ROBOT_STREAM_URL);
const fullscreenStreamUrl = ref(ROBOT_STREAM_URL_HD);

const handleStreamError = () => {
  console.log('스트림 연결 실패');
};

// ==================== 전체화면 스트리밍 ====================
const isFullscreenOpen = ref(false);
const showFsControls = ref(true);
const fullscreenImageRef = ref(null);
let fsControlTimeout = null;

// 사진/동영상 촬영 관련
const isRecording = ref(false);
const recordingTime = ref('00:00');
const showCaptureFlash = ref(false);
const showSaveToast = ref(false);
const saveToastMessage = ref('');
let recordingSeconds = 0;
let homeTimeInterval = null;
let homeMediaRecorder = null;
let homeRecordedChunks = [];
let homeRecordCanvas = null;
let homeRecordCtx = null;
let homeDrawFrameInterval = null;

const openFullscreenStream = async () => {
  isFullscreenOpen.value = true;
  showFsControls.value = true;
  resetFsControlTimeout();

  // 전체화면 + 가로모드 시도
  await nextTick();
  try {
    await document.documentElement.requestFullscreen();
    if (screen.orientation && screen.orientation.lock) {
      try {
        await screen.orientation.lock('landscape');
      } catch (e) {
        console.log('화면 회전 잠금 불가:', e);
      }
    }
  } catch (e) {
    console.log('전체화면 불가:', e);
  }
};

const closeFullscreenStream = async () => {
  isFullscreenOpen.value = false;
  if (fsControlTimeout) {
    clearTimeout(fsControlTimeout);
  }

  // 전체화면 해제
  if (document.fullscreenElement) {
    await document.exitFullscreen();
  }
  if (screen.orientation && screen.orientation.unlock) {
    screen.orientation.unlock();
  }
};

const toggleFullscreenControls = () => {
  showFsControls.value = !showFsControls.value;
  resetFsControlTimeout();
};

const resetFsControlTimeout = () => {
  if (fsControlTimeout) {
    clearTimeout(fsControlTimeout);
  }
  if (showFsControls.value) {
    fsControlTimeout = setTimeout(() => {
      showFsControls.value = false;
    }, 4000);
  }
};

// ESC 키로 전체화면 닫기 감지
const handleFullscreenChange = () => {
  if (!document.fullscreenElement && isFullscreenOpen.value) {
    isFullscreenOpen.value = false;
    if (fsControlTimeout) {
      clearTimeout(fsControlTimeout);
    }
    // 녹화 중이면 중지
    if (isRecording.value) {
      stopRecording();
    }
  }
};

// 사진 촬영
const capturePhoto = async () => {
  const img = fullscreenImageRef.value;
  if (!img) return;

  // 플래시 효과
  showCaptureFlash.value = true;
  setTimeout(() => {
    showCaptureFlash.value = false;
  }, 200);

  try {
    // 캔버스에 이미지 그리기
    const canvas = document.createElement('canvas');
    canvas.width = img.naturalWidth || 1280;
    canvas.height = img.naturalHeight || 720;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    // DataURL로 변환
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9);

    // 기록에 저장
    recordsStore.addPhoto(dataUrl);

    // 토스트 메시지
    showToast('사진이 기록에 저장되었습니다');
  } catch (error) {
    console.error('사진 촬영 실패:', error);
    showToast('사진 저장에 실패했습니다');
  }
};

// 녹화 시작/중지
const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording();
  } else {
    startRecording();
  }
};

// 녹화 시작 (MediaRecorder → WebM)
const startRecording = () => {
  const img = fullscreenImageRef.value;
  if (!img) {
    showToast('카메라 스트림이 없습니다');
    return;
  }

  homeRecordCanvas = document.createElement('canvas');
  homeRecordCanvas.width = 640;
  homeRecordCanvas.height = 360;
  homeRecordCtx = homeRecordCanvas.getContext('2d');

  try {
    homeRecordCtx.drawImage(img, 0, 0, homeRecordCanvas.width, homeRecordCanvas.height);
  } catch (e) { /* ignore */ }

  const canvasStream = homeRecordCanvas.captureStream(10);
  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
    ? 'video/webm;codecs=vp9'
    : MediaRecorder.isTypeSupported('video/webm;codecs=vp8')
      ? 'video/webm;codecs=vp8'
      : 'video/webm';

  homeRecordedChunks = [];
  homeMediaRecorder = new MediaRecorder(canvasStream, {
    mimeType,
    videoBitsPerSecond: 1000000
  });

  homeMediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) homeRecordedChunks.push(e.data);
  };

  homeMediaRecorder.onstop = () => {
    const blob = new Blob(homeRecordedChunks, { type: mimeType });
    const mins = Math.floor(recordingSeconds / 60);
    const secs = recordingSeconds % 60;
    const durationStr = mins > 0 ? `${mins}:${String(secs).padStart(2, '0')}` : `0:${String(secs).padStart(2, '0')}`;

    let thumbnail = '';
    try {
      const tc = document.createElement('canvas');
      tc.width = 320; tc.height = 180;
      tc.getContext('2d').drawImage(img, 0, 0, 320, 180);
      thumbnail = tc.toDataURL('image/jpeg', 0.7);
    } catch (e) { /* ignore */ }

    recordsStore.addVideo(blob, durationStr, '', thumbnail);
    showToast(`${recordingSeconds}초 녹화가 기록에 저장되었습니다`);
    homeRecordedChunks = [];
    recordingSeconds = 0;
    recordingTime.value = '00:00';
  };

  homeMediaRecorder.start(1000);
  isRecording.value = true;
  recordingSeconds = 0;
  updateRecordingTime();

  homeDrawFrameInterval = setInterval(() => {
    try {
      if (img.complete && img.naturalWidth > 0) {
        homeRecordCtx.drawImage(img, 0, 0, homeRecordCanvas.width, homeRecordCanvas.height);
      }
    } catch (e) { /* ignore */ }
  }, 100);

  homeTimeInterval = setInterval(() => {
    recordingSeconds++;
    updateRecordingTime();
  }, 1000);

  showToast('녹화가 시작되었습니다');
};

// 녹화 중지
const stopRecording = () => {
  isRecording.value = false;
  if (homeDrawFrameInterval) { clearInterval(homeDrawFrameInterval); homeDrawFrameInterval = null; }
  if (homeTimeInterval) { clearInterval(homeTimeInterval); homeTimeInterval = null; }
  if (homeMediaRecorder && homeMediaRecorder.state !== 'inactive') {
    homeMediaRecorder.stop();
  }
};

// 녹화 시간 업데이트
const updateRecordingTime = () => {
  const mins = Math.floor(recordingSeconds / 60);
  const secs = recordingSeconds % 60;
  recordingTime.value = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
};

// 토스트 메시지 표시
const showToast = (message) => {
  saveToastMessage.value = message;
  showSaveToast.value = true;
  setTimeout(() => {
    showSaveToast.value = false;
  }, 2500);
};

// 기록 페이지로 이동
const goToRecords = () => {
  closeFullscreenStream();
  router.push('/records');
};

// ==================== 지도 관련 ====================
const mapContainer = ref(null);
const mapCanvas = ref(null);
const kakaoMapRef = ref(null);
const isKakaoMapReady = ref(false);
const mapMode = ref('vslam');

let kakaoMap = null;
let robotMarkerKakao = null;

// VSLAM 좌표 설정
const coordConfig = reactive({
  originLat: 35.20527,
  originLng: 126.8117,
  heading: 0
});

const METERS_PER_LAT = 0.000009;
const METERS_PER_LNG = 0.000011;

const vslamToGps = (x, y) => {
  const headingRad = (coordConfig.heading * Math.PI) / 180;
  const cosH = Math.cos(headingRad);
  const sinH = Math.sin(headingRad);
  const rotatedX = x * cosH - y * sinH;
  const rotatedY = x * sinH + y * cosH;
  const lat = coordConfig.originLat + rotatedY * METERS_PER_LAT;
  const lng = coordConfig.originLng + rotatedX * METERS_PER_LNG;
  return { lat, lng };
};

const gpsCoord = computed(() => {
  const x = robotStore.robotPose.x || 0;
  const y = robotStore.robotPose.y || 0;
  return vslamToGps(x, y);
});

const mapConfig = { minX: -5, maxX: 5, minY: -5, maxY: 5, gridSize: 1 };

const drawGrid = () => {
  const canvas = mapCanvas.value;
  const container = mapContainer.value;
  if (!canvas || !container) return;

  canvas.width = container.offsetWidth;
  canvas.height = container.offsetHeight;
  const ctx = canvas.getContext('2d');
  const { width, height } = canvas;

  ctx.fillStyle = '#f8f9fa';
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = '#e9ecef';
  ctx.lineWidth = 1;
  const rangeX = mapConfig.maxX - mapConfig.minX;
  const rangeY = mapConfig.maxY - mapConfig.minY;
  const scaleX = width / rangeX;
  const scaleY = height / rangeY;

  for (let x = mapConfig.minX; x <= mapConfig.maxX; x += mapConfig.gridSize) {
    const px = (x - mapConfig.minX) * scaleX;
    ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, height); ctx.stroke();
  }
  for (let y = mapConfig.minY; y <= mapConfig.maxY; y += mapConfig.gridSize) {
    const py = height - (y - mapConfig.minY) * scaleY;
    ctx.beginPath(); ctx.moveTo(0, py); ctx.lineTo(width, py); ctx.stroke();
  }

  ctx.strokeStyle = '#adb5bd';
  ctx.lineWidth = 2;
  const originX = (0 - mapConfig.minX) * scaleX;
  const originY = height - (0 - mapConfig.minY) * scaleY;
  ctx.beginPath(); ctx.moveTo(0, originY); ctx.lineTo(width, originY); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(originX, 0); ctx.lineTo(originX, height); ctx.stroke();
};

const robotMarkerStyle = computed(() => {
  const container = mapContainer.value;
  if (!container) return { display: 'none' };
  const { offsetWidth: width, offsetHeight: height } = container;
  const rangeX = mapConfig.maxX - mapConfig.minX;
  const rangeY = mapConfig.maxY - mapConfig.minY;
  const x = robotStore.robotPose.x || 0;
  const y = robotStore.robotPose.y || 0;
  const px = ((x - mapConfig.minX) / rangeX) * width;
  const py = height - ((y - mapConfig.minY) / rangeY) * height;
  return { left: `${px}px`, top: `${py}px`, transform: 'translate(-50%, -50%)' };
});

// 로봇 방향 화살표 스타일 (theta 라디안 → CSS rotate)
const robotDirectionStyle = computed(() => {
  // theta: 라디안, 반시계 방향이 양수
  // CSS rotate: 시계 방향이 양수, 위쪽이 0도
  // 변환: -theta (라디안→도) - 90도 (위쪽 기준)
  const theta = robotStore.robotPose.theta || 0;
  const degrees = -(theta * 180 / Math.PI) + 90;
  return { transform: `rotate(${degrees}deg)` };
});

const switchToKakao = () => {
  mapMode.value = 'kakao';
  nextTick(() => {
    if (!isKakaoMapReady.value) {
      initKakaoMap();
    } else if (kakaoMap) {
      kakaoMap.relayout();
    }
  });
};

// 주소 정보 저장
const currentAddress = ref('위치 확인 중...');
let geocoder = null;

const loadKakaoMapSdk = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps && window.kakao.maps.services) {
      resolve();
      return;
    }
    const apiKey = import.meta.env.VITE_KAKAO_MAP_API_KEY;
    if (!apiKey || apiKey === '<your-kakao-javascript-key>') {
      reject(new Error('카카오맵 API 키가 .env 파일에 설정되지 않았습니다.'));
      return;
    }
    const script = document.createElement('script');
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&libraries=services&autoload=false`;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('카카오맵 SDK 로드 실패'));
    document.head.appendChild(script);
  });
};

// 역지오코딩: 좌표 → 주소 변환
const reverseGeocode = (lat, lng) => {
  if (!geocoder) {
    if (window.kakao && window.kakao.maps && window.kakao.maps.services) {
      geocoder = new window.kakao.maps.services.Geocoder();
    } else {
      return;
    }
  }

  const coord = new window.kakao.maps.LatLng(lat, lng);

  geocoder.coord2Address(coord.getLng(), coord.getLat(), (result, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      const address = result[0];
      if (address.road_address) {
        // 도로명 주소가 있는 경우
        const road = address.road_address;
        currentAddress.value = `${road.region_2depth_name} ${road.road_name} 근처`;
      } else if (address.address) {
        // 지번 주소
        const jibun = address.address;
        currentAddress.value = `${jibun.region_2depth_name} ${jibun.region_3depth_name} 근처`;
      }
    } else {
      currentAddress.value = '주소를 찾을 수 없음';
    }
  });
};

const initKakaoMap = async () => {
  try {
    await loadKakaoMapSdk();
    if (typeof window.kakao === 'undefined' || !window.kakao.maps) return;
    window.kakao.maps.load(() => {
      createKakaoMap();
    });
  } catch (error) {
    console.error('카카오맵 초기화 실패:', error.message);
  }
};

const createKakaoMap = () => {
  const container = kakaoMapRef.value;
  if (!container) return;

  try {
    const options = {
      center: new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng),
      level: 2,
      draggable: true
    };
    kakaoMap = new window.kakao.maps.Map(container, options);
    const zoomControl = new window.kakao.maps.ZoomControl();
    kakaoMap.addControl(zoomControl, window.kakao.maps.ControlPosition.RIGHT);

    const markerContent = `
      <div style="width: 20px; height: 20px; background: #3b82f6; border: 3px solid white; border-radius: 50%; box-shadow: 0 2px 6px rgba(0,0,0,0.3);"></div>
    `;
    robotMarkerKakao = new window.kakao.maps.CustomOverlay({
      position: new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng),
      content: markerContent,
      yAnchor: 0.5,
      xAnchor: 0.5
    });
    robotMarkerKakao.setMap(kakaoMap);
    isKakaoMapReady.value = true;

    // Geocoder 초기화 및 초기 주소 조회
    geocoder = new window.kakao.maps.services.Geocoder();
    reverseGeocode(coordConfig.originLat, coordConfig.originLng);

    setTimeout(() => {
      kakaoMap.relayout();
      kakaoMap.setCenter(new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng));
    }, 100);
  } catch (error) {
    console.error('카카오맵 생성 오류:', error);
  }
};

const syncKakaoMapPosition = () => {
  if (!kakaoMap || !robotMarkerKakao) return;
  kakaoMap.relayout();
  const { lat, lng } = gpsCoord.value;
  const position = new window.kakao.maps.LatLng(lat, lng);
  robotMarkerKakao.setPosition(position);
  kakaoMap.setCenter(position);
};

const currentLocationText = computed(() => {
  return currentAddress.value;
});

// 좌표 변경 시 주소 업데이트
watch(gpsCoord, (newCoord) => {
  if (geocoder && newCoord.lat && newCoord.lng) {
    reverseGeocode(newCoord.lat, newCoord.lng);
  }
}, { deep: true });

// ==================== 기존 상태 ====================
const apiSummary = ref({ walkTime: 0, alerts: 0 });
const apiLogs = ref([]);

const todaySummary = computed(() => ({
  walkTime: robotStore.dailySummary.walkTime || apiSummary.value.walkTime || 0,
  alerts: robotStore.dailySummary.alerts || apiSummary.value.alerts || 0
}));

const loading = ref(true);

onMounted(async () => {
  await robotState.fetchRobot();
  try {
    const summaryRes = await activityApi.getTodaySummary();
    apiSummary.value = {
      walkTime: summaryRes.data.walkTime || 0,
      alerts: summaryRes.data.alerts || 0
    };
  } catch (e) {
    console.error('요약 정보 로드 실패:', e);
  }
  try {
    const logsRes = await activityApi.getTodayLogs();
    apiLogs.value = logsRes.data.slice(0, 4);
  } catch (e) {
    console.error('활동 로그 로드 실패:', e);
  }
  robotStore.connectWebSocket();
  loading.value = false;

  nextTick(() => {
    drawGrid();
    window.addEventListener('resize', drawGrid);
    document.addEventListener('fullscreenchange', handleFullscreenChange);
  });

  // 카카오맵 SDK 로드 후 초기 주소 조회
  try {
    await loadKakaoMapSdk();
    window.kakao.maps.load(() => {
      geocoder = new window.kakao.maps.services.Geocoder();
      reverseGeocode(coordConfig.originLat, coordConfig.originLng);
    });
  } catch (e) {
    console.log('주소 조회 실패:', e);
    currentAddress.value = '주소 조회 불가';
  }
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
  window.removeEventListener('resize', drawGrid);
  document.removeEventListener('fullscreenchange', handleFullscreenChange);
  if (fsControlTimeout) {
    clearTimeout(fsControlTimeout);
  }
});

const currentBattery = computed(() => {
  return robotStore.robotStatus.battery || robotState.battery;
});

const currentLocation = computed(() => {
  if (robotStore.robotPose.x || robotStore.robotPose.y) {
    return `(${robotStore.robotPose.x.toFixed(1)}, ${robotStore.robotPose.y.toFixed(1)})`;
  }
  return robotState.location || '위치 정보 없음';
});

const isOnline = computed(() => {
  return robotStore.robotStatus.isOnline || robotState.status === 'ONLINE';
});

const batteryClass = computed(() => {
  if (currentBattery.value <= 20) return 'low';
  if (currentBattery.value <= 50) return 'medium';
  return 'high';
});

const batteryStatusText = computed(() => {
  if (currentBattery.value <= 20) return '충전 필요';
  if (currentBattery.value <= 50) return '보통';
  return '충분';
});

const displayLogs = computed(() => {
  const wsLogs = robotStore.activityLogs || [];
  const dbLogs = apiLogs.value || [];
  return [...wsLogs, ...dbLogs].slice(0, 4);
});

const handleLogout = () => {
  authStore.logout();
  router.push('/');
};
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f2f4f6;
  color: #191f28;
  padding-bottom: 80px;
}

/* 헤더 */
.header {
  background: linear-gradient(180deg, #fff 0%, #f8f9fa 100%);
  padding: 16px 20px 14px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.greeting {
  font-size: 14px;
  font-weight: 500;
  color: #8b95a1;
  letter-spacing: -0.01em;
}

.title {
  font-size: 22px;
  font-weight: 800;
  color: #191f28;
  letter-spacing: -0.02em;
}

.profile-btn {
  width: 36px;
  height: 36px;
  border-radius: 11px;
  margin-top: 16px;
  background: #fff;
  border: 1px solid #e5e8eb;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8b95a1;
  transition: all 0.2s ease;
}

.profile-btn:hover {
  color: #3182f6;
  border-color: #bfdbfe;
  background: #eff6ff;
}

/* 메인 콘텐츠 */
.content {
  padding: 0 16px;
  overflow-x: hidden;
}

/* 상태 카드 (컴팩트) */
.status-card {
  position: relative;
  background: #fff;
  border-radius: 16px;
  padding: 14px 16px;
  margin-top: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  transition: all 0.3s ease;
}

.status-card:active {
  transform: scale(0.98);
}

.status-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.robot-avatar {
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, #3182f6 0%, #5BA0F5 100%);
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(49, 130, 246, 0.25);
}

.robot-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.robot-name {
  font-size: 15px;
  font-weight: 700;
  color: #191f28;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.02em;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #b0b8c1;
  flex-shrink: 0;
}

.status-dot.online {
  background: #20c997;
  box-shadow: 0 0 0 3px rgba(32, 201, 151, 0.2);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(32, 201, 151, 0.2); }
  50% { box-shadow: 0 0 0 6px rgba(32, 201, 151, 0.1); }
}

.battery-value {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: -0.02em;
  flex-shrink: 0;
}

.battery-value.high { color: #20c997; }
.battery-value.medium { color: #F59E0B; }
.battery-value.low { color: #EF4444; }

.battery-arrow {
  color: #b0b8c1;
  flex-shrink: 0;
}

.battery-bar {
  width: 100%;
  height: 5px;
  background: #e5e8eb;
  border-radius: 3px;
  overflow: hidden;
}

.battery-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.battery-fill.high { background: linear-gradient(90deg, #20c997, #38d9a9); }
.battery-fill.medium { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
.battery-fill.low { background: linear-gradient(90deg, #EF4444, #F87171); }

/* 퀵 액션 버튼 */
.quick-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.quick-action-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.quick-action-btn:active {
  transform: scale(0.97);
}

.action-icon {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.action-icon svg {
  width: 18px;
  height: 18px;
}

.action-icon.camera {
  background: linear-gradient(135deg, #3182f6 0%, #5BA0F5 100%);
}

.action-icon.location {
  background: linear-gradient(135deg, #20c997 0%, #38d9a9 100%);
}

.action-icon.history {
  background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);
}

.quick-action-btn span {
  font-size: 11px;
  font-weight: 600;
  color: #4e5968;
  letter-spacing: -0.02em;
  text-align: center;
  word-break: keep-all;
}

/* 로봇 화면 스트리밍 섹션 */
.screen-section {
  margin-top: 10px;
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-badge {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1px;
  padding: 3px 7px;
  border-radius: 5px;
  color: #fff;
}

.section-badge.live {
  background: #ef4444;
}

.section-badge.location {
  background: #20c997;
}

.section-title {
  font-size: 15px;
  font-weight: 700;
  color: #191f28;
  letter-spacing: -0.02em;
}

.stream-container {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  background: #191f28;
  border-radius: 12px;
  overflow: hidden;
}

.stream-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.stream-overlay {
  position: absolute;
  top: 12px;
  left: 12px;
  pointer-events: none;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  background: rgba(239, 68, 68, 0.9);
  backdrop-filter: blur(8px);
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.live-dot {
  width: 6px;
  height: 6px;
  background: #fff;
  border-radius: 50%;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 50%, 100% { opacity: 1; }
  25%, 75% { opacity: 0.4; }
}

/* 지도 섹션 */
.map-section {
  margin-top: 10px;
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.map-container {
  height: 240px;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  background: #f8f9fa;
}

.grid-map {
  width: 100%;
  height: 100%;
  position: relative;
}

.map-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.robot-marker {
  position: absolute;
  z-index: 10;
  pointer-events: none;
}

.robot-dot {
  width: 14px;
  height: 14px;
  background: #3182f6;
  border: 3px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(49, 130, 246, 0.4);
}

.robot-direction {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 18px solid #3182f6;
  transform-origin: center bottom;
  margin-left: -6px;
  margin-top: -18px;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
}

.vslam-status {
  position: absolute;
  bottom: 8px;
  left: 8px;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  color: #8b95a1;
  box-shadow: 0 1px 6px rgba(0,0,0,0.08);
}

.vslam-status.connected {
  color: #20c997;
}

.vslam-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #b0b8c1;
}

.vslam-status.connected .vslam-dot {
  background: #20c997;
  box-shadow: 0 0 0 3px rgba(32, 201, 151, 0.2);
  animation: pulse 2s infinite;
}

.coord-display {
  position: absolute;
  bottom: 8px;
  right: 8px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  color: #4e5968;
  font-variant-numeric: tabular-nums;
  box-shadow: 0 1px 6px rgba(0,0,0,0.08);
}

.kakao-map {
  width: 100%;
  height: 100%;
}

.map-loading {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: #f8f9fa;
  color: #8b95a1;
  font-size: 13px;
  font-weight: 500;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e8eb;
  border-top-color: #3182f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.map-toggle {
  position: absolute;
  top: 8px;
  left: 8px;
  display: flex;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 8px;
  padding: 3px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 20;
}

.toggle-btn {
  padding: 4px 10px;
  font-size: 10px;
  font-weight: 600;
  color: #8b95a1;
  border-radius: 6px;
  transition: all 0.2s ease;
  letter-spacing: -0.01em;
}

.toggle-btn.active {
  background: #3182f6;
  color: white;
}

.sync-btn {
  margin-left: 3px;
  padding: 4px 8px;
  background: #20c997;
  color: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.sync-btn:active {
  transform: scale(0.95);
}

.sync-btn svg {
  width: 12px;
  height: 12px;
}

.location-text {
  font-size: 12px;
  font-weight: 600;
  color: #8b95a1;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bottom-spacer {
  height: 20px;
}

/* 하단 네비게이션 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-width: 600px;
  margin: 0 auto;
  height: 64px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 8px;
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex: 1 1 0%;
  width: 100%;
  min-width: 0;
  padding: 8px 0;
  color: #b0b8c1;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.nav-item:hover {
  color: #6b7684;
}

.nav-item svg {
  width: 22px;
  height: 22px;
}

.nav-item span {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.nav-item.active {
  color: #3182f6;
}

/* 전체화면 오버레이 */
.fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #000;
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fullscreen-stream {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fullscreen-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.fs-top-controls {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  padding-top: max(16px, env(safe-area-inset-top));
  background: linear-gradient(to bottom, rgba(0,0,0,0.7), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.fs-top-controls.visible {
  opacity: 1;
  pointer-events: auto;
}

.fs-close-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  transition: background 0.2s;
}

.fs-close-btn:hover {
  background: rgba(255,255,255,0.25);
}

.fs-live-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(239, 68, 68, 0.9);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.fs-live-dot {
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  animation: blink 1.5s infinite;
}

.fs-battery {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.fs-battery.high { color: #34d399; }
.fs-battery.medium { color: #fbbf24; }
.fs-battery.low { color: #f87171; }

/* 녹화 중 표시 */
.recording-indicator {
  position: absolute;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.9);
  border-radius: 20px;
  z-index: 10;
}

.rec-dot {
  width: 10px;
  height: 10px;
  background: #fff;
  border-radius: 50%;
  animation: recBlink 1s infinite;
}

@keyframes recBlink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}

.rec-text {
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.rec-time {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  font-variant-numeric: tabular-nums;
}

/* 하단 컨트롤 */
.fs-bottom-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  padding-bottom: max(24px, env(safe-area-inset-bottom));
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.fs-bottom-controls.visible {
  opacity: 1;
  pointer-events: auto;
}

.fs-control-buttons {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 16px;
}

.fs-control-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #fff;
}

.control-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.control-icon-wrap.photo {
  background: rgba(255,255,255,0.25);
}

.control-icon-wrap.video {
  background: rgba(239, 68, 68, 0.8);
}

.control-icon-wrap.video.recording {
  background: rgba(239, 68, 68, 1);
  animation: recordPulse 1s infinite;
}

@keyframes recordPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.control-icon-wrap.gallery {
  background: rgba(255,255,255,0.25);
}

.fs-control-btn:hover .control-icon-wrap {
  transform: scale(1.05);
}

.fs-control-btn:active .control-icon-wrap {
  transform: scale(0.95);
}

.fs-control-btn span {
  font-size: 12px;
  font-weight: 600;
}

.fs-hint-text {
  text-align: center;
  font-size: 12px;
  color: rgba(255,255,255,0.5);
}

/* 캡처 플래시 효과 */
.capture-flash {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #fff;
  animation: flash 0.2s ease-out;
  pointer-events: none;
  z-index: 100;
}

@keyframes flash {
  0% { opacity: 0.8; }
  100% { opacity: 0; }
}

/* 저장 완료 토스트 */
.save-toast {
  position: absolute;
  bottom: 140px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(32, 201, 151, 0.95);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  animation: toastIn 0.3s ease;
  z-index: 101;
}

@keyframes toastIn {
  0% { opacity: 0; transform: translate(-50%, 20px); }
  100% { opacity: 1; transform: translate(-50%, 0); }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .status-card,
  .action-card,
  .battery-fill,
  .quick-btn.healthcare,
  .expand-btn,
  .toggle-btn,
  .sync-btn {
    transition: none;
  }

  .status-dot.online,
  .live-dot,
  .loading-spinner {
    animation: none;
  }
}

/* Mobile Responsive */
@media (max-width: 380px) {
  .title {
    font-size: 22px;
  }
}
</style>
