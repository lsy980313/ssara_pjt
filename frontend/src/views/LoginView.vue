<template>
  <div class="login">
    <div class="login-content">
      <!-- 로고 영역 -->
      <div class="logo-section">
        <div class="logo">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
            <line x1="9" y1="9" x2="9.01" y2="9"/>
            <line x1="15" y1="9" x2="15.01" y2="9"/>
          </svg>
        </div>
        <h1 class="app-name">SSARA</h1>
        <p class="app-desc">소중한 가족을 위한 스마트 강아지</p>
      </div>

      <!-- 폼 영역 -->
      <form @submit.prevent="handleLogin" class="form-section">
        <div class="input-group">
          <label>이메일</label>
          <input
            type="email"
            v-model="email"
            placeholder="이메일을 입력해 주세요"
            required
          />
        </div>

        <div class="input-group">
          <label>비밀번호</label>
          <div class="input-wrapper">
            <input
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              placeholder="비밀번호를 입력해 주세요"
              required
            />
            <button type="button" class="eye-btn" @click="showPassword = !showPassword">
              <svg v-if="showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="options">
          <label class="checkbox-wrapper">
            <input type="checkbox" v-model="rememberMe" />
            <span class="checkmark"></span>
            <span class="checkbox-label">로그인 유지</span>
          </label>
          <div class="find-btns">
            <button type="button" class="text-btn" @click="openFindEmailModal">아이디 찾기</button>
            <span class="divider">|</span>
            <button type="button" class="text-btn" @click="openResetPasswordModal">비밀번호 찾기</button>
          </div>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <!-- 회원가입 링크 -->
      <div class="signup-section">
        <span class="signup-text">아직 계정이 없으신가요?</span>
        <button class="signup-btn" @click="$router.push('/signup')">회원가입</button>
      </div>
    </div>

    <!-- 아이디 찾기 모달 -->
    <div v-if="showFindEmailModal" class="modal-overlay" @click.self="closeFindEmailModal">
      <div class="modal">
        <div class="modal-header">
          <h2>아이디 찾기</h2>
          <button class="close-btn" @click="closeFindEmailModal">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- 입력 폼 -->
        <div v-if="!foundEmail" class="modal-body">
          <p class="modal-desc">가입 시 입력한 이름과 전화번호를 입력해 주세요.</p>

          <div class="input-group">
            <label>이름</label>
            <input
              type="text"
              v-model="findName"
              placeholder="이름을 입력해 주세요"
            />
          </div>

          <div class="input-group">
            <label>전화번호</label>
            <input
              type="tel"
              v-model="findPhone"
              placeholder="010-0000-0000"
            />
          </div>

          <button
            class="modal-btn"
            @click="handleFindEmail"
            :disabled="findLoading"
          >
            {{ findLoading ? '찾는 중...' : '아이디 찾기' }}
          </button>
        </div>

        <!-- 결과 화면 -->
        <div v-else class="modal-body result">
          <div class="result-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <p class="result-text">가입된 이메일을 찾았어요!</p>
          <p class="result-email">{{ foundEmail }}</p>
          <button class="modal-btn" @click="closeFindEmailModal">확인</button>
        </div>
      </div>
    </div>

    <!-- 비밀번호 찾기 모달 -->
    <div v-if="showResetPasswordModal" class="modal-overlay" @click.self="closeResetPasswordModal">
      <div class="modal">
        <div class="modal-header">
          <h2>비밀번호 찾기</h2>
          <button class="close-btn" @click="closeResetPasswordModal">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- 입력 폼 -->
        <div v-if="!resetSuccess" class="modal-body">
          <p class="modal-desc">가입한 이메일을 입력하시면 임시 비밀번호를 보내드려요.</p>

          <div class="input-group">
            <label>이메일</label>
            <input
              type="email"
              v-model="resetEmail"
              placeholder="이메일을 입력해 주세요"
            />
          </div>

          <button
            class="modal-btn"
            @click="handleSendTempPassword"
            :disabled="resetLoading"
          >
            {{ resetLoading ? '발송 중...' : '임시 비밀번호 받기' }}
          </button>
        </div>

        <!-- 성공 화면 -->
        <div v-else class="modal-body result">
          <div class="result-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <p class="result-text">임시 비밀번호를 발송했어요!</p>
          <p class="result-sub">이메일을 확인해 주세요.</p>
          <button class="modal-btn" @click="closeResetPasswordModal">확인</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '../api';
import { useAuthStore } from '../stores/authStore';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const rememberMe = ref(false);
const showPassword = ref(false);
const loading = ref(false);

// 아이디 찾기 관련
const showFindEmailModal = ref(false);
const findName = ref('');
const findPhone = ref('');
const findLoading = ref(false);
const foundEmail = ref('');

// 비밀번호 찾기 관련
const showResetPasswordModal = ref(false);
const resetEmail = ref('');
const resetLoading = ref(false);
const resetSuccess = ref(false);

const handleLogin = async () => {
  if (!email.value || !password.value) {
    alert('이메일과 비밀번호를 입력해 주세요');
    return;
  }

  loading.value = true;

  try {
    const response = await authApi.login({
      email: email.value,
      password: password.value
    });

    const { accessToken } = response.data;

    // authStore를 통해 토큰 저장 (rememberMe에 따라 스토리지 선택)
    authStore.login(accessToken, rememberMe.value);

    router.push('/home');
  } catch (error) {
    console.error('로그인 실패:', error);
    if (error.response?.status === 401) {
      alert('이메일 또는 비밀번호가 올바르지 않아요');
    } else {
      alert('로그인에 실패했어요. 잠시 후 다시 시도해 주세요');
    }
  } finally {
    loading.value = false;
  }
};

// 아이디 찾기 모달 열기
const openFindEmailModal = () => {
  showFindEmailModal.value = true;
  findName.value = '';
  findPhone.value = '';
  foundEmail.value = '';
};

// 아이디 찾기 모달 닫기
const closeFindEmailModal = () => {
  showFindEmailModal.value = false;
  findName.value = '';
  findPhone.value = '';
  foundEmail.value = '';
};

// 아이디 찾기 요청
const handleFindEmail = async () => {
  if (!findName.value || !findPhone.value) {
    alert('이름과 전화번호를 모두 입력해 주세요');
    return;
  }

  findLoading.value = true;

  try {
    const response = await authApi.findEmail({
      name: findName.value,
      phoneNumber: findPhone.value
    });

    foundEmail.value = response.data.email;
  } catch (error) {
    console.error('아이디 찾기 실패:', error);
    if (error.response?.status === 500) {
      alert('일치하는 회원 정보가 없어요');
    } else {
      alert('아이디 찾기에 실패했어요. 잠시 후 다시 시도해 주세요');
    }
  } finally {
    findLoading.value = false;
  }
};

// 비밀번호 찾기 모달 열기
const openResetPasswordModal = () => {
  showResetPasswordModal.value = true;
  resetEmail.value = '';
  resetSuccess.value = false;
};

// 비밀번호 찾기 모달 닫기
const closeResetPasswordModal = () => {
  showResetPasswordModal.value = false;
  resetEmail.value = '';
  resetSuccess.value = false;
};

// 임시 비밀번호 발송 요청
const handleSendTempPassword = async () => {
  if (!resetEmail.value) {
    alert('이메일을 입력해 주세요');
    return;
  }

  resetLoading.value = true;

  try {
    await authApi.sendTempPassword({
      email: resetEmail.value
    });

    resetSuccess.value = true;
  } catch (error) {
    console.error('임시 비밀번호 발송 실패:', error);
    if (error.response?.status === 500) {
      alert('가입되지 않은 이메일이에요');
    } else {
      alert('임시 비밀번호 발송에 실패했어요. 잠시 후 다시 시도해 주세요');
    }
  } finally {
    resetLoading.value = false;
  }
};
</script>

<style scoped>
.login {
  min-height: 100vh;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
}

.login-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 60px 24px 40px;
  max-width: 400px;
  margin: 0 auto;
  width: 100%;
}

/* 로고 */
.logo-section {
  text-align: center;
  margin-bottom: 48px;
}

.logo {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--primary) 0%, #5BA0F5 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: white;
}

.app-name {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.app-desc {
  font-size: 15px;
  color: var(--text-tertiary);
}

/* 폼 */
.form-section {
  flex: 1;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.input-group input {
  width: 100%;
  height: 52px;
  padding: 0 16px;
  background: var(--bg-secondary);
  border: 1px solid transparent;
  border-radius: 12px;
  font-size: 16px;
  color: var(--text-primary);
  transition: all 0.2s;
}

.input-group input::placeholder {
  color: var(--text-disabled);
}

.input-group input:focus {
  background: var(--bg-primary);
  border-color: var(--primary);
}

.input-wrapper {
  position: relative;
}

.input-wrapper input {
  padding-right: 48px;
}

.eye-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  padding: 8px;
  color: var(--text-tertiary);
}

/* 옵션 */
.options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-wrapper input {
  display: none;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid var(--gray-300);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.checkbox-wrapper input:checked + .checkmark {
  background: var(--primary);
  border-color: var(--primary);
}

.checkbox-wrapper input:checked + .checkmark::after {
  content: '';
  width: 6px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  margin-bottom: 2px;
}

.checkbox-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.text-btn {
  font-size: 14px;
  color: var(--text-tertiary);
}

.find-btns {
  display: flex;
  align-items: center;
  gap: 8px;
}

.divider {
  color: var(--text-disabled);
  font-size: 12px;
}

/* 제출 버튼 */
.submit-btn {
  width: 100%;
  height: 54px;
  background: var(--primary);
  color: white;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  transition: opacity 0.2s;
}

.submit-btn:disabled {
  opacity: 0.6;
}

.submit-btn:not(:disabled):active {
  opacity: 0.9;
}

/* 회원가입 */
.signup-section {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: auto;
  padding-top: 24px;
}

.signup-text {
  font-size: 14px;
  color: var(--text-tertiary);
}

.signup-btn {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
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
  padding: 24px;
}

.modal {
  background: var(--bg-primary);
  border-radius: 20px;
  width: 100%;
  max-width: 360px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 0;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.close-btn {
  padding: 4px;
  color: var(--text-tertiary);
}

.modal-body {
  padding: 20px;
}

.modal-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 20px;
  line-height: 1.5;
}

.modal-btn {
  width: 100%;
  height: 50px;
  background: var(--primary);
  color: white;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  margin-top: 8px;
}

.modal-btn:disabled {
  opacity: 0.6;
}

/* 결과 화면 */
.modal-body.result {
  text-align: center;
  padding: 32px 20px;
}

.result-icon {
  color: var(--primary);
  margin-bottom: 16px;
}

.result-text {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.result-email {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.result-sub {
  font-size: 14px;
  color: var(--text-tertiary);
  margin-bottom: 24px;
}
</style>
