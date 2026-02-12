package com.gae.server.api.robot.dto;

import com.gae.server.domain.robot.Robot;
import com.gae.server.domain.robot.RobotStatus;

public record RobotResponse(
    Long id,
    String serialNumber,
    String name,
    RobotStatus status,
    Integer battery,
    String location
) {
    public static RobotResponse from(Robot robot) {
        return new RobotResponse(
            robot.getId(),
            robot.getSerialNumber(),
            robot.getName(),
            robot.getStatus(),
            robot.getBattery(),
            robot.getLocation()
        );
    }
}
