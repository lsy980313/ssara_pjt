<template>
  <div class="memo-page">
    <!-- Header -->
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
      <h1 class="header-title">메모장</h1>
      <button class="add-btn" @click="openNewMemo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
      </button>
    </header>

    <!-- Memo List -->
    <main class="content">
      <div class="memo-list" v-if="memos.length > 0">
        <article
          v-for="memo in memos"
          :key="memo.id"
          class="memo-card"
          @click="openMemo(memo)"
        >
          <div class="memo-header">
            <h3 class="memo-title">{{ memo.title || '제목 없음' }}</h3>
            <button class="delete-btn" @click.stop="deleteMemo(memo.id)">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
            </button>
          </div>
          <p class="memo-preview">{{ memo.content || '내용 없음' }}</p>
          <span class="memo-date">{{ formatDate(memo.updatedAt) }}</span>
        </article>
      </div>

      <!-- Empty State -->
      <div class="empty-state" v-else>
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
        <p>메모가 없습니다</p>
        <button class="create-btn" @click="openNewMemo">새 메모 작성</button>
      </div>
    </main>

    <!-- Memo Modal -->
    <div class="modal-overlay" v-if="showModal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <input
            type="text"
            v-model="currentMemo.title"
            placeholder="제목을 입력하세요"
            class="title-input"
          />
          <button class="close-btn" @click="closeModal">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <textarea
          v-model="currentMemo.content"
          placeholder="내용을 입력하세요..."
          class="content-input"
        ></textarea>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeModal">취소</button>
          <button class="save-btn" @click="saveMemo">저장</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const memos = ref([])
const showModal = ref(false)
const currentMemo = ref({ id: null, title: '', content: '' })
const isEditing = ref(false)

const STORAGE_KEY = 'pet-care-memos'

const loadMemos = () => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved) {
    memos.value = JSON.parse(saved)
  }
}

const saveMemos = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(memos.value))
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '방금 전'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}분 전`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}시간 전`

  return date.toLocaleDateString('ko-KR', {
    month: 'long',
    day: 'numeric'
  })
}

const openNewMemo = () => {
  currentMemo.value = { id: null, title: '', content: '' }
  isEditing.value = false
  showModal.value = true
}

const openMemo = (memo) => {
  currentMemo.value = { ...memo }
  isEditing.value = true
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  currentMemo.value = { id: null, title: '', content: '' }
}

const saveMemo = () => {
  if (!currentMemo.value.title.trim() && !currentMemo.value.content.trim()) {
    closeModal()
    return
  }

  const now = new Date().toISOString()

  if (isEditing.value) {
    const index = memos.value.findIndex(m => m.id === currentMemo.value.id)
    if (index !== -1) {
      memos.value[index] = {
        ...currentMemo.value,
        updatedAt: now
      }
    }
  } else {
    memos.value.unshift({
      id: Date.now(),
      title: currentMemo.value.title,
      content: currentMemo.value.content,
      createdAt: now,
      updatedAt: now
    })
  }

  saveMemos()
  closeModal()
}

const deleteMemo = (id) => {
  if (confirm('이 메모를 삭제하시겠습니까?')) {
    memos.value = memos.value.filter(m => m.id !== id)
    saveMemos()
  }
}

onMounted(() => {
  loadMemos()
})
</script>

<style scoped>
.memo-page {
  min-height: 100vh;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  background: #f5f5f5;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fff;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn, .add-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #333;
  border-radius: 8px;
  transition: background 0.2s;
}

.back-btn:hover, .add-btn:hover {
  background: #f5f5f5;
}

.add-btn {
  color: #f59e0b;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: #191f28;
}

/* Content */
.content {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

/* Memo List */
.memo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.memo-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px 20px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.memo-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.memo-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.memo-title {
  font-size: 16px;
  font-weight: 600;
  color: #191f28;
  margin: 0;
  flex: 1;
}

.delete-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: #adb5bd;
  border-radius: 4px;
  transition: color 0.2s;
}

.delete-btn:hover {
  color: #ef4444;
}

.memo-preview {
  font-size: 14px;
  color: #6b7684;
  margin: 0 0 12px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.memo-date {
  font-size: 12px;
  color: #adb5bd;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #adb5bd;
}

.empty-state svg {
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 16px;
  margin-bottom: 20px;
}

.create-btn {
  background: #f59e0b;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.create-btn:hover {
  background: #d97706;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 100;
}

.modal-content {
  background: #fff;
  border-radius: 20px;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.title-input {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  border: none;
  outline: none;
  color: #191f28;
}

.title-input::placeholder {
  color: #adb5bd;
}

.close-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #6b7684;
  border-radius: 8px;
}

.close-btn:hover {
  background: #f5f5f5;
}

.content-input {
  flex: 1;
  min-height: 200px;
  padding: 20px;
  border: none;
  outline: none;
  font-size: 15px;
  line-height: 1.6;
  resize: none;
  color: #191f28;
}

.content-input::placeholder {
  color: #adb5bd;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

.cancel-btn, .save-btn {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.cancel-btn {
  background: #f5f5f5;
  border: none;
  color: #6b7684;
}

.cancel-btn:hover {
  background: #eee;
}

.save-btn {
  background: #f59e0b;
  border: none;
  color: #fff;
}

.save-btn:hover {
  background: #d97706;
}
</style>
