<template>
  <div class="screen-view" :class="{ landscape: isLandscape }" @click="toggleControls">
    <!-- 영상 배경 -->
    <img
      ref="streamImageRef"
      :src="streamUrl"
      alt="로봇 카메라"
      class="stream-bg"
      crossorigin="anonymous"
      @error="handleStreamError"
    />

    <!-- 스트림 연결 실패 시 -->
    <div v-if="streamError" class="stream-fallback">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
        <line x1="8" y1="21" x2="16" y2="21"/>
        <line x1="12" y1="17" x2="12" y2="21"/>
      </svg>
      <p>카메라 연결 대기 중...</p>
    </div>

    <!-- 상단 바 -->
    <div class="top-bar" :class="{ visible: showControls }">
      <!-- 뒤로가기 -->
      <button class="icon-btn" @click.stop="$router.back()">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>

      <!-- LIVE 뱃지 -->
      <div class="top-center">
        <span class="live-badge">
          <span class="live-dot"></span>
          LIVE
        </span>
      </div>

      <!-- 우측 상단: 맵 토글 버튼 -->
      <button class="icon-btn" @click.stop="showMap = !showMap">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/>
          <line x1="8" y1="2" x2="8" y2="18"/>
          <line x1="16" y1="6" x2="16" y2="22"/>
        </svg>
      </button>
    </div>

    <!-- 우측 상단: 투명 미니맵 오버레이 -->
    <div class="map-overlay" :class="{ visible: showMap }" @click.stop>
      <!-- 맵 모드 토글 -->
      <div class="map-tabs">
        <button
          class="map-tab"
          :class="{ active: mapMode === 'vslam' }"
          @click="mapMode = 'vslam'"
        >VSLAM</button>
        <button
          class="map-tab"
          :class="{ active: mapMode === 'kakao' }"
          @click="switchToKakao"
        >카카오맵</button>
        <button class="map-sync-btn" @click="syncKakaoMapPosition" v-if="mapMode === 'kakao'">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
        </button>
      </div>

      <!-- 맵 컨테이너 -->
      <div class="map-content" ref="miniMapContainer">
        <!-- VSLAM 그리드 맵 -->
        <div v-show="mapMode === 'vslam'" class="mini-grid-map">
          <canvas ref="miniMapCanvas" class="mini-map-canvas"></canvas>
          <div class="mini-robot-marker" :style="miniRobotMarkerStyle">
            <div class="mini-robot-dot"></div>
          </div>
        </div>
        <!-- 카카오맵 -->
        <div v-show="mapMode === 'kakao'" ref="miniKakaoMapRef" class="mini-kakao-map">
          <div v-if="!isKakaoMapReady" class="mini-map-loading">
            <span>로딩중...</span>
          </div>
        </div>
      </div>

      <!-- 좌표 표시 -->
      <div class="map-coord">
        X: {{ robotStore.robotPose.x.toFixed(2) }}m, Y: {{ robotStore.robotPose.y.toFixed(2) }}m
      </div>
    </div>

    <!-- 우측 사이드: 컨트롤 아이콘 -->
    <div class="right-controls" :class="{ visible: showControls }" @click.stop>
      <!-- 가로/세로 모드 전환 -->
      <button class="ctrl-btn" @click="toggleOrientation">
        <svg v-if="!isLandscape" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="4" y="2" width="16" height="20" rx="2" ry="2"/>
          <line x1="12" y1="18" x2="12.01" y2="18"/>
        </svg>
        <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="2" y="4" width="20" height="16" rx="2" ry="2"/>
          <line x1="18" y1="12" x2="18.01" y2="12"/>
        </svg>
        <span>{{ isLandscape ? '세로' : '가로' }}</span>
      </button>

      <!-- 사진 촬영 -->
      <button class="ctrl-btn" @click="capturePhoto">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
        <span>사진</span>
      </button>

      <!-- 녹화 -->
      <button class="ctrl-btn" :class="{ recording: isRecording }" @click="toggleRecording">
        <svg v-if="!isRecording" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="23 7 16 12 23 17 23 7"/>
          <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
        </svg>
        <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
          <rect x="6" y="6" width="12" height="12" rx="2"/>
        </svg>
        <span>{{ isRecording ? recordingTime : '녹화' }}</span>
      </button>

      <!-- 기록 보기 -->
      <button class="ctrl-btn" @click.stop="$router.push('/records')">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <circle cx="8.5" cy="8.5" r="1.5"/>
          <polyline points="21 15 16 10 5 21"/>
        </svg>
        <span>기록</span>
      </button>
    </div>

    <!-- 녹화 중 표시 -->
    <div v-if="isRecording" class="recording-indicator">
      <span class="rec-dot"></span>
      <span class="rec-text">REC</span>
      <span class="rec-time">{{ recordingTime }}</span>
    </div>

    <!-- 좌측 하단: AI비서 버튼 -->
    <button class="ai-btn" :class="{ visible: showControls }" @click.stop="showChatOverlay = !showChatOverlay">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    </button>

    <!-- AI 채팅 오버레이 -->
    <div v-if="showChatOverlay" class="chat-overlay" @click.stop>
      <!-- 헤더 -->
      <div class="chat-header">
        <span class="chat-title">AI 비서</span>
        <div class="chat-header-right">
          <div class="chat-status" :class="{ connected: isMqttConnected }">
            <span class="chat-status-dot"></span>
          </div>
          <button class="chat-close" @click="showChatOverlay = false">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 메시지 목록 -->
      <div class="chat-messages" ref="chatMessagesRef">
        <div v-if="chatMessages.length === 0" class="chat-empty">
          <p>대화가 여기에 표시됩니다</p>
        </div>
        <div
          v-for="(msg, index) in chatMessages"
          :key="index"
          :class="['chat-msg', `chat-msg-${msg.sender}`]"
        >
          <div class="chat-msg-sender">{{ getSenderName(msg.sender) }}</div>
          <div class="chat-msg-bubble">{{ msg.text }}</div>
          <div class="chat-msg-time">{{ msg.time }}</div>
        </div>
      </div>

      <!-- 입력창 -->
      <div class="chat-input-area">
        <input
          type="text"
          v-model="chatInput"
          placeholder="메시지를 입력하세요..."
          @keyup.enter="sendChatMessage"
          :disabled="!isMqttConnected"
        />
        <button class="chat-send-btn" @click="sendChatMessage" :disabled="!chatInput.trim() || !isMqttConnected">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 캡처 플래시 -->
    <div v-if="showFlash" class="capture-flash"></div>

    <!-- 토스트 -->
    <div v-if="showToast" class="toast">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive, nextTick, watch } from 'vue'
import { useRobotStore } from '@/stores/robotStore'
import { useRecordsStore } from '@/stores/recordsStore'
import { useAiAssistantStore } from '@/stores/aiAssistantStore'
import mqtt from 'mqtt'

const robotStore = useRobotStore()
const recordsStore = useRecordsStore()
const aiStore = useAiAssistantStore()

// ==================== 스트림 ====================
const STREAM_URL = '/robot-stream/stream?topic=/camera/color/image_raw&type=mjpeg&width=1280&height=720'
const streamUrl = ref(STREAM_URL)
const streamImageRef = ref(null)
const streamError = ref(false)

const handleStreamError = () => {
  streamError.value = true
}

// ==================== UI 상태 ====================
const showControls = ref(true)
const showMap = ref(false)
const mapMode = ref('vslam')
const showChatOverlay = ref(false)
const isLandscape = ref(false)
let controlTimeout = null

const toggleControls = () => {
  showControls.value = !showControls.value
  resetControlTimeout()
}

const resetControlTimeout = () => {
  if (controlTimeout) clearTimeout(controlTimeout)
  if (showControls.value) {
    controlTimeout = setTimeout(() => {
      showControls.value = false
    }, 5000)
  }
}

// ==================== 가로/세로 모드 ====================
const toggleOrientation = async () => {
  if (isLandscape.value) {
    await exitLandscape()
  } else {
    await enterLandscape()
  }
}

const enterLandscape = async () => {
  try {
    // 1) fullscreen 진입 (orientation.lock은 fullscreen 필수)
    const el = document.documentElement
    if (el.requestFullscreen) {
      await el.requestFullscreen()
    } else if (el.webkitRequestFullscreen) {
      await el.webkitRequestFullscreen()
    }

    // 2) 가로 모드 잠금
    if (screen.orientation && screen.orientation.lock) {
      await screen.orientation.lock('landscape')
    }

    isLandscape.value = true
  } catch (e) {
    console.log('가로 모드 전환 실패:', e.message)
    // fullscreen은 됐지만 lock이 실패한 경우에도 가로 상태로 표시
    if (document.fullscreenElement) {
      isLandscape.value = true
    }
  }
}

const exitLandscape = async () => {
  try {
    // 1) 방향 잠금 해제
    if (screen.orientation && screen.orientation.unlock) {
      screen.orientation.unlock()
    }

    // 2) fullscreen 해제
    if (document.fullscreenElement) {
      await document.exitFullscreen()
    }
  } catch (e) {
    console.log('세로 모드 전환 실패:', e.message)
  }
  isLandscape.value = false
}

// fullscreen 해제 감지 (ESC 키 등)
const handleFullscreenChange = () => {
  if (!document.fullscreenElement && isLandscape.value) {
    if (screen.orientation && screen.orientation.unlock) {
      screen.orientation.unlock()
    }
    isLandscape.value = false
  }
}

// ==================== 위치/좌표 ====================
const coordConfig = reactive({
  originLat: 35.20527,
  originLng: 126.8117,
  heading: 0
})
const METERS_PER_LAT = 0.000009
const METERS_PER_LNG = 0.000011

const vslamToGps = (x, y) => {
  const headingRad = (coordConfig.heading * Math.PI) / 180
  const cosH = Math.cos(headingRad)
  const sinH = Math.sin(headingRad)
  const rotatedX = x * cosH - y * sinH
  const rotatedY = x * sinH + y * cosH
  const lat = coordConfig.originLat + rotatedY * METERS_PER_LAT
  const lng = coordConfig.originLng + rotatedX * METERS_PER_LNG
  return { lat, lng }
}

const gpsCoord = computed(() => {
  const x = robotStore.robotPose.x || 0
  const y = robotStore.robotPose.y || 0
  return vslamToGps(x, y)
})

// ==================== 배터리 ====================
const currentBattery = computed(() => robotStore.robotStatus.battery || 100)

// ==================== 미니맵: VSLAM 그리드 ====================
const miniMapContainer = ref(null)
const miniMapCanvas = ref(null)
const mapConfig = { minX: -5, maxX: 5, minY: -5, maxY: 5, gridSize: 1 }

const drawMiniGrid = () => {
  const canvas = miniMapCanvas.value
  const container = miniMapContainer.value
  if (!canvas || !container) return

  canvas.width = container.offsetWidth
  canvas.height = container.offsetHeight - 30 // tabs + coord 높이 제외
  const ctx = canvas.getContext('2d')
  const { width, height } = canvas

  ctx.fillStyle = 'rgba(248, 249, 250, 0.8)'
  ctx.fillRect(0, 0, width, height)

  ctx.strokeStyle = 'rgba(200, 200, 200, 0.5)'
  ctx.lineWidth = 0.5
  const rangeX = mapConfig.maxX - mapConfig.minX
  const rangeY = mapConfig.maxY - mapConfig.minY
  const scaleX = width / rangeX
  const scaleY = height / rangeY

  for (let x = mapConfig.minX; x <= mapConfig.maxX; x += mapConfig.gridSize) {
    const px = (x - mapConfig.minX) * scaleX
    ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, height); ctx.stroke()
  }
  for (let y = mapConfig.minY; y <= mapConfig.maxY; y += mapConfig.gridSize) {
    const py = height - (y - mapConfig.minY) * scaleY
    ctx.beginPath(); ctx.moveTo(0, py); ctx.lineTo(width, py); ctx.stroke()
  }

  ctx.strokeStyle = 'rgba(150, 150, 150, 0.6)'
  ctx.lineWidth = 1
  const originX = (0 - mapConfig.minX) * scaleX
  const originY = height - (0 - mapConfig.minY) * scaleY
  ctx.beginPath(); ctx.moveTo(0, originY); ctx.lineTo(width, originY); ctx.stroke()
  ctx.beginPath(); ctx.moveTo(originX, 0); ctx.lineTo(originX, height); ctx.stroke()
}

const miniRobotMarkerStyle = computed(() => {
  const container = miniMapContainer.value
  if (!container) return { display: 'none' }
  const width = container.offsetWidth
  const height = container.offsetHeight - 30
  const rangeX = mapConfig.maxX - mapConfig.minX
  const rangeY = mapConfig.maxY - mapConfig.minY
  const x = robotStore.robotPose.x || 0
  const y = robotStore.robotPose.y || 0
  const px = ((x - mapConfig.minX) / rangeX) * width
  const py = height - ((y - mapConfig.minY) / rangeY) * height
  return { left: `${px}px`, top: `${py}px`, transform: 'translate(-50%, -50%)' }
})

// ==================== 미니맵: 카카오맵 ====================
const miniKakaoMapRef = ref(null)
const isKakaoMapReady = ref(false)
let kakaoMap = null
let robotMarkerKakao = null

const switchToKakao = () => {
  mapMode.value = 'kakao'
  nextTick(() => {
    if (!isKakaoMapReady.value) {
      initKakaoMap()
    } else if (kakaoMap) {
      kakaoMap.relayout()
    }
  })
}

const loadKakaoMapSdk = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) {
      resolve()
      return
    }
    const apiKey = import.meta.env.VITE_KAKAO_MAP_API_KEY
    if (!apiKey || apiKey === '<your-kakao-javascript-key>') {
      reject(new Error('카카오맵 API 키가 설정되지 않았습니다.'))
      return
    }
    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false`
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('카카오맵 SDK 로드 실패'))
    document.head.appendChild(script)
  })
}

const initKakaoMap = async () => {
  try {
    await loadKakaoMapSdk()
    if (typeof window.kakao === 'undefined' || !window.kakao.maps) return
    window.kakao.maps.load(() => {
      createKakaoMap()
    })
  } catch (error) {
    console.error('카카오맵 초기화 실패:', error.message)
  }
}

const createKakaoMap = () => {
  const container = miniKakaoMapRef.value
  if (!container) return

  try {
    const options = {
      center: new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng),
      level: 2,
      draggable: true
    }
    kakaoMap = new window.kakao.maps.Map(container, options)

    const markerContent = `
      <div style="
        width: 14px; height: 14px;
        background: #3b82f6;
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 1px 4px rgba(0,0,0,0.3);
      "></div>
    `
    robotMarkerKakao = new window.kakao.maps.CustomOverlay({
      position: new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng),
      content: markerContent,
      yAnchor: 0.5,
      xAnchor: 0.5
    })
    robotMarkerKakao.setMap(kakaoMap)
    isKakaoMapReady.value = true

    setTimeout(() => {
      kakaoMap.relayout()
      kakaoMap.setCenter(new window.kakao.maps.LatLng(coordConfig.originLat, coordConfig.originLng))
    }, 100)
  } catch (error) {
    console.error('카카오맵 생성 오류:', error)
  }
}

const syncKakaoMapPosition = () => {
  if (!kakaoMap || !robotMarkerKakao) return
  kakaoMap.relayout()
  const { lat, lng } = gpsCoord.value
  const position = new window.kakao.maps.LatLng(lat, lng)
  robotMarkerKakao.setPosition(position)
  kakaoMap.setCenter(position)
}

// ==================== 사진 촬영 ====================
const showFlash = ref(false)
const showToast = ref(false)
const toastMessage = ref('')

const toast = (msg) => {
  toastMessage.value = msg
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 2500)
}

const capturePhoto = () => {
  const img = streamImageRef.value
  if (!img) return

  showFlash.value = true
  setTimeout(() => { showFlash.value = false }, 200)

  try {
    const canvas = document.createElement('canvas')
    canvas.width = img.naturalWidth || 1280
    canvas.height = img.naturalHeight || 720
    const ctx = canvas.getContext('2d')
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9)
    recordsStore.addPhoto(dataUrl)
    toast('사진이 기록에 저장되었습니다')
  } catch (error) {
    console.error('사진 촬영 실패:', error)
    toast('사진 저장에 실패했습니다')
  }
}

// ==================== 녹화 (MediaRecorder → WebM) ====================
const isRecording = ref(false)
const recordingTime = ref('00:00')
let recordingSeconds = 0
let timeInterval = null
let mediaRecorder = null
let recordedChunks = []
let recordCanvas = null
let recordCtx = null
let drawFrameInterval = null

const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = () => {
  const img = streamImageRef.value
  if (!img) {
    toast('카메라 스트림이 없습니다')
    return
  }

  // 녹화용 캔버스 생성
  recordCanvas = document.createElement('canvas')
  recordCanvas.width = 640
  recordCanvas.height = 360
  recordCtx = recordCanvas.getContext('2d')

  // 첫 프레임 그리기
  try {
    recordCtx.drawImage(img, 0, 0, recordCanvas.width, recordCanvas.height)
  } catch (e) {
    console.log('첫 프레임 그리기 실패:', e)
  }

  // 캔버스에서 스트림 캡처 (10fps)
  const canvasStream = recordCanvas.captureStream(10)

  // MediaRecorder 생성
  const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
    ? 'video/webm;codecs=vp9'
    : MediaRecorder.isTypeSupported('video/webm;codecs=vp8')
      ? 'video/webm;codecs=vp8'
      : 'video/webm'

  recordedChunks = []
  mediaRecorder = new MediaRecorder(canvasStream, {
    mimeType,
    videoBitsPerSecond: 1000000 // 1Mbps
  })

  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) {
      recordedChunks.push(e.data)
    }
  }

  mediaRecorder.onstop = () => {
    const blob = new Blob(recordedChunks, { type: mimeType })
    const mins = Math.floor(recordingSeconds / 60)
    const secs = recordingSeconds % 60
    const durationStr = mins > 0 ? `${mins}:${String(secs).padStart(2, '0')}` : `0:${String(secs).padStart(2, '0')}`

    // 썸네일 캡처
    let thumbnail = ''
    try {
      const thumbCanvas = document.createElement('canvas')
      thumbCanvas.width = 320
      thumbCanvas.height = 180
      const thumbCtx = thumbCanvas.getContext('2d')
      thumbCtx.drawImage(img, 0, 0, 320, 180)
      thumbnail = thumbCanvas.toDataURL('image/jpeg', 0.7)
    } catch (e) {
      console.log('썸네일 생성 실패:', e)
    }

    recordsStore.addVideo(blob, durationStr, '', thumbnail)
    toast(`${recordingSeconds}초 녹화가 기록에 저장되었습니다`)

    recordedChunks = []
    recordingSeconds = 0
    recordingTime.value = '00:00'
  }

  // 녹화 시작
  mediaRecorder.start(1000) // 1초마다 데이터 chunk
  isRecording.value = true
  recordingSeconds = 0
  updateRecordingTime()

  // 주기적으로 스트림 이미지를 캔버스에 그리기 (100ms = 10fps)
  drawFrameInterval = setInterval(() => {
    try {
      if (img.complete && img.naturalWidth > 0) {
        recordCtx.drawImage(img, 0, 0, recordCanvas.width, recordCanvas.height)
      }
    } catch (e) { /* cross-origin 등 무시 */ }
  }, 100)

  // 시간 업데이트
  timeInterval = setInterval(() => {
    recordingSeconds++
    updateRecordingTime()
  }, 1000)

  toast('녹화가 시작되었습니다')
}

const stopRecording = () => {
  isRecording.value = false

  if (drawFrameInterval) {
    clearInterval(drawFrameInterval)
    drawFrameInterval = null
  }
  if (timeInterval) {
    clearInterval(timeInterval)
    timeInterval = null
  }
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop() // onstop에서 Blob 생성 + 저장
  }
}

const updateRecordingTime = () => {
  const mins = Math.floor(recordingSeconds / 60)
  const secs = recordingSeconds % 60
  recordingTime.value = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

// ==================== AI 채팅 (MQTT) ====================
const MQTT_BROKER = `ws://${import.meta.env.VITE_MQTT_BROKER_IP}:9001`
const TOPICS = {
  VOICE_TO_WEB: '/gae/voice_to_web',
  WEB_TO_VOICE: '/gae/web_to_voice',
  VOICE_TO_MAP: '/gae/voice_to_map',
  MAP_TO_VOICE: '/gae/map_to_voice'
}

const chatMessages = computed(() => aiStore.messages)
const chatInput = ref('')
const isMqttConnected = ref(false)
const chatMessagesRef = ref(null)
let mqttClient = null

const typeToSender = {
  user: 'user',
  robot: 'robot',
  guardian: 'guardian',
  action: 'robot',
  yolo: 'robot',
  search_request: 'robot',
  map: 'robot',
  error: 'robot'
}

const typeToMsgType = {
  user: 'voice',
  robot: 'voice',
  guardian: 'text',
  action: 'action',
  yolo: 'yolo',
  search_request: 'search',
  map: 'map',
  error: 'error'
}

const getSenderName = (sender) => {
  const names = { user: '시각장애인', robot: '로봇견', guardian: '보호자(나)' }
  return names[sender] || sender
}

const formatTime = (timestamp) => {
  if (!timestamp) {
    const now = new Date()
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  }
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const scrollChatToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

const connectMqtt = () => {
  mqttClient = mqtt.connect(MQTT_BROKER, {
    reconnectPeriod: 3000,
    connectTimeout: 10000
  })

  mqttClient.on('connect', () => {
    isMqttConnected.value = true
    mqttClient.subscribe(TOPICS.VOICE_TO_WEB)
    mqttClient.subscribe(TOPICS.VOICE_TO_MAP)
  })

  mqttClient.on('message', (topic, message) => {
    try {
      const data = JSON.parse(message.toString())
      handleMqttMessage(topic, data)
    } catch (e) {
      console.error('MQTT 메시지 파싱 오류:', e)
    }
  })

  mqttClient.on('error', () => {
    isMqttConnected.value = false
  })

  mqttClient.on('close', () => {
    isMqttConnected.value = false
  })
}

const handleMqttMessage = (topic, data) => {
  if (topic === TOPICS.VOICE_TO_WEB) {
    const sender = typeToSender[data.type] || 'robot'
    const msgType = typeToMsgType[data.type] || 'text'
    let text = data.message || ''
    text = text.replace(/^\[(사용자|로봇|실행|YOLO|보호자|검색 요청)\]\s*/g, '')

    aiStore.addMessage({
      sender,
      text,
      type: msgType,
      time: formatTime(data.timestamp),
      timestamp: data.timestamp || new Date().toISOString()
    })
    scrollChatToBottom()
  }
}

const sendChatMessage = () => {
  if (!chatInput.value.trim() || !isMqttConnected.value) return

  const text = chatInput.value.trim()
  const now = new Date().toISOString()

  aiStore.addMessage({
    sender: 'guardian',
    text,
    type: 'text',
    time: formatTime(),
    timestamp: now
  })

  if (mqttClient && mqttClient.connected) {
    mqttClient.publish(TOPICS.WEB_TO_VOICE, text)
  }

  chatInput.value = ''
  scrollChatToBottom()
}

const disconnectMqtt = () => {
  if (mqttClient) {
    mqttClient.end()
    mqttClient = null
    isMqttConnected.value = false
  }
}

// ==================== 맵 표시 시 그리드 그리기 ====================
watch(showMap, (val) => {
  if (val && mapMode.value === 'vslam') {
    nextTick(() => drawMiniGrid())
  }
})

// 채팅 오버레이 열릴 때 최신 메시지로 스크롤
watch(showChatOverlay, (val) => {
  if (val) {
    scrollChatToBottom()
  }
})

// ==================== Lifecycle ====================
onMounted(() => {
  robotStore.connectWebSocket()
  resetControlTimeout()
  connectMqtt()
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  robotStore.disconnectWebSocket()
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  // 페이지 떠날 때 가로모드/풀스크린 해제
  if (isLandscape.value) {
    if (screen.orientation && screen.orientation.unlock) {
      screen.orientation.unlock()
    }
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {})
    }
  }
  if (controlTimeout) clearTimeout(controlTimeout)
  if (isRecording.value) stopRecording()
  disconnectMqtt()
})
</script>

<style scoped>
.screen-view {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #000;
  overflow: hidden;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

/* 영상 배경 */
.stream-bg {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.landscape .stream-bg {
  object-fit: cover;
}

.stream-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #6b7684;
  font-size: 14px;
  font-weight: 500;
}

/* 상단 바 */
.top-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  padding-top: max(12px, env(safe-area-inset-top));
  background: linear-gradient(to bottom, rgba(0,0,0,0.6), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: 20;
}

.top-bar.visible {
  opacity: 1;
  pointer-events: auto;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  transition: background 0.2s;
}

.icon-btn:active {
  background: rgba(255,255,255,0.3);
}

.top-center {
  display: flex;
  align-items: center;
}

.live-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(239, 68, 68, 0.9);
  border-radius: 16px;
  font-size: 12px;
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

/* 우측 상단: 투명 미니맵 오버레이 */
.map-overlay {
  position: absolute;
  top: 60px;
  right: 12px;
  width: 200px;
  height: 180px;
  background: rgba(0,0,0,0.35);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 12px;
  overflow: hidden;
  opacity: 0;
  transform: scale(0.9);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
  z-index: 25;
}

.map-overlay.visible {
  opacity: 1;
  transform: scale(1);
  pointer-events: auto;
}

.map-tabs {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px;
  background: rgba(0,0,0,0.3);
}

.map-tab {
  flex: 1;
  padding: 4px 8px;
  font-size: 10px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  border-radius: 6px;
  text-align: center;
  transition: all 0.2s;
}

.map-tab.active {
  background: rgba(59, 130, 246, 0.8);
  color: #fff;
}

.map-sync-btn {
  padding: 4px 6px;
  background: rgba(16, 185, 129, 0.7);
  color: #fff;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-content {
  width: 100%;
  height: calc(100% - 50px);
  position: relative;
}

.mini-grid-map {
  width: 100%;
  height: 100%;
  position: relative;
}

.mini-map-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.mini-robot-marker {
  position: absolute;
  z-index: 10;
  pointer-events: none;
}

.mini-robot-dot {
  width: 10px;
  height: 10px;
  background: #3b82f6;
  border: 2px solid white;
  border-radius: 50%;
  box-shadow: 0 1px 4px rgba(0,0,0,0.4);
}

.mini-kakao-map {
  width: 100%;
  height: 100%;
}

.mini-map-loading {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.6);
  font-size: 11px;
}

.map-coord {
  padding: 3px 8px;
  font-size: 10px;
  font-weight: 500;
  color: rgba(255,255,255,0.7);
  background: rgba(0,0,0,0.2);
  font-variant-numeric: tabular-nums;
  text-align: center;
}

/* 우측 사이드: 컨트롤 아이콘 */
.right-controls {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 8px;
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.1);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: 20;
}

.right-controls.visible {
  opacity: 1;
  pointer-events: auto;
}

.ctrl-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px;
  border-radius: 12px;
  background: rgba(255,255,255,0.1);
  color: #fff;
  transition: all 0.2s;
  min-width: 52px;
}

.ctrl-btn:active {
  transform: scale(0.93);
  background: rgba(255,255,255,0.25);
}

.ctrl-btn span {
  font-size: 10px;
  font-weight: 600;
}

.ctrl-btn.recording {
  background: rgba(239, 68, 68, 1);
  animation: recordPulse 1s infinite;
}

@keyframes recordPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}

/* 녹화 중 표시 */
.recording-indicator {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.9);
  border-radius: 20px;
  z-index: 30;
}

.rec-dot {
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  animation: recBlink 1s infinite;
}

@keyframes recBlink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}

.rec-text {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.rec-time {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  font-variant-numeric: tabular-nums;
}

/* 좌측 하단: AI비서 버튼 */
.ai-btn {
  position: absolute;
  bottom: 24px;
  left: 24px;
  bottom: max(24px, env(safe-area-inset-bottom));
  width: 52px;
  height: 52px;
  background: rgba(49, 130, 246, 0.85);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 20px rgba(49, 130, 246, 0.4);
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 20;
}

.ai-btn.visible {
  opacity: 1;
  transform: scale(1);
}

.ai-btn:active {
  transform: scale(0.9);
}

/* AI 채팅 오버레이 */
.chat-overlay {
  position: absolute;
  bottom: 88px;
  left: 16px;
  width: 300px;
  max-width: calc(100vw - 100px);
  height: 400px;
  max-height: calc(100vh - 160px);
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 30;
  animation: chatSlideIn 0.3s ease;
}

@keyframes chatSlideIn {
  0% { opacity: 0; transform: translateY(16px); }
  100% { opacity: 1; transform: translateY(0); }
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.chat-title {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.chat-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
}

.chat-status.connected {
  background: #10b981;
}

.chat-status-dot {
  display: none;
}

.chat-close {
  color: rgba(255,255,255,0.6);
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-close:active {
  background: rgba(255,255,255,0.1);
}

/* 채팅 메시지 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px 12px;
}

.chat-empty {
  text-align: center;
  padding: 30px 10px;
  color: rgba(255,255,255,0.4);
  font-size: 12px;
}

.chat-msg {
  margin-bottom: 10px;
}

.chat-msg-sender {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255,255,255,0.5);
  margin-bottom: 3px;
}

.chat-msg-bubble {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.4;
  max-width: 90%;
  word-break: break-word;
}

.chat-msg-user .chat-msg-bubble {
  background: rgba(59, 130, 246, 0.5);
  color: #fff;
  border-radius: 12px 12px 12px 4px;
}

.chat-msg-robot .chat-msg-bubble {
  background: rgba(139, 92, 246, 0.5);
  color: #fff;
  border-radius: 12px 12px 12px 4px;
}

.chat-msg-guardian {
  text-align: right;
}

.chat-msg-guardian .chat-msg-sender {
  text-align: right;
}

.chat-msg-guardian .chat-msg-bubble {
  background: rgba(16, 185, 129, 0.6);
  color: #fff;
  border-radius: 12px 12px 4px 12px;
}

.chat-msg-time {
  font-size: 9px;
  color: rgba(255,255,255,0.3);
  margin-top: 2px;
}

.chat-msg-guardian .chat-msg-time {
  text-align: right;
}

/* 채팅 입력 */
.chat-input-area {
  display: flex;
  gap: 8px;
  padding: 8px 10px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.chat-input-area input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 20px;
  background: rgba(255,255,255,0.1);
  color: #fff;
  font-size: 13px;
  outline: none;
}

.chat-input-area input::placeholder {
  color: rgba(255,255,255,0.4);
}

.chat-input-area input:focus {
  border-color: rgba(59, 130, 246, 0.6);
}

.chat-input-area input:disabled {
  opacity: 0.4;
}

.chat-send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.8);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.chat-send-btn:active:not(:disabled) {
  transform: scale(0.9);
}

.chat-send-btn:disabled {
  opacity: 0.3;
}

/* 캡처 플래시 */
.capture-flash {
  position: absolute;
  inset: 0;
  background: #fff;
  animation: flash 0.2s ease-out;
  pointer-events: none;
  z-index: 50;
}

@keyframes flash {
  0% { opacity: 0.8; }
  100% { opacity: 0; }
}

/* 토스트 */
.toast {
  position: absolute;
  bottom: 90px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(32, 201, 151, 0.9);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  animation: toastIn 0.3s ease;
  z-index: 40;
  white-space: nowrap;
}

@keyframes toastIn {
  0% { opacity: 0; transform: translate(-50%, 16px); }
  100% { opacity: 1; transform: translate(-50%, 0); }
}

/* ==================== 가로 모드 레이아웃 ==================== */

/* 컨트롤: 우측 세로 → 하단 가로 */
.landscape .right-controls {
  right: auto;
  top: auto;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  flex-direction: row;
  gap: 12px;
  padding: 8px 16px;
  border-radius: 20px;
}

.landscape .ctrl-btn {
  flex-direction: row;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 10px;
  min-width: auto;
}

.landscape .ctrl-btn svg {
  width: 18px;
  height: 18px;
}

.landscape .ctrl-btn span {
  font-size: 11px;
}

/* AI버튼: 좌하단 → 우하단 */
.landscape .ai-btn {
  left: auto;
  right: 16px;
  bottom: 16px;
  width: 44px;
  height: 44px;
}

/* 미니맵: 우상단 유지, 약간 더 크게 */
.landscape .map-overlay {
  top: 56px;
  right: 12px;
  width: 220px;
  height: 160px;
}

/* 채팅 오버레이: 우측으로 이동 */
.landscape .chat-overlay {
  left: auto;
  right: 72px;
  bottom: 16px;
  width: 320px;
  height: 280px;
  max-height: calc(100vh - 80px);
}

/* 녹화 표시: 위치 유지 */
.landscape .recording-indicator {
  top: 12px;
}

/* 토스트: 하단 컨트롤 위로 */
.landscape .toast {
  bottom: 80px;
}
</style>
