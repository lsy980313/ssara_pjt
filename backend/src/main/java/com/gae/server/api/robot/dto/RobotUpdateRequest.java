package com.gae.server.api.robot.dto;

import com.gae.server.domain.robot.RobotStatus;

public record RobotUpdateRequest(
    String name,
    RobotStatus status,
    Integer battery,
    String location
) {
}
