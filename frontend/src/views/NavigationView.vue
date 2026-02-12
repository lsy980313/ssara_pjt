<template>
  <div class="navigation-view">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <h1 class="header-title">위치간 이동</h1>
      <button class="reset-btn" @click="resetNavigation" v-if="startPoint || endPoint">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 4 23 10 17 10"/>
          <polyline points="1 20 1 14 7 14"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
      </button>
      <div v-else class="header-spacer"></div>
    </header>

    <main class="content">
      <!-- 경로 설정 카드 -->
      <section class="route-card">
        <div class="route-item" @click="selectingPoint = 'start'">
          <div class="route-icon start">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="8"/>
            </svg>
          </div>
          <div class="route-info">
            <span class="route-label">출발지</span>
            <span class="route-value" :class="{ placeholder: !startPoint }">
              {{ startPoint ? startPoint.name : '지도에서 선택하세요' }}
            </span>
          </div>
          <button class="current-location-btn" @click.stop="setCurrentAsStart" title="현재 위치">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          </button>
        </div>

        <div class="route-divider">
          <div class="divider-line"></div>
          <button class="swap-btn" @click="swapPoints" :disabled="!startPoint || !endPoint">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="17 1 21 5 17 9"/>
              <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
              <polyline points="7 23 3 19 7 15"/>
              <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
            </svg>
          </button>
          <div class="divider-line"></div>
        </div>

        <div class="route-item" @click="selectingPoint = 'end'">
          <div class="route-icon end">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
          <div class="route-info">
            <span class="route-label">도착지</span>
            <span class="route-value" :class="{ placeholder: !endPoint }">
              {{ endPoint ? endPoint.name : '지도에서 선택하세요' }}
            </span>
          </div>
        </div>
      </section>

      <!-- 선택 모드 안내 -->
      <div class="selection-guide" v-if="selectingPoint">
        <div class="guide-content">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>지도에서 {{ selectingPoint === 'start' ? '출발지' : '도착지' }}를 선택하세요</span>
        </div>
        <button class="cancel-btn" @click="selectingPoint = null">취소</button>
      </div>

      <!-- 지도 영역 -->
      <section class="map-section">
        <div class="map-container" ref="mapContainer">
          <!-- VSLAM 그리드 맵 -->
          <div v-show="mapMode === 'vslam'" class="grid-map">
            <canvas ref="mapCanvas" class="map-canvas"></canvas>
            <!-- 경로 그리기 캔버스 -->
            <canvas
              ref="drawCanvas"
              class="draw-canvas"
              @mousedown="onDrawStart"
              @mousemove="onDrawMove"
              @mouseup="onDrawEnd"
              @mouseleave="onDrawEnd"
              @touchstart.prevent="onTouchDrawStart"
              @touchmove.prevent="onTouchDrawMove"
              @touchend.prevent="onDrawEnd"
              @click="onVslamMapClick"
            ></canvas>

            <!-- 로봇 마커 -->
            <div class="robot-marker" :style="robotMarkerStyle">
              <div class="robot-dot"></div>
              <div class="robot-direction" :style="robotDirectionStyle"></div>
            </div>

            <!-- 목적지 핀 -->
            <div v-if="vslamDestination" class="dest-marker" :style="destMarkerStyle">
              <div class="dest-pin">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#EF4444" stroke="white" stroke-width="1.5">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3" fill="white"/>
                </svg>
              </div>
              <span class="dest-label">
                ({{ vslamDestination.x.toFixed(1) }}, {{ vslamDestination.y.toFixed(1) }})
              </span>
            </div>

            <!-- VSLAM 컨트롤 -->
            <div class="vslam-controls">
              <button
                class="vslam-control-btn"
                :class="{ active: vslamDrawMode }"
                @click="toggleDrawMode"
                :title="vslamDrawMode ? '그리기 종료' : '경로 그리기'"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 19l7-7 3 3-7 7-3-3z"/>
                  <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/>
                  <path d="M2 2l7.586 7.586"/>
                  <circle cx="11" cy="11" r="2"/>
                </svg>
              </button>
              <button
                v-if="vslamDrawnPath.length > 0 || vslamDestination"
                class="vslam-control-btn clear-btn"
                @click="clearVslamRoute"
                title="경로 초기화"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
              <button
                v-if="vslamDrawnPath.length > 1"
                class="vslam-control-btn undo-btn"
                @click="undoDrawnPath"
                title="되돌리기"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="1 4 1 10 7 10"/>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
                </svg>
              </button>
            </div>

            <!-- 그리기 모드 안내 -->
            <div v-if="vslamDrawMode" class="draw-mode-badge">
              <span class="draw-mode-dot"></span>
              경로 그리기 모드
            </div>

            <!-- VSLAM 경로 정보 -->
            <div v-if="vslamRouteDistance > 0" class="vslam-route-info">
              {{ vslamRouteDistance.toFixed(1) }}m
            </div>

            <div class="vslam-status" :class="{ connected: robotStore.vslamConnected }">
              <span class="vslam-dot"></span>
              <span>{{ robotStore.vslamConnected ? 'VSLAM 연결됨' : 'VSLAM 연결 중...' }}</span>
            </div>
            <div class="coord-display">
              X: {{ robotStore.robotPose.x.toFixed(2) }}m,
              Y: {{ robotStore.robotPose.y.toFixed(2) }}m,
              θ: {{ (robotStore.robotPose.theta * 180 / Math.PI).toFixed(0) }}°
            </div>
          </div>

          <!-- 카카오맵 -->
          <div v-show="mapMode === 'kakao'" ref="kakaoMapRef" class="kakao-map"></div>

          <!-- 맵 모드 토글 -->
          <div class="map-toggle">
            <button
              class="toggle-btn"
              :class="{ active: mapMode === 'vslam' }"
              @click="switchToVslam"
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
          </div>

          <!-- 지도 컨트롤 (카카오맵 모드에서만) -->
          <div class="map-controls" v-show="mapMode === 'kakao'">
            <div class="zoom-group">
              <button class="map-control-btn" @click="zoomIn" title="확대">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
              </button>
              <div class="zoom-divider"></div>
              <button class="map-control-btn" @click="zoomOut" title="축소">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
              </button>
            </div>
            <button class="map-control-btn my-location-btn" @click="moveToCurrentLocation" title="현재 위치">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 2v3"/>
                <path d="M12 19v3"/>
                <path d="M2 12h3"/>
                <path d="M19 12h3"/>
              </svg>
            </button>
          </div>
        </div>
      </section>

      <!-- 프리셋 위치 -->
      <section class="preset-section">
        <div class="preset-header">
          <h3 class="section-title">자주 가는 위치</h3>
          <button class="preset-edit-btn" @click="presetEditMode = !presetEditMode">
            {{ presetEditMode ? '완료' : '편집' }}
          </button>
        </div>
        <div class="preset-list">
          <button
            class="preset-item"
            v-for="preset in presetLocations"
            :key="preset.id"
            @click="!presetEditMode && selectPreset(preset)"
          >
            <div class="preset-delete-btn" v-if="presetEditMode" @click.stop="deletePreset(preset.id)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </div>
            <div class="preset-icon" :style="{ background: preset.color }">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
            </div>
            <span class="preset-name">{{ preset.name }}</span>
          </button>

          <!-- 추가 버튼 -->
          <button class="preset-item add-preset" @click="openAddPreset">
            <div class="preset-icon add-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </div>
            <span class="preset-name">추가</span>
          </button>
        </div>
      </section>

      <!-- 프리셋 추가 모달 -->
      <Teleport to="body">
        <div v-if="showAddPreset" class="modal-overlay" @click.self="showAddPreset = false">
          <div class="modal-card">
            <h3 class="modal-title">위치 추가</h3>

            <div class="modal-field">
              <label class="modal-label">이름</label>
              <input
                v-model="newPreset.name"
                class="modal-input"
                placeholder="예: 거실, 침실, 현관..."
                maxlength="10"
              />
            </div>

            <div class="modal-field">
              <label class="modal-label">색상</label>
              <div class="color-picker">
                <button
                  v-for="c in presetColors"
                  :key="c"
                  class="color-option"
                  :class="{ selected: newPreset.color === c }"
                  :style="{ background: c }"
                  @click="newPreset.color = c"
                ></button>
              </div>
            </div>

            <div class="modal-field">
              <label class="modal-label">위치 설정</label>
              <div class="location-options">
                <button
                  class="location-option-btn"
                  :class="{ active: newPreset.locMode === 'robot' }"
                  @click="newPreset.locMode = 'robot'"
                >
                  현재 로봇 위치
                </button>
                <button
                  class="location-option-btn"
                  :class="{ active: newPreset.locMode === 'pin' }"
                  @click="newPreset.locMode = 'pin'"
                  :disabled="!vslamDestination"
                >
                  맵 핀 위치
                </button>
              </div>
              <p class="modal-hint" v-if="newPreset.locMode === 'robot'">
                로봇의 현재 좌표로 저장됩니다.
              </p>
              <p class="modal-hint" v-else-if="!vslamDestination">
                VSLAM 맵에서 먼저 핀을 찍어주세요.
              </p>
              <p class="modal-hint" v-else>
                핀 좌표 ({{ vslamDestination.x.toFixed(1) }}, {{ vslamDestination.y.toFixed(1) }})로 저장됩니다.
              </p>
            </div>

            <div class="modal-actions">
              <button class="modal-cancel-btn" @click="showAddPreset = false">취소</button>
              <button
                class="modal-confirm-btn"
                :disabled="!newPreset.name.trim()"
                @click="confirmAddPreset"
              >
                추가
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- 경로 정보 -->
      <section class="route-info-section" v-if="routeInfo">
        <h3 class="section-title">경로 정보</h3>
        <div class="route-info-card">
          <div class="route-stat">
            <span class="stat-value">{{ routeInfo.distance }}</span>
            <span class="stat-label">예상 거리</span>
          </div>
          <div class="route-stat">
            <span class="stat-value">{{ routeInfo.duration }}</span>
            <span class="stat-label">예상 시간</span>
          </div>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 하단 액션 버튼 -->
    <div class="bottom-action" v-if="isNavigating || (startPoint && endPoint) || (vslamDestination && vslamDrawnPath.length > 1)">
      <!-- 이동 중: 정지 버튼 -->
      <button v-if="isNavigating" class="stop-navigation-btn" @click="stopNavigation">
        <div class="stop-icon-wrap">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" rx="2"/>
          </svg>
        </div>
        <span>이동 정지</span>
      </button>
      <!-- 이동 전: 시작 버튼 -->
      <button v-else class="start-navigation-btn" @click="startNavigation">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="3 11 22 2 13 21 11 13 3 11"/>
        </svg>
        <span>이동 시작</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useRobotStore } from '@/stores/robotStore';

const robotStore = useRobotStore();

// 지도 관련
const mapContainer = ref(null);
const kakaoMapRef = ref(null);
const mapCanvas = ref(null);
const drawCanvas = ref(null);
const mapMode = ref('vslam');
let kakaoMap = null;
let startMarker = null;
let endMarker = null;
let polyline = null;

// 경로 설정
const startPoint = ref(null);
const endPoint = ref(null);
const selectingPoint = ref(null);
const routeInfo = ref(null);

// VSLAM 경로 그리기
const vslamDrawMode = ref(false);
const vslamDestination = ref(null);
const vslamDrawnPath = ref([]);
let isDrawing = false;
let drawHistory = [];

// 이동 상태
const isNavigating = ref(false);

// VSLAM 좌표 설정
const coordConfig = reactive({
  originLat: 35.20527,
  originLng: 126.8117,
  heading: 0
});

// VSLAM 그리드 맵
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

// 화면 좌표 → VSLAM 좌표 변환
const pixelToVslam = (px, py) => {
  const container = mapContainer.value;
  if (!container) return { x: 0, y: 0 };
  const { offsetWidth: w, offsetHeight: h } = container;
  const rangeX = mapConfig.maxX - mapConfig.minX;
  const rangeY = mapConfig.maxY - mapConfig.minY;
  const x = (px / w) * rangeX + mapConfig.minX;
  const y = ((h - py) / h) * rangeY + mapConfig.minY;
  return { x, y };
};

// VSLAM 좌표 → 화면 좌표 변환
const vslamToPixel = (x, y) => {
  const container = mapContainer.value;
  if (!container) return { px: 0, py: 0 };
  const { offsetWidth: w, offsetHeight: h } = container;
  const rangeX = mapConfig.maxX - mapConfig.minX;
  const rangeY = mapConfig.maxY - mapConfig.minY;
  const px = ((x - mapConfig.minX) / rangeX) * w;
  const py = h - ((y - mapConfig.minY) / rangeY) * h;
  return { px, py };
};

// 드로잉 캔버스 초기화
const initDrawCanvas = () => {
  const canvas = drawCanvas.value;
  const container = mapContainer.value;
  if (!canvas || !container) return;
  canvas.width = container.offsetWidth;
  canvas.height = container.offsetHeight;
};

// 드로잉 캔버스에 경로 렌더링
const renderDrawnPath = () => {
  const canvas = drawCanvas.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const path = vslamDrawnPath.value;
  if (path.length < 2) return;

  // 경로 그림자
  ctx.beginPath();
  const first = vslamToPixel(path[0].x, path[0].y);
  ctx.moveTo(first.px, first.py);
  for (let i = 1; i < path.length; i++) {
    const p = vslamToPixel(path[i].x, path[i].y);
    ctx.lineTo(p.px, p.py);
  }
  ctx.strokeStyle = 'rgba(49, 130, 246, 0.15)';
  ctx.lineWidth = 8;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.stroke();

  // 경로 본체
  ctx.beginPath();
  ctx.moveTo(first.px, first.py);
  for (let i = 1; i < path.length; i++) {
    const p = vslamToPixel(path[i].x, path[i].y);
    ctx.lineTo(p.px, p.py);
  }
  ctx.strokeStyle = '#3182f6';
  ctx.lineWidth = 3.5;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.setLineDash([]);
  ctx.stroke();

  // 시작점 마커 (초록)
  ctx.beginPath();
  ctx.arc(first.px, first.py, 6, 0, Math.PI * 2);
  ctx.fillStyle = '#20c997';
  ctx.fill();
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();

  // 끝점 마커 (빨강) - 경로 끝
  if (path.length > 1) {
    const last = vslamToPixel(path[path.length - 1].x, path[path.length - 1].y);
    ctx.beginPath();
    ctx.arc(last.px, last.py, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#EF4444';
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.stroke();
  }
};

// 경로 거리 계산
const vslamRouteDistance = computed(() => {
  const path = vslamDrawnPath.value;
  if (path.length < 2) return 0;
  let dist = 0;
  for (let i = 1; i < path.length; i++) {
    const dx = path[i].x - path[i - 1].x;
    const dy = path[i].y - path[i - 1].y;
    dist += Math.sqrt(dx * dx + dy * dy);
  }
  return dist;
});

// 목적지 마커 위치
const destMarkerStyle = computed(() => {
  if (!vslamDestination.value || !mapContainer.value) return { display: 'none' };
  const { px, py } = vslamToPixel(vslamDestination.value.x, vslamDestination.value.y);
  return { left: `${px}px`, top: `${py}px`, transform: 'translate(-50%, -100%)' };
});

// 그리기 모드 토글
const toggleDrawMode = () => {
  vslamDrawMode.value = !vslamDrawMode.value;
  if (vslamDrawMode.value) {
    // 그리기 시작 시 기존 경로를 히스토리에 저장
    if (vslamDrawnPath.value.length > 0) {
      drawHistory = [...vslamDrawnPath.value];
    }
  }
};

// VSLAM 맵 클릭 (핀 찍기)
const onVslamMapClick = (e) => {
  if (vslamDrawMode.value || isDrawing) return;
  const rect = e.target.getBoundingClientRect();
  const px = e.clientX - rect.left;
  const py = e.clientY - rect.top;
  const coord = pixelToVslam(px, py);
  vslamDestination.value = coord;
};

// 드로잉 이벤트 (마우스)
const onDrawStart = (e) => {
  if (!vslamDrawMode.value) return;
  isDrawing = true;
  drawHistory = [...vslamDrawnPath.value];
  const rect = e.target.getBoundingClientRect();
  const px = e.clientX - rect.left;
  const py = e.clientY - rect.top;
  const coord = pixelToVslam(px, py);
  vslamDrawnPath.value = [coord];
  renderDrawnPath();
};

const onDrawMove = (e) => {
  if (!isDrawing || !vslamDrawMode.value) return;
  const rect = e.target.getBoundingClientRect();
  const px = e.clientX - rect.left;
  const py = e.clientY - rect.top;
  const coord = pixelToVslam(px, py);

  // 너무 가까운 점은 건너뛰기 (성능)
  const last = vslamDrawnPath.value[vslamDrawnPath.value.length - 1];
  const dx = coord.x - last.x;
  const dy = coord.y - last.y;
  if (Math.sqrt(dx * dx + dy * dy) < 0.05) return;

  vslamDrawnPath.value.push(coord);
  renderDrawnPath();
};

const onDrawEnd = () => {
  if (!isDrawing) return;
  isDrawing = false;

  // 경로의 마지막 점을 목적지로 설정
  if (vslamDrawnPath.value.length > 1) {
    const last = vslamDrawnPath.value[vslamDrawnPath.value.length - 1];
    vslamDestination.value = { x: last.x, y: last.y };
  }
};

// 드로잉 이벤트 (터치)
const onTouchDrawStart = (e) => {
  if (!vslamDrawMode.value) return;
  const touch = e.touches[0];
  const rect = e.target.getBoundingClientRect();
  isDrawing = true;
  drawHistory = [...vslamDrawnPath.value];
  const px = touch.clientX - rect.left;
  const py = touch.clientY - rect.top;
  const coord = pixelToVslam(px, py);
  vslamDrawnPath.value = [coord];
  renderDrawnPath();
};

const onTouchDrawMove = (e) => {
  if (!isDrawing || !vslamDrawMode.value) return;
  const touch = e.touches[0];
  const rect = e.target.getBoundingClientRect();
  const px = touch.clientX - rect.left;
  const py = touch.clientY - rect.top;
  const coord = pixelToVslam(px, py);

  const last = vslamDrawnPath.value[vslamDrawnPath.value.length - 1];
  const dx = coord.x - last.x;
  const dy = coord.y - last.y;
  if (Math.sqrt(dx * dx + dy * dy) < 0.05) return;

  vslamDrawnPath.value.push(coord);
  renderDrawnPath();
};

// 경로 초기화
const clearVslamRoute = () => {
  vslamDrawnPath.value = [];
  vslamDestination.value = null;
  drawHistory = [];
  vslamDrawMode.value = false;
  renderDrawnPath();
};

// 되돌리기
const undoDrawnPath = () => {
  if (drawHistory.length > 0) {
    vslamDrawnPath.value = [...drawHistory];
    drawHistory = [];
  } else {
    vslamDrawnPath.value = [];
  }
  if (vslamDrawnPath.value.length > 1) {
    const last = vslamDrawnPath.value[vslamDrawnPath.value.length - 1];
    vslamDestination.value = { x: last.x, y: last.y };
  } else {
    vslamDestination.value = null;
  }
  renderDrawnPath();
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

const robotDirectionStyle = computed(() => {
  const theta = robotStore.robotPose.theta || 0;
  const degrees = -(theta * 180 / Math.PI) + 90;
  return { transform: `rotate(${degrees}deg)` };
});

const switchToVslam = () => {
  mapMode.value = 'vslam';
  nextTick(() => {
    drawGrid();
    initDrawCanvas();
    renderDrawnPath();
  });
};

const switchToKakao = () => {
  mapMode.value = 'kakao';
  nextTick(() => {
    if (!kakaoMap) {
      initMap();
    } else {
      kakaoMap.relayout();
    }
  });
};

// 프리셋 위치 (localStorage 저장)
const DEFAULT_PRESETS = [
  { id: 1, name: '거실', lat: 35.20530, lng: 126.8118, vx: 0, vy: 0, color: '#3182f6' },
  { id: 2, name: '침실', lat: 35.20525, lng: 126.8116, vx: -2, vy: 1, color: '#20c997' },
  { id: 3, name: '주방', lat: 35.20528, lng: 126.8119, vx: 1, vy: 2, color: '#F59E0B' },
  { id: 4, name: '현관', lat: 35.20522, lng: 126.8115, vx: -1, vy: -2, color: '#EF4444' },
];

const loadPresets = () => {
  try {
    const saved = localStorage.getItem('nav_presets');
    return saved ? JSON.parse(saved) : [...DEFAULT_PRESETS];
  } catch {
    return [...DEFAULT_PRESETS];
  }
};

const savePresets = () => {
  localStorage.setItem('nav_presets', JSON.stringify(presetLocations.value));
};

const presetLocations = ref(loadPresets());
const presetEditMode = ref(false);
const showAddPreset = ref(false);

const presetColors = [
  '#3182f6', '#20c997', '#F59E0B', '#EF4444',
  '#8b5cf6', '#ec4899', '#14b8a6', '#6366f1'
];

const newPreset = reactive({
  name: '',
  color: '#3182f6',
  locMode: 'robot'
});

const openAddPreset = () => {
  newPreset.name = '';
  newPreset.color = '#3182f6';
  newPreset.locMode = 'robot';
  showAddPreset.value = true;
};

const confirmAddPreset = () => {
  if (!newPreset.name.trim()) return;

  const METERS_PER_LAT = 0.000009;
  const METERS_PER_LNG = 0.000011;

  let vx = 0, vy = 0, lat = coordConfig.originLat, lng = coordConfig.originLng;

  if (newPreset.locMode === 'pin' && vslamDestination.value) {
    vx = vslamDestination.value.x;
    vy = vslamDestination.value.y;
    lat = coordConfig.originLat + vy * METERS_PER_LAT;
    lng = coordConfig.originLng + vx * METERS_PER_LNG;
  } else {
    vx = robotStore.robotPose.x || 0;
    vy = robotStore.robotPose.y || 0;
    lat = coordConfig.originLat + vy * METERS_PER_LAT;
    lng = coordConfig.originLng + vx * METERS_PER_LNG;
  }

  const maxId = presetLocations.value.reduce((max, p) => Math.max(max, p.id), 0);
  presetLocations.value.push({
    id: maxId + 1,
    name: newPreset.name.trim(),
    lat, lng, vx, vy,
    color: newPreset.color
  });

  savePresets();
  showAddPreset.value = false;
};

const deletePreset = (id) => {
  presetLocations.value = presetLocations.value.filter(p => p.id !== id);
  savePresets();
  if (presetLocations.value.length === 0) {
    presetEditMode.value = false;
  }
};

// 카카오맵 SDK 로드
const loadKakaoMapSdk = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) {
      resolve();
      return;
    }
    const apiKey = import.meta.env.VITE_KAKAO_MAP_API_KEY;
    if (!apiKey) {
      reject(new Error('카카오맵 API 키가 설정되지 않았습니다.'));
      return;
    }
    const script = document.createElement('script');
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&libraries=services&autoload=false`;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('카카오맵 SDK 로드 실패'));
    document.head.appendChild(script);
  });
};

// 지도 초기화
const initMap = async () => {
  try {
    await loadKakaoMapSdk();
    window.kakao.maps.load(() => {
      createMap();
    });
  } catch (error) {
    console.error('카카오맵 초기화 실패:', error);
  }
};

const createMap = () => {
  const container = kakaoMapRef.value;
  if (!container) return;

  const options = {
    center: new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng),
    level: 2
  };

  kakaoMap = new window.kakao.maps.Map(container, options);

  // 지도 클릭 이벤트
  window.kakao.maps.event.addListener(kakaoMap, 'click', (mouseEvent) => {
    if (!selectingPoint.value) return;

    const latlng = mouseEvent.latLng;
    const point = {
      lat: latlng.getLat(),
      lng: latlng.getLng(),
      name: `선택한 위치`
    };

    // 역지오코딩으로 주소 가져오기
    const geocoder = new window.kakao.maps.services.Geocoder();
    geocoder.coord2Address(latlng.getLng(), latlng.getLat(), (result, status) => {
      if (status === window.kakao.maps.services.Status.OK) {
        const address = result[0];
        if (address.road_address) {
          point.name = address.road_address.building_name || address.road_address.road_name;
        } else if (address.address) {
          point.name = address.address.region_3depth_name;
        }
      }

      if (selectingPoint.value === 'start') {
        setStartPoint(point);
      } else if (selectingPoint.value === 'end') {
        setEndPoint(point);
      }
      selectingPoint.value = null;
    });
  });

  // 현재 로봇 위치 표시
  addRobotMarker();
};

// 로봇 마커 추가
const addRobotMarker = () => {
  if (!kakaoMap) return;

  const robotPosition = new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng);
  const markerContent = `
    <div style="width: 24px; height: 24px; background: #3182f6; border: 3px solid white; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>
  `;

  new window.kakao.maps.CustomOverlay({
    position: robotPosition,
    content: markerContent,
    yAnchor: 0.5,
    xAnchor: 0.5,
    map: kakaoMap
  });
};

// 시작점 설정
const setStartPoint = (point) => {
  startPoint.value = point;

  if (startMarker) {
    startMarker.setMap(null);
  }

  const position = new window.kakao.maps.LatLng(point.lat, point.lng);
  const markerContent = `
    <div style="display: flex; flex-direction: column; align-items: center;">
      <div style="width: 32px; height: 32px; background: #20c997; border: 3px solid white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="white"><circle cx="12" cy="12" r="6"/></svg>
      </div>
      <div style="margin-top: 4px; padding: 4px 8px; background: #20c997; color: white; border-radius: 4px; font-size: 11px; font-weight: 600; white-space: nowrap;">출발</div>
    </div>
  `;

  startMarker = new window.kakao.maps.CustomOverlay({
    position: position,
    content: markerContent,
    yAnchor: 1,
    xAnchor: 0.5,
    map: kakaoMap
  });

  updateRoute();
};

// 도착점 설정
const setEndPoint = (point) => {
  endPoint.value = point;

  if (endMarker) {
    endMarker.setMap(null);
  }

  const position = new window.kakao.maps.LatLng(point.lat, point.lng);
  const markerContent = `
    <div style="display: flex; flex-direction: column; align-items: center;">
      <div style="width: 32px; height: 32px; background: #EF4444; border: 3px solid white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/></svg>
      </div>
      <div style="margin-top: 4px; padding: 4px 8px; background: #EF4444; color: white; border-radius: 4px; font-size: 11px; font-weight: 600; white-space: nowrap;">도착</div>
    </div>
  `;

  endMarker = new window.kakao.maps.CustomOverlay({
    position: position,
    content: markerContent,
    yAnchor: 1,
    xAnchor: 0.5,
    map: kakaoMap
  });

  updateRoute();
};

// 경로 업데이트
const updateRoute = () => {
  if (!startPoint.value || !endPoint.value || !kakaoMap) return;

  // 기존 경로선 제거
  if (polyline) {
    polyline.setMap(null);
  }

  const path = [
    new window.kakao.maps.LatLng(startPoint.value.lat, startPoint.value.lng),
    new window.kakao.maps.LatLng(endPoint.value.lat, endPoint.value.lng)
  ];

  polyline = new window.kakao.maps.Polyline({
    path: path,
    strokeWeight: 5,
    strokeColor: '#3182f6',
    strokeOpacity: 0.8,
    strokeStyle: 'solid'
  });

  polyline.setMap(kakaoMap);

  // 경로 정보 계산
  const distance = calculateDistance(startPoint.value, endPoint.value);
  const duration = Math.ceil(distance / 0.5); // 로봇 속도 0.5m/s 가정

  routeInfo.value = {
    distance: distance < 1000 ? `${distance.toFixed(0)}m` : `${(distance / 1000).toFixed(1)}km`,
    duration: duration < 60 ? `${duration}초` : `${Math.ceil(duration / 60)}분`
  };

  // 경로가 보이도록 지도 범위 조정
  const bounds = new window.kakao.maps.LatLngBounds();
  bounds.extend(path[0]);
  bounds.extend(path[1]);
  kakaoMap.setBounds(bounds);
};

// 거리 계산 (Haversine formula)
const calculateDistance = (point1, point2) => {
  const R = 6371000; // 지구 반지름 (m)
  const dLat = (point2.lat - point1.lat) * Math.PI / 180;
  const dLng = (point2.lng - point1.lng) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(point1.lat * Math.PI / 180) * Math.cos(point2.lat * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

// 현재 위치를 출발지로 설정
const setCurrentAsStart = () => {
  const point = {
    lat: coordConfig.originLat,
    lng: coordConfig.originLng,
    name: '현재 위치'
  };
  setStartPoint(point);
};

// 출발/도착 교환
const swapPoints = () => {
  if (!startPoint.value || !endPoint.value) return;

  const temp = { ...startPoint.value };
  setStartPoint({ ...endPoint.value });
  setEndPoint(temp);
};

// 프리셋 선택
const selectPreset = (preset) => {
  const point = {
    lat: preset.lat,
    lng: preset.lng,
    name: preset.name
  };

  if (!startPoint.value) {
    setStartPoint(point);
  } else if (!endPoint.value) {
    setEndPoint(point);
  } else {
    // 둘 다 있으면 도착지 변경
    setEndPoint(point);
  }
};

// 초기화
const resetNavigation = () => {
  startPoint.value = null;
  endPoint.value = null;
  routeInfo.value = null;
  selectingPoint.value = null;
  clearVslamRoute();

  if (startMarker) {
    startMarker.setMap(null);
    startMarker = null;
  }
  if (endMarker) {
    endMarker.setMap(null);
    endMarker = null;
  }
  if (polyline) {
    polyline.setMap(null);
    polyline = null;
  }

  if (kakaoMap) {
    kakaoMap.setCenter(new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng));
    kakaoMap.setLevel(2);
  }
};

// 지도 컨트롤
const zoomIn = () => {
  if (kakaoMap) kakaoMap.setLevel(kakaoMap.getLevel() - 1);
};

const zoomOut = () => {
  if (kakaoMap) kakaoMap.setLevel(kakaoMap.getLevel() + 1);
};

const moveToCurrentLocation = () => {
  if (kakaoMap) {
    kakaoMap.setCenter(new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng));
  }
};

// 이동 시작
const startNavigation = () => {
  isNavigating.value = true;

  // VSLAM 경로가 있는 경우
  if (mapMode.value === 'vslam' && vslamDestination.value && vslamDrawnPath.value.length > 1) {
    // TODO: robotStore를 통해 VSLAM 경로 전송
    // robotStore.sendVslamPath(vslamDrawnPath.value);
    return;
  }

  // 카카오맵 경로
  if (!startPoint.value || !endPoint.value) return;
  // TODO: robotStore를 통해 이동 명령 전송
  // robotStore.sendNavigationCommand(startPoint.value, endPoint.value);
};

// 이동 정지
const stopNavigation = () => {
  isNavigating.value = false;
  // TODO: robotStore를 통해 정지 명령 전송
  // robotStore.sendStopCommand();
};

const handleResize = () => {
  drawGrid();
  initDrawCanvas();
  renderDrawnPath();
};

onMounted(() => {
  robotStore.connectWebSocket();
  nextTick(() => {
    drawGrid();
    initDrawCanvas();
    window.addEventListener('resize', handleResize);
  });
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.navigation-view {
  min-height: 100vh;
  background: #f2f4f6;
  padding-bottom: 100px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
}

.back-btn, .reset-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7684;
}

.reset-btn:hover {
  background: #f2f4f6;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #191f28;
}

.header-spacer {
  width: 40px;
}

.content {
  padding: 16px;
}

/* 경로 설정 카드 */
.route-card {
  background: #fff;
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.route-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.route-item:hover {
  background: #f8f9fa;
}

.route-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.route-icon.start {
  background: #e6f7f2;
  color: #20c997;
}

.route-icon.end {
  background: #fee2e2;
  color: #EF4444;
}

.route-info {
  flex: 1;
  min-width: 0;
}

.route-label {
  display: block;
  font-size: 12px;
  color: #8b95a1;
  margin-bottom: 2px;
}

.route-value {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #191f28;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.route-value.placeholder {
  color: #b0b8c1;
  font-weight: 400;
}

.current-location-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #e7f1ff;
  color: #3182f6;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.current-location-btn:hover {
  background: #3182f6;
  color: #fff;
}

.route-divider {
  display: flex;
  align-items: center;
  padding: 4px 12px;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: #e5e8eb;
}

.swap-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f2f4f6;
  color: #6b7684;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 8px;
  transition: all 0.2s;
}

.swap-btn:hover:not(:disabled) {
  background: #3182f6;
  color: #fff;
}

.swap-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 선택 모드 안내 */
.selection-guide {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding: 12px 16px;
  background: #e7f1ff;
  border-radius: 12px;
}

.guide-content {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #3182f6;
}

.cancel-btn {
  padding: 6px 12px;
  background: #fff;
  color: #6b7684;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
}

/* 지도 섹션 */
.map-section {
  margin-top: 16px;
}

.map-container {
  position: relative;
  height: 300px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.kakao-map {
  width: 100%;
  height: 100%;
}

/* VSLAM 그리드 맵 */
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

.draw-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 5;
  cursor: crosshair;
  touch-action: none;
}

/* 목적지 핀 마커 */
.dest-marker {
  position: absolute;
  z-index: 12;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.dest-pin {
  filter: drop-shadow(0 2px 4px rgba(239, 68, 68, 0.4));
  animation: pinDrop 0.3s ease-out;
}

@keyframes pinDrop {
  0% { transform: translateY(-12px); opacity: 0; }
  60% { transform: translateY(2px); }
  100% { transform: translateY(0); opacity: 1; }
}

.dest-label {
  margin-top: 2px;
  padding: 2px 6px;
  background: rgba(239, 68, 68, 0.9);
  color: #fff;
  font-size: 9px;
  font-weight: 600;
  border-radius: 4px;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

/* VSLAM 컨트롤 */
.vslam-controls {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  z-index: 20;
}

.vslam-control-btn {
  width: 38px;
  height: 38px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4e5968;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.vslam-control-btn.active {
  background: #3182f6;
  color: #fff;
  box-shadow: 0 2px 12px rgba(49, 130, 246, 0.4);
}

.vslam-control-btn.clear-btn:active {
  background: #fee2e2;
  color: #EF4444;
}

.vslam-control-btn.undo-btn:active {
  background: #fef3c7;
  color: #F59E0B;
}

/* 그리기 모드 안내 배지 */
.draw-mode-badge {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background: rgba(49, 130, 246, 0.9);
  backdrop-filter: blur(8px);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  z-index: 20;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  0% { opacity: 0; transform: translateX(-50%) translateY(-4px); }
  100% { opacity: 1; transform: translateX(-50%) translateY(0); }
}

.draw-mode-dot {
  width: 6px;
  height: 6px;
  background: #fff;
  border-radius: 50%;
  animation: blink 1.2s infinite;
}

@keyframes blink {
  0%, 50%, 100% { opacity: 1; }
  25%, 75% { opacity: 0.3; }
}

/* VSLAM 경로 거리 정보 */
.vslam-route-info {
  position: absolute;
  bottom: 36px;
  right: 8px;
  padding: 4px 10px;
  background: rgba(49, 130, 246, 0.9);
  backdrop-filter: blur(8px);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  font-variant-numeric: tabular-nums;
  box-shadow: 0 2px 8px rgba(49, 130, 246, 0.3);
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

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(32, 201, 151, 0.2); }
  50% { box-shadow: 0 0 0 6px rgba(32, 201, 151, 0.1); }
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

/* 맵 모드 토글 */
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

.map-controls {
  position: absolute;
  right: 10px;
  top: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 15;
}

.zoom-group {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.zoom-divider {
  height: 1px;
  background: #e5e8eb;
  margin: 0 8px;
}

.map-control-btn {
  width: 40px;
  height: 40px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4e5968;
  transition: all 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}

.map-control-btn:active {
  background: #f2f4f6;
  color: #3182f6;
}

.my-location-btn {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  color: #3182f6;
}

.my-location-btn:active {
  background: #e7f1ff;
}

/* 프리셋 섹션 */
.preset-section {
  margin-top: 24px;
}

.preset-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.preset-header .section-title {
  margin-bottom: 0;
}

.preset-edit-btn {
  font-size: 13px;
  font-weight: 600;
  color: #3182f6;
  padding: 4px 10px;
  border-radius: 8px;
  transition: background 0.2s;
}

.preset-edit-btn:active {
  background: #e7f1ff;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: #191f28;
  margin-bottom: 12px;
}

.preset-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 4px;
  -webkit-overflow-scrolling: touch;
}

.preset-list::-webkit-scrollbar {
  display: none;
}

.preset-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 16px;
  min-width: 80px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
  flex-shrink: 0;
}

.preset-item:active {
  transform: scale(0.96);
}

.preset-item.add-preset {
  background: #f2f4f6;
  border: 2px dashed #d1d6db;
  box-shadow: none;
}

.preset-item.add-preset:active {
  background: #e5e8eb;
}

.add-icon {
  background: transparent !important;
  color: #8b95a1 !important;
  border: 2px dashed #b0b8c1;
}

/* 삭제 버튼 */
.preset-delete-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 22px;
  height: 22px;
  background: #EF4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.4);
  animation: shake 0.4s ease;
  z-index: 5;
}

@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-3deg); }
  75% { transform: rotate(3deg); }
}

.preset-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.preset-name {
  font-size: 13px;
  font-weight: 600;
  color: #4e5968;
}

/* 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

.modal-card {
  width: 100%;
  max-width: 500px;
  background: #fff;
  border-radius: 24px 24px 0 0;
  padding: 28px 24px;
  padding-bottom: max(28px, env(safe-area-inset-bottom));
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  0% { transform: translateY(100%); }
  100% { transform: translateY(0); }
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #191f28;
  margin-bottom: 24px;
}

.modal-field {
  margin-bottom: 20px;
}

.modal-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #6b7684;
  margin-bottom: 8px;
}

.modal-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 15px;
  font-weight: 500;
  color: #191f28;
  background: #f2f4f6;
  border: 2px solid transparent;
  border-radius: 12px;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}

.modal-input:focus {
  border-color: #3182f6;
  background: #fff;
}

.modal-input::placeholder {
  color: #b0b8c1;
}

.color-picker {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.color-option {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 3px solid transparent;
  transition: all 0.15s;
  cursor: pointer;
}

.color-option.selected {
  border-color: #191f28;
  transform: scale(1.15);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.location-options {
  display: flex;
  gap: 8px;
}

.location-option-btn {
  flex: 1;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7684;
  background: #f2f4f6;
  border-radius: 10px;
  transition: all 0.2s;
}

.location-option-btn.active {
  background: #e7f1ff;
  color: #3182f6;
}

.location-option-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.modal-hint {
  font-size: 12px;
  color: #8b95a1;
  margin-top: 8px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
}

.modal-cancel-btn {
  flex: 1;
  padding: 14px;
  font-size: 15px;
  font-weight: 600;
  color: #6b7684;
  background: #f2f4f6;
  border-radius: 12px;
  transition: background 0.2s;
}

.modal-cancel-btn:active {
  background: #e5e8eb;
}

.modal-confirm-btn {
  flex: 1;
  padding: 14px;
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  background: #3182f6;
  border-radius: 12px;
  transition: all 0.2s;
}

.modal-confirm-btn:active {
  background: #1b6de8;
}

.modal-confirm-btn:disabled {
  background: #b0b8c1;
  cursor: not-allowed;
}

/* 경로 정보 섹션 */
.route-info-section {
  margin-top: 24px;
}

.route-info-card {
  display: flex;
  gap: 12px;
}

.route-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #3182f6;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #8b95a1;
}

.bottom-spacer {
  height: 80px;
}

/* 하단 이동 버튼 */
.bottom-action {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  padding-bottom: max(16px, env(safe-area-inset-bottom));
  background: linear-gradient(to top, #fff 80%, transparent);
}

.start-navigation-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px;
  background: linear-gradient(135deg, #3182f6 0%, #5BA0F5 100%);
  color: #fff;
  border-radius: 16px;
  font-size: 17px;
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(49, 130, 246, 0.4);
  transition: all 0.2s;
}

.start-navigation-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(49, 130, 246, 0.5);
}

.start-navigation-btn:active {
  transform: translateY(0);
}

.stop-navigation-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px;
  background: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
  color: #fff;
  border-radius: 16px;
  font-size: 17px;
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.4);
  transition: all 0.2s;
  animation: stopPulse 2s ease-in-out infinite;
}

@keyframes stopPulse {
  0%, 100% { box-shadow: 0 4px 16px rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 4px 24px rgba(239, 68, 68, 0.6); }
}

.stop-navigation-btn:active {
  transform: scale(0.97);
  animation: none;
}

.stop-icon-wrap {
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
