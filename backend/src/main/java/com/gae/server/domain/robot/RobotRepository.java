package com.gae.server.domain.robot;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface RobotRepository extends JpaRepository<Robot, Long> {
    Optional<Robot> findByMemberId(Long memberId);
    Optional<Robot> findBySerialNumber(String serialNumber);
    boolean existsBySerialNumber(String serialNumber);
}
