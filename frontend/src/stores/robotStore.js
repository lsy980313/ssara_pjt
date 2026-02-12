import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Client } from '@stomp/stompjs'
import { robotApi } from '@/api'

export const useRobotStore = defineStore('robot', () => {
  // ==================== State ====================
  const robotStatus = ref({
    battery: 100,
    state: 'UNKNOWN',
    isOnline: false
  })

  const robotPose = ref({
    x: 0,
    y: 0,
    theta: 0
  })

  // 일일 요약 (산책시간, 이상감지 등)
  const dailySummary = ref({
    walkTime: 0,
    alerts: 0,
    distance: 0,
    totalEvents: 0
  })

  // 최근 활동 로그
  const activityLogs = ref([])

  // ==================== VSLAM → GPS 변환 ====================
  const VSLAM_ORIGIN_LAT = 35.20527
  const VSLAM_ORIGIN_LNG = 126.8117
  const VSLAM_HEADING = 0
  const METERS_PER_LAT = 0.000009
  const METERS_PER_LNG = 0.000011

  function vslamToGps(x, y) {
    const headingRad = (VSLAM_HEADING * Math.PI) / 180
    const cosH = Math.cos(headingRad)
    const sinH = Math.sin(headingRad)
    const rotatedX = x * cosH - y * sinH
    const rotatedY = x * sinH + y * cosH
    return {
      lat: VSLAM_ORIGIN_LAT + rotatedY * METERS_PER_LAT,
      lng: VSLAM_ORIGIN_LNG + rotatedX * METERS_PER_LNG
    }
  }

  function getGpsCoord() {
    return vslamToGps(robotPose.value.x || 0, robotPose.value.y || 0)
  }

  const isConnected = ref(false)
  const vslamConnected = ref(false)
  let stompClient = null
  let vslamTimeout = null

  // ==================== Actions ====================

  /**
   * WebSocket 연결 및 토픽 구독
   * robot/pose 데이터는 MQTT → 백엔드 → WebSocket 경로로 수신
   */
  function connectWebSocket() {
    // 이미 연결되어 있으면 무시
    if (stompClient && isConnected.value) {
      return
    }

    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken')

    stompClient = new Client({
      brokerURL: 'ws://localhost:8080/ws/websocket',
      connectHeaders: {
        Authorization: `Bearer ${token}`
      },
      reconnectDelay: 5000,
      heartbeatIncoming: 4000,
      heartbeatOutgoing: 4000,

      onConnect: () => {
        isConnected.value = true

        // robot/status 구독
        stompClient.subscribe('/topic/robot/status', (message) => {
          try {
            const data = JSON.parse(message.body)
            robotStatus.value = {
              battery: data.battery ?? 0,
              state: data.state ?? 'UNKNOWN',
              isOnline: data.isOnline ?? false
            }
          } catch (e) {
            console.error('Status 파싱 오류:', e)
          }
        })

        // robot/pose 구독 (MQTT → 백엔드 → WebSocket)
        stompClient.subscribe('/topic/robot/pose', (message) => {
          try {
            const data = JSON.parse(message.body)
            robotPose.value = {
              x: data.x ?? 0,
              y: data.y ?? 0,
              theta: data.theta ?? 0
            }
            if (data.state) {
              robotStatus.value.state = data.state
              robotStatus.value.isOnline = data.state === 'active'
            }
            // pose 데이터가 들어오면 VSLAM 연결 상태 활성화
            vslamConnected.value = true
            resetVslamTimeout()
          } catch (e) {
            console.error('Pose 파싱 오류:', e)
          }
        })

        // robot/summary 구독 (산책시간, 이상감지 등)
        stompClient.subscribe('/topic/robot/summary', (message) => {
          try {
            const data = JSON.parse(message.body)
            dailySummary.value = {
              walkTime: data.walkTime ?? 0,
              alerts: data.alerts ?? 0,
              distance: data.distance ?? 0,
              totalEvents: data.totalEvents ?? 0
            }
          } catch (e) {
            console.error('Summary 파싱 오류:', e)
          }
        })

        // robot/activity 구독 (이상 감지 이벤트)
        stompClient.subscribe('/topic/robot/activity', (message) => {
          try {
            const data = JSON.parse(message.body)
            const log = {
              type: data.severity === 'HIGH' ? 'warning' : 'info',
              msg: data.message ?? '알 수 없는 이벤트',
              time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
            }
            activityLogs.value.unshift(log)
            // 최대 10개 유지
            if (activityLogs.value.length > 10) {
              activityLogs.value.pop()
            }
          } catch (e) {
            console.error('Activity 파싱 오류:', e)
          }
        })
      },

      onDisconnect: () => {
        isConnected.value = false
        vslamConnected.value = false
      },

      onStompError: (frame) => {
        console.error('STOMP 오류:', frame.headers['message'])
        isConnected.value = false
      },

      onWebSocketError: (event) => {
        console.error('WebSocket 오류:', event)
        isConnected.value = false
      }
    })

    stompClient.activate()
  }

  /**
   * VSLAM 연결 상태 타임아웃 (5초간 pose 데이터 없으면 끊김 판정)
   */
  function resetVslamTimeout() {
    if (vslamTimeout) clearTimeout(vslamTimeout)
    vslamTimeout = setTimeout(() => {
      vslamConnected.value = false
    }, 5000)
  }

  /**
   * WebSocket 연결 해제
   */
  function disconnectWebSocket() {
    if (stompClient) {
      stompClient.deactivate()
      stompClient = null
      isConnected.value = false
      vslamConnected.value = false
    }
    if (vslamTimeout) {
      clearTimeout(vslamTimeout)
      vslamTimeout = null
    }
  }

  /**
   * 집으로 복귀 명령
   */
  async function sendHomeCommand() {
    const response = await robotApi.sendHome()
    return response.data
  }

  /**
   * 정지 명령 (Rosbridge Protocol)
   */
  async function sendStopCommand() {
    const response = await robotApi.sendStop()
    return response.data
  }

  /**
   * 속도 제어 명령 (Rosbridge Protocol)
   * @param {number} linearX - 전진(+)/후진(-) 속도 (-1.0 ~ 1.0)
   * @param {number} angularZ - 좌회전(+)/우회전(-) 각속도 (-1.0 ~ 1.0)
   */
  async function sendVelocityCommand(linearX, angularZ) {
    const response = await robotApi.sendVelocity(linearX, angularZ)
    return response.data
  }

  /**
   * 좌표 이동 명령
   */
  async function sendNavCommand(x, y) {
    const response = await robotApi.sendNav(x, y)
    return response.data
  }

  return {
    // State
    robotStatus,
    robotPose,
    dailySummary,
    activityLogs,
    isConnected,
    vslamConnected,
    // Actions
    connectWebSocket,
    disconnectWebSocket,
    sendHomeCommand,
    sendStopCommand,
    sendVelocityCommand,
    sendNavCommand,
    getGpsCoord
  }
})
