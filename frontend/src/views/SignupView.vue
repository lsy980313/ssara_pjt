<template>
  <div class="signup">
    <header class="header">
      <button class="back-btn" @click="$router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="header-title">회원가입</h1>
      <div style="width: 24px;"></div>
    </header>

    <div class="signup-content">
      <div class="intro">
        <h2>반가워요!</h2>
        <p>소중한 가족을 위한 첫 걸음을 시작해 볼까요?</p>
      </div>

      <form @submit.prevent="handleSignup" class="form">
        <div class="input-group">
          <label>이름</label>
          <input type="text" v-model="name" placeholder="이름을 입력해 주세요" required />
        </div>

        <div class="input-group">
          <label>이메일</label>
          <input type="email" v-model="email" placeholder="이메일을 입력해 주세요" required />
        </div>

        <div class="input-group">
          <label>비밀번호</label>
          <input type="password" v-model="password" placeholder="비밀번호를 입력해 주세요" required />
          <span class="helper">8자 이상 입력해 주세요</span>
        </div>

        <div class="input-group">
          <label>비밀번호 확인</label>
          <input type="password" v-model="passwordConfirm" placeholder="비밀번호를 다시 입력해 주세요" required />
        </div>

        <div class="input-group">
          <label>전화번호</label>
          <input type="tel" v-model="phoneNumber" placeholder="010-0000-0000" />
        </div>

        <div class="input-group">
          <label>로봇 S/N</label>
          <input type="text" v-model="serialNumber" placeholder="로봇 시리얼 넘버를 입력해 주세요" required />
          <span class="helper">로봇 하단에 있는 시리얼 넘버를 입력해 주세요</span>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '가입 중...' : '가입하기' }}
        </button>
      </form>

      <div class="login-link">
        <span>이미 계정이 있으신가요?</span>
        <button @click="$router.push('/')">로그인</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '../api';

const router = useRouter();

const name = ref('');
const email = ref('');
const password = ref('');
const passwordConfirm = ref('');
const phoneNumber = ref('');
const serialNumber = ref('');
const loading = ref(false);

const handleSignup = async () => {
  if (password.value.length < 8) {
    alert('비밀번호는 8자 이상이어야 해요');
    return;
  }

  if (password.value !== passwordConfirm.value) {
    alert('비밀번호가 일치하지 않아요');
    return;
  }

  loading.value = true;

  try {
    await authApi.signup({
      name: name.value,
      email: email.value,
      password: password.value,
      phoneNumber: phoneNumber.value || null,
      serialNumber: serialNumber.value
    });

    alert('회원가입이 완료되었어요! 로그인해 주세요');
    router.push('/');
  } catch (error) {
    console.error('회원가입 실패:', error);
    if (error.response?.data) {
      alert(error.response.data);
    } else {
      alert('회원가입에 실패했어요. 잠시 후 다시 시도해 주세요');
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.signup {
  min-height: 100vh;
  background: var(--bg-primary);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  position: sticky;
  top: 0;
  background: var(--bg-primary);
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

.signup-content {
  padding: 20px 24px 40px;
  max-width: 400px;
  margin: 0 auto;
}

.intro {
  margin-bottom: 36px;
}

.intro h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.intro p {
  font-size: 15px;
  color: var(--text-tertiary);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.helper {
  display: block;
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 6px;
}

.submit-btn {
  width: 100%;
  height: 54px;
  background: var(--primary);
  color: white;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  margin-top: 12px;
  transition: opacity 0.2s;
}

.submit-btn:disabled {
  opacity: 0.6;
}

.submit-btn:not(:disabled):active {
  opacity: 0.9;
}

.login-link {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 24px;
}

.login-link span {
  font-size: 14px;
  color: var(--text-tertiary);
}

.login-link button {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
}
</style>
