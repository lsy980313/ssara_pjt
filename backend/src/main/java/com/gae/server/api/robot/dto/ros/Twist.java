package com.gae.server.api.robot.dto.ros;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * ROS geometry_msgs/Twist 표준 메시지
 * - linear: 선형 속도 (x: 전진/후진, y: 좌우, z: 상하)
 * - angular: 각속도 (x: roll, y: pitch, z: yaw 회전)
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Twist {
    private Vector3 linear;
    private Vector3 angular;

    /**
     * 2D 평면 이동용 Twist 생성 (일반적인 로봇 제어)
     * @param linearX 전진(+)/후진(-) 속도
     * @param angularZ 좌회전(+)/우회전(-) 각속도
     */
    public static Twist of(double linearX, double angularZ) {
        return Twist.builder()
                .linear(Vector3.of(linearX, 0.0, 0.0))
                .angular(Vector3.of(0.0, 0.0, angularZ))
                .build();
    }

    public static Twist stop() {
        return Twist.builder()
                .linear(Vector3.zero())
                .angular(Vector3.zero())
                .build();
    }
}
