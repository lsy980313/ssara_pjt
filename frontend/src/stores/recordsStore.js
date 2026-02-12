import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useRecordsStore = defineStore('records', () => {
  // 저장된 미디어 목록
  const mediaItems = ref([]);

  // 비디오 Blob 메모리 저장소 (localStorage에 Blob을 넣을 수 없으므로)
  const videoBlobs = new Map();

  // 상수
  const MAX_FAVORITES = 20;
  const RECENT_DAYS = 2;

  // localStorage에서 불러오기
  const loadFromStorage = () => {
    try {
      const saved = localStorage.getItem('robotRecords');
      if (saved) {
        mediaItems.value = JSON.parse(saved);
        // 로드 시 오래된 기록 정리
        cleanupOldRecords();
      }
    } catch (e) {
      console.error('기록 불러오기 실패:', e);
    }
  };

  // localStorage에 저장
  const saveToStorage = () => {
    try {
      localStorage.setItem('robotRecords', JSON.stringify(mediaItems.value));
    } catch (e) {
      console.error('기록 저장 실패:', e);
    }
  };

  // 오래된 기록 정리 (즐겨찾기 제외, 2일 초과 항목 삭제)
  const cleanupOldRecords = () => {
    const twoDaysAgo = Date.now() - (RECENT_DAYS * 24 * 60 * 60 * 1000);
    const beforeCount = mediaItems.value.length;

    mediaItems.value = mediaItems.value.filter(item => {
      // 즐겨찾기는 유지
      if (item.isFavorite) return true;
      // 2일 이내 기록만 유지
      return item.timestamp > twoDaysAgo;
    });

    if (mediaItems.value.length !== beforeCount) {
      saveToStorage();
    }
  };

  // 사진 추가
  const addPhoto = (dataUrl, title = '') => {
    const now = new Date();
    const id = Date.now();
    const dateStr = `${now.getFullYear()}.${String(now.getMonth() + 1).padStart(2, '0')}.${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

    const item = {
      id,
      type: 'photo',
      title: title || `사진 ${now.getHours()}시 ${now.getMinutes()}분`,
      date: dateStr,
      timestamp: now.getTime(),
      thumbnail: dataUrl,
      url: dataUrl,
      isFavorite: false
    };

    mediaItems.value.unshift(item);
    saveToStorage();
    return item;
  };

  // 동영상 추가 (실제 WebM Blob)
  const addVideo = (videoBlob, duration, title = '', thumbnail = '') => {
    const now = new Date();
    const id = Date.now();
    const dateStr = `${now.getFullYear()}.${String(now.getMonth() + 1).padStart(2, '0')}.${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

    // Blob URL 생성 및 메모리 저장
    const blobUrl = URL.createObjectURL(videoBlob);
    videoBlobs.set(id, { blob: videoBlob, url: blobUrl });

    const item = {
      id,
      type: 'video',
      title: title || `녹화 ${now.getHours()}시 ${now.getMinutes()}분`,
      date: dateStr,
      timestamp: now.getTime(),
      duration: duration,
      thumbnail: thumbnail,
      url: blobUrl,
      isFavorite: false
    };

    mediaItems.value.unshift(item);
    saveToStorage();
    return item;
  };

  // 비디오 Blob 가져오기
  const getVideoBlob = (id) => {
    return videoBlobs.get(id) || null;
  };

  // 즐겨찾기 토글 (최대 20개 제한)
  const toggleFavorite = (id) => {
    const item = mediaItems.value.find(m => m.id === id);
    if (!item) return false;

    // 즐겨찾기 추가 시 최대 개수 확인
    if (!item.isFavorite) {
      const currentFavorites = mediaItems.value.filter(m => m.isFavorite).length;
      if (currentFavorites >= MAX_FAVORITES) {
        return { success: false, message: `즐겨찾기는 최대 ${MAX_FAVORITES}개까지 저장할 수 있습니다.` };
      }
    }

    item.isFavorite = !item.isFavorite;
    saveToStorage();
    return { success: true };
  };

  // 삭제
  const deleteItem = (id) => {
    const index = mediaItems.value.findIndex(m => m.id === id);
    if (index > -1) {
      mediaItems.value.splice(index, 1);
      saveToStorage();
    }
  };

  // 여러 개 삭제
  const deleteItems = (ids) => {
    mediaItems.value = mediaItems.value.filter(m => !ids.includes(m.id));
    saveToStorage();
  };

  // 전체 삭제
  const clearAll = () => {
    mediaItems.value = [];
    saveToStorage();
  };

  // 최근 기록 (2일 이내, 즐겨찾기 제외)
  const recentItems = computed(() => {
    const twoDaysAgo = Date.now() - (RECENT_DAYS * 24 * 60 * 60 * 1000);
    return [...mediaItems.value]
      .filter(item => !item.isFavorite && item.timestamp > twoDaysAgo)
      .sort((a, b) => b.timestamp - a.timestamp);
  });

  // 즐겨찾기 목록 (최대 20개)
  const favoriteItems = computed(() => {
    return mediaItems.value
      .filter(m => m.isFavorite)
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, MAX_FAVORITES);
  });

  // 즐겨찾기 개수
  const favoriteCount = computed(() => {
    return mediaItems.value.filter(m => m.isFavorite).length;
  });

  // 사진만
  const photoItems = computed(() => {
    return mediaItems.value.filter(m => m.type === 'photo');
  });

  // 동영상만
  const videoItems = computed(() => {
    return mediaItems.value.filter(m => m.type === 'video');
  });

  // 특정 날짜의 기록 가져오기 (YYYY-MM-DD 형식)
  const getItemsByDate = (dateString) => {
    return mediaItems.value.filter(item => {
      const itemDate = new Date(item.timestamp);
      const itemDateStr = `${itemDate.getFullYear()}-${String(itemDate.getMonth() + 1).padStart(2, '0')}-${String(itemDate.getDate()).padStart(2, '0')}`;
      return itemDateStr === dateString;
    }).sort((a, b) => b.timestamp - a.timestamp);
  };

  // 기록이 있는 날짜 목록 가져오기
  const getRecordDates = () => {
    const dates = new Set();
    mediaItems.value.forEach(item => {
      const itemDate = new Date(item.timestamp);
      const dateStr = `${itemDate.getFullYear()}-${String(itemDate.getMonth() + 1).padStart(2, '0')}-${String(itemDate.getDate()).padStart(2, '0')}`;
      dates.add(dateStr);
    });
    return Array.from(dates).sort((a, b) => b.localeCompare(a));
  };

  // 모든 기록 (날짜별 그룹)
  const allItemsGroupedByDate = computed(() => {
    const groups = {};
    mediaItems.value.forEach(item => {
      const itemDate = new Date(item.timestamp);
      const dateStr = `${itemDate.getFullYear()}-${String(itemDate.getMonth() + 1).padStart(2, '0')}-${String(itemDate.getDate()).padStart(2, '0')}`;
      if (!groups[dateStr]) {
        groups[dateStr] = [];
      }
      groups[dateStr].push(item);
    });
    // 각 그룹 내에서 시간순 정렬
    Object.keys(groups).forEach(date => {
      groups[date].sort((a, b) => b.timestamp - a.timestamp);
    });
    return groups;
  });

  // 초기화 시 localStorage에서 불러오기
  loadFromStorage();

  return {
    mediaItems,
    recentItems,
    favoriteItems,
    favoriteCount,
    photoItems,
    videoItems,
    allItemsGroupedByDate,
    addPhoto,
    addVideo,
    getVideoBlob,
    toggleFavorite,
    deleteItem,
    deleteItems,
    clearAll,
    loadFromStorage,
    getItemsByDate,
    getRecordDates,
    MAX_FAVORITES,
    RECENT_DAYS
  };
});
