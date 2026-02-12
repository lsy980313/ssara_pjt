package com.gae.server.api.robot.dto.ros;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * ROS geometry_msgs/Vector3 표준 메시지
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Vector3 {
    private double x;
    private double y;
    private double z;

    public static Vector3 zero() {
        return new Vector3(0.0, 0.0, 0.0);
    }

    public static Vector3 of(double x, double y, double z) {
        return new Vector3(x, y, z);
    }
}
