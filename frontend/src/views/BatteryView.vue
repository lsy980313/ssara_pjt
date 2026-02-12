<template>
  <div class="battery-view">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <h1 class="header-title">배터리 상태</h1>
      <div class="header-spacer"></div>
    </header>

    <main class="content">
      <!-- 배터리 메인 카드 -->
      <section class="battery-main-card">
        <div class="battery-visual">
          <div class="battery-circle" :class="batteryClass">
            <svg class="progress-ring" viewBox="0 0 120 120">
              <circle
                class="progress-ring-bg"
                cx="60"
                cy="60"
                r="52"
                fill="none"
                stroke-width="12"
              />
              <circle
                class="progress-ring-fill"
                :class="batteryClass"
                cx="60"
                cy="60"
                r="52"
                fill="none"
                stroke-width="12"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="strokeDashoffset"
              />
            </svg>
            <div class="battery-percent-large">
              <span class="percent-value">{{ currentBattery }}</span>
              <span class="percent-sign">%</span>
            </div>
          </div>
        </div>

        <div class="battery-status-text">
          <span class="status-label" :class="batteryClass">{{ batteryStatusText }}</span>
          <p class="status-desc">{{ batteryDescription }}</p>
        </div>
      </section>

      <!-- 충전 알림 설정 -->
      <section class="alert-section">
        <h3 class="section-title">충전 알림 설정</h3>

        <!-- 알림 활성화 토글 -->
        <div class="alert-card">
          <div class="alert-info">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
            <span>배터리 부족 알림</span>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" v-model="lowBatteryAlert">
            <span class="toggle-slider"></span>
          </label>
        </div>

        <!-- 알림 퍼센트 설정 -->
        <div class="percent-setting-card" v-if="lowBatteryAlert">
          <div class="percent-header">
            <span class="percent-label">알림 받을 배터리 잔량</span>
            <span class="percent-value-display">{{ alertPercent }}%</span>
          </div>

          <!-- 슬라이더 -->
          <div class="slider-container">
            <input
              type="range"
              min="5"
              max="50"
              step="5"
              v-model="alertPercent"
              class="percent-slider"
            />
            <div class="slider-labels">
              <span>5%</span>
              <span>50%</span>
            </div>
          </div>

          <!-- 퀵 선택 버튼 -->
          <div class="quick-select">
            <button
              v-for="percent in quickPercents"
              :key="percent"
              class="quick-btn"
              :class="{ active: alertPercent == percent }"
              @click="alertPercent = percent"
            >
              {{ percent }}%
            </button>
          </div>

          <p class="setting-desc">
            배터리가 <strong>{{ alertPercent }}% 이하</strong>로 떨어지면 알림을 보내드립니다.
          </p>

          <!-- 저장 버튼 -->
          <button class="save-btn" @click="saveAlertSetting">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span>설정 저장</span>
          </button>
        </div>
      </section>

      <!-- 배터리 정보 -->
      <section class="info-section">
        <h3 class="section-title">배터리 정보</h3>
        <div class="info-cards">
          <div class="info-card">
            <div class="info-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div class="info-content">
              <span class="info-value">{{ estimatedTime }}</span>
              <span class="info-label">예상 사용 시간</span>
            </div>
          </div>

          <div class="info-card">
            <div class="info-icon charging">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
            </div>
            <div class="info-content">
              <span class="info-value">{{ chargingStatus }}</span>
              <span class="info-label">충전 상태</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 배터리 관리 팁 -->
      <section class="tips-section">
        <h3 class="section-title">배터리 관리 팁</h3>
        <div class="tips-list">
          <div class="tip-item">
            <div class="tip-number">1</div>
            <div class="tip-content">
              <h4>정기적인 충전</h4>
              <p>배터리가 20% 이하로 떨어지기 전에 충전하면 배터리 수명을 연장할 수 있습니다.</p>
            </div>
          </div>

          <div class="tip-item">
            <div class="tip-number">2</div>
            <div class="tip-content">
              <h4>적정 온도 유지</h4>
              <p>로봇을 너무 덥거나 추운 환경에 두지 마세요. 실온(15-25도)이 가장 좋습니다.</p>
            </div>
          </div>

          <div class="tip-item">
            <div class="tip-number">3</div>
            <div class="tip-content">
              <h4>완전 방전 피하기</h4>
              <p>배터리가 완전히 방전되면 배터리 성능이 저하될 수 있습니다.</p>
            </div>
          </div>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 하단 네비게이션 -->
    <nav class="bottom-nav">
      <button class="nav-item" @click="$router.push('/home')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>홈</span>
      </button>
      <button class="nav-item" @click="$router.push('/features')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <rect x="3" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="14" width="7" height="7" rx="1.5"/>
          <rect x="3" y="14" width="7" height="7" rx="1.5"/>
        </svg>
        <span>기능</span>
      </button>
      <button class="nav-item" @click="$router.push('/history')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        <span>기록</span>
      </button>
      <button class="nav-item" @click="$router.push('/help')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
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
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRobotStore } from '@/stores/robotStore';

const robotStore = useRobotStore();
const lowBatteryAlert = ref(true);
const alertPercent = ref(20);
const quickPercents = [10, 15, 20, 30, 40];

// 저장된 설정 불러오기
const loadSavedSettings = () => {
  const savedAlert = localStorage.getItem('batteryAlertEnabled');
  const savedPercent = localStorage.getItem('batteryAlertPercent');
  if (savedAlert !== null) {
    lowBatteryAlert.value = savedAlert === 'true';
  }
  if (savedPercent !== null) {
    alertPercent.value = parseInt(savedPercent);
  }
};

// 설정 저장
const saveAlertSetting = () => {
  localStorage.setItem('batteryAlertEnabled', lowBatteryAlert.value);
  localStorage.setItem('batteryAlertPercent', alertPercent.value);
  alert(`배터리가 ${alertPercent.value}% 이하일 때 알림이 설정되었습니다.`);
};

onMounted(() => {
  loadSavedSettings();
  robotStore.connectWebSocket();
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
});

// 배터리 상태
const currentBattery = computed(() => robotStore.robotStatus.battery || 100);

const batteryClass = computed(() => {
  if (currentBattery.value <= 20) return 'low';
  if (currentBattery.value <= 50) return 'medium';
  return 'high';
});

const batteryStatusText = computed(() => {
  if (currentBattery.value <= 20) return '충전 필요';
  if (currentBattery.value <= 50) return '보통';
  return '충분';
});

const batteryDescription = computed(() => {
  if (currentBattery.value <= 20) return '배터리가 부족합니다. 곧 충전이 필요합니다.';
  if (currentBattery.value <= 50) return '배터리가 보통 수준입니다.';
  return '배터리가 충분합니다. 정상적으로 사용 가능합니다.';
});

const estimatedTime = computed(() => {
  const hours = Math.floor(currentBattery.value * 0.05);
  const minutes = Math.floor((currentBattery.value * 0.05 - hours) * 60);
  if (hours > 0) {
    return `약 ${hours}시간 ${minutes}분`;
  }
  return `약 ${minutes}분`;
});

const chargingStatus = computed(() => {
  // 실제로는 robotStore에서 충전 상태를 가져와야 함
  return '방전 중';
});

// 원형 프로그레스 바 계산
const circumference = 2 * Math.PI * 52;
const strokeDashoffset = computed(() => {
  return circumference - (currentBattery.value / 100) * circumference;
});
</script>

<style scoped>
.battery-view {
  min-height: 100vh;
  background: #f2f4f6;
  padding-bottom: 100px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7684;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #191f28;
}

.header-spacer {
  width: 40px;
}

.content {
  padding: 16px 20px;
}

/* 배터리 메인 카드 */
.battery-main-card {
  background: #fff;
  border-radius: 24px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.battery-visual {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.battery-circle {
  position: relative;
  width: 140px;
  height: 140px;
}

.progress-ring {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.progress-ring-bg {
  stroke: #e5e8eb;
}

.progress-ring-fill {
  stroke-linecap: round;
  transition: stroke-dashoffset 0.5s ease;
}

.progress-ring-fill.high { stroke: #20c997; }
.progress-ring-fill.medium { stroke: #F59E0B; }
.progress-ring-fill.low { stroke: #EF4444; }

.battery-percent-large {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: baseline;
}

.percent-value {
  font-size: 40px;
  font-weight: 800;
  color: #191f28;
  letter-spacing: -0.02em;
}

.percent-sign {
  font-size: 20px;
  font-weight: 600;
  color: #8b95a1;
  margin-left: 2px;
}

.battery-status-text {
  text-align: center;
}

.status-label {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.status-label.high {
  background: #e6f7f2;
  color: #20c997;
}

.status-label.medium {
  background: #fff3e0;
  color: #F59E0B;
}

.status-label.low {
  background: #fee2e2;
  color: #EF4444;
}

.status-desc {
  font-size: 14px;
  color: #6b7684;
}

/* 정보 섹션 */
.info-section {
  margin-top: 24px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: #191f28;
  margin-bottom: 14px;
}

.info-cards {
  display: flex;
  gap: 12px;
}

.info-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.info-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #e7f1ff;
  color: #3182f6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-icon.charging {
  background: #fff3e0;
  color: #F59E0B;
}

.info-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.info-value {
  font-size: 15px;
  font-weight: 700;
  color: #191f28;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-label {
  font-size: 12px;
  color: #8b95a1;
  margin-top: 2px;
}

/* 팁 섹션 */
.tips-section {
  margin-top: 24px;
}

.tips-list {
  background: #fff;
  border-radius: 16px;
  padding: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.tip-item {
  display: flex;
  gap: 14px;
  padding: 16px 12px;
  border-bottom: 1px solid #f2f4f6;
}

.tip-item:last-child {
  border-bottom: none;
}

.tip-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #3182f6;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tip-content h4 {
  font-size: 15px;
  font-weight: 600;
  color: #191f28;
  margin-bottom: 4px;
}

.tip-content p {
  font-size: 13px;
  color: #6b7684;
  line-height: 1.5;
}

/* 알림 섹션 */
.alert-section {
  margin-top: 24px;
}

.alert-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 16px;
  padding: 16px 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.alert-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-weight: 500;
  color: #191f28;
}

.alert-info svg {
  color: #6b7684;
}

/* 토글 스위치 */
.toggle-switch {
  position: relative;
  width: 52px;
  height: 28px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e5e8eb;
  border-radius: 28px;
  transition: 0.3s;
}

.toggle-slider::before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  border-radius: 50%;
  transition: 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.toggle-switch input:checked + .toggle-slider {
  background-color: #3182f6;
}

.toggle-switch input:checked + .toggle-slider::before {
  transform: translateX(24px);
}

/* 퍼센트 설정 카드 */
.percent-setting-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  margin-top: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.percent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.percent-label {
  font-size: 15px;
  font-weight: 500;
  color: #191f28;
}

.percent-value-display {
  font-size: 24px;
  font-weight: 800;
  color: #3182f6;
}

/* 슬라이더 */
.slider-container {
  margin-bottom: 20px;
}

.percent-slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #e5e8eb;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.percent-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #3182f6;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(49, 130, 246, 0.4);
  transition: transform 0.2s;
}

.percent-slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.percent-slider::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #3182f6;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 8px rgba(49, 130, 246, 0.4);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #8b95a1;
}

/* 퀵 선택 버튼 */
.quick-select {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.quick-btn {
  flex: 1;
  padding: 10px 8px;
  border-radius: 10px;
  background: #f2f4f6;
  color: #6b7684;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #e5e8eb;
}

.quick-btn.active {
  background: #3182f6;
  color: #fff;
}

.setting-desc {
  font-size: 14px;
  color: #6b7684;
  text-align: center;
  margin-bottom: 16px;
  line-height: 1.5;
}

.setting-desc strong {
  color: #3182f6;
  font-weight: 600;
}

/* 저장 버튼 */
.save-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  background: #3182f6;
  color: #fff;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  transition: background 0.2s;
}

.save-btn:hover {
  background: #1b64da;
}

.save-btn:active {
  transform: scale(0.98);
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
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: saturate(180%) blur(20px);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 8px;
  padding-bottom: env(safe-area-inset-bottom);
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
  color: #b0b8c1;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
}

.nav-item svg {
  width: 24px;
  height: 24px;
}

.nav-item span {
  font-size: 10px;
  font-weight: 600;
}

.nav-item.active {
  color: #3182f6;
}
</style>
