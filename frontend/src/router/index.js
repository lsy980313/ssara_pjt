// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import SignupView from '../views/SignupView.vue'
import ProfileView from '../views/ProfileView.vue'
import LocationView from '../views/LocationView.vue'
import HistoryView from '../views/HistoryView.vue'
import NoticesView from '../views/NoticesView.vue'
import InquiriesView from '../views/InquiriesView.vue'
import ScreenView from '../views/ScreenView.vue'
import HealthcareView from '../views/HealthcareView.vue'
import FeaturesView from '../views/FeaturesView.vue'
import HelpView from '../views/HelpView.vue'
import BatteryView from '../views/BatteryView.vue'
import NavigationView from '../views/NavigationView.vue'
import RecordsView from '../views/RecordsView.vue'
import AiAssistantView from '../views/AiAssistantView.vue'
import MemoView from '../views/MemoView.vue'
import CommunityView from '../views/CommunityView.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/signup',
    name: 'Signup',
    component: SignupView
  },
  {
    path: '/home',
    name: 'Home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/location',
    name: 'Location',
    component: LocationView,
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryView,
    meta: { requiresAuth: true }
  },
  {
    path: '/notices',
    name: 'Notices',
    component: NoticesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/inquiries',
    name: 'Inquiries',
    component: InquiriesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/screen',
    name: 'Screen',
    component: ScreenView,
    meta: { requiresAuth: true }
  },
  {
    path: '/healthcare',
    name: 'Healthcare',
    component: HealthcareView,
    meta: { requiresAuth: true }
  },
  {
    path: '/features',
    name: 'Features',
    component: FeaturesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/help',
    name: 'Help',
    component: HelpView,
    meta: { requiresAuth: true }
  },
  {
    path: '/battery',
    name: 'Battery',
    component: BatteryView,
    meta: { requiresAuth: true }
  },
  {
    path: '/navigation',
    name: 'Navigation',
    component: NavigationView,
    meta: { requiresAuth: true }
  },
  {
    path: '/records',
    name: 'Records',
    component: RecordsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-assistant',
    name: 'AiAssistant',
    component: AiAssistantView,
    meta: { requiresAuth: true }
  },
  {
    path: '/memo',
    name: 'Memo',
    component: MemoView,
    meta: { requiresAuth: true }
  },
  {
    path: '/community',
    name: 'Community',
    component: CommunityView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 네비게이션 가드: 인증 필요한 페이지 보호
router.beforeEach((to, from, next) => {
  // localStorage 또는 sessionStorage에서 토큰 확인
  const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken')

  if (to.meta.requiresAuth && !token) {
    // 인증 필요한 페이지인데 토큰 없으면 로그인으로
    next('/')
  } else if ((to.path === '/' || to.path === '/signup') && token) {
    // 로그인/회원가입 페이지인데 토큰 있으면 홈으로
    next('/home')
  } else {
    next()
  }
})

export default router
