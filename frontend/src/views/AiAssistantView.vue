<template>
  <div class="ai-assistant-page">
    <!-- Header -->
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
      <h1 class="header-title">AI 비서</h1>
      <div class="header-right">
        <button class="clear-btn" @click="clearChat" v-if="messages.length > 0" title="대화 기록 삭제">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
        <div class="connection-status" :class="{ connected: isConnected }">
          <span class="status-dot"></span>
          <span class="status-text">{{ isConnected ? '연결됨' : '연결 중...' }}</span>
        </div>
      </div>
    </header>

    <!-- Participants Info -->
    <div class="participants-bar">
      <div class="participant">
        <div class="participant-avatar user-avatar">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <span>시각장애인</span>
      </div>
      <div class="participant-divider">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </div>
      <div class="participant">
        <div class="participant-avatar robot-avatar">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="10" rx="2"/>
            <circle cx="12" cy="5" r="2"/>
            <path d="M12 7v4"/>
            <line x1="8" y1="16" x2="8" y2="16"/>
            <line x1="16" y1="16" x2="16" y2="16"/>
          </svg>
        </div>
        <span>로봇견</span>
      </div>
      <div class="participant-divider">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </div>
      <div class="participant">
        <div class="participant-avatar guardian-avatar">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <span>보호자(나)</span>
      </div>
    </div>

    <!-- Chat Container -->
    <main class="chat-container">
      <div class="messages-wrapper" ref="messagesWrapper">
        <!-- System Message -->
        <div class="system-message" v-if="messages.length === 0">
          <p>시각장애인과 로봇견의 대화가 여기에 표시됩니다.</p>
          <p>보호자는 텍스트로 메시지를 보낼 수 있습니다.</p>
        </div>

        <!-- Chat Messages -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', `${msg.sender}-message`]"
        >
          <div class="message-sender">
            <div :class="['sender-avatar', `${msg.sender}-avatar`]">
              <!-- 시각장애인 아이콘 -->
              <svg v-if="msg.sender === 'user'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <!-- 로봇견 아이콘 -->
              <svg v-else-if="msg.sender === 'robot'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="10" rx="2"/>
                <circle cx="12" cy="5" r="2"/>
                <path d="M12 7v4"/>
              </svg>
              <!-- 보호자 아이콘 -->
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              </svg>
            </div>
            <span class="sender-name">{{ getSenderName(msg.sender) }}</span>
            <span class="message-type" :class="msg.type" v-if="msg.type">{{ getTypeLabel(msg.type) }}</span>
            <span class="message-time">{{ msg.time }}</span>
          </div>
          <div class="message-content">
            <p>{{ msg.text }}</p>
          </div>
        </div>

        <!-- Typing Indicator -->
        <div class="message robot-message" v-if="isTyping">
          <div class="message-sender">
            <div class="sender-avatar robot-avatar">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="10" rx="2"/>
                <circle cx="12" cy="5" r="2"/>
                <path d="M12 7v4"/>
              </svg>
            </div>
            <span class="sender-name">로봇견</span>
          </div>
          <div class="message-content typing">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>

    </main>

    <!-- Scroll Down Button -->
    <button v-if="messages.length > 0" class="scroll-down-btn" @click="scrollToBottom">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="6 9 12 15 18 9"/>
      </svg>
    </button>

    <!-- Input Area -->
    <div class="input-area" :class="{ 'ai-mode-active': isAiMode }">
      <div class="input-hint" v-if="!isAiMode">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        <span>보내신 메시지는 로봇견이 음성으로 전달합니다</span>
      </div>
      <div class="ai-mode-hint" v-if="isAiMode">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <span>로봇 위치 기준으로 주변 장소를 검색합니다</span>
        <button class="ai-mode-close" @click="isAiMode = false">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      <div class="input-container">
        <button class="ai-toggle-btn" :class="{ active: isAiMode }" @click="isAiMode = !isAiMode" title="AI 장소 검색">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
          </svg>
        </button>
        <input
          type="text"
          v-model="inputText"
          :placeholder="isAiMode ? '검색할 장소를 입력하세요... (예: 빵집, 약국)' : '메시지를 입력하세요...'"
          @keyup.enter="isAiMode ? sendAiSearch() : sendMessage()"
          :disabled="!isConnected"
        />
        <button
          class="send-btn"
          :class="{ 'ai-send': isAiMode }"
          @click="isAiMode ? sendAiSearch() : sendMessage()"
          :disabled="!inputText.trim() || !isConnected"
        >
          <svg v-if="!isAiMode" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, computed } from 'vue'
import mqtt from 'mqtt'
import { useAiAssistantStore } from '@/stores/aiAssistantStore'
import { useRobotStore } from '@/stores/robotStore'
import api from '@/api/index.js'

// MQTT 설정
const MQTT_BROKER = `ws://${import.meta.env.VITE_MQTT_BROKER_IP}:9001`
const TOPICS = {
  VOICE_TO_WEB: '/gae/voice_to_web',      // 구독: 대화 내용 수신
  WEB_TO_VOICE: '/gae/web_to_voice',      // 발행: 보호자 메시지
  VOICE_TO_MAP: '/gae/voice_to_map',      // 구독: 위치 검색 요청
  MAP_TO_VOICE: '/gae/map_to_voice'       // 발행: 지도 결과
}

const aiStore = useAiAssistantStore()
const robotStore = useRobotStore()
const messages = computed(() => aiStore.messages)
const inputText = ref('')
const isConnected = ref(false)
const isTyping = ref(false)
const isAiMode = ref(false)
const isAiSearching = ref(false)
const messagesWrapper = ref(null)
const showScrollBtn = ref(false)

let mqttClient = null

// type → sender 매핑
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

// type → 메시지 유형
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
  const names = {
    user: '시각장애인',
    robot: '로봇견',
    guardian: '보호자(나)'
  }
  return names[sender] || sender
}

const getTypeLabel = (type) => {
  const labels = {
    voice: '음성',
    text: '텍스트',
    action: '실행',
    yolo: 'YOLO',
    search: '검색',
    map: '지도',
    error: '오류'
  }
  return labels[type] || type
}

const formatTime = (timestamp) => {
  if (!timestamp) {
    const now = new Date()
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  }
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesWrapper.value) {
      messagesWrapper.value.scrollTo({
        top: messagesWrapper.value.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
}

// MQTT 연결
const connectMqtt = () => {
  console.log('MQTT 연결 시도:', MQTT_BROKER)

  mqttClient = mqtt.connect(MQTT_BROKER, {
    reconnectPeriod: 3000,
    connectTimeout: 10000
  })

  mqttClient.on('connect', () => {
    console.log('✅ MQTT 연결 성공')
    isConnected.value = true

    // 토픽 구독
    mqttClient.subscribe(TOPICS.VOICE_TO_WEB, (err) => {
      if (err) console.error('voice_to_web 구독 실패:', err)
      else console.log('📥 구독:', TOPICS.VOICE_TO_WEB)
    })

    mqttClient.subscribe(TOPICS.VOICE_TO_MAP, (err) => {
      if (err) console.error('voice_to_map 구독 실패:', err)
      else console.log('📥 구독:', TOPICS.VOICE_TO_MAP)
    })
  })

  mqttClient.on('message', (topic, message) => {
    try {
      const data = JSON.parse(message.toString())
      console.log('📨 수신:', topic, data)

      handleIncomingMessage(topic, data)
    } catch (e) {
      console.error('메시지 파싱 오류:', e)
    }
  })

  mqttClient.on('error', (err) => {
    console.error('❌ MQTT 오류:', err)
    isConnected.value = false
  })

  mqttClient.on('close', () => {
    console.log('MQTT 연결 종료')
    isConnected.value = false
  })

  mqttClient.on('reconnect', () => {
    console.log('MQTT 재연결 시도...')
  })
}

// 수신 메시지 처리
const handleIncomingMessage = (topic, data) => {
  if (topic === TOPICS.VOICE_TO_WEB) {
    // 대화 메시지
    const sender = typeToSender[data.type] || 'robot'
    const msgType = typeToMsgType[data.type] || 'text'

    // [사용자], [로봇] 등 접두어 제거
    let text = data.message || ''
    text = text.replace(/^\[(사용자|로봇|실행|YOLO|보호자|검색 요청)\]\s*/g, '')

    aiStore.addMessage({
      sender,
      text,
      type: msgType,
      time: formatTime(data.timestamp),
      timestamp: data.timestamp || new Date().toISOString()
    })
    scrollToBottom()

  } else if (topic === TOPICS.VOICE_TO_MAP) {
    console.log('🗺️ 위치 검색 요청:', data.message)
    if (isLocationQuery(data.message)) {
      handleLocationQuery(data.message)
    } else {
      searchNearbyPlaces(data.message)
    }
  }
}

// 보호자 메시지 전송
const sendMessage = () => {
  if (!inputText.value.trim() || !isConnected.value) return

  const text = inputText.value.trim()
  const now = new Date().toISOString()

  // store에 저장 (localStorage에도 자동 저장됨)
  aiStore.addMessage({
    sender: 'guardian',
    text,
    type: 'text',
    time: formatTime(),
    timestamp: now
  })

  // MQTT로 전송 (Plain Text)
  if (mqttClient && mqttClient.connected) {
    mqttClient.publish(TOPICS.WEB_TO_VOICE, text)
    console.log('📤 보호자 메시지 전송:', text)
  }

  inputText.value = ''
  scrollToBottom()
}

// 보호자 AI 장소 검색
const sendAiSearch = async () => {
  if (!inputText.value.trim() || !isConnected.value) return
  const query = inputText.value.trim()
  inputText.value = ''

  // 보호자 검색 요청 메시지 표시
  aiStore.addMessage({
    sender: 'guardian',
    text: `"${query}" 검색 중...`,
    type: 'search',
    time: formatTime(),
    timestamp: new Date().toISOString()
  })
  scrollToBottom()

  isAiSearching.value = true
  try {
    if (isLocationQuery(query)) {
      await handleLocationQuery(query)
    } else {
      await searchNearbyPlaces(query)
    }
  } finally {
    isAiSearching.value = false
  }
}

// GMS (GPT)로 자연어 → 검색 키워드 추출
const extractKeyword = async (naturalText) => {
  try {
    const { data } = await api.post('/proxy/gms/chat', {
      model: 'gpt-4.1-mini',
      messages: [
        {
          role: 'system',
          content: '사용자의 자연어에서 카카오맵 장소 검색 키워드를 추출하세요. 키워드만 출력하세요. 예: "밥 먹을 데" → "음식점", "커피 마시고 싶어" → "카페", "약 사야 해" → "약국"'
        },
        {
          role: 'user',
          content: naturalText
        }
      ],
      maxTokens: 20,
      temperature: 0
    })
    const keyword = data.choices?.[0]?.message?.content?.trim()
    console.log(`🤖 GPT 키워드 추출: "${naturalText}" → "${keyword}"`)
    return keyword || naturalText
  } catch (e) {
    console.error('GPT 키워드 추출 실패, 로컬 추출 시도:', e)
    return extractKeywordLocal(naturalText)
  }
}

// GPT 실패 시 로컬 키워드 추출 (조사/동사 제거)
const extractKeywordLocal = (text) => {
  const stopWords = ['근처', '주변', '어디', '어딨', '있는', '알려줘', '알려', '찾아줘', '찾아', '가고싶', '싶어', '가까운', '에서', '좀', '나', '나한테', '여기', '이', '저', '그', '을', '를', '이', '가', '은', '는', '에', '의', '도', '와', '과', '하고', '해줘', '해', '줘', '요', '있나', '있어', '어딘지', '어디에']
  const words = text.replace(/[?.!,]/g, '').split(/\s+/)
  const filtered = words.filter(w => !stopWords.includes(w) && w.length > 0)
  const keyword = filtered.join(' ') || text
  console.log(`🔧 로컬 키워드 추출: "${text}" → "${keyword}"`)
  return keyword
}

// 로봇 방향 기준으로 장소의 상대 방향 계산
const calcDirection = (robotLat, robotLng, robotTheta, placeLat, placeLng) => {
  const angleToPlace = Math.atan2(placeLng - robotLng, placeLat - robotLat)
  let relative = angleToPlace - robotTheta
  // -PI ~ PI 범위로 정규화
  while (relative > Math.PI) relative -= 2 * Math.PI
  while (relative < -Math.PI) relative += 2 * Math.PI

  const deg = (relative * 180) / Math.PI
  if (deg > -30 && deg < 30) return '앞쪽'
  if (deg >= 30 && deg < 150) return '오른쪽'
  if (deg <= -30 && deg > -150) return '왼쪽'
  return '뒤쪽'
}

// GPT로 시각장애인 친화적 안내 생성
const generateGuide = async (question, placesInfo) => {
  try {
    const { data } = await api.post('/proxy/gms/chat', {
      model: 'gpt-4.1-mini',
      messages: [
        {
          role: 'system',
          content: '시각장애인에게 주변 장소를 안내하는 도우미입니다. 로봇이 바라보는 방향 기준으로 왼쪽/오른쪽/앞쪽 방향과 걸음 수(1걸음=약 0.7m)로 안내하세요. 짧고 따뜻하게 말하세요. 가장 가까운 곳을 먼저 안내하세요.'
        },
        {
          role: 'user',
          content: `질문: "${question}"\n\n검색 결과:\n${placesInfo.map((p, i) => `${i + 1}. ${p.name} - ${p.direction} ${p.distance}m (약 ${p.steps}걸음), 주소: ${p.address}`).join('\n')}`
        }
      ],
      maxTokens: 200,
      temperature: 0.7
    })
    return data.choices?.[0]?.message?.content?.trim() || placesInfo.map(p => `${p.name} ${p.direction} ${p.distance}m`).join(', ')
  } catch (e) {
    console.error('GPT 안내 생성 실패:', e)
    return placesInfo.map(p => `${p.direction} ${p.distance}m에 ${p.name}`).join(', ')
  }
}

// 현재 위치 질문 감지
const isLocationQuery = (text) => {
  const patterns = ['여기 어디', '현재 위치', '어디에 있', '어디야', '어디예요', '어디에요', '위치 알려', '위치가 어디', '지금 어디', '여긴 어디', '이곳이 어디', '어디쯤', '어디인지', '위치를 알려', '내 위치', '내가 어디']
  return patterns.some(p => text.includes(p))
}

// 카카오 역지오코딩: GPS 좌표 → 주소
const reverseGeocode = async (lat, lng) => {
  try {
    const { data } = await api.get('/proxy/kakao/geocode', {
      params: { lat, lng }
    })
    if (data.documents && data.documents.length > 0) {
      const doc = data.documents[0]
      if (doc.road_address) {
        return doc.road_address.address_name
      }
      return doc.address?.address_name || null
    }
  } catch (e) {
    console.error('역지오코딩 실패:', e)
  }
  return null
}

// 현재 위치 안내 응답
const handleLocationQuery = async (message) => {
  const { lat, lng } = robotStore.getGpsCoord()
  console.log(`📍 현재 위치 조회: (${lat.toFixed(5)}, ${lng.toFixed(5)})`)

  const address = await reverseGeocode(lat, lng)

  let resultText
  if (address) {
    resultText = `현재 위치는 ${address} 근처입니다.`
  } else {
    resultText = `현재 GPS 좌표는 (${lat.toFixed(5)}, ${lng.toFixed(5)})이지만, 정확한 주소를 확인할 수 없습니다.`
  }

  aiStore.addMessage({
    sender: 'robot',
    text: resultText,
    type: 'map',
    time: formatTime(),
    timestamp: new Date().toISOString()
  })
  scrollToBottom()
  sendMapResult(resultText)
}

// 카카오 로컬 API로 주변 장소 검색
const searchNearbyPlaces = async (message) => {
  // 1단계: GPT로 자연어 → 검색 키워드 변환
  const keyword = await extractKeyword(message)

  const { lat, lng } = robotStore.getGpsCoord()
  const theta = robotStore.robotPose.theta || 0
  console.log(`🗺️ 검색: "${message}" → "${keyword}" @ (${lat.toFixed(5)}, ${lng.toFixed(5)}) θ=${theta.toFixed(2)}`)

  try {
    const { data } = await api.get('/proxy/kakao/search', {
      params: { query: keyword, lat, lng, radius: 2000, sort: 'distance' }
    })

    let resultText
    if (data.documents && data.documents.length > 0) {
      // 2단계: 방향 계산 + GPT 안내 생성
      const placesInfo = data.documents.slice(0, 3).map(place => {
        const dist = parseInt(place.distance) || 0
        const direction = calcDirection(lat, lng, theta, parseFloat(place.y), parseFloat(place.x))
        return {
          name: place.place_name,
          distance: dist,
          steps: Math.round(dist / 0.7),
          direction,
          address: place.road_address_name || place.address_name
        }
      })

      resultText = await generateGuide(message, placesInfo)
    } else {
      resultText = `"${keyword}" 근처 검색 결과가 없습니다.`
    }

    // 채팅에 표시
    aiStore.addMessage({
      sender: 'robot',
      text: resultText,
      type: 'map',
      time: formatTime(),
      timestamp: new Date().toISOString()
    })
    scrollToBottom()

    // MQTT로 음성 AI에 결과 전송
    sendMapResult(resultText)
  } catch (e) {
    console.error('장소 검색 실패:', e)
    sendMapResult(`장소 검색 중 오류가 발생했습니다.`)
  }
}

// 지도 검색 결과 전송 (외부에서 호출 가능)
const sendMapResult = (result) => {
  if (mqttClient && mqttClient.connected) {
    mqttClient.publish(TOPICS.MAP_TO_VOICE, result)
    console.log('📤 지도 결과 전송:', result)
  }
}

// MQTT 연결 해제
const disconnectMqtt = () => {
  if (mqttClient) {
    mqttClient.end()
    mqttClient = null
    isConnected.value = false
    console.log('MQTT 연결 해제')
  }
}

const onMessagesScroll = () => {
  if (!messagesWrapper.value) return
  const el = messagesWrapper.value
  const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
  showScrollBtn.value = distanceFromBottom > 100
}

onMounted(() => {
  connectMqtt()
  scrollToBottom()
  setTimeout(() => scrollToBottom(), 300)
  if (messagesWrapper.value) {
    messagesWrapper.value.addEventListener('scroll', onMessagesScroll)
  }
})

onUnmounted(() => {
  disconnectMqtt()
  if (messagesWrapper.value) {
    messagesWrapper.value.removeEventListener('scroll', onMessagesScroll)
  }
})

// 대화 기록 삭제
const clearChat = () => {
  if (confirm('대화 기록을 모두 삭제하시겠습니까?')) {
    aiStore.clearMessages()
  }
}

// 외부에서 사용할 수 있도록 expose
defineExpose({ sendMapResult })
</script>

<style scoped>
.ai-assistant-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  background: #f5f5f5;
  overflow: hidden;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fff;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #333;
  border-radius: 8px;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #f5f5f5;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: #191f28;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.clear-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #8b95a1;
  border-radius: 8px;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #fee2e2;
  color: #dc2626;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #fef3c7;
  border-radius: 20px;
}

.connection-status.connected {
  background: #d1fae5;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
  animation: pulse 1.5s infinite;
}

.connection-status.connected .status-dot {
  background: #10b981;
  animation: none;
}

.status-text {
  font-size: 12px;
  font-weight: 600;
  color: #92400e;
}

.connection-status.connected .status-text {
  color: #065f46;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Participants Bar */
.participants-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #eee;
}

.participant {
  display: flex;
  align-items: center;
  gap: 6px;
}

.participant span {
  font-size: 12px;
  font-weight: 600;
  color: #6b7684;
}

.participant-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.user-avatar {
  background: #3b82f6;
}

.robot-avatar {
  background: #8b5cf6;
}

.guardian-avatar {
  background: #10b981;
}

.participant-divider {
  color: #d1d5db;
}

/* Chat Container */
.chat-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.scroll-down-btn {
  position: fixed;
  bottom: 110px;
  right: 20px;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: #10b981;
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 15;
  box-shadow: 0 2px 10px rgba(16, 185, 129, 0.4);
  transition: transform 0.2s;
}

.scroll-down-btn:active {
  transform: scale(0.9);
}

.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  padding-bottom: 20px;
}

/* System Message */
.system-message {
  text-align: center;
  padding: 40px 20px;
  color: #8b95a1;
}

.system-message p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
}

.system-message p + p {
  margin-top: 4px;
}

/* Messages */
.message {
  margin-bottom: 16px;
  max-width: 85%;
}

.user-message {
  margin-right: auto;
}

.robot-message {
  margin-right: auto;
}

.guardian-message {
  margin-left: auto;
}

.message-sender {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.guardian-message .message-sender {
  flex-direction: row-reverse;
}

.sender-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.sender-name {
  font-size: 12px;
  font-weight: 600;
  color: #6b7684;
}

.message-type {
  font-size: 10px;
  padding: 2px 6px;
  background: #f3f4f6;
  border-radius: 4px;
  color: #8b95a1;
}

.message-type.voice {
  background: #dbeafe;
  color: #1d4ed8;
}

.message-type.action {
  background: #fef3c7;
  color: #b45309;
}

.message-type.yolo {
  background: #fee2e2;
  color: #dc2626;
}

.message-type.search {
  background: #d1fae5;
  color: #059669;
}

.message-type.map {
  background: #e0e7ff;
  color: #4f46e5;
}

.message-type.error {
  background: #fecaca;
  color: #b91c1c;
}

.message-time {
  font-size: 11px;
  color: #adb5bd;
}

.message-content {
  background: #fff;
  padding: 12px 16px;
  border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.user-message .message-content {
  background: #dbeafe;
  border-radius: 16px 16px 16px 4px;
}

.robot-message .message-content {
  background: #ede9fe;
  border-radius: 16px 16px 16px 4px;
}

.guardian-message .message-content {
  background: #10b981;
  color: #fff;
  border-radius: 16px 16px 4px 16px;
}

.message-content p {
  margin: 0;
  font-size: 15px;
  line-height: 1.5;
}

/* Typing Animation */
.message-content.typing {
  display: flex;
  gap: 4px;
  padding: 16px 20px;
}

.dot {
  width: 8px;
  height: 8px;
  background: #8b5cf6;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Input Area */
.input-area {
  flex-shrink: 0;
  background: #fff;
  padding: 12px 20px 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
  border-top: 1px solid #eee;
}

.input-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-bottom: 10px;
  color: #8b95a1;
}

.input-hint span {
  font-size: 12px;
}

.input-container {
  display: flex;
  gap: 12px;
  max-width: 600px;
  margin: 0 auto;
}

.input-container input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e5e5e5;
  border-radius: 24px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.input-container input:focus {
  border-color: #10b981;
}

.input-container input::placeholder {
  color: #aaa;
}

.input-container input:disabled {
  background: #f5f5f5;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #10b981;
  border: none;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.1s;
}

.send-btn:hover:not(:disabled) {
  background: #059669;
}

.send-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.send-btn.ai-send {
  background: #8b5cf6;
}

.send-btn.ai-send:hover:not(:disabled) {
  background: #7c3aed;
}

/* AI Toggle Button */
.ai-toggle-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #f3f4f6;
  border: 2px solid transparent;
  color: #8b95a1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.ai-toggle-btn:active {
  transform: scale(0.92);
}

.ai-toggle-btn.active {
  background: #ede9fe;
  border-color: #8b5cf6;
  color: #8b5cf6;
}

/* AI Mode Hint */
.ai-mode-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-bottom: 10px;
  color: #7c3aed;
  background: #ede9fe;
  border-radius: 8px;
  padding: 8px 12px;
}

.ai-mode-hint span {
  font-size: 12px;
  font-weight: 600;
  flex: 1;
}

.ai-mode-close {
  background: none;
  border: none;
  color: #8b5cf6;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.ai-mode-close:hover {
  background: rgba(139, 92, 246, 0.15);
}

/* AI Mode Active Border */
.input-area.ai-mode-active {
  border-top: 2px solid #8b5cf6;
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .messages-wrapper {
    padding: 16px;
  }

  .message {
    max-width: 90%;
  }

  .participants-bar {
    gap: 4px;
    padding: 10px 12px;
  }

  .participant span {
    font-size: 11px;
  }

  .participant-avatar {
    width: 24px;
    height: 24px;
  }

  .participant-divider svg {
    width: 16px;
    height: 16px;
  }
}
</style>
