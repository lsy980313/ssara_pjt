import time
import board
import busio
import adafruit_mpu6050
from adafruit_extended_bus import ExtendedI2C as I2C

# 하드웨어 설정 파일 값 참고 (hardware_config_test.py)
i2c = I2C(1)  # Bus 1
mpu = adafruit_mpu6050.MPU6050(i2c, address=0x68)

print("MPU6050 Connected!")
while True:
    # 가속도(m/s^2), 자이로(rad/s), 온도
    accel = mpu.acceleration
    gyro = mpu.gyro
    
    print(f"Accel: X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f} | "
          f"Gyro: X={gyro[0]:.2f}, Y={gyro[1]:.2f}, Z={gyro[2]:.2f}")
    time.sleep(0.5)