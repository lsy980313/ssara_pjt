<template>
  <div class="location">
    <header class="header">
      <h1 class="header-title">위치</h1>
      <div class="status-badge" :class="{ online: robotState.status === 'ONLINE' }">
        <span class="dot"></span>
        {{ robotState.status === 'ONLINE' ? '활성화' : '비활성화' }}
      </div>
    </header>

    <main class="content">
      <!-- 지도 영역 -->
      <section class="map-section">
        <!-- VSLAM 그리드 맵 / 카카오맵 -->
        <div class="map-container" ref="mapContainer">
          <!-- VSLAM 그리드 맵 -->
          <div v-show="mapMode === 'vslam'" class="grid-map">
            <canvas ref="mapCanvas" class="map-canvas"></canvas>
            <div class="robot-marker" :style="robotMarkerStyle">
              <div class="robot-dot"></div>
            </div>
          </div>
          <!-- 카카오맵 -->
          <div v-show="mapMode === 'kakao'" ref="kakaoMapRef" class="kakao-map">
            <div v-if="!isKakaoMapReady" class="map-loading">
              <span>카카오맵 로딩중...</span>
            </div>
          </div>
        </div>

        <!-- 맵 모드 토글 + 현재 위치 버튼 -->
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
          <button class="sync-btn" @click="syncKakaoMapPosition">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </button>
        </div>

      </section>

      <!-- 현재 위치 카드 -->
      <div class="location-card">
        <div class="location-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
        </div>
        <div class="location-info">
          <span class="location-label">현재 위치</span>
          <span class="location-address">{{ currentLocationText }}</span>
        </div>
      </div>

      <!-- 상태 카드 -->
      <section class="status-section">
        <div class="status-card">
          <div class="status-icon blue">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="2" y1="12" x2="22" y2="12"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
          </div>
          <div class="status-content">
            <span class="status-value">{{ robotState.location }}</span>
            <span class="status-label">VSLAM 좌표</span>
          </div>
        </div>
        <div class="status-card">
          <div class="status-icon orange">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div class="status-content">
            <span class="status-value">{{ activityStatus }}</span>
            <span class="status-label">활동 상태</span>
          </div>
        </div>
      </section>

      <!-- 빠른 명령 -->
      <section class="command-section">
        <h3 class="section-title">빠른 명령</h3>
        <div class="command-list">
          <button class="command-btn" @click="sendCommand('home')">
            <div class="command-icon home">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
            </div>
            <span class="command-text">집으로 복귀</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
          <button class="command-btn" @click="sendCommand('stay')">
            <div class="command-icon stay">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
              </svg>
            </div>
            <span class="command-text">제자리 대기</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 하단 네비게이션 -->
    <nav class="bottom-nav">
      <button class="nav-item" @click="$router.push('/home')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>홈</span>
      </button>
      <button class="nav-item active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
          <circle cx="12" cy="10" r="3"/>
        </svg>
        <span>위치</span>
      </button>
      <button class="nav-item" @click="$router.push('/history')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        <span>기록</span>
      </button>
      <button class="nav-item" @click="$router.push('/help')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
import { computed, onMounted, onUnmounted, ref, nextTick, reactive } from 'vue';
import { useRobotStore } from '@/stores/robotStore';

const robotStore = useRobotStore();

// Refs
const mapContainer = ref(null);
const mapCanvas = ref(null);
const kakaoMapRef = ref(null);

const isKakaoMapReady = ref(false);
const mapMode = ref('vslam'); // 'vslam' | 'kakao'

// 카카오맵 객체
let kakaoMap = null;
let robotMarkerKakao = null;

// ==================== VSLAM 좌표 설정 (여기서 수정) ====================
const coordConfig = reactive({
  // [수정] VSLAM 원점(0,0)의 GPS 좌표
  originLat: 35.20527,   // 위도
  originLng: 126.8117,   // 경도
  // [수정] VSLAM x축 방향 (북=0, 동=90, 남=180, 서=270)
  heading: 0
});
// =====================================================================

// 미터당 위도/경도 변환 계수 (한국 기준 근사값)
const METERS_PER_LAT = 0.000009;  // 1m ≈ 0.000009도 (위도)
const METERS_PER_LNG = 0.000011;  // 1m ≈ 0.000011도 (경도, 위도에 따라 다름)

// ==================== VSLAM → GPS 변환 ====================
const vslamToGps = (x, y) => {
  const headingRad = (coordConfig.heading * Math.PI) / 180;
  const cosH = Math.cos(headingRad);
  const sinH = Math.sin(headingRad);

  // 회전 변환 적용
  const rotatedX = x * cosH - y * sinH;
  const rotatedY = x * sinH + y * cosH;

  // GPS 좌표 계산
  const lat = coordConfig.originLat + rotatedY * METERS_PER_LAT;
  const lng = coordConfig.originLng + rotatedX * METERS_PER_LNG;

  return { lat, lng };
};

// 현재 GPS 좌표 (computed)
const gpsCoord = computed(() => {
  const x = robotStore.robotPose.x || 0;
  const y = robotStore.robotPose.y || 0;
  return vslamToGps(x, y);
});

// ==================== VSLAM 그리드 맵 ====================
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

  ctx.fillStyle = '#868e96';
  ctx.font = '10px sans-serif';
  ctx.fillText('0', originX + 4, originY - 4);
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

// 카카오맵으로 전환
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

// ==================== 카카오맵 SDK 동적 로딩 ====================
const loadKakaoMapSdk = () => {
  return new Promise((resolve, reject) => {
    // 이미 로드된 경우
    if (window.kakao && window.kakao.maps) {
      resolve();
      return;
    }

    const apiKey = import.meta.env.VITE_KAKAO_MAP_API_KEY;
    if (!apiKey || apiKey === '<your-kakao-javascript-key>') {
      reject(new Error('카카오맵 API 키가 .env 파일에 설정되지 않았습니다.'));
      return;
    }

    const script = document.createElement('script');
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false`;
    script.onload = () => {
      console.log('카카오맵 SDK 스크립트 로드 완료');
      resolve();
    };
    script.onerror = () => reject(new Error('카카오맵 SDK 로드 실패'));
    document.head.appendChild(script);
  });
};

// ==================== 카카오맵 초기화 ====================
const initKakaoMap = async () => {
  console.log('initKakaoMap 호출됨');

  try {
    // SDK 동적 로딩
    await loadKakaoMapSdk();

    if (typeof window.kakao === 'undefined' || !window.kakao.maps) {
      console.error('카카오맵 SDK가 로드되지 않았습니다.');
      return;
    }

    // autoload=false 이므로 항상 load() 호출 필요
    console.log('kakao.maps.load 호출 중...');
    window.kakao.maps.load(() => {
      console.log('kakao.maps.load 완료');
      createKakaoMap();
    });
  } catch (error) {
    console.error('카카오맵 초기화 실패:', error.message);
  }
};

const createKakaoMap = () => {
  console.log('createKakaoMap 호출됨');

  const container = kakaoMapRef.value;
  if (!container) {
    console.error('카카오맵 컨테이너를 찾을 수 없습니다.');
    return;
  }

  try {
    const options = {
      center: new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng),
      level: 2,  // 좁은 범위 (1=가장 상세, 14=가장 넓음)
      draggable: true
    };

    kakaoMap = new window.kakao.maps.Map(container, options);

    // 줌 컨트롤 추가
    const zoomControl = new window.kakao.maps.ZoomControl();
    kakaoMap.addControl(zoomControl, window.kakao.maps.ControlPosition.RIGHT);

    console.log('카카오맵 생성 완료');

    // 로봇 마커 생성 (커스텀 원형 마커)
    const markerContent = `
      <div style="
        width: 20px;
        height: 20px;
        background: #3b82f6;
        border: 3px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      "></div>
    `;

    robotMarkerKakao = new window.kakao.maps.CustomOverlay({
      position: new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng),
      content: markerContent,
      yAnchor: 0.5,
      xAnchor: 0.5
    });
    robotMarkerKakao.setMap(kakaoMap);

    isKakaoMapReady.value = true;

    // 맵 리사이즈
    setTimeout(() => {
      kakaoMap.relayout();
      kakaoMap.setCenter(new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng));
    }, 100);

  } catch (error) {
    console.error('카카오맵 생성 오류:', error);
  }
};

// ==================== 카카오맵 수동 업데이트 ====================
// 수동 위치 동기화 (버튼 클릭 시 호출)
const syncKakaoMapPosition = () => {
  if (!kakaoMap || !robotMarkerKakao) {
    console.warn('카카오맵이 준비되지 않았습니다.');
    return;
  }

  // 지도 크기 재계산 (반쪽 렌더링 문제 해결)
  kakaoMap.relayout();

  const { lat, lng } = gpsCoord.value;
  const position = new window.kakao.maps.LatLng(lat, lng);

  // 마커 위치 업데이트
  robotMarkerKakao.setPosition(position);

  // 지도 중심 이동
  kakaoMap.setCenter(position);

  console.log(`위치 동기화: ${lat.toFixed(6)}, ${lng.toFixed(6)}`);
};

// ==================== 위치 텍스트 ====================
const currentLocationText = computed(() => {
  if (isKakaoMapReady.value) {
    return `${gpsCoord.value.lat.toFixed(5)}, ${gpsCoord.value.lng.toFixed(5)}`;
  }
  return `(${(robotStore.robotPose.x || 0).toFixed(1)}, ${(robotStore.robotPose.y || 0).toFixed(1)})`;
});

// ==================== 기존 상태 ====================
const robotState = computed(() => ({
  status: robotStore.robotStatus.isOnline ? 'ONLINE' : 'OFFLINE',
  location: `(${(robotStore.robotPose.x || 0).toFixed(1)}, ${(robotStore.robotPose.y || 0).toFixed(1)})`
}));

const activityStatus = computed(() => robotStore.robotStatus.state || '-');

const sendCommand = async (cmd) => {
  try {
    if (cmd === 'home') {
      await robotStore.sendHomeCommand();
      alert('집으로 복귀 명령을 보냈어요');
    } else if (cmd === 'stay') {
      await robotStore.sendStopCommand();
      alert('제자리 대기 명령을 보냈어요');
    }
  } catch (error) {
    alert('명령 전송에 실패했어요');
  }
};

// ==================== Lifecycle ====================
onMounted(() => {
  robotStore.connectWebSocket();
  nextTick(() => {
    drawGrid();
    window.addEventListener('resize', drawGrid);
  });
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
  window.removeEventListener('resize', drawGrid);
});
</script>

<style scoped>
.location {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 80px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--bg-primary);
}

.header-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
}

.status-badge.online {
  background: var(--success-light);
  color: var(--success);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.content {
  padding: 0 20px 20px;
}

/* 지도 */
.map-section {
  margin: 0 -20px;
  position: relative;
}

.map-container {
  height: 280px;
  position: relative;
  overflow: hidden;
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
  width: 16px;
  height: 16px;
  background: var(--primary);
  border: 3px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}

.kakao-map {
  width: 100%;
  height: 100%;
}

.map-loading {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  color: var(--text-tertiary);
  font-size: 14px;
}

/* 맵 토글 */
.map-toggle {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  background: var(--bg-primary);
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 20;
}

.toggle-btn {
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  border-radius: 6px;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: var(--primary);
  color: white;
}

.sync-btn {
  margin-left: 4px;
  padding: 6px 10px;
  background: var(--success);
  color: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.sync-btn:active {
  transform: scale(0.95);
  opacity: 0.8;
}

.location-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  margin-top: 12px;
  background: var(--bg-primary);
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.location-icon {
  width: 36px;
  height: 36px;
  background: var(--primary-light);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
}

.location-info {
  display: flex;
  flex-direction: column;
}

.location-label {
  font-size: 12px;
  color: var(--success);
  font-weight: 600;
}

.location-address {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 상태 카드 */
.status-section {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.status-card {
  flex: 1;
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
}

.status-icon {
  width: 40px;
  height: 40px;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.status-icon.blue {
  background: #e7f5ff;
  color: #228be6;
}

.status-icon.orange {
  background: var(--warning-light);
  color: var(--warning);
}

.status-content {
  display: flex;
  flex-direction: column;
}

.status-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.status-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* 빠른 명령 */
.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 14px;
}

.command-section {
  margin-top: 28px;
}

.command-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.command-btn {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: var(--bg-primary);
  border-radius: 14px;
  transition: background 0.2s;
}

.command-btn:active {
  background: var(--gray-50);
}

.command-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.command-icon.home {
  background: var(--primary-light);
  color: var(--primary);
}

.command-icon.stay {
  background: var(--warning-light);
  color: var(--warning);
}

.command-text {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  text-align: left;
}

.command-btn svg {
  color: var(--gray-400);
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
  height: 72px;
  background: var(--bg-primary);
  border-top: 1px solid var(--gray-100);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 8px;
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
  color: var(--gray-400);
}

.nav-item svg {
  width: 24px;
  height: 24px;
}

.nav-item span {
  font-size: 11px;
  font-weight: 500;
}

.nav-item.active {
  color: var(--primary);
}
</style>
