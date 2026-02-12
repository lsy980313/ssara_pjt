import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useAiAssistantStore = defineStore('aiAssistant', () => {
  // localStorage에서 기존 대화 기록 불러오기
  const savedMessages = localStorage.getItem('aiAssistantMessages')
  const messages = ref(savedMessages ? JSON.parse(savedMessages) : [])

  // 메시지 변경 시 localStorage에 저장
  watch(messages, (newMessages) => {
    localStorage.setItem('aiAssistantMessages', JSON.stringify(newMessages))
  }, { deep: true })

  // 메시지 추가
  function addMessage(message) {
    messages.value.push({
      ...message,
      id: Date.now()
    })

    // 최대 500개 유지 (오래된 것 삭제)
    if (messages.value.length > 500) {
      messages.value = messages.value.slice(-500)
    }
  }

  // 대화 기록 전체 삭제
  function clearMessages() {
    messages.value = []
    localStorage.removeItem('aiAssistantMessages')
  }

  // 오늘 대화만 가져오기
  function getTodayMessages() {
    const today = new Date().toDateString()
    return messages.value.filter(msg => {
      const msgDate = new Date(msg.timestamp || msg.id).toDateString()
      return msgDate === today
    })
  }

  return {
    messages,
    addMessage,
    clearMessages,
    getTodayMessages
  }
})
