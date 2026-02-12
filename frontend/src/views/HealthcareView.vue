<template>
  <div class="healthcare-page">
    <!-- Header -->
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <h1 class="header-title">헬스케어</h1>
      <div class="header-spacer"></div>
    </header>

    <!-- Hero Score Section -->
    <section class="hero-section">
      <div class="hero-content">
        <p class="hero-date">{{ formattedDate }}</p>
        <h2 class="hero-title">오늘의 건강</h2>
        <div class="score-display">
          <div class="score-ring" :class="healthScoreClass">
            <svg class="score-bg" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" fill="none" stroke="#e8e8ed" stroke-width="8"/>
              <circle
                class="score-progress"
                cx="50" cy="50" r="45"
                fill="none"
                :stroke="scoreColor"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="scoreOffset"
              />
            </svg>
            <div class="score-text">
              <span class="score-number">{{ healthScore }}</span>
              <span class="score-unit">점</span>
            </div>
          </div>
          <p class="score-message">{{ healthMessage }}</p>
        </div>
      </div>
    </section>

    <!-- Activity Metrics -->
    <section class="metrics-section">
      <div class="section-container">
        <h3 class="section-title">활동 지표</h3>
        <div class="metrics-grid">
          <!-- Walk Time -->
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon blue">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <span class="metric-label">산책 시간</span>
            </div>
            <div class="metric-value-row">
              <span class="metric-value">{{ dailySummary.walkTime }}</span>
              <span class="metric-unit">분</span>
            </div>
            <div class="metric-progress">
              <div class="progress-track">
                <div class="progress-fill blue" :style="{ width: walkProgress + '%' }"></div>
              </div>
              <span class="progress-label">목표 60분 중 {{ walkProgress.toFixed(0) }}%</span>
            </div>
          </div>

          <!-- Distance -->
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon green">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
              </div>
              <span class="metric-label">이동 거리</span>
            </div>
            <div class="metric-value-row">
              <span class="metric-value">{{ dailySummary.distance }}</span>
              <span class="metric-unit">km</span>
            </div>
            <div class="metric-progress">
              <div class="progress-track">
                <div class="progress-fill green" :style="{ width: distanceProgress + '%' }"></div>
              </div>
              <span class="progress-label">목표 2km 중 {{ distanceProgress.toFixed(0) }}%</span>
            </div>
          </div>

          <!-- Activities -->
          <div class="metric-card">
            <div class="metric-header">
              <div class="metric-icon orange">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
              </div>
              <span class="metric-label">활동 횟수</span>
            </div>
            <div class="metric-value-row">
              <span class="metric-value">{{ dailySummary.activities }}</span>
              <span class="metric-unit">회</span>
            </div>
            <div class="metric-progress">
              <div class="progress-track">
                <div class="progress-fill orange" :style="{ width: activityProgress + '%' }"></div>
              </div>
              <span class="progress-label">목표 10회 중 {{ activityProgress.toFixed(0) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Alerts Section -->
    <section class="alerts-section">
      <div class="section-container">
        <div class="section-header">
          <h3 class="section-title">이상 감지 알림</h3>
          <span class="alert-badge" :class="{ active: dailySummary.alerts > 0 }">
            {{ dailySummary.alerts }}건
          </span>
        </div>

        <div v-if="dailySummary.alerts === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <h4 class="empty-title">이상 없음</h4>
          <p class="empty-description">오늘은 모든 활동이 정상입니다</p>
        </div>

        <div v-else class="alert-list">
          <div v-for="(alert, index) in recentAlerts" :key="index" class="alert-card">
            <div class="alert-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <div class="alert-content">
              <p class="alert-message">{{ alert.msg }}</p>
              <span class="alert-time">{{ alert.time }}</span>
            </div>
            <svg class="alert-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </div>
        </div>
      </div>
    </section>

    <!-- Health Tips -->
    <section class="tips-section">
      <div class="section-container">
        <h3 class="section-title">오늘의 건강 팁</h3>
        <div class="tip-card">
          <div class="tip-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 16v-4"/>
              <path d="M12 8h.01"/>
            </svg>
          </div>
          <p class="tip-text">{{ healthTip }}</p>
        </div>
      </div>
    </section>

    <!-- Bottom Spacer -->
    <div class="bottom-spacer"></div>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <button class="nav-item" @click="$router.push('/home')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>홈</span>
      </button>
      <button class="nav-item" @click="$router.push('/features')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"/>
          <rect x="14" y="3" width="7" height="7"/>
          <rect x="14" y="14" width="7" height="7"/>
          <rect x="3" y="14" width="7" height="7"/>
        </svg>
        <span>기능</span>
      </button>
      <button class="nav-item" @click="$router.push('/history')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        <span>기록</span>
      </button>
      <button class="nav-item" @click="$router.push('/help')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
import { activityApi } from '@/api';

const robotStore = useRobotStore();

// 오늘 날짜
const formattedDate = computed(() => {
  return new Date().toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short'
  });
});

// 일일 요약 데이터
const dailySummary = ref({
  walkTime: 0,
  distance: 0,
  activities: 0,
  alerts: 0
});

// 최근 알림
const recentAlerts = ref([]);

// 건강 점수 계산
const healthScore = computed(() => {
  const walkScore = Math.min(dailySummary.value.walkTime / 60 * 40, 40);
  const distanceScore = Math.min(dailySummary.value.distance / 2 * 30, 30);
  const activityScore = Math.min(dailySummary.value.activities / 10 * 30, 30);
  return Math.round(walkScore + distanceScore + activityScore);
});

const healthScoreClass = computed(() => {
  if (healthScore.value >= 80) return 'excellent';
  if (healthScore.value >= 60) return 'good';
  if (healthScore.value >= 40) return 'fair';
  return 'poor';
});

const scoreColor = computed(() => {
  if (healthScore.value >= 80) return '#34c759';
  if (healthScore.value >= 60) return '#007aff';
  if (healthScore.value >= 40) return '#ff9500';
  return '#ff3b30';
});

// 원형 프로그레스 계산
const circumference = 2 * Math.PI * 45;
const scoreOffset = computed(() => {
  const progress = healthScore.value / 100;
  return circumference * (1 - progress);
});

const healthMessage = computed(() => {
  if (healthScore.value >= 80) return '오늘 활동량이 충분합니다!';
  if (healthScore.value >= 60) return '조금만 더 활동해 보세요!';
  if (healthScore.value >= 40) return '산책 시간을 늘려보세요';
  return '오늘 활동을 시작해 보세요!';
});

// 진행률 계산
const walkProgress = computed(() => Math.min((dailySummary.value.walkTime / 60) * 100, 100));
const distanceProgress = computed(() => Math.min((dailySummary.value.distance / 2) * 100, 100));
const activityProgress = computed(() => Math.min((dailySummary.value.activities / 10) * 100, 100));

// 건강 팁
const healthTips = [
  '규칙적인 산책은 심혈관 건강에 도움이 됩니다.',
  '하루 30분 이상의 활동이 권장됩니다.',
  '충분한 휴식도 건강 유지에 중요합니다.',
  '꾸준한 활동이 치매 예방에 도움이 됩니다.',
  '적절한 수분 섭취를 잊지 마세요.'
];

const healthTip = ref(healthTips[Math.floor(Math.random() * healthTips.length)]);

// 데이터 로드
const loadData = async () => {
  try {
    const summaryRes = await activityApi.getTodaySummary();
    dailySummary.value = {
      walkTime: summaryRes.data.walkTime || 0,
      distance: summaryRes.data.distance || 0,
      activities: summaryRes.data.activities || 0,
      alerts: summaryRes.data.alerts || 0
    };

    const logsRes = await activityApi.getTodayLogs();
    recentAlerts.value = logsRes.data
      .filter(log => log.type === 'warning')
      .slice(0, 5);
  } catch (e) {
    console.error('헬스케어 데이터 로드 실패:', e);
  }
};

onMounted(() => {
  robotStore.connectWebSocket();
  loadData();
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
});

const unwatch = robotStore.$subscribe((mutation, state) => {
  if (state.dailySummary) {
    dailySummary.value = {
      ...dailySummary.value,
      walkTime: state.dailySummary.walkTime || dailySummary.value.walkTime,
      alerts: state.dailySummary.alerts || dailySummary.value.alerts
    };
  }
});

onUnmounted(() => {
  if (typeof unwatch === 'function') unwatch();
});
</script>

<style scoped>
.healthcare-page {
  min-height: 100vh;
  background: #f5f5f7;
  font-family: -apple-system, BlinkMacSystemFont, 'Pretendard', sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  position: sticky;
  top: 0;
  z-index: 50;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0066cc;
  background: none;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}

.back-btn:hover {
  background: rgba(0, 102, 204, 0.1);
}

.header-title {
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
}

.header-spacer {
  width: 40px;
}

/* Hero Section */
.hero-section {
  background: #fff;
  padding: 32px 24px 48px;
  text-align: center;
}

.hero-content {
  max-width: 400px;
  margin: 0 auto;
}

.hero-date {
  font-size: 15px;
  color: #86868b;
  margin-bottom: 4px;
}

.hero-title {
  font-size: 32px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.02em;
  margin-bottom: 32px;
}

.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.score-ring {
  position: relative;
  width: 160px;
  height: 160px;
}

.score-bg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.score-progress {
  transition: stroke-dashoffset 1s ease-out;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-number {
  display: block;
  font-size: 48px;
  font-weight: 600;
  color: #1d1d1f;
  line-height: 1;
}

.score-unit {
  font-size: 17px;
  color: #86868b;
}

.score-message {
  font-size: 17px;
  color: #1d1d1f;
  font-weight: 500;
}

/* Section Common */
.section-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  font-size: 22px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.01em;
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

/* Metrics Section */
.metrics-section {
  padding: 32px 0;
}

.metrics-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.metric-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-icon.blue {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.metric-icon.green {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.metric-icon.orange {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.metric-label {
  font-size: 15px;
  color: #86868b;
  font-weight: 500;
}

.metric-value-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 16px;
}

.metric-value {
  font-size: 40px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.02em;
}

.metric-unit {
  font-size: 17px;
  color: #86868b;
}

.metric-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-track {
  height: 8px;
  background: #e8e8ed;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease-out;
}

.progress-fill.blue {
  background: linear-gradient(90deg, #007aff, #5ac8fa);
}

.progress-fill.green {
  background: linear-gradient(90deg, #34c759, #30d158);
}

.progress-fill.orange {
  background: linear-gradient(90deg, #ff9500, #ffcc00);
}

.progress-label {
  font-size: 13px;
  color: #86868b;
  text-align: right;
}

/* Alerts Section */
.alerts-section {
  padding: 32px 0;
}

.alert-badge {
  font-size: 14px;
  font-weight: 600;
  color: #34c759;
  padding: 4px 12px;
  background: rgba(52, 199, 89, 0.1);
  border-radius: 20px;
}

.alert-badge.active {
  color: #ff9500;
  background: rgba(255, 149, 0, 0.1);
}

.empty-state {
  background: #fff;
  border-radius: 16px;
  padding: 48px 24px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 4px;
}

.empty-description {
  font-size: 15px;
  color: #86868b;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alert-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border-radius: 14px;
  padding: 16px;
}

.alert-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-message {
  font-size: 15px;
  font-weight: 500;
  color: #1d1d1f;
  margin-bottom: 2px;
}

.alert-time {
  font-size: 13px;
  color: #86868b;
}

.alert-chevron {
  color: #c7c7cc;
  flex-shrink: 0;
}

/* Tips Section */
.tips-section {
  padding: 32px 0;
}

.tip-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.tip-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #007aff 0%, #5ac8fa 100%);
  color: #fff;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tip-text {
  font-size: 17px;
  color: #1d1d1f;
  line-height: 1.6;
  font-weight: 500;
  padding-top: 4px;
}

/* Bottom Spacer & Nav */
.bottom-spacer {
  height: 100px;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  max-width: 600px;
  margin: 0 auto;
  height: 72px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid #e8e8ed;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 8px;
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
  color: #86868b;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.nav-item:hover {
  color: #0066cc;
}

.nav-item svg {
  width: 24px;
  height: 24px;
}

.nav-item span {
  font-size: 11px;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 480px) {
  .hero-title {
    font-size: 28px;
  }

  .score-ring {
    width: 140px;
    height: 140px;
  }

  .score-number {
    font-size: 40px;
  }

  .metric-value {
    font-size: 32px;
  }

  .section-title {
    font-size: 20px;
  }
}
</style>
