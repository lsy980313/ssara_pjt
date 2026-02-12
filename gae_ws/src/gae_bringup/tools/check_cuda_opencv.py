import cv2
import numpy as np
import time

# 1. 테스트용 랜덤 이미지 생성 (CPU)
img = np.random.random((1024, 1024)).astype(np.float32)

try:
    # 2. GPU 메모리로 업로드
    gpu_img = cv2.cuda_GpuMat()
    gpu_img.upload(img)

    # 3. GPU 연산 수행 (예: 리사이즈)
    start = time.time()
    # 1024x1024 -> 512x512로 줄이기
    gpu_resized = cv2.cuda.resize(gpu_img, (512, 512))
    end = time.time()

    # 4. 결과 다시 CPU로 다운로드
    result = gpu_resized.download()

    print(f"✅ GPU 연산 성공! (소요시간: {(end - start)*1000:.2f} ms)")
    print(f"원본 크기: {img.shape} -> 결과 크기: {result.shape}")

except Exception as e:
    print(f"❌ 실패... 에러 내용: {e}")