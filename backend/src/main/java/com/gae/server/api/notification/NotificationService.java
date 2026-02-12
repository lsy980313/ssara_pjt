package com.gae.server.api.notification;

import com.gae.server.api.notification.dto.NotificationSettingsDto;
import com.gae.server.domain.member.Member;
import com.gae.server.domain.member.MemberRepository;
import com.gae.server.domain.notification.NotificationSetting;
import com.gae.server.domain.notification.NotificationSettingRepository;
import com.gae.server.global.exception.BusinessException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class NotificationService {

    private final NotificationSettingRepository notificationSettingRepository;
    private final MemberRepository memberRepository;
    private final FCMService fcmService;

    /**
     * FCM 토큰 등록/갱신
     */
    @Transactional
    public void registerToken(String fcmToken) {
        Member member = getCurrentMember();
        NotificationSetting setting = getOrCreateSetting(member);
        setting.updateFcmToken(fcmToken);
        log.info("FCM token registered for member: {}", member.getEmail());
    }

    /**
     * FCM 토큰 삭제 (알림 비활성화)
     */
    @Transactional
    public void deleteToken() {
        Member member = getCurrentMember();
        notificationSettingRepository.findByMember(member)
                .ifPresent(setting -> {
                    setting.clearFcmToken();
                    log.info("FCM token deleted for member: {}", member.getEmail());
                });
    }

    /**
     * 알림 설정 조회
     */
    @Transactional(readOnly = true)
    public NotificationSettingsDto getSettings() {
        Member member = getCurrentMember();
        NotificationSetting setting = getOrCreateSetting(member);
        return NotificationSettingsDto.from(setting);
    }

    /**
     * 알림 설정 수정
     */
    @Transactional
    public void updateSettings(NotificationSettingsDto dto) {
        Member member = getCurrentMember();
        NotificationSetting setting = getOrCreateSetting(member);
        setting.updateSettings(
                dto.isPushEnabled(),
                dto.isRobotStatusEnabled(),
                dto.isBatteryEnabled(),
                dto.isAlertEnabled(),
                dto.isMarketingEnabled()
        );
        log.info("Notification settings updated for member: {}", member.getEmail());
    }

    /**
     * 특정 회원에게 알림 발송
     */
    @Transactional(readOnly = true)
    public boolean sendToMember(Long memberId, String title, String body, String notificationType) {
        return notificationSettingRepository.findByMemberId(memberId)
                .filter(setting -> isNotificationEnabled(setting, notificationType))
                .filter(setting -> setting.getFcmToken() != null)
                .map(setting -> fcmService.sendNotification(setting.getFcmToken(), title, body))
                .orElse(false);
    }

    /**
     * 특정 회원에게 데이터와 함께 알림 발송
     */
    @Transactional(readOnly = true)
    public boolean sendToMember(Long memberId, String title, String body, String notificationType, Map<String, String> data) {
        return notificationSettingRepository.findByMemberId(memberId)
                .filter(setting -> isNotificationEnabled(setting, notificationType))
                .filter(setting -> setting.getFcmToken() != null)
                .map(setting -> fcmService.sendNotification(setting.getFcmToken(), title, body, data))
                .orElse(false);
    }

    private boolean isNotificationEnabled(NotificationSetting setting, String type) {
        if (!setting.isPushEnabled()) return false;

        return switch (type) {
            case "ROBOT_STATUS" -> setting.isRobotStatusEnabled();
            case "BATTERY" -> setting.isBatteryEnabled();
            case "ALERT" -> setting.isAlertEnabled();
            case "MARKETING" -> setting.isMarketingEnabled();
            default -> true;
        };
    }

    private NotificationSetting getOrCreateSetting(Member member) {
        return notificationSettingRepository.findByMember(member)
                .orElseGet(() -> notificationSettingRepository.save(
                        NotificationSetting.builder()
                                .member(member)
                                .build()
                ));
    }

    private Member getCurrentMember() {
        String email = SecurityContextHolder.getContext().getAuthentication().getName();
        return memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("회원을 찾을 수 없습니다."));
    }
}
