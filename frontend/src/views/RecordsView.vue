<template>
  <div class="records-view">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
      <h1 class="header-title">핵심기록</h1>
      <button class="select-btn" @click="toggleSelectMode">
        {{ selectMode ? '취소' : '선택' }}
      </button>
    </header>

    <main class="content">
      <!-- 탭 메뉴 -->
      <div class="tab-menu">
        <button
          class="tab-item"
          :class="{ active: activeTab === 'recent' }"
          @click="activeTab = 'recent'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>최근</span>
          <span class="tab-badge small">{{ recordsStore.RECENT_DAYS }}일</span>
        </button>
        <button
          class="tab-item"
          :class="{ active: activeTab === 'favorites' }"
          @click="activeTab = 'favorites'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          <span>즐겨찾기</span>
          <span class="tab-badge small">{{ recordsStore.favoriteCount }}/{{ recordsStore.MAX_FAVORITES }}</span>
        </button>
        <button
          class="tab-item"
          :class="{ active: activeTab === 'activity' }"
          @click="activeTab = 'activity'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
            <line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/>
            <line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <span>활동기록</span>
        </button>
      </div>

      <!-- 활동기록 탭 콘텐츠 -->
      <div v-if="activeTab === 'activity'" class="activity-content">
        <!-- 날짜 선택 -->
        <div class="date-picker-section">
          <label class="date-label">날짜 선택</label>
          <input
            type="date"
            v-model="selectedDate"
            class="date-input"
            :max="todayDate"
          />
        </div>

        <!-- 카테고리 버튼들 -->
        <div v-if="!activityViewMode" class="activity-buttons">
          <button class="activity-btn" @click="viewActivityMedia('photo', false)">
            <div class="activity-btn-icon photo">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
            <div class="activity-btn-text">
              <span class="activity-btn-title">사진</span>
              <span class="activity-btn-desc">저장된 사진 보기</span>
            </div>
            <svg class="activity-btn-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>

          <button class="activity-btn" @click="viewActivityMedia('video', false)">
            <div class="activity-btn-icon video">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="23 7 16 12 23 17 23 7"/>
                <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
              </svg>
            </div>
            <div class="activity-btn-text">
              <span class="activity-btn-title">동영상</span>
              <span class="activity-btn-desc">저장된 동영상 보기</span>
            </div>
            <svg class="activity-btn-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>

          <button class="activity-btn" @click="viewActivityMedia('photo', true)">
            <div class="activity-btn-icon favorite-photo">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              <svg class="star-badge" width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
            </div>
            <div class="activity-btn-text">
              <span class="activity-btn-title">즐겨찾기 사진</span>
              <span class="activity-btn-desc">즐겨찾기한 사진 보기</span>
            </div>
            <svg class="activity-btn-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>

          <button class="activity-btn" @click="viewActivityMedia('video', true)">
            <div class="activity-btn-icon favorite-video">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="23 7 16 12 23 17 23 7"/>
                <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
              </svg>
              <svg class="star-badge" width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
            </div>
            <div class="activity-btn-text">
              <span class="activity-btn-title">즐겨찾기 동영상</span>
              <span class="activity-btn-desc">즐겨찾기한 동영상 보기</span>
            </div>
            <svg class="activity-btn-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>
        </div>

        <!-- 선택된 날짜의 미디어 표시 영역 -->
        <div v-if="activityViewMode" class="activity-media-section">
          <div class="activity-media-header">
            <button class="activity-back-btn" @click="activityViewMode = null">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M15 18l-6-6 6-6"/>
              </svg>
              <span>뒤로</span>
            </button>
            <span class="activity-media-title">{{ activityMediaTitle }}</span>
          </div>

          <div v-if="activityFilteredMedia.length === 0" class="empty-state small">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            <p>해당 날짜에 기록이 없습니다</p>
          </div>

          <div v-else class="media-grid">
            <div
              class="media-item"
              v-for="item in activityFilteredMedia"
              :key="item.id"
              @click="openPreview(item)"
            >
              <div class="media-thumbnail">
                <img :src="item.thumbnail" :alt="item.title" />
                <div v-if="item.type === 'video'" class="video-badge">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  <span>{{ item.duration }}</span>
                </div>
                <button
                  class="favorite-btn"
                  :class="{ active: item.isFavorite }"
                  @click.stop="handleToggleFavorite(item)"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" :fill="item.isFavorite ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                  </svg>
                </button>
              </div>
              <div class="media-info">
                <span class="media-title">{{ item.title }}</span>
                <span class="media-date">{{ item.date }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 최근/즐겨찾기 탭 콘텐츠 -->
      <div v-if="activeTab !== 'activity'">
        <!-- 필터 -->
        <div class="filter-bar">
          <button
            class="filter-chip"
            :class="{ active: mediaFilter === 'all' }"
            @click="mediaFilter = 'all'"
          >
            전체
          </button>
          <button
            class="filter-chip"
            :class="{ active: mediaFilter === 'photo' }"
            @click="mediaFilter = 'photo'"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            사진
          </button>
          <button
            class="filter-chip"
            :class="{ active: mediaFilter === 'video' }"
            @click="mediaFilter = 'video'"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="23 7 16 12 23 17 23 7"/>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
            </svg>
            동영상
          </button>
        </div>

        <!-- 안내 메시지 -->
        <div v-if="activeTab === 'recent'" class="info-banner">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>최근 {{ recordsStore.RECENT_DAYS }}일 이내 기록만 표시됩니다. 즐겨찾기에 추가하면 영구 보관됩니다.</span>
        </div>

        <!-- 미디어 그리드 -->
        <section class="media-section">
          <div v-if="filteredMedia.length === 0" class="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            <p>{{ activeTab === 'favorites' ? '즐겨찾기한 기록이 없습니다' : '최근 기록이 없습니다' }}</p>
            <span v-if="activeTab === 'recent'" class="empty-hint">전체화면에서 사진/동영상을 촬영해보세요</span>
          </div>

          <div v-else class="media-grid">
            <div
              class="media-item"
              v-for="item in filteredMedia"
              :key="item.id"
              @click="selectMode ? toggleSelect(item) : openPreview(item)"
            >
              <div class="media-thumbnail">
                <img :src="item.thumbnail" :alt="item.title" />
                <div v-if="item.type === 'video'" class="video-badge">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  <span>{{ item.duration }}</span>
                </div>
                <button
                  class="favorite-btn"
                  :class="{ active: item.isFavorite }"
                  @click.stop="handleToggleFavorite(item)"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" :fill="item.isFavorite ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                  </svg>
                </button>
              </div>
              <div class="media-info">
                <span class="media-title">{{ item.title }}</span>
                <span class="media-date">{{ item.date }}</span>
              </div>
              <div v-if="selectMode" class="select-checkbox" :class="{ selected: selectedItems.includes(item.id) }">
                <svg v-if="selectedItems.includes(item.id)" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <polyline points="20 6 9 17 4 12" stroke="white" stroke-width="3" fill="none"/>
                </svg>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 선택 모드 하단 액션 -->
    <div class="bottom-actions" v-if="selectMode && selectedItems.length > 0">
      <div class="selected-count">{{ selectedItems.length }}개 선택됨</div>
      <div class="action-buttons">
        <button class="action-btn" @click="downloadSelected">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          <span>저장</span>
        </button>
        <button class="action-btn" @click="shareSelected">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="18" cy="5" r="3"/>
            <circle cx="6" cy="12" r="3"/>
            <circle cx="18" cy="19" r="3"/>
            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
          </svg>
          <span>내보내기</span>
        </button>
        <button class="action-btn delete" @click="deleteSelected">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          <span>삭제</span>
        </button>
      </div>
    </div>

    <!-- 미리보기 모달 -->
    <Teleport to="body">
      <div v-if="previewItem" class="preview-modal" @click="closePreview">
        <div class="preview-header" @click.stop>
          <button class="preview-close" @click="closePreview">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <div class="preview-title">
            <span class="title-text">{{ previewItem.title }}</span>
            <span class="title-date">{{ previewItem.date }}</span>
          </div>
          <button
            class="preview-favorite"
            :class="{ active: previewItem.isFavorite }"
            @click="handleToggleFavorite(previewItem)"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" :fill="previewItem.isFavorite ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </button>
        </div>

        <div class="preview-content" @click.stop>
          <img v-if="previewItem.type === 'photo'" :src="previewItem.url" :alt="previewItem.title" />
          <!-- 동영상 재생 -->
          <div v-else class="video-player">
            <!-- Blob URL이 있는 경우: 실제 비디오 재생 -->
            <video
              v-if="hasVideoUrl"
              ref="videoPlayerRef"
              :src="previewItem.url"
              class="video-frame"
              controls
              playsinline
              :poster="previewItem.thumbnail"
            ></video>
            <!-- Blob이 만료된 경우: 썸네일만 표시 -->
            <div v-else class="no-frames-overlay">
              <img v-if="previewItem.thumbnail" :src="previewItem.thumbnail" class="video-frame" style="opacity: 0.6;" />
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <polygon points="23 7 16 12 23 17 23 7"/>
                <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
              </svg>
              <p>영상이 만료되었습니다</p>
              <span>{{ previewItem.duration || '0:00' }}</span>
            </div>
          </div>
        </div>

        <div class="preview-actions" @click.stop>
          <button class="preview-action-btn" @click="downloadItem(previewItem)">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>저장</span>
          </button>
          <button class="preview-action-btn" @click="shareItem(previewItem)">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="18" cy="5" r="3"/>
              <circle cx="6" cy="12" r="3"/>
              <circle cx="18" cy="19" r="3"/>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
            </svg>
            <span>내보내기</span>
          </button>
        </div>
      </div>
    </Teleport>

    <!-- 토스트 메시지 -->
    <Teleport to="body">
      <div v-if="toastMessage" class="toast-message">
        {{ toastMessage }}
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useRecordsStore } from '@/stores/recordsStore';

const recordsStore = useRecordsStore();
const route = useRoute();

const activeTab = ref('recent');
const mediaFilter = ref('all');
const selectMode = ref(false);
const selectedItems = ref([]);
const previewItem = ref(null);
const toastMessage = ref('');

// 활동기록 관련
const selectedDate = ref(new Date().toISOString().split('T')[0]);
const todayDate = new Date().toISOString().split('T')[0];
const activityViewMode = ref(null); // { type: 'photo'|'video', isFavorite: boolean }

// 동영상 재생 관련

const videoPlayerRef = ref(null);

// Blob URL이 유효한지 확인 (blob: 프로토콜)
const hasVideoUrl = computed(() => {
  return previewItem.value?.type === 'video' &&
         previewItem.value?.url &&
         previewItem.value.url.startsWith('blob:');
});

watch(previewItem, (newVal) => {
  if (!newVal && videoPlayerRef.value) {
    videoPlayerRef.value.pause();
  }
});

// 탭 변경 시 활동기록 뷰 모드 리셋
watch(activeTab, (newVal) => {
  if (newVal !== 'activity') {
    activityViewMode.value = null;
  }
  // 탭 변경 시 선택 모드 해제
  selectMode.value = false;
  selectedItems.value = [];
});

// 쿼리 파라미터로 진입 시 처리
onMounted(() => {
  const { date, type, favorite } = route.query;
  if (date && type) {
    // 활동기록 탭으로 이동
    activeTab.value = 'activity';
    selectedDate.value = date;
    activityViewMode.value = {
      type: type,
      isFavorite: favorite === 'true'
    };
  }
});

onUnmounted(() => {
  // cleanup
});

// 필터링된 미디어
const filteredMedia = computed(() => {
  let items;

  if (activeTab.value === 'favorites') {
    items = [...recordsStore.favoriteItems];
  } else {
    items = [...recordsStore.recentItems];
  }

  if (mediaFilter.value !== 'all') {
    items = items.filter(item => item.type === mediaFilter.value);
  }

  return items;
});

// 활동기록 - 선택된 날짜와 타입에 맞는 미디어
const activityFilteredMedia = computed(() => {
  if (!activityViewMode.value) return [];

  const { type, isFavorite } = activityViewMode.value;
  let items = isFavorite ? [...recordsStore.favoriteItems] : [...recordsStore.mediaItems];

  // 타입 필터
  items = items.filter(item => item.type === type);

  // 날짜 필터 (선택된 날짜와 일치하는 항목만)
  items = items.filter(item => {
    const itemDate = item.rawDate || item.date;
    if (!itemDate) return false;

    // rawDate가 있으면 사용, 없으면 date 문자열에서 파싱
    if (item.rawDate) {
      const itemDateStr = new Date(item.rawDate).toISOString().split('T')[0];
      return itemDateStr === selectedDate.value;
    }

    // date 문자열 파싱 시도 (예: "2024.01.15" 또는 "2024-01-15")
    const dateMatch = item.date.match(/(\d{4})[.-](\d{2})[.-](\d{2})/);
    if (dateMatch) {
      const itemDateStr = `${dateMatch[1]}-${dateMatch[2]}-${dateMatch[3]}`;
      return itemDateStr === selectedDate.value;
    }

    return false;
  });

  return items;
});

// 활동기록 제목
const activityMediaTitle = computed(() => {
  if (!activityViewMode.value) return '';
  const { type, isFavorite } = activityViewMode.value;
  const typeText = type === 'photo' ? '사진' : '동영상';
  const favoriteText = isFavorite ? '즐겨찾기 ' : '';
  return `${favoriteText}${typeText} (${selectedDate.value})`;
});

// 활동기록 미디어 보기
const viewActivityMedia = (type, isFavorite) => {
  activityViewMode.value = { type, isFavorite };
};

// 선택 모드 토글
const toggleSelectMode = () => {
  selectMode.value = !selectMode.value;
  if (!selectMode.value) {
    selectedItems.value = [];
  }
};

// 아이템 선택 토글
const toggleSelect = (item) => {
  const index = selectedItems.value.indexOf(item.id);
  if (index > -1) {
    selectedItems.value.splice(index, 1);
  } else {
    selectedItems.value.push(item.id);
  }
};

// 토스트 표시
const showToast = (message) => {
  toastMessage.value = message;
  setTimeout(() => {
    toastMessage.value = '';
  }, 2500);
};

// 즐겨찾기 토글 (최대 20개 제한 처리)
const handleToggleFavorite = (item) => {
  const result = recordsStore.toggleFavorite(item.id);
  if (result && !result.success) {
    showToast(result.message);
  }
};

// 미리보기 열기
const openPreview = (item) => {
  previewItem.value = item;
};

// 미리보기 닫기
const closePreview = () => {
  previewItem.value = null;
};

// 단일 아이템 다운로드
const downloadItem = async (item) => {
  try {
    if (item.type === 'video') {
      // 비디오: Blob에서 직접 다운로드
      const videoData = recordsStore.getVideoBlob(item.id);
      if (videoData && videoData.blob) {
        const url = URL.createObjectURL(videoData.blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${item.title}.webm`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast('영상이 저장되었습니다.');
      } else if (item.url && item.url.startsWith('blob:')) {
        // Blob Map에 없지만 URL이 아직 유효한 경우
        const response = await fetch(item.url);
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${item.title}.webm`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast('영상이 저장되었습니다.');
      } else {
        showToast('영상이 만료되었습니다. 새로 녹화해주세요.');
      }
    } else {
      // 사진: 기존 방식
      const response = await fetch(item.url);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${item.title}.jpg`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast('저장되었습니다.');
    }
  } catch (error) {
    console.error('다운로드 실패:', error);
    showToast('저장에 실패했습니다.');
  }
};

// 선택된 아이템들 다운로드
const downloadSelected = () => {
  const items = recordsStore.mediaItems.filter(item => selectedItems.value.includes(item.id));
  items.forEach(item => downloadItem(item));
};

// 단일 아이템 공유
const shareItem = async (item) => {
  if (navigator.share) {
    try {
      await navigator.share({
        title: item.title,
        text: `${item.title} - ${item.date}`,
        url: item.url
      });
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('공유 실패:', error);
      }
    }
  } else {
    try {
      await navigator.clipboard.writeText(item.url);
      showToast('링크가 클립보드에 복사되었습니다.');
    } catch (error) {
      showToast('내보내기를 지원하지 않는 브라우저입니다.');
    }
  }
};

// 선택된 아이템들 공유
const shareSelected = async () => {
  const items = recordsStore.mediaItems.filter(item => selectedItems.value.includes(item.id));
  if (navigator.share) {
    const text = items.map(item => `${item.title}: ${item.url}`).join('\n');
    try {
      await navigator.share({
        title: '핵심기록 내보내기',
        text: text
      });
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('공유 실패:', error);
      }
    }
  } else {
    const urls = items.map(item => item.url).join('\n');
    try {
      await navigator.clipboard.writeText(urls);
      showToast('링크가 클립보드에 복사되었습니다.');
    } catch (error) {
      showToast('내보내기를 지원하지 않는 브라우저입니다.');
    }
  }
};

// 선택된 아이템들 삭제
const deleteSelected = () => {
  if (confirm(`${selectedItems.value.length}개의 기록을 삭제하시겠습니까?`)) {
    recordsStore.deleteItems(selectedItems.value);
    selectedItems.value = [];
    selectMode.value = false;
    showToast('삭제되었습니다.');
  }
};
</script>

<style scoped>
.records-view {
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

.select-btn {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #3182f6;
  background: none;
}

.content {
  padding: 16px;
}

/* 탭 메뉴 */
.tab-menu {
  display: flex;
  gap: 6px;
  margin-bottom: 14px;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 10px 4px;
  background: #fff;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: #8b95a1;
  transition: all 0.2s;
}

.tab-item.active {
  background: #3182f6;
  color: #fff;
}

.tab-badge.small {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 5px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 6px;
}

.tab-item.active .tab-badge {
  background: rgba(255, 255, 255, 0.2);
}

/* 활동기록 탭 */
.activity-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.date-picker-section {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
}

.date-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #6b7684;
  margin-bottom: 10px;
}

.date-input {
  width: 100%;
  padding: 14px 16px;
  font-size: 16px;
  font-weight: 600;
  color: #191f28;
  background: #f2f4f6;
  border: none;
  border-radius: 12px;
  cursor: pointer;
}

.date-input:focus {
  outline: 2px solid #3182f6;
  background: #fff;
}

.activity-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activity-btn {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: #fff;
  border-radius: 16px;
  text-align: left;
  transition: all 0.2s;
}

.activity-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.activity-btn:active {
  transform: scale(0.98);
}

.activity-btn-icon {
  position: relative;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-btn-icon.photo {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  color: #0284c7;
}

.activity-btn-icon.video {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  color: #db2777;
}

.activity-btn-icon.favorite-photo {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
}

.activity-btn-icon.favorite-video {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #6366f1;
}

.activity-btn-icon .star-badge {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  padding: 3px;
  color: #F59E0B;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.activity-btn-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.activity-btn-title {
  font-size: 16px;
  font-weight: 600;
  color: #191f28;
}

.activity-btn-desc {
  font-size: 13px;
  color: #8b95a1;
}

.activity-btn-arrow {
  color: #b0b8c1;
  flex-shrink: 0;
}

/* 활동기록 미디어 섹션 */
.activity-media-section {
  margin-top: 8px;
}

.activity-media-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.activity-back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: #fff;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #3182f6;
}

.activity-media-title {
  font-size: 15px;
  font-weight: 600;
  color: #191f28;
}

/* 필터 바 */
.filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #fff;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7684;
  transition: all 0.2s;
}

.filter-chip.active {
  background: #191f28;
  color: #fff;
}

/* 안내 배너 */
.info-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: #e7f1ff;
  border-radius: 12px;
  margin-bottom: 16px;
}

.info-banner svg {
  flex-shrink: 0;
  color: #3182f6;
  margin-top: 2px;
}

.info-banner span {
  font-size: 13px;
  color: #3182f6;
  line-height: 1.5;
}

/* 미디어 섹션 */
.media-section {
  min-height: 300px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #b0b8c1;
}

.empty-state.small {
  padding: 40px 20px;
}

.empty-state p {
  margin-top: 12px;
  font-size: 14px;
}

.empty-hint {
  margin-top: 8px;
  font-size: 13px;
  color: #8b95a1;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.media-item {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: transform 0.2s;
  position: relative;
}

.media-item:hover {
  transform: translateY(-2px);
}

.media-thumbnail {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
}

.media-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 6px;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
}

.video-badge.small {
  padding: 3px 6px;
  font-size: 10px;
  gap: 3px;
}

.favorite-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b0b8c1;
  transition: all 0.2s;
}

.favorite-btn.active {
  color: #F59E0B;
}

.media-info {
  padding: 12px;
}

.media-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #191f28;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.media-date {
  font-size: 12px;
  color: #8b95a1;
}

.select-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid #b0b8c1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.select-checkbox.selected {
  background: #3182f6;
  border-color: #3182f6;
}

.bottom-spacer {
  height: 80px;
}

/* 하단 액션 */
.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  padding-bottom: max(16px, env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1px solid #e5e8eb;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
}

.selected-count {
  font-size: 14px;
  font-weight: 600;
  color: #3182f6;
  margin-bottom: 12px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px;
  background: #f2f4f6;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #4e5968;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #e5e8eb;
}

.action-btn.delete {
  color: #EF4444;
}

/* 미리보기 모달 */
.preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  z-index: 99999;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  padding-top: max(16px, env(safe-area-inset-top));
}

.preview-close, .preview-favorite {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.preview-favorite.active {
  color: #F59E0B;
}

.preview-title {
  text-align: center;
}

.title-text {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.title-date {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.preview-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: hidden;
}

.preview-content img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

/* 동영상 플레이어 */
.video-player {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 100%;
  cursor: pointer;
}

.video-frame {
  max-width: 100%;
  max-height: calc(100vh - 220px);
  object-fit: contain;
  border-radius: 12px;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  transition: opacity 0.3s;
}

.video-overlay.hidden {
  opacity: 0;
  pointer-events: none;
}

.play-overlay-btn {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #191f28;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.play-overlay-btn svg {
  margin-left: 4px;
}

.video-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  max-width: 400px;
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
}

.play-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #3182f6;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.play-btn:hover {
  background: #1b64da;
  transform: scale(1.05);
}

.progress-wrapper {
  flex: 1;
  cursor: pointer;
  padding: 8px 0;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-wrapper:hover .progress-bar {
  height: 6px;
}

.progress-fill {
  height: 100%;
  background: #3182f6;
  border-radius: 2px;
  transition: width 0.1s linear;
}

.video-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  white-space: nowrap;
  min-width: 50px;
  text-align: right;
}

.no-frames-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 12px;
  color: #fff;
}

.no-frames-overlay p {
  font-size: 16px;
  font-weight: 600;
}

.no-frames-overlay span {
  font-size: 24px;
  font-weight: 700;
  color: #3182f6;
}

.video-duration-badge {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
}

.preview-actions {
  display: flex;
  justify-content: center;
  gap: 32px;
  padding: 20px;
  padding-bottom: max(20px, env(safe-area-inset-bottom));
}

.preview-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
}

.preview-action-btn svg {
  width: 28px;
  height: 28px;
}

/* 토스트 메시지 */
.toast-message {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  z-index: 999999;
  animation: toastFade 0.3s ease;
}

@keyframes toastFade {
  from {
    opacity: 0;
    transform: translate(-50%, 20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>
