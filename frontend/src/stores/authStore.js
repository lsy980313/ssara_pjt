import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'

const TOKEN_KEY = 'accessToken'
const REMEMBER_KEY = 'rememberMe'

export const useAuthStore = defineStore('auth', () => {
  // ==================== State ====================
  const accessToken = ref(null)
  const isLoggedIn = computed(() => !!accessToken.value)

  // ==================== Helpers ====================

  /**
   * 스토리지에서 토큰 가져오기 (localStorage 또는 sessionStorage)
   */
  function getStoredToken() {
    return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY)
  }

  /**
   * 로그인 유지 설정 가져오기
   */
  function getRememberMe() {
    return localStorage.getItem(REMEMBER_KEY) === 'true'
  }

  /**
   * 토큰을 적절한 스토리지에 저장
   */
  function saveToken(token, rememberMe) {
    // 먼저 기존 토큰 모두 삭제
    clearAllTokens()

    if (rememberMe) {
      // 로그인 유지 체크 시: localStorage에 저장 (브라우저 꺼도 유지)
      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(REMEMBER_KEY, 'true')
    } else {
      // 체크 해제 시: sessionStorage에 저장 (브라우저 끄면 삭제)
      sessionStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(REMEMBER_KEY, 'false')
    }

    accessToken.value = token
  }

  /**
   * 모든 스토리지에서 토큰 삭제
   */
  function clearAllTokens() {
    localStorage.removeItem(TOKEN_KEY)
    sessionStorage.removeItem(TOKEN_KEY)
    accessToken.value = null
  }

  // ==================== Actions ====================

  /**
   * 앱 초기화 시 토큰 복원 (자동 로그인)
   * @returns {boolean} 토큰 존재 여부
   */
  function initAuth() {
    const storedToken = getStoredToken()
    if (storedToken) {
      accessToken.value = storedToken
      return true
    }
    return false
  }

  /**
   * 로그인 성공 시 토큰 저장
   * @param {string} token - JWT 토큰
   * @param {boolean} rememberMe - 로그인 유지 여부
   */
  function login(token, rememberMe = false) {
    saveToken(token, rememberMe)
  }

  /**
   * 로그아웃 처리
   */
  function logout() {
    clearAllTokens()
    localStorage.removeItem(REMEMBER_KEY)
    router.push('/')
  }

  /**
   * 현재 토큰 반환 (API 요청용)
   */
  function getToken() {
    return accessToken.value || getStoredToken()
  }

  return {
    // State
    accessToken,
    isLoggedIn,
    // Actions
    initAuth,
    login,
    logout,
    getToken,
    clearAllTokens
  }
})
