package com.gae.server.api.robot.dto;

import jakarta.validation.constraints.NotNull;

public record NavRequest(
        @NotNull(message = "x 좌표는 필수입니다.")
        Double x,
        @NotNull(message = "y 좌표는 필수입니다.")
        Double y
) {
}
