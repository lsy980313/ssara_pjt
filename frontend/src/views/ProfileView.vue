<template>
  <div class="profile">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="header-title">내 정보</h1>
      <div style="width: 24px;"></div>
    </header>

    <main class="content">
      <!-- 프로필 카드 -->
      <section class="profile-card">
        <div class="avatar-wrapper" @click="showImageOptions = true">
          <div class="avatar" :style="profileImageStyle">
            <span v-if="!userInfo.profileImage">{{ userInfo.name?.charAt(0) || '?' }}</span>
          </div>
          <div class="avatar-edit">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleImageChange"
          />
        </div>
        <div class="user-info">
          <h2 class="user-name">{{ userInfo.name }}</h2>
          <p class="user-email">{{ userInfo.email }}</p>
        </div>
      </section>

      <!-- 프로필 사진 옵션 모달 -->
      <div v-if="showImageOptions" class="modal-overlay" @click.self="showImageOptions = false">
        <div class="action-sheet">
          <div class="action-sheet-header">
            <h3>프로필 사진</h3>
          </div>
          <div class="action-sheet-body">
            <button class="action-item" @click="triggerFileInput">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
              <span>앨범에서 선택</span>
            </button>
            <button class="action-item" @click="resetToDefault">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <span>기본 이미지로 변경</span>
            </button>
          </div>
          <button class="action-cancel" @click="showImageOptions = false">취소</button>
        </div>
      </div>

      <!-- 정보 섹션 -->
      <section class="section">
        <h3 class="section-title">기본 정보</h3>
        <div class="info-card">
          <div class="info-item">
            <span class="label">이름</span>
            <input
              v-if="isEditing"
              type="text"
              v-model="editForm.name"
              class="edit-input"
            />
            <span v-else class="value">{{ userInfo.name }}</span>
          </div>
          <div class="info-item">
            <span class="label">이메일</span>
            <span class="value text-tertiary">{{ userInfo.email }}</span>
          </div>
          <div class="info-item">
            <span class="label">전화번호</span>
            <input
              v-if="isEditing"
              type="tel"
              v-model="editForm.phoneNumber"
              placeholder="입력해 주세요"
              class="edit-input"
            />
            <span v-else class="value">{{ userInfo.phoneNumber || '미등록' }}</span>
          </div>
          <div v-if="isEditing" class="info-item">
            <span class="label">새 비밀번호</span>
            <input
              type="password"
              v-model="editForm.password"
              placeholder="변경 시에만 입력"
              class="edit-input"
            />
          </div>
        </div>

        <div class="button-row">
          <template v-if="isEditing">
            <button class="btn btn-secondary" @click="cancelEdit">취소</button>
            <button class="btn btn-primary" @click="saveChanges" :disabled="saving">
              {{ saving ? '저장 중...' : '저장' }}
            </button>
          </template>
          <button v-else class="btn btn-secondary full" @click="isEditing = true">
            정보 수정
          </button>
        </div>
      </section>

      <!-- 알림 설정 -->
      <section class="section">
        <h3 class="section-title">알림 설정</h3>
        <div class="info-card">
          <div class="toggle-item">
            <div class="toggle-info">
              <span class="toggle-label">푸시 알림</span>
              <span class="toggle-desc">앱 알림을 받습니다</span>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="notifications.push" @change="saveNotifications">
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="toggle-item">
            <div class="toggle-info">
              <span class="toggle-label">로봇 상태 알림</span>
              <span class="toggle-desc">연결 상태 변경 시 알림</span>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="notifications.robotStatus" @change="saveNotifications">
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="toggle-item">
            <div class="toggle-info">
              <span class="toggle-label">배터리 알림</span>
              <span class="toggle-desc">배터리 부족 시 알림</span>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="notifications.battery" @change="saveNotifications">
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="toggle-item">
            <div class="toggle-info">
              <span class="toggle-label">이상 감지 알림</span>
              <span class="toggle-desc">위험 상황 감지 시 알림</span>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="notifications.alert" @change="saveNotifications">
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="toggle-item">
            <div class="toggle-info">
              <span class="toggle-label">마케팅 알림</span>
              <span class="toggle-desc">이벤트 및 혜택 정보</span>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="notifications.marketing" @change="saveNotifications">
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
      </section>

      <!-- 연결된 로봇 -->
      <section class="section">
        <h3 class="section-title">연결된 로봇</h3>
        <div class="robot-card">
          <div class="robot-avatar">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
              <line x1="9" y1="9" x2="9.01" y2="9"/>
              <line x1="15" y1="9" x2="15.01" y2="9"/>
            </svg>
          </div>
          <div class="robot-info">
            <span class="robot-name">{{ robotState.name }}</span>
            <span class="robot-status" :class="{ online: robotState.status === 'ONLINE' }">
              {{ robotState.status === 'ONLINE' ? '연결됨' : '오프라인' }}
            </span>
          </div>
          <div class="robot-battery">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="1" y="6" width="18" height="12" rx="2" ry="2"/>
              <line x1="23" y1="13" x2="23" y2="11"/>
            </svg>
            {{ robotState.battery }}%
          </div>
        </div>
      </section>

      <!-- 계정 관리 -->
      <section class="section">
        <h3 class="section-title">계정</h3>
        <div class="menu-list">
          <button class="menu-item" @click="handleLogout">
            <span>로그아웃</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
          </button>
          <button class="menu-item danger" @click="handleDelete">
            <span>회원 탈퇴</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
      </section>

      <!-- 고객지원 -->
      <section class="section">
        <h3 class="section-title">고객지원</h3>
        <div class="menu-list">
          <button class="menu-item" @click="$router.push('/notices')">
            <span>공지사항</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
          <button class="menu-item" @click="$router.push('/inquiries')">
            <span>1:1문의 내역</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
        </div>
      </section>

      <!-- 고객센터 -->
      <section class="section">
        <div class="customer-center">
          <div class="cs-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
          </div>
          <div class="cs-info">
            <span class="cs-label">고객센터</span>
            <span class="cs-number">010-0000-0000</span>
          </div>
        </div>
      </section>

      <div class="bottom-spacer"></div>
    </main>

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
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { memberApi, notificationApi } from '../api';
import { robotState } from '../store.js';
import { useAuthStore } from '../stores/authStore';
import { requestFCMToken, onForegroundMessage } from '../firebase';

const router = useRouter();
const authStore = useAuthStore();

const fileInput = ref(null);

const userInfo = reactive({
  name: '',
  email: '',
  phoneNumber: '',
  profileImage: null
});

const editForm = reactive({
  name: '',
  phoneNumber: '',
  password: ''
});

const notifications = reactive({
  push: true,
  robotStatus: true,
  battery: true,
  alert: true,
  marketing: false
});

const isEditing = ref(false);
const saving = ref(false);
const showImageOptions = ref(false);

const profileImageStyle = computed(() => {
  if (userInfo.profileImage) {
    return {
      backgroundImage: `url(${userInfo.profileImage})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    };
  }
  return {};
});

const triggerFileInput = () => {
  showImageOptions.value = false;
  fileInput.value?.click();
};

const resetToDefault = () => {
  userInfo.profileImage = null;
  localStorage.removeItem('profileImage');
  showImageOptions.value = false;
};

const handleImageChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      alert('이미지 크기는 5MB 이하여야 합니다.');
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      userInfo.profileImage = e.target.result;
      localStorage.setItem('profileImage', e.target.result);
    };
    reader.readAsDataURL(file);
  }
};

const loadNotifications = async () => {
  try {
    const response = await notificationApi.getSettings();
    notifications.push = response.data.pushEnabled;
    notifications.robotStatus = response.data.robotStatusEnabled;
    notifications.battery = response.data.batteryEnabled;
    notifications.alert = response.data.alertEnabled;
    notifications.marketing = response.data.marketingEnabled;
  } catch (error) {
    console.error('알림 설정 조회 실패:', error);
    // 로컬 저장소에서 로드
    const saved = localStorage.getItem('notifications');
    if (saved) {
      Object.assign(notifications, JSON.parse(saved));
    }
  }
};

const saveNotifications = async () => {
  try {
    await notificationApi.updateSettings({
      pushEnabled: notifications.push,
      robotStatusEnabled: notifications.robotStatus,
      batteryEnabled: notifications.battery,
      alertEnabled: notifications.alert,
      marketingEnabled: notifications.marketing
    });

    // 푸시 알림이 활성화되면 FCM 토큰 등록
    if (notifications.push) {
      const fcmToken = await requestFCMToken();
      if (fcmToken) {
        await notificationApi.registerToken(fcmToken);
      }
    } else {
      // 비활성화 시 토큰 삭제
      await notificationApi.deleteToken();
    }

    localStorage.setItem('notifications', JSON.stringify(notifications));
  } catch (error) {
    console.error('알림 설정 저장 실패:', error);
    localStorage.setItem('notifications', JSON.stringify(notifications));
  }
};

const loadProfileImage = () => {
  const saved = localStorage.getItem('profileImage');
  if (saved) {
    userInfo.profileImage = saved;
  }
};

const fetchMyInfo = async () => {
  try {
    const response = await memberApi.getMyInfo();
    Object.assign(userInfo, response.data);
    editForm.name = userInfo.name;
    editForm.phoneNumber = userInfo.phoneNumber || '';
  } catch (error) {
    console.error('정보 조회 실패:', error);
  }
};

const cancelEdit = () => {
  isEditing.value = false;
  editForm.name = userInfo.name;
  editForm.phoneNumber = userInfo.phoneNumber || '';
  editForm.password = '';
};

const saveChanges = async () => {
  if (!editForm.name.trim()) {
    alert('이름을 입력해 주세요');
    return;
  }

  saving.value = true;
  try {
    await memberApi.updateMyInfo({
      name: editForm.name,
      phoneNumber: editForm.phoneNumber || null,
      password: editForm.password || null
    });
    alert('정보가 수정되었어요');
    isEditing.value = false;
    editForm.password = '';
    await fetchMyInfo();
  } catch (error) {
    console.error('수정 실패:', error);
    alert('수정에 실패했어요');
  } finally {
    saving.value = false;
  }
};

const handleLogout = () => {
  if (confirm('로그아웃 하시겠어요?')) {
    robotState.reset();
    authStore.logout(); // 두 스토리지 모두에서 토큰 삭제 후 로그인 페이지로 이동
  }
};

const handleDelete = async () => {
  if (!confirm('정말 탈퇴하시겠어요?')) return;
  if (!confirm('탈퇴하면 모든 데이터가 삭제되고 복구할 수 없어요. 계속할까요?')) return;

  try {
    await memberApi.deleteAccount();
    alert('탈퇴가 완료되었어요');
    robotState.reset();
    authStore.logout(); // 두 스토리지 모두에서 토큰 삭제 후 로그인 페이지로 이동
  } catch (error) {
    console.error('탈퇴 실패:', error);
    alert('탈퇴에 실패했어요');
  }
};

onMounted(async () => {
  loadProfileImage();

  // 포그라운드 메시지 수신 리스너
  onForegroundMessage((payload) => {
    if (Notification.permission === 'granted') {
      new Notification(payload.notification?.title || '알림', {
        body: payload.notification?.body,
        icon: '/icon-192x192.png'
      });
    }
  });

  await Promise.all([
    fetchMyInfo(),
    robotState.fetchRobot(),
    loadNotifications()
  ]);
});
</script>

<style scoped>
.profile {
  min-height: 100vh;
  background: var(--bg-secondary);
  padding-bottom: 80px;
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

/* 프로필 카드 */
.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-primary);
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 24px;
}

.avatar-wrapper {
  position: relative;
  cursor: pointer;
}

.avatar {
  width: 64px;
  height: 64px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  overflow: hidden;
}

.avatar-edit {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 24px;
  height: 24px;
  background: var(--bg-primary);
  border: 2px solid var(--bg-secondary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.avatar-wrapper:active .avatar-edit {
  background: var(--gray-100);
}

/* 모달 오버레이 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

/* 액션 시트 */
.action-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--bg-primary);
  border-radius: 20px 20px 0 0;
  padding: 0 20px 34px;
  z-index: 1001;
}

.action-sheet-header {
  padding: 16px 0;
  text-align: center;
  border-bottom: 1px solid var(--gray-100);
}

.action-sheet-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.action-sheet-body {
  padding: 8px 0;
}

.action-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 4px;
  font-size: 16px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--gray-100);
}

.action-item:last-child {
  border-bottom: none;
}

.action-item svg {
  color: var(--text-secondary);
}

.action-cancel {
  width: 100%;
  height: 50px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-top: 8px;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.user-email {
  font-size: 14px;
  color: var(--text-tertiary);
}

/* 섹션 */
.section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 10px;
  padding-left: 4px;
}

.info-card {
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid var(--gray-100);
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  font-size: 14px;
  color: var(--text-secondary);
}

.info-item .value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.info-item .value.text-tertiary {
  color: var(--text-tertiary);
}

.edit-input {
  text-align: right;
  width: 180px;
  height: 36px;
  padding: 0 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-primary);
}

.edit-input:focus {
  border-color: var(--primary);
  background: var(--bg-primary);
}

/* 토글 아이템 */
.toggle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-bottom: 1px solid var(--gray-100);
}

.toggle-item:last-child {
  border-bottom: none;
}

.toggle-info {
  display: flex;
  flex-direction: column;
}

.toggle-label {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.toggle-desc {
  font-size: 13px;
  color: var(--text-tertiary);
}

/* 토글 스위치 */
.toggle-switch {
  position: relative;
  width: 48px;
  height: 28px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--gray-300);
  transition: 0.3s;
  border-radius: 28px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toggle-switch input:checked + .toggle-slider {
  background-color: var(--primary);
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

/* 버튼 */
.button-row {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.btn {
  flex: 1;
  height: 48px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  transition: opacity 0.2s;
}

.btn.full {
  flex: none;
  width: 100%;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.btn:disabled {
  opacity: 0.6;
}

.btn:not(:disabled):active {
  opacity: 0.9;
}

/* 로봇 카드 */
.robot-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-primary);
  padding: 16px 18px;
  border-radius: 16px;
}

.robot-avatar {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--primary) 0%, #5BA0F5 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.robot-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.robot-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.robot-status {
  font-size: 13px;
  color: var(--text-tertiary);
}

.robot-status.online {
  color: var(--success);
}

.robot-battery {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* 메뉴 */
.menu-list {
  background: var(--bg-primary);
  border-radius: 16px;
  overflow: hidden;
}

.menu-item {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  font-size: 15px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--gray-100);
  transition: background 0.2s;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:active {
  background: var(--gray-50);
}

.menu-item.danger {
  color: var(--danger);
}

.bottom-spacer {
  height: 20px;
}

/* 고객센터 */
.customer-center {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-primary);
  padding: 18px;
  border-radius: 16px;
}

.cs-icon {
  width: 44px;
  height: 44px;
  background: var(--primary-light);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
}

.cs-info {
  display: flex;
  flex-direction: column;
}

.cs-label {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 2px;
}

.cs-number {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
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
</style>
