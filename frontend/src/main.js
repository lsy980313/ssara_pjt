// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/authStore'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 앱 시작 시 저장된 토큰 복원 (로그인 유지)
const authStore = useAuthStore()
authStore.initAuth()

app.mount('#app')