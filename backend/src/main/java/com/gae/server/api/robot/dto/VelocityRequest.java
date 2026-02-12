package com.gae.server.api.robot.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

/**
 * 로봇 속도 제어 요청 DTO
 * @param linearX 전진(+)/후진(-) 속도 (-1.0 ~ 1.0)
 * @param angularZ 좌회전(+)/우회전(-) 각속도 (-1.0 ~ 1.0)
 */
public record VelocityRequest(
        @Min(-1) @Max(1)
        Double linearX,

        @Min(-1) @Max(1)
        Double angularZ
) {
    public VelocityRequest {
        if (linearX == null) linearX = 0.0;
        if (angularZ == null) angularZ = 0.0;
    }
}
