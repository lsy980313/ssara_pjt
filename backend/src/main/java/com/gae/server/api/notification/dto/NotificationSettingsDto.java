package com.gae.server.api.notification.dto;

import com.gae.server.domain.notification.NotificationSetting;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class NotificationSettingsDto {

    private boolean pushEnabled;
    private boolean robotStatusEnabled;
    private boolean batteryEnabled;
    private boolean alertEnabled;
    private boolean marketingEnabled;

    public static NotificationSettingsDto from(NotificationSetting setting) {
        return NotificationSettingsDto.builder()
                .pushEnabled(setting.isPushEnabled())
                .robotStatusEnabled(setting.isRobotStatusEnabled())
                .batteryEnabled(setting.isBatteryEnabled())
                .alertEnabled(setting.isAlertEnabled())
                .marketingEnabled(setting.isMarketingEnabled())
                .build();
    }
}
