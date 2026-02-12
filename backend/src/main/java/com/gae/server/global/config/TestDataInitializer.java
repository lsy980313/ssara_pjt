package com.gae.server.global.config;

import com.gae.server.domain.activity.ActivityLog;
import com.gae.server.domain.activity.ActivityLogRepository;
import com.gae.server.domain.member.Member;
import com.gae.server.domain.member.MemberRepository;
import com.gae.server.domain.robot.Robot;
import com.gae.server.domain.robot.RobotRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Random;

@Slf4j
@Component
@Profile("dev")
@RequiredArgsConstructor
public class TestDataInitializer implements CommandLineRunner {

    private final RobotRepository robotRepository;
    private final ActivityLogRepository activityLogRepository;
    private final MemberRepository memberRepository;
    private final PasswordEncoder passwordEncoder;
    private final Random random = new Random();

    @Override
    public void run(String... args) {
        // 테스트 회원이 없으면 생성
        if (memberRepository.count() == 0) {
            Member testMember = memberRepository.save(Member.builder()
                    .email("test@test.com")
                    .password(passwordEncoder.encode("test1234"))
                    .name("테스트")
                    .phoneNumber("010-1234-5678")
                    .serialNumber("TEST-ROBOT-001")
                    .build());

            robotRepository.save(Robot.builder()
                    .serialNumber("TEST-ROBOT-001")
                    .name("테스트의 로봇")
                    .member(testMember)
                    .build());

            log.info("Test member and robot created: test@test.com / test1234");
        }

        // 로봇이 있는 경우에만 테스트 데이터 생성
        List<Robot> robots = robotRepository.findAll();
        if (robots.isEmpty()) {
            log.info("No robots found. Skipping test data initialization.");
            return;
        }

        // 이미 데이터가 있으면 스킵
        if (activityLogRepository.count() > 0) {
            log.info("Activity logs already exist. Skipping test data initialization.");
            return;
        }

        Robot robot = robots.get(0);
        LocalDateTime now = LocalDateTime.now();

        // 오늘 데이터 생성
        createTodayLogs(robot, now);

        // 어제 데이터 생성
        createYesterdayLogs(robot, now.minusDays(1));

        // 과거 2주간의 데이터 생성 (2~13일 전)
        for (int i = 2; i <= 13; i++) {
            createPastDayLogs(robot, now.minusDays(i), i);
        }

        log.info("Test activity logs created successfully for the past 2 weeks.");
    }

    private void createTodayLogs(Robot robot, LocalDateTime now) {
        createLog(robot, ActivityLog.ActivityType.INFO, "로봇이 시작되었습니다.", null, now.minusHours(8));
        createLog(robot, ActivityLog.ActivityType.ACTION, "산책을 시작합니다.", "거실 → 현관", now.minusHours(7).minusMinutes(30));
        createLog(robot, ActivityLog.ActivityType.INFO, "현관 도착", null, now.minusHours(7));
        createLog(robot, ActivityLog.ActivityType.WARNING, "배터리 부족 알림", "배터리 20% 이하", now.minusHours(5));
        createLog(robot, ActivityLog.ActivityType.ACTION, "충전 시작", "충전 스테이션 도킹", now.minusHours(4).minusMinutes(50));
        createLog(robot, ActivityLog.ActivityType.INFO, "충전 완료", "100% 충전됨", now.minusHours(3));
        createLog(robot, ActivityLog.ActivityType.ACTION, "순찰 시작", "거실 순찰 모드", now.minusHours(2));
        createLog(robot, ActivityLog.ActivityType.INFO, "이상 없음", "순찰 완료", now.minusHours(1).minusMinutes(30));
        createLog(robot, ActivityLog.ActivityType.WARNING, "움직임 감지", "현관 센서 작동", now.minusMinutes(45));
        createLog(robot, ActivityLog.ActivityType.INFO, "정상 확인", "가족 귀가 확인", now.minusMinutes(40));
    }

    private void createYesterdayLogs(Robot robot, LocalDateTime yesterday) {
        createLog(robot, ActivityLog.ActivityType.INFO, "로봇이 시작되었습니다.", null, yesterday.withHour(9).withMinute(0));
        createLog(robot, ActivityLog.ActivityType.ACTION, "아침 순찰 시작", "전체 구역", yesterday.withHour(9).withMinute(30));
        createLog(robot, ActivityLog.ActivityType.INFO, "순찰 완료", "이상 없음", yesterday.withHour(10).withMinute(0));
        createLog(robot, ActivityLog.ActivityType.WARNING, "소음 감지", "거실에서 큰 소리", yesterday.withHour(14).withMinute(20));
        createLog(robot, ActivityLog.ActivityType.INFO, "정상 확인", "TV 소리로 확인", yesterday.withHour(14).withMinute(25));
        createLog(robot, ActivityLog.ActivityType.ACTION, "산책 동행", "공원 코스 30분", yesterday.withHour(16).withMinute(0));
        createLog(robot, ActivityLog.ActivityType.INFO, "산책 완료", "총 1.2km 이동", yesterday.withHour(16).withMinute(35));
        createLog(robot, ActivityLog.ActivityType.WARNING, "배터리 낮음", "30% 남음", yesterday.withHour(17).withMinute(50));
        createLog(robot, ActivityLog.ActivityType.ACTION, "집으로 복귀", "충전 스테이션으로 이동", yesterday.withHour(18).withMinute(0));
        createLog(robot, ActivityLog.ActivityType.INFO, "충전 시작", null, yesterday.withHour(18).withMinute(5));
    }

    private void createPastDayLogs(Robot robot, LocalDateTime day, int dayOffset) {
        // 매일 다양한 활동 로그 생성
        String[] morningMessages = {"로봇이 시작되었습니다.", "아침 점검 완료", "시스템 정상 가동"};
        String[] patrolMessages = {"순찰 시작", "거실 순찰", "복도 순찰", "방 순찰"};
        String[] walkMessages = {"산책 동행 시작", "공원 산책", "동네 산책"};
        String[] warningMessages = {"움직임 감지", "소음 감지", "온도 이상", "배터리 부족"};
        String[] normalMessages = {"정상 확인", "이상 없음", "점검 완료"};

        // 아침 시작
        createLog(robot, ActivityLog.ActivityType.INFO,
                morningMessages[random.nextInt(morningMessages.length)],
                null,
                day.withHour(8 + random.nextInt(2)).withMinute(random.nextInt(60)));

        // 오전 순찰
        createLog(robot, ActivityLog.ActivityType.ACTION,
                patrolMessages[random.nextInt(patrolMessages.length)],
                "전체 구역 점검",
                day.withHour(9 + random.nextInt(2)).withMinute(random.nextInt(60)));

        createLog(robot, ActivityLog.ActivityType.INFO,
                normalMessages[random.nextInt(normalMessages.length)],
                "순찰 완료",
                day.withHour(10 + random.nextInt(2)).withMinute(random.nextInt(60)));

        // 점심 시간 이벤트
        if (random.nextBoolean()) {
            createLog(robot, ActivityLog.ActivityType.WARNING,
                    warningMessages[random.nextInt(warningMessages.length)],
                    "거실 센서 작동",
                    day.withHour(12 + random.nextInt(2)).withMinute(random.nextInt(60)));

            createLog(robot, ActivityLog.ActivityType.INFO,
                    "정상 확인",
                    "가족 활동 확인",
                    day.withHour(12 + random.nextInt(2)).withMinute(random.nextInt(60)));
        }

        // 오후 산책 (일부 날만)
        if (dayOffset % 2 == 0) {
            createLog(robot, ActivityLog.ActivityType.ACTION,
                    walkMessages[random.nextInt(walkMessages.length)],
                    String.format("예상 시간: %d분", 20 + random.nextInt(30)),
                    day.withHour(15 + random.nextInt(2)).withMinute(random.nextInt(60)));

            createLog(robot, ActivityLog.ActivityType.INFO,
                    "산책 완료",
                    String.format("총 %.1fkm 이동", 0.5 + random.nextDouble() * 1.5),
                    day.withHour(16 + random.nextInt(2)).withMinute(random.nextInt(60)));
        }

        // 저녁 순찰
        createLog(robot, ActivityLog.ActivityType.ACTION,
                "저녁 순찰",
                "전체 구역",
                day.withHour(18 + random.nextInt(2)).withMinute(random.nextInt(60)));

        // 배터리 관련
        if (dayOffset % 3 == 0) {
            createLog(robot, ActivityLog.ActivityType.WARNING,
                    "배터리 부족",
                    String.format("%d%% 남음", 15 + random.nextInt(20)),
                    day.withHour(19 + random.nextInt(2)).withMinute(random.nextInt(60)));
        }

        // 충전
        createLog(robot, ActivityLog.ActivityType.ACTION,
                "충전 시작",
                "충전 스테이션 도킹",
                day.withHour(20 + random.nextInt(2)).withMinute(random.nextInt(60)));

        createLog(robot, ActivityLog.ActivityType.INFO,
                "대기 모드",
                "충전 중",
                day.withHour(21 + random.nextInt(2)).withMinute(random.nextInt(60)));
    }

    private void createLog(Robot robot, ActivityLog.ActivityType type, String message, String detail, LocalDateTime createdAt) {
        ActivityLog log = ActivityLog.builder()
                .robot(robot)
                .type(type)
                .message(message)
                .detail(detail)
                .createdAt(createdAt)
                .build();

        activityLogRepository.save(log);
    }
}
