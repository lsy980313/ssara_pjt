package com.gae.server.global.scheduler;

import com.gae.server.domain.activity.ActivityLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Slf4j
@Component
@RequiredArgsConstructor
public class ActivityLogCleanupScheduler {

    private final ActivityLogRepository activityLogRepository;

    // 2주 (14일)
    private static final int RETENTION_DAYS = 14;

    /**
     * 매일 새벽 3시에 2주 이전 로그 삭제
     * cron: 초 분 시 일 월 요일
     */
    @Scheduled(cron = "0 0 3 * * *")
    @Transactional
    public void cleanupOldActivityLogs() {
        LocalDateTime cutoffDate = LocalDateTime.now().minusDays(RETENTION_DAYS);

        long oldLogsCount = activityLogRepository.countOldLogs(cutoffDate);

        if (oldLogsCount > 0) {
            int deletedCount = activityLogRepository.deleteOldLogs(cutoffDate);
            log.info("Activity log cleanup completed: {} old logs deleted (older than {} days)",
                    deletedCount, RETENTION_DAYS);
        } else {
            log.debug("Activity log cleanup: No old logs to delete");
        }
    }

    /**
     * 서버 시작 시 한 번 실행 (즉시 정리)
     */
    @Scheduled(initialDelay = 10000, fixedDelay = Long.MAX_VALUE)
    @Transactional
    public void cleanupOnStartup() {
        LocalDateTime cutoffDate = LocalDateTime.now().minusDays(RETENTION_DAYS);

        long oldLogsCount = activityLogRepository.countOldLogs(cutoffDate);

        if (oldLogsCount > 0) {
            int deletedCount = activityLogRepository.deleteOldLogs(cutoffDate);
            log.info("Startup cleanup: {} old activity logs deleted (older than {} days)",
                    deletedCount, RETENTION_DAYS);
        }
    }
}
