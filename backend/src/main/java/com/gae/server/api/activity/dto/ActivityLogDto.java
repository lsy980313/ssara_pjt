package com.gae.server.api.activity.dto;

import com.gae.server.domain.activity.ActivityLog;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ActivityLogDto {

    private Long id;
    private String type;
    private String msg;
    private String detail;
    private String time;
    private LocalDateTime createdAt;

    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("HH:mm");

    public static ActivityLogDto from(ActivityLog log) {
        return ActivityLogDto.builder()
                .id(log.getId())
                .type(log.getType().name().toLowerCase())
                .msg(log.getMessage())
                .detail(log.getDetail())
                .time(log.getCreatedAt().format(TIME_FORMATTER))
                .createdAt(log.getCreatedAt())
                .build();
    }
}
