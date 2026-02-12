package com.gae.server.api.robot.dto.ros;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * Rosbridge Protocol 표준 메시지 포맷
 * https://github.com/RobotWebTools/rosbridge_suite/blob/ros1/ROSBRIDGE_PROTOCOL.md
 *
 * @param <T> 메시지 타입 (예: Twist, Pose 등)
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RosMessage<T> {

    @Builder.Default
    private String op = "publish";

    private String topic;
    private T msg;

    /**
     * /cmd_vel 토픽용 Twist 메시지 생성
     */
    public static RosMessage<Twist> cmdVel(Twist twist) {
        return RosMessage.<Twist>builder()
                .op("publish")
                .topic("/cmd_vel")
                .msg(twist)
                .build();
    }

    /**
     * 커스텀 토픽용 메시지 생성
     */
    public static <T> RosMessage<T> of(String topic, T msg) {
        return RosMessage.<T>builder()
                .op("publish")
                .topic(topic)
                .msg(msg)
                .build();
    }
}
