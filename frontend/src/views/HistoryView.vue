<template>
  <div class="history">
    <header class="header">
      <h1 class="header-title">활동 기록</h1>
      <button class="filter-btn" @click="showFilter = !showFilter">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
        </svg>
      </button>
    </header>

    <!-- 월간 달력 -->
    <div class="calendar-section">
      <div class="calendar-header">
        <button class="cal-nav-btn" @click="prevMonth">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <span class="cal-month">{{ currentMonthText }}</span>
        <button class="cal-nav-btn" @click="nextMonth" :disabled="isCurrentMonth">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>

      <!-- 요일 헤더 -->
      <div class="weekday-header">
        <span v-for="day in weekdays" :key="day" class="weekday" :class="{ sun: day === '일', sat: day === '토' }">{{ day }}</span>
      </div>

      <!-- 월간 달력 그리드 -->
      <div class="calendar-grid">
        <button
          v-for="(day, index) in calendarDays"
          :key="index"
          class="calendar-day"
          :class="{
            'other-month': !day.isCurrentMonth,
            'today': day.isToday,
            'selected': day.dateStr === selectedDateStr,
            'has-records': day.hasLogs,
            'disabled': day.isFuture || day.isOld
          }"
          :disabled="day.isFuture || day.isOld || !day.isCurrentMonth"
          @click="selectCalendarDay(day)"
        >
          <span class="day-number">{{ day.day }}</span>
          <span v-if="day.hasLogs && day.isCurrentMonth && !day.isOld" class="day-dot"></span>
        </button>
      </div>
    </div>

    <!-- 2주 보관 안내 배너 -->
    <div class="retention-banner">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12.01" y2="8"/>
      </svg>
      <span>활동 기록은 <strong>최근 2주간</strong>만 보관됩니다. 필요한 기록은 내보내기 또는 저장해 주세요.</span>
    </div>

    <!-- 필터 패널 -->
    <div v-if="showFilter" class="filter-panel">
      <div class="filter-chips">
        <button
          v-for="filter in filters"
          :key="filter.value"
          class="filter-chip"
          :class="{ active: selectedFilter === filter.value }"
          @click="selectedFilter = filter.value"
        >
          {{ filter.label }}
        </button>
      </div>
    </div>

    <main class="content">
      <!-- 미디어 기록 섹션 -->
      <section class="media-section">
        <div class="section-header">
          <h3 class="section-title">미디어 기록</h3>
          <div class="media-filter-tabs">
            <button
              class="media-tab"
              :class="{ active: mediaTab === 'all' }"
              @click="mediaTab = 'all'"
            >전체</button>
            <button
              class="media-tab"
              :class="{ active: mediaTab === 'photo' }"
              @click="mediaTab = 'photo'"
            >사진</button>
            <button
              class="media-tab"
              :class="{ active: mediaTab === 'video' }"
              @click="mediaTab = 'video'"
            >동영상</button>
            <button
              class="media-tab favorite"
              :class="{ active: mediaTab === 'favorite' }"
              @click="mediaTab = 'favorite'"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="dateMediaItems.length === 0" class="media-empty">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
          <p>{{ formatDisplayDate(selectedDate) }}에 저장된 미디어가 없습니다</p>
        </div>

        <div v-else class="media-grid">
          <div
            v-for="item in dateMediaItems"
            :key="item.id"
            class="media-item"
            @click="openMediaPreview(item)"
          >
            <div class="media-thumb">
              <img :src="item.thumbnail" :alt="item.title" />
              <div v-if="item.type === 'video'" class="media-badge video">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                {{ item.duration }}
              </div>
              <div v-if="item.isFavorite" class="media-badge favorite">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 선택된 날짜 요약 카드 -->
      <section class="summary-card">
        <div class="summary-header">
          <span class="summary-label">{{ isToday ? '오늘의 활동' : formatDisplayDate(selectedDate) + ' 활동' }}</span>
          <span class="summary-date">{{ formatWeekday(selectedDate) }}</span>
        </div>
        <div class="summary-stats">
          <div class="stat-item">
            <div class="stat-icon walk">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 4v16M7 4v16M3 8l4-4 4 4M13 20l4-4 4 4"/>
              </svg>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ selectedSummary.walkTime }}분</span>
              <span class="stat-label">산책 시간</span>
            </div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-icon events">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ selectedSummary.totalEvents }}건</span>
              <span class="stat-label">알림</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 활동 로그 목록 -->
      <section class="log-section">
        <div class="section-header">
          <h3 class="section-title">{{ formatSectionTitle(selectedDate) }}</h3>
          <span class="section-date">{{ formatFullDate(selectedDate) }}</span>
        </div>

        <div class="log-list">
          <div v-if="loading" class="empty-state">
            <p>로딩 중...</p>
          </div>
          <div v-else-if="filteredLogs.length === 0" class="empty-state">
            <p>{{ formatDisplayDate(selectedDate) }} 기록이 없습니다.</p>
          </div>
          <div
            v-else
            v-for="(log, index) in filteredLogs"
            :key="index"
            class="log-item"
          >
            <div class="log-icon" :class="log.type">
              <component :is="getIcon(log.type)" />
            </div>
            <div class="log-content">
              <span class="log-message">{{ log.msg }}</span>
              <span class="log-detail" v-if="log.detail">{{ log.detail }}</span>
            </div>
            <span class="log-time">{{ log.time }}</span>
          </div>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

    <!-- 미디어 미리보기 모달 -->
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
          <div style="width: 44px;"></div>
        </div>

        <div class="preview-content" @click.stop>
          <img v-if="previewItem.type === 'photo'" :src="previewItem.url" :alt="previewItem.title" />
          <div v-else class="video-preview">
            <img :src="previewItem.thumbnail" :alt="previewItem.title" />
            <div class="video-play-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
            </div>
            <span class="video-duration">{{ previewItem.duration }}</span>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 날짜 선택 모달 -->
    <div v-if="showDatePicker" class="modal-overlay" @click="showDatePicker = false">
      <div class="date-picker-modal" @click.stop>
        <div class="modal-header">
          <h3>날짜 선택</h3>
          <button class="modal-close" @click="showDatePicker = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="calendar-input">
          <input
            type="date"
            :value="formatDateForInput(selectedDate)"
            :min="formatDateForInput(minSelectableDate)"
            :max="formatDateForInput(new Date())"
            @change="onDateSelect"
          />
          <p class="date-hint">최근 2주간의 기록만 확인할 수 있습니다.</p>
        </div>
        <div class="recent-dates">
          <p class="recent-label">최근 2주</p>
          <div class="recent-list">
            <button
              v-for="date in recentDates"
              :key="date.toISOString()"
              class="recent-date-btn"
              :class="{ active: isSameDay(date, selectedDate) }"
              @click="selectDate(date)"
            >
              {{ formatRecentDate(date) }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 하단 네비게이션 -->
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
      <button class="nav-item active">
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
import { ref, computed, h, onMounted, onUnmounted, watch } from 'vue';
import { activityApi } from '../api';
import { useRobotStore } from '@/stores/robotStore';
import { useRecordsStore } from '@/stores/recordsStore';

const robotStore = useRobotStore();
const recordsStore = useRecordsStore();

const showFilter = ref(false);

// 미디어 관련
const mediaTab = ref('all'); // 'all' | 'photo' | 'video' | 'favorite'
const previewItem = ref(null);
const showDatePicker = ref(false);
const selectedFilter = ref('all');
const loading = ref(true);
const selectedDate = ref(new Date());

// 요일 배열
const weekdays = ['일', '월', '화', '수', '목', '금', '토'];

// 월간 달력 관련
const currentYear = ref(new Date().getFullYear());
const currentMonth = ref(new Date().getMonth());
const datesWithLogs = ref(new Set()); // 기록이 있는 날짜들

// 선택된 날짜 문자열 (YYYY-MM-DD)
const selectedDateStr = computed(() => formatDateStr(selectedDate.value));

const currentMonthText = computed(() => {
  return `${currentYear.value}년 ${currentMonth.value + 1}월`;
});

const isCurrentMonth = computed(() => {
  const now = new Date();
  return currentYear.value === now.getFullYear() && currentMonth.value === now.getMonth();
});

// 월간 달력 날짜 배열 (6주 = 42일)
const calendarDays = computed(() => {
  const days = [];
  const firstDay = new Date(currentYear.value, currentMonth.value, 1);
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // 2주 전 날짜 (이보다 오래된 날짜는 비활성화)
  const twoWeeksAgo = new Date(today);
  twoWeeksAgo.setDate(today.getDate() - (MAX_DAYS - 1));
  twoWeeksAgo.setHours(0, 0, 0, 0);

  const startDayOfWeek = firstDay.getDay();
  const prevMonthLastDay = new Date(currentYear.value, currentMonth.value, 0).getDate();

  // 이전 달 날짜
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const day = prevMonthLastDay - i;
    const date = new Date(currentYear.value, currentMonth.value - 1, day);
    date.setHours(0, 0, 0, 0);
    const dateStr = formatDateStr(date);
    days.push({
      day,
      dateStr,
      isCurrentMonth: false,
      isToday: false,
      isFuture: date > today,
      isOld: date < twoWeeksAgo,
      hasLogs: datesWithLogs.value.has(dateStr)
    });
  }

  // 이번 달 날짜
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const date = new Date(currentYear.value, currentMonth.value, day);
    date.setHours(0, 0, 0, 0);
    const dateStr = formatDateStr(date);
    days.push({
      day,
      dateStr,
      isCurrentMonth: true,
      isToday: date.getTime() === today.getTime(),
      isFuture: date > today,
      isOld: date < twoWeeksAgo,
      hasLogs: datesWithLogs.value.has(dateStr)
    });
  }

  // 다음 달 날짜 (4주 = 28일 채우기)
  const remainingDays = 28 - days.length;
  for (let day = 1; day <= remainingDays; day++) {
    const date = new Date(currentYear.value, currentMonth.value + 1, day);
    date.setHours(0, 0, 0, 0);
    const dateStr = formatDateStr(date);
    days.push({
      day,
      dateStr,
      isCurrentMonth: false,
      isToday: false,
      isFuture: date > today,
      isOld: date < twoWeeksAgo,
      hasLogs: datesWithLogs.value.has(dateStr)
    });
  }

  return days;
});

function formatDateStr(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11;
    currentYear.value--;
  } else {
    currentMonth.value--;
  }
};

const nextMonth = () => {
  if (!isCurrentMonth.value) {
    if (currentMonth.value === 11) {
      currentMonth.value = 0;
      currentYear.value++;
    } else {
      currentMonth.value++;
    }
  }
};

const selectCalendarDay = (day) => {
  if (day.isCurrentMonth && !day.isFuture && !day.isOld) {
    const [year, month, dayNum] = day.dateStr.split('-').map(Number);
    selectedDate.value = new Date(year, month - 1, dayNum);
  }
};

const filters = [
  { label: '전체', value: 'all' },
  { label: '정보', value: 'info' },
  { label: '주의', value: 'warning' },
  { label: '활동', value: 'action' }
];

const selectedSummary = ref({
  totalEvents: 0,
  walkTime: 0,
  alerts: 0,
  distance: 0
});

// 선택된 날짜의 로그
const selectedLogs = ref([]);

// 최대 조회 가능 기간 (2주 = 14일)
const MAX_DAYS = 14;

// 최근 14일 날짜 목록 (최신순)
const recentDates = computed(() => {
  const dates = [];
  const today = new Date();
  for (let i = 0; i < MAX_DAYS; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    dates.push(date);
  }
  return dates;
});

// 2주 전 날짜 (최소 선택 가능 날짜)
const minSelectableDate = computed(() => {
  const date = new Date();
  date.setDate(date.getDate() - (MAX_DAYS - 1));
  date.setHours(0, 0, 0, 0);
  return date;
});

// 오늘인지 확인
const isToday = computed(() => {
  const today = new Date();
  return isSameDay(selectedDate.value, today);
});

// 어제인지 확인
const isYesterday = computed(() => {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  return isSameDay(selectedDate.value, yesterday);
});

// 2주 전인지 확인
const isTwoWeeksAgo = computed(() => {
  const twoWeeksAgo = new Date();
  twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 13);
  return isSameDay(selectedDate.value, twoWeeksAgo);
});

// 가장 오래된 날짜인지 확인 (더 이전으로 이동 불가)
const isOldestDate = computed(() => {
  return selectedDate.value <= minSelectableDate.value;
});

// 필터링된 로그 (오늘이면 WebSocket 로그 포함)
const filteredLogs = computed(() => {
  let logs = selectedLogs.value;

  // 오늘이면 WebSocket에서 받은 실시간 로그도 포함
  if (isToday.value && robotStore.activityLogs.length > 0) {
    logs = [...robotStore.activityLogs, ...logs];
  }

  if (selectedFilter.value === 'all') return logs;
  return logs.filter(log => log.type === selectedFilter.value);
});

// 날짜 비교 함수
function isSameDay(date1, date2) {
  return date1.getFullYear() === date2.getFullYear() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getDate() === date2.getDate();
}


// 날짜 포맷 함수들
function formatDisplayDate(date) {
  return date.toLocaleDateString('ko-KR', {
    month: 'long', day: 'numeric'
  });
}

function formatWeekday(date) {
  return date.toLocaleDateString('ko-KR', { weekday: 'short' });
}

function formatFullDate(date) {
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric', month: 'long', day: 'numeric'
  });
}

function formatSectionTitle(date) {
  if (isToday.value) return '오늘';
  if (isYesterday.value) return '어제';
  return formatDisplayDate(date);
}

function formatDateForInput(date) {
  return date.toISOString().split('T')[0];
}

function formatRecentDate(date) {
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);

  if (isSameDay(date, today)) return '오늘';
  if (isSameDay(date, yesterday)) return '어제';
  return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', weekday: 'short' });
}

function formatDateForApi(date) {
  return date.toISOString().split('T')[0];
}

// 날짜 변경 함수
function changeDate(offset) {
  const newDate = new Date(selectedDate.value);
  newDate.setDate(newDate.getDate() + offset);

  // 미래 날짜는 선택 불가
  if (newDate > new Date()) return;

  // 2주 이전 날짜는 선택 불가
  if (newDate < minSelectableDate.value) return;

  selectedDate.value = newDate;
}

function goToToday() {
  selectedDate.value = new Date();
}

function goToYesterday() {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  selectedDate.value = yesterday;
}

function goToTwoWeeksAgo() {
  const twoWeeksAgo = new Date();
  twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 13); // 오늘 포함 14일
  selectedDate.value = twoWeeksAgo;
}

function selectDate(date) {
  // 2주 이전 날짜는 선택 불가
  if (date < minSelectableDate.value) return;
  selectedDate.value = new Date(date);
  showDatePicker.value = false;
}


function onDateSelect(event) {
  const date = new Date(event.target.value);
  // 2주 이전 날짜는 선택 불가
  if (date < minSelectableDate.value) {
    alert('최근 2주간의 기록만 확인할 수 있습니다.');
    return;
  }
  selectedDate.value = date;
  showDatePicker.value = false;
}

// 선택된 날짜의 미디어 필터링
const dateMediaItems = computed(() => {
  const selectedDateStr = formatDateForApi(selectedDate.value);
  let items = [...recordsStore.mediaItems];

  // 날짜 필터
  items = items.filter(item => {
    const itemDate = item.rawDate || item.date;
    if (!itemDate) return false;

    if (item.rawDate) {
      const itemDateStr = new Date(item.rawDate).toISOString().split('T')[0];
      return itemDateStr === selectedDateStr;
    }

    // date 문자열 파싱 (예: "2024.01.15" 또는 "2024-01-15")
    const dateMatch = item.date.match(/(\d{4})[.-](\d{2})[.-](\d{2})/);
    if (dateMatch) {
      const itemDateStr = `${dateMatch[1]}-${dateMatch[2]}-${dateMatch[3]}`;
      return itemDateStr === selectedDateStr;
    }

    return false;
  });

  // 탭 필터
  if (mediaTab.value === 'photo') {
    items = items.filter(item => item.type === 'photo');
  } else if (mediaTab.value === 'video') {
    items = items.filter(item => item.type === 'video');
  } else if (mediaTab.value === 'favorite') {
    items = items.filter(item => item.isFavorite);
  }

  return items;
});

// 미디어 미리보기 열기
function openMediaPreview(item) {
  previewItem.value = item;
}

// 미디어 미리보기 닫기
function closePreview() {
  previewItem.value = null;
}

// 데이터 로드
const fetchActivityData = async () => {
  loading.value = true;
  try {
    const dateStr = formatDateForApi(selectedDate.value);

    let logsResponse;
    if (isToday.value) {
      logsResponse = await activityApi.getTodayLogs();
    } else if (isYesterday.value) {
      logsResponse = await activityApi.getYesterdayLogs();
    } else {
      logsResponse = await activityApi.getLogsByDate(dateStr);
    }

    selectedLogs.value = logsResponse.data;

    // 요약 정보: 오늘이면 실시간 WebSocket 데이터, 아니면 API 로그 기반 계산
    const logs = logsResponse.data;
    if (isToday.value && robotStore.dailySummary.walkTime > 0) {
      // 오늘: WebSocket 실시간 데이터 사용
      selectedSummary.value = {
        totalEvents: robotStore.dailySummary.totalEvents || logs.length,
        walkTime: robotStore.dailySummary.walkTime,
        distance: robotStore.dailySummary.distance || 0,
        alerts: robotStore.dailySummary.alerts
      };
    } else {
      // 과거: API 로그 기반 계산
      selectedSummary.value = {
        totalEvents: logs.length,
        walkTime: logs.filter(l => l.type === 'action').length * 5,
        distance: (logs.length * 0.1).toFixed(1),
        alerts: logs.filter(l => l.type === 'warning').length
      };
    }
  } catch (error) {
    console.error('활동 기록 조회 실패:', error);
    selectedLogs.value = [];
  } finally {
    loading.value = false;
  }
};

// 날짜 변경 시 데이터 다시 로드
watch(selectedDate, () => {
  fetchActivityData();
});

// WebSocket에서 실시간 요약 데이터 받으면 업데이트 (오늘만)
watch(() => robotStore.dailySummary, (newSummary) => {
  if (isToday.value && newSummary.walkTime > 0) {
    selectedSummary.value = {
      ...selectedSummary.value,
      walkTime: newSummary.walkTime,
      alerts: newSummary.alerts,
      totalEvents: newSummary.totalEvents || selectedSummary.value.totalEvents
    };
  }
}, { deep: true });

onMounted(() => {
  robotStore.connectWebSocket();
  fetchActivityData();
});

onUnmounted(() => {
  robotStore.disconnectWebSocket();
});

// 아이콘 컴포넌트
const getIcon = (type) => {
  const icons = {
    info: () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('circle', { cx: 12, cy: 12, r: 10 }),
      h('line', { x1: 12, y1: 16, x2: 12, y2: 12 }),
      h('line', { x1: 12, y1: 8, x2: 12.01, y2: 8 })
    ]),
    warning: () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' }),
      h('line', { x1: 12, y1: 9, x2: 12, y2: 13 }),
      h('line', { x1: 12, y1: 17, x2: 12.01, y2: 17 })
    ]),
    action: () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('polygon', { points: '13 2 3 14 12 14 11 22 21 10 12 10 13 2' })
    ])
  };
  return icons[type] || icons.info;
};
</script>

<style scoped>
.history {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 80px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--bg-primary);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.filter-btn {
  width: 40px;
  height: 40px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: background 0.2s;
}

.filter-btn:active {
  background: var(--gray-200);
}

/* 월간 달력 */
.calendar-section {
  background: var(--bg-primary);
  padding: 16px 20px 20px;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.cal-nav-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.cal-nav-btn:hover:not(:disabled) {
  background: var(--gray-200);
}

.cal-nav-btn:disabled {
  opacity: 0.3;
}

.cal-month {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 6px;
}

.weekday {
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  padding: 6px 0;
}

.weekday.sun {
  color: #EF4444;
}

.weekday.sat {
  color: var(--primary);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  transition: all 0.15s;
  position: relative;
}

.calendar-day:hover:not(:disabled):not(.other-month) {
  background: var(--bg-tertiary);
}

.calendar-day.other-month {
  color: var(--gray-300);
}

.calendar-day.disabled {
  color: var(--gray-300);
  opacity: 0.4;
  cursor: not-allowed;
  background: transparent;
}

.calendar-day.disabled:hover {
  background: transparent;
}

.calendar-day .day-number {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

.calendar-day.today .day-number {
  background: var(--primary);
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.calendar-day.selected {
  background: var(--primary-light);
}

.calendar-day.selected .day-number {
  color: var(--primary);
  font-weight: 700;
}

.calendar-day.today.selected .day-number {
  background: var(--primary);
  color: white;
}

.day-dot {
  width: 5px;
  height: 5px;
  background: var(--success);
  border-radius: 50%;
  position: absolute;
  bottom: 4px;
}

.selected-date-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--gray-100);
  text-align: center;
}

.selected-date-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
}

/* 2주 보관 안내 배너 */
.retention-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  margin: 0 16px;
  background: #fff3cd;
  border-radius: 12px;
  border: 1px solid #ffc107;
}

.retention-banner svg {
  flex-shrink: 0;
  color: #856404;
  margin-top: 2px;
}

.retention-banner span {
  font-size: 13px;
  color: #856404;
  line-height: 1.5;
}

.retention-banner strong {
  font-weight: 700;
}

/* 필터 패널 */
.filter-panel {
  background: var(--bg-primary);
  padding: 12px 20px 16px;
  border-bottom: 1px solid var(--gray-100);
}

.filter-chips {
  display: flex;
  gap: 8px;
}

.filter-chip {
  padding: 8px 16px;
  border: 1px solid var(--gray-200);
  border-radius: 20px;
  background: var(--bg-primary);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.filter-chip.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.content {
  padding: 0 20px 20px;
}

/* 요약 카드 */
.summary-card {
  background: var(--bg-primary);
  border-radius: 20px;
  padding: 20px;
  margin-top: 20px;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.summary-label {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.summary-date {
  font-size: 13px;
  color: var(--text-tertiary);
}

.summary-stats {
  display: flex;
  align-items: center;
}

.stat-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--gray-100);
  margin: 0 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.walk {
  background: var(--primary-light);
  color: var(--primary);
}

.stat-icon.distance {
  background: var(--success-light);
  color: var(--success);
}

.stat-icon.events {
  background: var(--warning-light);
  color: var(--warning);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* 미디어 섹션 */
.media-section {
  margin-top: 24px;
  background: var(--bg-primary);
  border-radius: 20px;
  padding: 20px;
}

.media-section .section-header {
  margin-bottom: 16px;
}

.media-filter-tabs {
  display: flex;
  gap: 6px;
}

.media-tab {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  background: var(--bg-tertiary);
  transition: all 0.2s;
}

.media-tab.active {
  background: var(--primary);
  color: white;
}

.media-tab.favorite {
  padding: 6px 10px;
  display: flex;
  align-items: center;
  color: var(--text-tertiary);
}

.media-tab.favorite.active {
  background: #F59E0B;
  color: white;
}

.media-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  color: var(--text-tertiary);
}

.media-empty svg {
  opacity: 0.5;
}

.media-empty p {
  margin-top: 12px;
  font-size: 13px;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.media-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.media-item:active {
  transform: scale(0.95);
}

.media-thumb {
  position: relative;
  aspect-ratio: 1;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-tertiary);
}

.media-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.media-badge {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 9px;
  font-weight: 600;
}

.media-badge.video {
  bottom: 4px;
  left: 4px;
  padding: 2px 5px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 4px;
  color: #fff;
}

.media-badge.favorite {
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  justify-content: center;
  color: #F59E0B;
}

/* 로그 섹션 */
.log-section {
  margin-top: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-date {
  font-size: 13px;
  color: var(--text-tertiary);
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 28px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 16px;
}

.log-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.log-icon.info {
  background: var(--success-light);
  color: var(--success);
}

.log-icon.warning {
  background: var(--warning-light);
  color: var(--warning);
}

.log-icon.action {
  background: var(--primary-light);
  color: var(--primary);
}

.log-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.log-message {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.log-detail {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.log-time {
  font-size: 13px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.bottom-spacer {
  height: 20px;
}

.empty-state {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 32px 16px;
  text-align: center;
  color: var(--text-tertiary);
  font-size: 14px;
}

/* 날짜 선택 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}

.date-picker-modal {
  background: var(--bg-primary);
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 600px;
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.calendar-input {
  margin-bottom: 24px;
}

.calendar-input input {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  font-size: 16px;
  color: var(--text-primary);
  background: var(--bg-primary);
}

.date-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 8px;
  text-align: center;
}

.recent-dates {
  margin-bottom: 20px;
}

.recent-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
  margin-bottom: 12px;
}

.recent-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.recent-date-btn {
  padding: 10px 16px;
  border-radius: 12px;
  background: var(--bg-tertiary);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.recent-date-btn.active {
  background: var(--primary);
  color: white;
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
  background: var(--bg-primary);
  border-top: 1px solid var(--gray-100);
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
  color: var(--gray-400);
}

.nav-item svg {
  width: 24px;
  height: 24px;
}

.nav-item span {
  font-size: 11px;
  font-weight: 500;
}

.nav-item.active {
  color: var(--primary);
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

.preview-close {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
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

.video-preview {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-preview img {
  max-width: 100%;
  max-height: calc(100vh - 200px);
  object-fit: contain;
  border-radius: 12px;
}

.video-play-icon {
  position: absolute;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #191f28;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.video-play-icon svg {
  margin-left: 4px;
}

.video-duration {
  position: absolute;
  bottom: 12px;
  right: 12px;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
}
</style>
