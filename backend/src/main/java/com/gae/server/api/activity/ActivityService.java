package com.gae.server.api.activity;

import com.gae.server.api.activity.dto.ActivityLogDto;
import com.gae.server.api.activity.dto.DailySummaryDto;
import com.gae.server.domain.activity.ActivityLog;
import com.gae.server.domain.activity.ActivityLogRepository;
import com.gae.server.domain.member.Member;
import com.gae.server.domain.member.MemberRepository;
import com.gae.server.domain.robot.Robot;
import com.gae.server.domain.robot.RobotRepository;
import com.gae.server.global.exception.BusinessException;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ActivityService {

    private final ActivityLogRepository activityLogRepository;
    private final MemberRepository memberRepository;
    private final RobotRepository robotRepository;

    /**
     * 오늘 활동 로그 조회
     */
    @Transactional(readOnly = true)
    public List<ActivityLogDto> getTodayLogs() {
        Robot robot = getCurrentRobot();
        LocalDateTime startOfDay = LocalDate.now().atStartOfDay();
        LocalDateTime endOfDay = startOfDay.plusDays(1);

        return activityLogRepository.findByRobotIdAndDateRange(robot.getId(), startOfDay, endOfDay)
                .stream()
                .map(ActivityLogDto::from)
                .toList();
    }

    /**
     * 어제 활동 로그 조회
     */
    @Transactional(readOnly = true)
    public List<ActivityLogDto> getYesterdayLogs() {
        Robot robot = getCurrentRobot();
        LocalDateTime startOfYesterday = LocalDate.now().minusDays(1).atStartOfDay();
        LocalDateTime endOfYesterday = startOfYesterday.plusDays(1);

        return activityLogRepository.findByRobotIdAndDateRange(robot.getId(), startOfYesterday, endOfYesterday)
                .stream()
                .map(ActivityLogDto::from)
                .toList();
    }

    /**
     * 특정 날짜 활동 로그 조회
     */
    @Transactional(readOnly = true)
    public List<ActivityLogDto> getLogsByDate(LocalDate date) {
        Robot robot = getCurrentRobot();
        LocalDateTime startOfDay = date.atStartOfDay();
        LocalDateTime endOfDay = startOfDay.plusDays(1);

        return activityLogRepository.findByRobotIdAndDateRange(robot.getId(), startOfDay, endOfDay)
                .stream()
                .map(ActivityLogDto::from)
                .toList();
    }

    /**
     * 오늘 요약 정보 조회
     */
    @Transactional(readOnly = true)
    public DailySummaryDto getTodaySummary() {
        Robot robot = getCurrentRobot();
        LocalDateTime startOfDay = LocalDate.now().atStartOfDay();
        LocalDateTime endOfDay = startOfDay.plusDays(1);

        List<ActivityLog> todayLogs = activityLogRepository.findByRobotIdAndDateRange(
                robot.getId(), startOfDay, endOfDay);

        int totalEvents = todayLogs.size();
        int alerts = (int) todayLogs.stream()
                .filter(log -> log.getType() == ActivityLog.ActivityType.WARNING)
                .count();

        // 산책 시간과 거리는 실제 센서 데이터에서 계산해야 하지만,
        // 현재는 활동 로그 기반으로 추정값 사용
        int walkTime = (int) todayLogs.stream()
                .filter(log -> log.getType() == ActivityLog.ActivityType.ACTION)
                .count() * 10; // 액션 1개당 10분으로 추정

        double distance = walkTime * 0.05; // 10분당 0.5km로 추정

        return DailySummaryDto.builder()
                .totalEvents(totalEvents)
                .walkTime(walkTime)
                .distance(Math.round(distance * 10) / 10.0)
                .alerts(alerts)
                .build();
    }

    /**
     * 활동 로그 생성 (내부용 / MQTT 등에서 호출)
     */
    @Transactional
    public ActivityLog createLog(Long robotId, ActivityLog.ActivityType type, String message, String detail) {
        Robot robot = robotRepository.findById(robotId)
                .orElseThrow(() -> new BusinessException("로봇을 찾을 수 없습니다."));

        return activityLogRepository.save(ActivityLog.builder()
                .robot(robot)
                .type(type)
                .message(message)
                .detail(detail)
                .build());
    }

    private Robot getCurrentRobot() {
        String email = SecurityContextHolder.getContext().getAuthentication().getName();
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException("회원을 찾을 수 없습니다."));

        return robotRepository.findByMemberId(member.getId())
                .orElseThrow(() -> new BusinessException("로봇을 찾을 수 없습니다."));
    }
}
