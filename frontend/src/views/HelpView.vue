<template>
  <div class="help-view">
    <header class="header">
      <h1 class="header-title">도움말</h1>
    </header>

    <main class="content">
      <!-- 앱 정보 -->
      <section class="info-card">
        <div class="app-logo">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
            <line x1="9" y1="9" x2="9.01" y2="9"/>
            <line x1="15" y1="9" x2="15.01" y2="9"/>
          </svg>
        </div>
        <h2 class="app-name">우리 가족 돌봄</h2>
        <p class="app-version">버전 1.0.0</p>
      </section>

      <!-- FAQ -->
      <section class="faq-section">
        <h3 class="section-title">자주 묻는 질문</h3>

        <div class="faq-list">
          <div class="faq-item" v-for="(faq, index) in faqs" :key="index">
            <button class="faq-question" @click="toggleFaq(index)">
              <span>{{ faq.question }}</span>
              <svg
                width="20" height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                :class="{ rotated: faq.open }"
              >
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </button>
            <div class="faq-answer" v-show="faq.open">
              <p>{{ faq.answer }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 기능 안내 -->
      <section class="guide-section">
        <h3 class="section-title">기능 안내</h3>

        <div class="guide-list">
          <div class="guide-item">
            <div class="guide-icon home">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              </svg>
            </div>
            <div class="guide-content">
              <h4>홈</h4>
              <p>로봇 상태, 실시간 카메라, 현재 위치를 한눈에 확인할 수 있습니다.</p>
            </div>
          </div>

          <div class="guide-item">
            <div class="guide-icon features">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"/>
                <rect x="14" y="3" width="7" height="7"/>
                <rect x="14" y="14" width="7" height="7"/>
                <rect x="3" y="14" width="7" height="7"/>
              </svg>
            </div>
            <div class="guide-content">
              <h4>기능</h4>
              <p>로봇 이동, 건강관리 등 다양한 기능을 사용할 수 있습니다.</p>
            </div>
          </div>

          <div class="guide-item">
            <div class="guide-icon history">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div class="guide-content">
              <h4>기록</h4>
              <p>로봇의 활동 기록과 알림 내역을 확인할 수 있습니다.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 문의하기 -->
      <section class="contact-section">
        <h3 class="section-title">문의하기</h3>
        <div class="contact-card">
          <p>서비스 이용 중 문제가 발생하셨나요?</p>
          <button class="contact-btn" @click="$router.push('/inquiries')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <span>1:1 문의하기</span>
          </button>
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
      <button class="nav-item active">
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
import { reactive } from 'vue';

const faqs = reactive([
  {
    question: '로봇이 연결되지 않아요',
    answer: '로봇의 전원이 켜져 있는지 확인하고, 같은 Wi-Fi 네트워크에 연결되어 있는지 확인해주세요. 문제가 지속되면 로봇을 재시작해보세요.',
    open: false
  },
  {
    question: '카메라 화면이 안 나와요',
    answer: '카메라 스트리밍은 로봇이 온라인 상태일 때만 가능합니다. 로봇 연결 상태를 확인하고, 새로고침 버튼을 눌러보세요.',
    open: false
  },
  {
    question: '위치가 정확하지 않아요',
    answer: 'VSLAM 기반 위치는 실내 환경에 따라 오차가 발생할 수 있습니다. 카카오맵 모드로 전환하면 GPS 기반 위치를 확인할 수 있습니다.',
    open: false
  },
  {
    question: '배터리 잔량이 표시되지 않아요',
    answer: '로봇이 오프라인 상태이면 배터리 정보를 받아올 수 없습니다. 로봇이 연결되면 자동으로 업데이트됩니다.',
    open: false
  }
]);

const toggleFaq = (index) => {
  faqs[index].open = !faqs[index].open;
};
</script>

<style scoped>
.help-view {
  min-height: 100vh;
  background: #f2f4f6;
  padding-bottom: 100px;
}

.header {
  display: flex;
  justify-content: center;
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

/* 앱 정보 */
.info-card {
  background: #fff;
  border-radius: 20px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.app-logo {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #3182f6 0%, #5BA0F5 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.app-name {
  font-size: 20px;
  font-weight: 700;
  color: #191f28;
  margin-bottom: 4px;
}

.app-version {
  font-size: 14px;
  color: #8b95a1;
}

/* FAQ 섹션 */
.faq-section {
  margin-top: 24px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: #191f28;
  margin-bottom: 14px;
}

.faq-list {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.faq-item {
  border-bottom: 1px solid #f2f4f6;
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-question {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  font-size: 15px;
  font-weight: 500;
  color: #191f28;
  text-align: left;
}

.faq-question svg {
  flex-shrink: 0;
  color: #8b95a1;
  transition: transform 0.2s ease;
}

.faq-question svg.rotated {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 0 20px 16px;
}

.faq-answer p {
  font-size: 14px;
  line-height: 1.6;
  color: #6b7684;
}

/* 기능 안내 */
.guide-section {
  margin-top: 24px;
}

.guide-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.guide-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.guide-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.guide-icon.home {
  background: #e7f1ff;
  color: #3182f6;
}

.guide-icon.features {
  background: #e6f7f2;
  color: #20c997;
}

.guide-icon.history {
  background: #fff3e0;
  color: #F59E0B;
}

.guide-content h4 {
  font-size: 15px;
  font-weight: 600;
  color: #191f28;
  margin-bottom: 4px;
}

.guide-content p {
  font-size: 13px;
  color: #6b7684;
  line-height: 1.5;
}

/* 문의하기 */
.contact-section {
  margin-top: 24px;
}

.contact-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.contact-card p {
  font-size: 14px;
  color: #6b7684;
  margin-bottom: 16px;
}

.contact-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #3182f6;
  color: #fff;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  transition: background 0.2s;
}

.contact-btn:hover {
  background: #1b64da;
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
