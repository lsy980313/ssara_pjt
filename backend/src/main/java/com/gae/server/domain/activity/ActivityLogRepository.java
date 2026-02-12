package com.gae.server.domain.activity;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface ActivityLogRepository extends JpaRepository<ActivityLog, Long> {

    // 특정 로봇의 특정 기간 로그 조회
    @Query("SELECT a FROM ActivityLog a WHERE a.robot.id = :robotId " +
           "AND a.createdAt >= :startDate AND a.createdAt < :endDate " +
           "ORDER BY a.createdAt DESC")
    List<ActivityLog> findByRobotIdAndDateRange(
            @Param("robotId") Long robotId,
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate
    );

    // 특정 로봇의 최근 N개 로그 조회
    @Query("SELECT a FROM ActivityLog a WHERE a.robot.id = :robotId ORDER BY a.createdAt DESC LIMIT :limit")
    List<ActivityLog> findRecentByRobotId(@Param("robotId") Long robotId, @Param("limit") int limit);

    // 특정 로봇의 오늘 로그 개수
    @Query("SELECT COUNT(a) FROM ActivityLog a WHERE a.robot.id = :robotId " +
           "AND a.createdAt >= :startOfDay AND a.createdAt < :endOfDay")
    int countTodayLogs(
            @Param("robotId") Long robotId,
            @Param("startOfDay") LocalDateTime startOfDay,
            @Param("endOfDay") LocalDateTime endOfDay
    );

    // 특정 날짜 이전의 로그 삭제 (2주 이전 데이터 정리용)
    @Modifying
    @Query("DELETE FROM ActivityLog a WHERE a.createdAt < :cutoffDate")
    int deleteOldLogs(@Param("cutoffDate") LocalDateTime cutoffDate);

    // 특정 날짜 이전의 로그 개수 조회
    @Query("SELECT COUNT(a) FROM ActivityLog a WHERE a.createdAt < :cutoffDate")
    long countOldLogs(@Param("cutoffDate") LocalDateTime cutoffDate);
}
