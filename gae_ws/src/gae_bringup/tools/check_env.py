#!/usr/bin/env python3
import sys
import os

# [중요 1] OpenCV 충돌 방지를 위해 가장 먼저 import (설치 여부 확인 겸용)
try:
    import cv2
except ImportError:
    cv2 = None

import subprocess
import importlib
import platform

def check_python_package(package_name, import_name=None, expected_version=None):
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        # 패키지마다 버전 확인 변수가 다를 수 있음
        version = getattr(module, '__version__', getattr(module, 'VERSION', '설치됨 (버전 정보 없음)'))
        
        status = "✅ OK"
        # 버전 문자열에 expected_version이 포함되어 있는지 확인
        if expected_version and expected_version not in version:
            status = f"⚠️ 버전 다름 (Current: {version} / Target: {expected_version})"
            
        print(f"[{status}] {package_name:<30} : {version}")
        return module
    except ImportError:
        print(f"[❌ MISSING] {package_name:<30} : 설치 안됨")
        return None

def check_ros_package(package_name):
    try:
        result = subprocess.run(['ros2', 'pkg', 'list'], capture_output=True, text=True)
        if package_name in result.stdout:
            print(f"[✅ OK] ROS Package: {package_name:<17} : 설치됨")
        else:
            print(f"[❌ MISSING] ROS Package: {package_name:<17} : 리스트에 없음 (source setup.bash 확인)")
    except Exception:
        print(f"[❌ ERROR] ROS 2 환경을 찾을 수 없음")

def check_command(command, version_flag="--version"):
    cmd_name = command.split()[0]
    try:
        # jtop 같은 경우 실행 시 인터랙티브 모드로 갈 수 있어 버전 확인만 시도
        res = subprocess.run(f"{command} {version_flag}", shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            # 첫 줄만 가져오거나 버전 정보 파싱
            output = res.stdout.split('\n')[0].strip()
            if not output: output = "설치됨"
            # 너무 긴 출력은 자르기
            if len(output) > 50: output = output[:47] + "..."
            print(f"[✅ OK] System Tool: {cmd_name:<17} : {output}")
        else:
            # play 같은 명령어는 인자 없이 실행하면 도움말을 띄우며 에러코드를 뱉을 수 있음
            if cmd_name == "play": # play 명령어 예외 처리
                 print(f"[✅ OK] System Tool: {cmd_name:<17} : 설치됨 (SoX Component)")
            else:
                 print(f"[❌ MISSING] System Tool: {cmd_name:<17} : 실행 불가")
    except Exception:
        print(f"[❌ MISSING] System Tool: {cmd_name:<17} : 명령어를 찾을 수 없음")

def check_apt_package(package_name):
    res = subprocess.run(f"dpkg -s {package_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode == 0:
        print(f"[✅ OK] APT Package: {package_name:<17} : 설치됨")
    else:
        print(f"[❌ MISSING] APT Package: {package_name:<17} : 설치 안됨")

def run_system_check():
    print("="*60)
    print("🚀 GAE Robot 환경 진단 (v2.5 Updated)")
    print("="*60)

    # 0. System & Core
    print("\n---------- 0. System & Core ----------")

    # JetPack & L4T 버전 확인
    jetpack_ver = "알 수 없음"
    l4t_ver = "확인 불가"
    try:
        with open("/etc/nv_tegra_release", "r") as f:
            line = f.readline().strip()
            l4t_ver = line.replace("#", "").split(",")[0].strip()
            
            if "R36" in l4t_ver:
                jetpack_ver = "JetPack 6.x (Orin/Ubuntu 22.04)"
            elif "R35" in l4t_ver:
                jetpack_ver = "JetPack 5.x (Xavier/Orin/Ubuntu 20.04)"
            elif "R32" in l4t_ver:
                jetpack_ver = "JetPack 4.x (Nano/TX2/Ubuntu 18.04)"
                
        print(f"[✅ OK] JetPack Version             : {jetpack_ver}")
        print(f"[✅ OK] L4T Driver Version          : {l4t_ver}")
    except FileNotFoundError:
        print(f"[⚠️ INFO] Jetson L4T Check           : 파일 없음 (일반 PC 또는 Docker?)")
    
    # OS Check
    try:
        with open("/etc/os-release") as f:
            lines = f.readlines()
            name = next((line.split("=")[1].strip().strip('"') for line in lines if line.startswith("PRETTY_NAME")), "Linux")
            print(f"[✅ OK] OS Check                      : {name}")
    except:
        print(f"[⚠️ INFO] OS Check                      : {platform.system()} {platform.release()}")

    # Python Version
    py_ver = sys.version.split()[0]
    print(f"[✅ OK] Python Version                : {py_ver} (Target: 3.10.12)")

    # ROS Distro
    ros_distro = os.environ.get("ROS_DISTRO", "Not Found")
    print(f"[{'✅ OK' if ros_distro == 'humble' else '❌ NO'}] ROS 2 Distro                  : {ros_distro} (Target: Humble)")

    # Core Tools
    check_command("nvcc", "--version") # CUDA
    check_command("jtop", "--version") # jetson-stats

    # [v2.5] Dependency Fix Check
    print("  --- Dependency Safety Check ---")
    check_python_package("Click", "click", "8.1.7")
    check_python_package("Blinker", "blinker", "1.9.0")

    # 1. AI & Deep Learning
    print("\n---------- 1. AI & Deep Learning ----------")
    check_python_package("numpy", "numpy", "1.26.4")
    
    torch_mod = check_python_package("torch", "torch", "2.2.0")
    if torch_mod:
        cuda_ok = torch_mod.cuda.is_available()
        print(f"   ㄴ CUDA 가속 활성화?               : {'✅ YES' if cuda_ok else '❌ NO (GPU 안 잡힘!)'}")
        if cuda_ok:
            print(f"   ㄴ 감지된 GPU 장치                 : {torch_mod.cuda.get_device_name(0)}")

    check_python_package("torchvision", "torchvision", "0.17.2")
    check_python_package("ultralytics", "ultralytics", "8.4.9")
    check_python_package("faster-whisper", "faster_whisper", "1.2.1")
    check_python_package("openai", "openai", "2.16.0") 
    check_python_package("torch2trt", "torch2trt", "0.5.0")

    # 2. Vision & Sensors
    print("\n---------- 2. Vision & Sensors ----------")
    if cv2:
        print(f"[✅ OK] OpenCV (System)               : {cv2.__version__} (Target: 4.9.0)")
        try:
            count = cv2.cuda.getCudaEnabledDeviceCount()
            print(f"   ㄴ OpenCV CUDA 가속?               : {'✅ YES' if count > 0 else '❌ NO (CPU 전용 - 성능저하 주의)'}")
        except:
            print(f"   ㄴ OpenCV CUDA 확인 불가")
    else:
        print(f"[❌ MISSING] OpenCV (System)               : import 실패")

    check_ros_package("astra_camera")
    check_ros_package("astra_camera_msgs")
    check_ros_package("rtabmap_ros")
    check_ros_package("camera_info_manager")

    # 3. Audio & Voice
    print("\n---------- 3. Audio & Voice ----------")
    check_python_package("SpeechRecognition", "speech_recognition", "3.14.5")
    check_python_package("PyAudio", "pyaudio", "0.2.14")
    check_python_package("gTTS", "gtts", "2.5.4")
    
    # Audio System Tools
    check_apt_package("pulseaudio-utils")
    check_apt_package("libasound2-plugins")
    check_command("sox", "--version")
    check_command("play", "--help") # [v2.5] Play check
    check_apt_package("libsox-fmt-all") # [v2.5] Codec Check

    # 4. Hardware Control
    print("\n---------- 4. Hardware Control ----------")
    check_python_package("Jetson.GPIO", "Jetson.GPIO", "2.1.12") 
    
    check_python_package("adafruit-circuitpython-servokit", "adafruit_servokit", "1.3.22")
    check_python_package("adafruit-circuitpython-mpu6050", "adafruit_mpu6050", "1.3.5")
    check_python_package("adafruit-blinka", "adafruit_blinka", "8.23.0")
    check_python_package("smbus2", "smbus2", "0.6.0")
    
    check_python_package("adafruit-extended-bus", "adafruit_extended_bus") 
    check_python_package("setuptools_scm", "setuptools_scm") 
    
    # New Standard GPIO
    check_python_package("python3-libgpiod", "gpiod") 
    check_apt_package("gpiod")

    # 5. Communication & Interface
    print("\n---------- 5. Communication & Interface ----------")
    check_python_package("paho-mqtt", "paho.mqtt", "2.1.0")
    # [v2.5] Web & IoT Tools
    check_python_package("Flask", "flask", "3.1.2")
    check_python_package("Flask-Cors", "flask_cors", "6.0.2")
    check_apt_package("mosquitto-clients")
    
    check_ros_package("web_video_server")

    print("="*60)
    print("✅ 진단 완료! (Segmentation Fault 방지를 위해 강제 종료합니다)")
    print("="*60)
    
    # [중요 2] 프로그램 종료 시 Segfault 방지
    os._exit(0)

if __name__ == "__main__":
    run_system_check()