import math

class IMUProcessor:
    def __init__(self):
        print("IMU Processor Initialized")
        # 변환 규칙: x->x, y->-y, z->-z
        # 이는 X축 기준 180도 회전과 동일합니다.

    def process_data(self, accel_raw, gyro_raw):
        """
        raw data: list [x, y, z]
        return:
            projected_gravity (sim frame, normalized)
            base_ang_vel (sim frame, rad/s)
        """
        ax, ay, az = accel_raw
        gx, gy, gz = gyro_raw

        # 1. 좌표 변환 (Sensor Frame -> Base/Sim Frame)
        # x_sim = x_sensor
        # y_sim = -y_sensor
        # z_sim = -z_sensor
        
        # 가속도 변환
        ax_sim = ax
        ay_sim = -ay
        az_sim = -az
        
        # 자이로 변환 (Proper Rotation이므로 벡터와 동일하게 변환)
        gx_sim = gx
        gy_sim = -gy
        gz_sim = -gz

        # 2. 중력 벡터 정규화 (Projected Gravity)
        # 벡터의 크기 계산
        norm = math.sqrt(ax_sim**2 + ay_sim**2 + az_sim**2)
        
        if norm < 1e-6:
            pg_x, pg_y, pg_z = 0.0, 0.0, -1.0 # Fallback
        else:
            pg_x = ax_sim / norm
            pg_y = ay_sim / norm
            pg_z = az_sim / norm

        projected_gravity = [pg_x, pg_y, pg_z]
        base_ang_vel = [gx_sim, gy_sim, gz_sim]

        return projected_gravity, base_ang_vel

if __name__ == "__main__":
    processor = IMUProcessor()

    # 테스트 케이스 1: 로봇이 평평하게 놓여있을 때
    # Sensor: Z축 +9.8 (지면 반발력)
    raw_accel = [0.0, 0.0, 9.81]
    raw_gyro = [0.1, 0.2, 0.3] # 임의의 회전
    
    grav, ang_vel = processor.process_data(raw_accel, raw_gyro)
    print("--- Test Case 1: Flat ---")
    print(f"Input Accel: {raw_accel}")
    print(f"Input Gyro : {raw_gyro}")
    print(f"Transformed Gravity: {grav} (Expected: [0.0, 0.0, -1.0])")
    print(f"Transformed Gyro   : {ang_vel} (Expected: [0.1, -0.2, -0.3])")
    
    # 테스트 케이스 2: 우측으로 90도 (Roll +90)
    # Sensor: Y축 +9.8
    raw_accel_2 = [0.0, 9.81, 0.0]
    grav2, _ = processor.process_data(raw_accel_2, raw_gyro)
    print("\n--- Test Case 2: Roll +90 ---")
    print(f"Input Accel: {raw_accel_2}")
    print(f"Transformed Gravity: {grav2} (Expected: [0.0, -1.0, 0.0])")
