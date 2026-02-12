package com.gae.server.api.notification;

import com.google.firebase.FirebaseApp;
import com.google.firebase.messaging.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Slf4j
@Service
public class FCMService {

    /**
     * 단일 기기에 푸시 알림 발송
     */
    public boolean sendNotification(String fcmToken, String title, String body) {
        return sendNotification(fcmToken, title, body, null);
    }

    /**
     * 단일 기기에 데이터와 함께 푸시 알림 발송
     */
    public boolean sendNotification(String fcmToken, String title, String body, Map<String, String> data) {
        if (!isFirebaseInitialized()) {
            log.warn("Firebase is not initialized. Skipping notification.");
            return false;
        }

        try {
            Message.Builder messageBuilder = Message.builder()
                    .setToken(fcmToken)
                    .setNotification(Notification.builder()
                            .setTitle(title)
                            .setBody(body)
                            .build())
                    .setAndroidConfig(AndroidConfig.builder()
                            .setPriority(AndroidConfig.Priority.HIGH)
                            .setNotification(AndroidNotification.builder()
                                    .setClickAction("OPEN_APP")
                                    .build())
                            .build())
                    .setWebpushConfig(WebpushConfig.builder()
                            .setNotification(WebpushNotification.builder()
                                    .setTitle(title)
                                    .setBody(body)
                                    .setIcon("/icon-192x192.png")
                                    .build())
                            .build());

            if (data != null && !data.isEmpty()) {
                messageBuilder.putAllData(data);
            }

            String response = FirebaseMessaging.getInstance().send(messageBuilder.build());
            log.info("FCM notification sent successfully: {}", response);
            return true;

        } catch (FirebaseMessagingException e) {
            log.error("FCM notification failed: {}", e.getMessage());
            return false;
        }
    }

    /**
     * 여러 기기에 푸시 알림 발송
     */
    public int sendMulticastNotification(List<String> fcmTokens, String title, String body) {
        if (!isFirebaseInitialized() || fcmTokens.isEmpty()) {
            return 0;
        }

        try {
            MulticastMessage message = MulticastMessage.builder()
                    .addAllTokens(fcmTokens)
                    .setNotification(Notification.builder()
                            .setTitle(title)
                            .setBody(body)
                            .build())
                    .build();

            BatchResponse response = FirebaseMessaging.getInstance().sendEachForMulticast(message);
            log.info("FCM multicast sent: {} success, {} failure",
                    response.getSuccessCount(), response.getFailureCount());
            return response.getSuccessCount();

        } catch (FirebaseMessagingException e) {
            log.error("FCM multicast failed: {}", e.getMessage());
            return 0;
        }
    }

    private boolean isFirebaseInitialized() {
        return !FirebaseApp.getApps().isEmpty();
    }
}
