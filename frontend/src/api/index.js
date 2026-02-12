// src/api/index.js
import axios from 'axios';

// Axios 인스턴스 생성 (인증 토큰 자동 첨부)
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 요청 인터셉터: 토큰 자동 첨부 (localStorage 또는 sessionStorage)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터: 401 에러 시 로그인 페이지로 이동
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // 두 스토리지 모두에서 토큰 삭제
      localStorage.removeItem('accessToken');
      sessionStorage.removeItem('accessToken');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default api;

// API 함수들
export const memberApi = {
  // 내 정보 조회
  getMyInfo: () => api.get('/members/me'),

  // 내 정보 수정
  updateMyInfo: (data) => api.patch('/members/me', data),

  // 회원 탈퇴
  deleteAccount: () => api.delete('/members/me')
};

export const authApi = {
  // 로그인
  login: (data) => axios.post('/api/auth/login', data),

  // 회원가입
  signup: (data) => axios.post('/api/auth/signup', data),

  // 아이디(이메일) 찾기
  findEmail: (data) => axios.post('/api/auth/find-email', data),

  // 비밀번호 재설정 (직접 입력)
  resetPassword: (data) => axios.post('/api/auth/reset-password', data),

  // 임시 비밀번호 발송 (이메일)
  sendTempPassword: (data) => axios.post('/api/auth/send-temp-password', data)
};

export const notificationApi = {
  // FCM 토큰 등록/갱신
  registerToken: (fcmToken) => api.post('/notifications/token', { fcmToken }),

  // FCM 토큰 삭제 (알림 비활성화)
  deleteToken: () => api.delete('/notifications/token'),

  // 알림 설정 조회
  getSettings: () => api.get('/notifications/settings'),

  // 알림 설정 수정
  updateSettings: (settings) => api.patch('/notifications/settings', settings)
};

export const activityApi = {
  // 오늘 활동 로그 조회
  getTodayLogs: () => api.get('/activities/today'),

  // 어제 활동 로그 조회
  getYesterdayLogs: () => api.get('/activities/yesterday'),

  // 특정 날짜 활동 로그 조회
  getLogsByDate: (date) => api.get(`/activities/date/${date}`),

  // 오늘 요약 정보 조회
  getTodaySummary: () => api.get('/activities/summary/today')
};

export const robotApi = {
  // 내 로봇 조회
  getMyRobot: () => api.get('/robots/me'),

  // 내 로봇 정보 수정
  updateMyRobot: (data) => api.patch('/robots/me', data),

  // 로봇 속도 제어 (Rosbridge Protocol)
  sendVelocity: (linearX, angularZ) => api.post('/robot/control', { linearX, angularZ }),

  // 정지 (Rosbridge Protocol)
  sendStop: () => api.post('/robot/control', { linearX: 0, angularZ: 0 }),

  // 집으로 복귀
  sendHome: () => api.post('/robot/home'),

  // 좌표 이동
  sendNav: (x, y) => api.post('/robot/nav', { x, y })
};
