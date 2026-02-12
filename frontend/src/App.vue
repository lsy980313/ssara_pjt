<template>
  <router-view />
</template>

<style>
#app {
  width: 100%;
  min-height: 100vh; /* 화면 전체 높이 사용 */
  margin: 0 auto;
  padding: 0;
  background-color: var(--bg-color);
  max-width: 600px; /* PC에서 너무 넓게 보이지 않도록 제한 (선택사항) */
  position: relative;
  box-shadow: 0 0 20px rgba(0,0,0,0.05); /* PC에서 앱처럼 보이게 그림자 추가 */
}

/* 모바일에서는 꽉 차게 */
@media (max-width: 600px) {
  #app {
    box-shadow: none;
  }
}
</style>