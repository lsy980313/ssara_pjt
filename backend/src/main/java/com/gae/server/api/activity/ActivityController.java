package com.gae.server.api.activity;

import com.gae.server.api.activity.dto.ActivityLogDto;
import com.gae.server.api.activity.dto.DailySummaryDto;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/activities")
@RequiredArgsConstructor
public class ActivityController {

    private final ActivityService activityService;

    /**
     * 오늘 활동 로그 조회
     */
    @GetMapping("/today")
    public ResponseEntity<List<ActivityLogDto>> getTodayLogs() {
        return ResponseEntity.ok(activityService.getTodayLogs());
    }

    /**
     * 어제 활동 로그 조회
     */
    @GetMapping("/yesterday")
    public ResponseEntity<List<ActivityLogDto>> getYesterdayLogs() {
        return ResponseEntity.ok(activityService.getYesterdayLogs());
    }

    /**
     * 특정 날짜 활동 로그 조회
     */
    @GetMapping("/date/{date}")
    public ResponseEntity<List<ActivityLogDto>> getLogsByDate(
            @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return ResponseEntity.ok(activityService.getLogsByDate(date));
    }

    /**
     * 오늘 요약 정보 조회
     */
    @GetMapping("/summary/today")
    public ResponseEntity<DailySummaryDto> getTodaySummary() {
        return ResponseEntity.ok(activityService.getTodaySummary());
    }
}
