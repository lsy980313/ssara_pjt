<template>
  <div class="features-page">
    <!-- Features Content -->
    <section class="features-section">
      <div class="features-container">
        <div class="section-header">
          <h2 class="section-title">추가 기능</h2>
          <p class="section-desc">소중한 가족을 위한 스마트 케어 솔루션</p>
        </div>

        <div class="features-grid">
          <!-- Healthcare Card -->
          <article class="feature-card" @click="$router.push('/healthcare')">
            <div class="card-badge health">HEALTH</div>
            <div class="card-image-wrapper health-bg">
              <img
                src="https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=400&q=70"
                alt="Healthcare"
                class="card-image"
                loading="lazy"
              />
            </div>
            <div class="card-inner">
              <h3 class="card-title">헬스케어</h3>
              <p class="card-description">건강 모니터링으로<br/>체계적인 관리</p>
            </div>
          </article>

          <!-- AI Assistant Card -->
          <article class="feature-card" @click="$router.push('/ai-assistant')">
            <div class="card-badge ai">AI</div>
            <div class="card-image-wrapper ai-bg">
              <img
                src="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&q=70"
                alt="AI Assistant"
                class="card-image"
                loading="lazy"
              />
            </div>
            <div class="card-inner">
              <h3 class="card-title">AI 비서</h3>
              <p class="card-description">가족과 대화 및<br/>명령 수행</p>
            </div>
          </article>

          <!-- Memo Card -->
          <article class="feature-card" @click="$router.push('/memo')">
            <div class="card-badge memo">MEMO</div>
            <div class="card-image-wrapper memo-bg">
              <img
                src="https://images.unsplash.com/photo-1517842645767-c639042777db?w=400&q=70"
                alt="Memo"
                class="card-image"
                loading="lazy"
              />
            </div>
            <div class="card-inner">
              <h3 class="card-title">메모장</h3>
              <p class="card-description">간편하게<br/>기록하고 관리</p>
            </div>
          </article>

          <!-- Community Card -->
          <article class="feature-card" @click="$router.push('/community')">
            <div class="card-badge community">COMMUNITY</div>
            <div class="card-image-wrapper community-bg">
              <img
                src="https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?w=400&q=70"
                alt="Community"
                class="card-image"
                loading="lazy"
              />
            </div>
            <div class="card-inner">
              <h3 class="card-title">커뮤니티</h3>
              <p class="card-description">정보 공유 및<br/>소통의 공간</p>
            </div>
          </article>

          <!-- Screen Card - Coming Soon -->
          <article class="feature-card coming-soon">
            <div class="card-badge screen">SCREEN</div>
            <div class="card-image-wrapper screen-bg">
              <div class="coming-soon-overlay">
                <svg class="coming-soon-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="2" y="3" width="20" height="14" rx="2"/>
                  <line x1="8" y1="21" x2="16" y2="21"/>
                  <line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
                <span class="coming-soon-label">추가 예정</span>
              </div>
            </div>
            <div class="card-inner">
              <h3 class="card-title">화면 보기</h3>
              <p class="card-description">실시간 카메라<br/>영상 확인</p>
            </div>
          </article>

          <!-- Location Card - Coming Soon -->
          <article class="feature-card coming-soon">
            <div class="card-badge location">LOCATION</div>
            <div class="card-image-wrapper location-bg">
              <div class="coming-soon-overlay">
                <svg class="coming-soon-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
                <span class="coming-soon-label">추가 예정</span>
              </div>
            </div>
            <div class="card-inner">
              <h3 class="card-title">위치 추적</h3>
              <p class="card-description">실시간 위치<br/>확인 및 추적</p>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <button class="nav-item" @click="$router.push('/home')">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>홈</span>
      </button>
      <button class="nav-item active" @click="$router.push('/features')">
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
// FeaturesView - 반려견 스마트 케어 기능 페이지
// Galaxy S20 Ultra 최적화 (412 x 915 CSS viewport, 20:9 비율)
</script>

<style scoped>
.features-page {
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f2f4f6;
  color: #191f28;
}

/* Features Section */
.features-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 16px;
  overflow: hidden;
}

.features-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 500px;
  width: 100%;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  padding: 24px 0 14px;
  flex-shrink: 0;
}

.section-title {
  font-size: 22px;
  font-weight: 800;
  color: #191f28;
  letter-spacing: -0.02em;
  margin-bottom: 4px;
}

.section-desc {
  font-size: 13px;
  font-weight: 500;
  color: #8b95a1;
}

/* 2x3 Grid - S20 Ultra 비율 최적화 */
.features-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 10px;
  min-height: 0;
  padding-bottom: 8px;
}

/* Feature Card */
.feature-card {
  position: relative;
  background: #fff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  min-height: 0;
}

.feature-card:active {
  transform: scale(0.96);
}

/* Badge */
.card-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.6px;
  color: #fff;
  padding: 3px 7px;
  border-radius: 4px;
  z-index: 2;
}

.card-badge.health { background: #ff6b6b; }
.card-badge.ai { background: #8b5cf6; }
.card-badge.memo { background: #f59e0b; }
.card-badge.community { background: #10b981; }
.card-badge.screen { background: #3b82f6; }
.card-badge.location { background: #ec4899; }

/* Image Area */
.card-image-wrapper {
  flex: 1;
  overflow: hidden;
  min-height: 0;
  position: relative;
}

.card-image-wrapper::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30px;
  background: linear-gradient(transparent, rgba(255,255,255,0.6));
  pointer-events: none;
}

.health-bg { background: #fee2e2; }
.ai-bg { background: #ede9fe; }
.memo-bg { background: #fef3c7; }
.community-bg { background: #d1fae5; }
.screen-bg { background: #dbeafe; }
.location-bg { background: #fce7f3; }

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.feature-card:active .card-image {
  transform: scale(1.05);
}

/* Coming Soon Card */
.feature-card.coming-soon {
  cursor: default;
  opacity: 0.75;
}

.feature-card.coming-soon:active {
  transform: none;
}

.coming-soon-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.coming-soon-icon {
  color: #b0b8c1;
}

.coming-soon-label {
  font-size: 11px;
  font-weight: 600;
  color: #8b95a1;
  letter-spacing: -0.01em;
}

/* Text Area */
.card-inner {
  flex-shrink: 0;
  padding: 10px 12px 12px;
  text-align: center;
}

.card-title {
  font-size: 14px;
  font-weight: 700;
  color: #191f28;
  letter-spacing: -0.02em;
  margin-bottom: 2px;
}

.card-description {
  font-size: 10px;
  font-weight: 500;
  color: #8b95a1;
  line-height: 1.4;
  letter-spacing: -0.01em;
}

/* Bottom Nav */
.bottom-nav {
  flex-shrink: 0;
  height: 60px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
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
  gap: 3px;
  flex: 1 1 0%;
  width: 100%;
  min-width: 0;
  padding: 6px 0;
  color: #b0b8c1;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.nav-item svg {
  width: 22px;
  height: 22px;
}

.nav-item span {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.nav-item.active {
  color: #3182f6;
  outline: none;
  box-shadow: none;
  border: none;
}

.nav-item:focus,
.nav-item:focus-visible {
  outline: none;
  box-shadow: none;
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .card-image,
  .feature-card {
    transition: none;
  }
}
</style>
