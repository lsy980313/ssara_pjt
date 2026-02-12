// src/firebase.js
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';

// Firebase 설정 (Firebase Console에서 발급받은 값으로 교체 필요)
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Firebase 초기화
const app = initializeApp(firebaseConfig);

// Messaging 인스턴스 (브라우저 지원 확인)
let messaging = null;
if (typeof window !== 'undefined' && 'Notification' in window) {
  try {
    messaging = getMessaging(app);
  } catch (error) {
    console.error('FCM not supported:', error);
  }
}

// FCM 토큰 발급
export const requestFCMToken = async () => {
  if (!messaging) {
    console.warn('FCM is not supported in this browser');
    return null;
  }

  try {
    // 알림 권한 요청
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      console.warn('Notification permission denied');
      return null;
    }

    // FCM 토큰 발급 (VAPID 키는 Firebase Console에서 발급)
    const token = await getToken(messaging, {
      vapidKey: 'YOUR_VAPID_KEY'
    });

    return token;
  } catch (error) {
    console.error('FCM Token error:', error);
    return null;
  }
};

// 포그라운드 메시지 수신 리스너
export const onForegroundMessage = (callback) => {
  if (!messaging) return;

  onMessage(messaging, (payload) => {
    callback(payload);
  });
};

export { messaging };
