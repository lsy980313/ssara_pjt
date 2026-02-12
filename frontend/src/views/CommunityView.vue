<template>
  <div class="community-page">
    <!-- Header -->
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>
      <h1 class="header-title">커뮤니티</h1>
      <button class="write-btn" @click="openNewPost">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
      </button>
    </header>

    <!-- Category Tabs -->
    <div class="category-tabs">
      <button
        v-for="cat in categories"
        :key="cat.id"
        :class="['tab-btn', { active: selectedCategory === cat.id }]"
        @click="selectedCategory = cat.id"
      >
        {{ cat.name }}
      </button>
    </div>

    <!-- Posts List -->
    <main class="content">
      <div class="posts-list">
        <article
          v-for="post in filteredPosts"
          :key="post.id"
          class="post-card"
          @click="viewPost(post)"
        >
          <div class="post-header">
            <div class="author-info">
              <div class="author-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <span class="author-name">{{ post.author }}</span>
            </div>
            <span class="post-date">{{ formatDate(post.createdAt) }}</span>
          </div>
          <span class="post-category">{{ getCategoryName(post.category) }}</span>
          <h3 class="post-title">{{ post.title }}</h3>
          <p class="post-preview">{{ post.content }}</p>
          <div class="post-footer">
            <div class="stat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
              <span>{{ post.likes }}</span>
            </div>
            <div class="stat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              <span>{{ post.comments }}</span>
            </div>
          </div>
        </article>
      </div>
    </main>

    <!-- New Post Modal -->
    <div class="modal-overlay" v-if="showModal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>새 글 작성</h2>
          <button class="close-btn" @click="closeModal">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <select v-model="newPost.category" class="category-select">
            <option value="" disabled>카테고리 선택</option>
            <option v-for="cat in categories.slice(1)" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
          <input
            type="text"
            v-model="newPost.title"
            placeholder="제목을 입력하세요"
            class="title-input"
          />
          <textarea
            v-model="newPost.content"
            placeholder="내용을 입력하세요..."
            class="content-input"
          ></textarea>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeModal">취소</button>
          <button class="submit-btn" @click="submitPost" :disabled="!canSubmit">등록</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const categories = [
  { id: 'all', name: '전체' },
  { id: 'daily', name: '일상' },
  { id: 'health', name: '건강' },
  { id: 'tips', name: '꿀팁' },
  { id: 'qna', name: 'Q&A' }
]

const selectedCategory = ref('all')
const showModal = ref(false)
const newPost = ref({ category: '', title: '', content: '' })

// 샘플 게시글 데이터
const posts = ref([
  {
    id: 1,
    author: '멍멍이맘',
    category: 'daily',
    title: '오늘 산책하다가 친구를 만났어요',
    content: '오늘 공원에서 산책하다가 같은 견종 친구를 만났는데 둘이 너무 잘 놀더라구요! 다음에 또 만나기로 했어요.',
    likes: 24,
    comments: 8,
    createdAt: new Date(Date.now() - 3600000).toISOString()
  },
  {
    id: 2,
    author: '초보집사',
    category: 'qna',
    title: '강아지 발톱 깎기 어떻게 하세요?',
    content: '처음 키우는 강아지인데 발톱을 깎으려고 하면 너무 싫어해요. 어떻게 하면 좋을까요? 팁 좀 부탁드려요.',
    likes: 15,
    comments: 12,
    createdAt: new Date(Date.now() - 7200000).toISOString()
  },
  {
    id: 3,
    author: '행복한하루',
    category: 'health',
    title: '정기검진 다녀왔어요',
    content: '6개월만에 정기검진 다녀왔는데 건강하다고 해서 안심이에요. 다들 정기검진 꼭 챙기세요!',
    likes: 32,
    comments: 5,
    createdAt: new Date(Date.now() - 86400000).toISOString()
  },
  {
    id: 4,
    author: '트레이너K',
    category: 'tips',
    title: '간식으로 훈련하는 방법 공유',
    content: '간식을 이용한 효과적인 훈련 방법을 공유합니다. 먼저 강아지가 좋아하는 간식을 준비하고...',
    likes: 48,
    comments: 15,
    createdAt: new Date(Date.now() - 172800000).toISOString()
  }
])

const filteredPosts = computed(() => {
  if (selectedCategory.value === 'all') {
    return posts.value
  }
  return posts.value.filter(p => p.category === selectedCategory.value)
})

const canSubmit = computed(() => {
  return newPost.value.category && newPost.value.title.trim() && newPost.value.content.trim()
})

const getCategoryName = (categoryId) => {
  const cat = categories.find(c => c.id === categoryId)
  return cat ? cat.name : ''
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

const openNewPost = () => {
  newPost.value = { category: '', title: '', content: '' }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const submitPost = () => {
  if (!canSubmit.value) return

  posts.value.unshift({
    id: Date.now(),
    author: '나',
    category: newPost.value.category,
    title: newPost.value.title,
    content: newPost.value.content,
    likes: 0,
    comments: 0,
    createdAt: new Date().toISOString()
  })

  closeModal()
}

const viewPost = (post) => {
  // 게시글 상세 보기 (추후 구현)
  alert(`"${post.title}" 상세 페이지는 추후 구현 예정입니다.`)
}
</script>

<style scoped>
.community-page {
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

.back-btn, .write-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #333;
  border-radius: 8px;
  transition: background 0.2s;
}

.back-btn:hover, .write-btn:hover {
  background: #f5f5f5;
}

.write-btn {
  color: #10b981;
}

.header-title {
  font-size: 18px;
  font-weight: 700;
  color: #191f28;
}

/* Category Tabs */
.category-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  background: #fff;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.category-tabs::-webkit-scrollbar {
  display: none;
}

.tab-btn {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid #e5e5e5;
  background: #fff;
  font-size: 14px;
  font-weight: 500;
  color: #6b7684;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.tab-btn.active {
  background: #10b981;
  border-color: #10b981;
  color: #fff;
}

.tab-btn:hover:not(.active) {
  border-color: #10b981;
  color: #10b981;
}

/* Content */
.content {
  padding: 16px 20px;
  max-width: 600px;
  margin: 0 auto;
}

/* Posts List */
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px 20px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7684;
}

.author-name {
  font-size: 13px;
  font-weight: 600;
  color: #191f28;
}

.post-date {
  font-size: 12px;
  color: #adb5bd;
}

.post-category {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  color: #10b981;
  background: #d1fae5;
  padding: 4px 8px;
  border-radius: 6px;
  margin-bottom: 8px;
}

.post-title {
  font-size: 16px;
  font-weight: 600;
  color: #191f28;
  margin: 0 0 8px 0;
}

.post-preview {
  font-size: 14px;
  color: #6b7684;
  margin: 0 0 12px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-footer {
  display: flex;
  gap: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #adb5bd;
}

.stat svg {
  width: 16px;
  height: 16px;
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
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: #191f28;
  margin: 0;
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

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-select {
  padding: 12px 16px;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  color: #191f28;
  background: #fff;
}

.category-select:focus {
  border-color: #10b981;
}

.title-input {
  padding: 12px 16px;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  color: #191f28;
}

.title-input:focus {
  border-color: #10b981;
}

.title-input::placeholder {
  color: #adb5bd;
}

.content-input {
  min-height: 150px;
  padding: 12px 16px;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  color: #191f28;
  resize: none;
  line-height: 1.6;
}

.content-input:focus {
  border-color: #10b981;
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

.cancel-btn, .submit-btn {
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

.submit-btn {
  background: #10b981;
  border: none;
  color: #fff;
}

.submit-btn:hover:not(:disabled) {
  background: #059669;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
