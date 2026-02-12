import { reactive } from 'vue';
import { robotApi } from './api/index.js';

export const robotState = reactive({
  name: '',
  status: 'OFFLINE', // ONLINE, OFFLINE
  battery: 100,
  location: '',
  logs: [],

  // 서버에서 로봇 데이터 로드
  async fetchRobot() {
    try {
      const response = await robotApi.getMyRobot();
      const data = response.data;
      this.name = data.name || '';
      this.status = data.status || 'OFFLINE';
      this.battery = data.battery || 100;
      this.location = data.location || '위치 정보 없음';
      return true;
    } catch (error) {
      console.error('로봇 정보 로드 실패:', error);
      return false;
    }
  },

  // 로봇 상태를 업데이트하는 함수
  updateStatus(data) {
    if (data.battery !== undefined) this.battery = data.battery;
    if (data.status !== undefined) this.status = data.status;
  },

  // 로그 추가 함수
  addLog(msg, type = 'info') {
    const time = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
    this.logs.unshift({ time, msg, type });
  },

  // 상태 초기화 (로그아웃 시)
  reset() {
    this.name = '';
    this.status = 'OFFLINE';
    this.battery = 100;
    this.location = '';
    this.logs = [];
  }
});
