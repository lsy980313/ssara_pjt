<template>
  <div class="inquiries">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="header-title">1:1문의 내역</h1>
      <div style="width: 24px;"></div>
    </header>

    <main class="content">
      <!-- 문의하기 버튼 -->
      <button class="inquiry-btn" @click="showWriteModal = true">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        문의하기
      </button>

      <!-- 문의 내역 목록 -->
      <div class="inquiry-list">
        <div
          v-for="inquiry in inquiries"
          :key="inquiry.id"
          class="inquiry-item"
          @click="toggleInquiry(inquiry.id)"
        >
          <div class="inquiry-header">
            <div class="inquiry-info">
              <span class="status-badge" :class="inquiry.status">
                {{ inquiry.status === 'answered' ? '답변완료' : '대기중' }}
              </span>
              <span class="inquiry-title">{{ inquiry.title }}</span>
            </div>
            <div class="inquiry-meta">
              <span class="inquiry-date">{{ inquiry.date }}</span>
              <svg
                class="chevron"
                :class="{ open: openInquiryId === inquiry.id }"
                width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              >
                <path d="M6 9l6 6 6-6"/>
              </svg>
            </div>
          </div>
          <div v-if="openInquiryId === inquiry.id" class="inquiry-content">
            <div class="question-section">
              <span class="section-label">문의내용</span>
              <p>{{ inquiry.content }}</p>
            </div>
            <div v-if="inquiry.answer" class="answer-section">
              <span class="section-label">답변</span>
              <p>{{ inquiry.answer }}</p>
              <span class="answer-date">{{ inquiry.answerDate }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div v-if="inquiries.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <p>문의 내역이 없습니다.</p>
      </div>
    </main>

    <!-- 문의하기 모달 -->
    <div v-if="showWriteModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>1:1 문의하기</h2>
          <button class="close-btn" @click="closeModal">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>제목</label>
            <input
              type="text"
              v-model="newInquiry.title"
              placeholder="문의 제목을 입력해 주세요"
            />
          </div>
          <div class="form-group">
            <label>내용</label>
            <textarea
              v-model="newInquiry.content"
              placeholder="문의 내용을 입력해 주세요"
              rows="6"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">취소</button>
          <button class="btn btn-primary" @click="submitInquiry" :disabled="!canSubmit">
            문의하기
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const openInquiryId = ref(null);
const showWriteModal = ref(false);

const newInquiry = ref({
  title: '',
  content: ''
});

const inquiries = ref([
  {
    id: 1,
    title: '로봇 연결이 자꾸 끊어집니다',
    date: '2025.01.27',
    status: 'answered',
    content: '집에서 로봇을 사용하는데 Wi-Fi 연결이 자꾸 끊어집니다. 확인 부탁드립니다.',
    answer: '안녕하세요. 문의 주셔서 감사합니다. Wi-Fi 연결이 불안정한 경우, 로봇과 공유기 사이의 거리를 확인해 주세요. 또한 2.4GHz 대역의 Wi-Fi 사용을 권장드립니다.',
    answerDate: '2025.01.28'
  },
  {
    id: 2,
    title: '배터리 소모가 빠른 것 같습니다',
    date: '2025.01.25',
    status: 'pending',
    content: '최근 배터리 소모가 평소보다 빠른 것 같습니다. 점검이 필요할까요?',
    answer: null,
    answerDate: null
  }
]);

const canSubmit = computed(() => {
  return newInquiry.value.title.trim() && newInquiry.value.content.trim();
});

const toggleInquiry = (id) => {
  openInquiryId.value = openInquiryId.value === id ? null : id;
};

const closeModal = () => {
  showWriteModal.value = false;
  newInquiry.value = { title: '', content: '' };
};

const submitInquiry = () => {
  if (!canSubmit.value) return;

  const today = new Date();
  const dateStr = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`;

  inquiries.value.unshift({
    id: Date.now(),
    title: newInquiry.value.title,
    date: dateStr,
    status: 'pending',
    content: newInquiry.value.content,
    answer: null,
    answerDate: null
  });

  alert('문의가 등록되었습니다.');
  closeModal();
};
</script>

<style scoped>
.inquiries {
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

/* 문의하기 버튼 */
.inquiry-btn {
  width: 100%;
  height: 48px;
  background: var(--primary);
  color: white;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
}

.inquiry-btn:active {
  opacity: 0.9;
}

/* 문의 목록 */
.inquiry-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.inquiry-item {
  background: var(--bg-primary);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}

.inquiry-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
}

.inquiry-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.status-badge {
  flex-shrink: 0;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
}

.status-badge.answered {
  background: var(--success-light);
  color: var(--success);
}

.status-badge.pending {
  background: var(--gray-100);
  color: var(--text-tertiary);
}

.inquiry-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inquiry-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.inquiry-date {
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

.inquiry-content {
  padding: 0 16px 16px;
  border-top: 1px solid var(--gray-100);
  padding-top: 16px;
}

.question-section,
.answer-section {
  margin-bottom: 16px;
}

.answer-section {
  background: var(--bg-secondary);
  padding: 14px;
  border-radius: 8px;
  margin-bottom: 0;
}

.section-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

.inquiry-content p {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.answer-date {
  display: block;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 8px;
  text-align: right;
}

/* 빈 상태 */
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

/* 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  width: 100%;
  max-width: 400px;
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--gray-100);
}

.modal-header h2 {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  padding: 4px;
  color: var(--text-tertiary);
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--gray-200);
  border-radius: 10px;
  font-size: 15px;
  color: var(--text-primary);
  resize: none;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: var(--primary);
  background: var(--bg-primary);
}

.modal-footer {
  display: flex;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--gray-100);
}

.btn {
  flex: 1;
  height: 48px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:disabled {
  opacity: 0.5;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}
</style>
