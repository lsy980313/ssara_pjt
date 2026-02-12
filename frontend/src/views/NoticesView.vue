<template>
  <div class="notices">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="header-title">공지사항</h1>
      <div style="width: 24px;"></div>
    </header>

    <main class="content">
      <div class="notice-list">
        <div
          v-for="notice in notices"
          :key="notice.id"
          class="notice-item"
          @click="toggleNotice(notice.id)"
        >
          <div class="notice-header">
            <div class="notice-info">
              <span v-if="notice.important" class="badge">중요</span>
              <span class="notice-title">{{ notice.title }}</span>
            </div>
            <div class="notice-meta">
              <span class="notice-date">{{ notice.date }}</span>
              <svg
                class="chevron"
                :class="{ open: openNoticeId === notice.id }"
                width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              >
                <path d="M6 9l6 6 6-6"/>
              </svg>
            </div>
          </div>
          <div v-if="openNoticeId === notice.id" class="notice-content">
            <p>{{ notice.content }}</p>
          </div>
        </div>
      </div>

      <div v-if="notices.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
        </svg>
        <p>등록된 공지사항이 없습니다.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const openNoticeId = ref(null);

const notices = ref([
  {
    id: 1,
    title: '파트라슈 봇 서비스 오픈 안내',
    date: '2025.01.28',
    important: true,
    content: '안녕하세요, 파트라슈 봇 서비스가 정식 오픈되었습니다. 많은 이용 부탁드립니다. 서비스 이용 중 불편한 점이 있으시면 1:1 문의를 통해 알려주세요.'
  },
  {
    id: 2,
    title: '앱 업데이트 안내 (v1.0.1)',
    date: '2025.01.25',
    important: false,
    content: '앱이 v1.0.1로 업데이트 되었습니다. 주요 변경사항: 로봇 연결 안정성 개선, UI/UX 개선, 버그 수정.'
  },
  {
    id: 3,
    title: '개인정보처리방침 변경 안내',
    date: '2025.01.20',
    important: false,
    content: '개인정보처리방침이 일부 변경되었습니다. 변경된 내용은 홈페이지에서 확인하실 수 있습니다.'
  }
]);

const toggleNotice = (id) => {
  openNoticeId.value = openNoticeId.value === id ? null : id;
};
</script>

<style scoped>
.notices {
  min-height: 100vh;
  background: var(--bg-secondary);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-primary);
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn {
  padding: 8px;
  color: var(--text-primary);
}

.header-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.content {
  padding: 20px;
}

.notice-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notice-item {
  background: var(--bg-primary);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.notice-item:active {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.notice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
}

.notice-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.badge {
  flex-shrink: 0;
  padding: 4px 8px;
  background: var(--primary);
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
}

.notice-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notice-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.notice-date {
  font-size: 13px;
  color: var(--text-tertiary);
}

.chevron {
  color: var(--text-tertiary);
  transition: transform 0.2s;
}

.chevron.open {
  transform: rotate(180deg);
}

.notice-content {
  padding: 0 16px 16px;
  border-top: 1px solid var(--gray-100);
  margin-top: -1px;
  padding-top: 16px;
}

.notice-content p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
}

.empty-state svg {
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 15px;
}
</style>
