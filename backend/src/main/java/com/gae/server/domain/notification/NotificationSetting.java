package com.gae.server.domain.notification;

import com.gae.server.domain.member.Member;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "notification_settings")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class NotificationSetting {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id", nullable = false, unique = true)
    private Member member;

    @Column(name = "fcm_token")
    private String fcmToken;

    @Builder.Default
    @Column(name = "push_enabled")
    private boolean pushEnabled = true;

    @Builder.Default
    @Column(name = "robot_status_enabled")
    private boolean robotStatusEnabled = true;

    @Builder.Default
    @Column(name = "battery_enabled")
    private boolean batteryEnabled = true;

    @Builder.Default
    @Column(name = "alert_enabled")
    private boolean alertEnabled = true;

    @Builder.Default
    @Column(name = "marketing_enabled")
    private boolean marketingEnabled = false;

    public void updateFcmToken(String fcmToken) {
        this.fcmToken = fcmToken;
    }

    public void clearFcmToken() {
        this.fcmToken = null;
    }

    public void updateSettings(boolean pushEnabled, boolean robotStatusEnabled,
                               boolean batteryEnabled, boolean alertEnabled, boolean marketingEnabled) {
        this.pushEnabled = pushEnabled;
        this.robotStatusEnabled = robotStatusEnabled;
        this.batteryEnabled = batteryEnabled;
        this.alertEnabled = alertEnabled;
        this.marketingEnabled = marketingEnabled;
    }
}
