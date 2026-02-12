 Analysis of  `train.py`

`train.py` 파일은 **Isaac Lab 환경에서 RSL-RL 라이브러리를 사용하여 강화학습 모델을 학습시키기 위한 메인 실행 스크립트**입니다.

주요 기능과 코드의 흐름을 단계별로 설명합니다.

### 1. 주요 기능 및 특징
*   **로컬 환경 호환성 (커스텀 수정)**:
    *   **Line 14-17, 60-66**: `[MODIFICATION START]` 주석 부분에서 볼 수 있듯, 현재 실행 파일의 경로를 `sys.path`에 추가하고 있습니다.
    *   **목적**: `cli_args.py`나 사용자 정의 패키지인 `custom_quadruped_isaac` 등 **로컬에 있는 모듈들을 문제없이 import** 하여 사용할 수 있도록 경로를 강제로 지정해 준 것입니다.
*   **Isaac Sim 앱 실행**: `AppLauncher`를 통해 시뮬레이션 인스턴스를 시작합니다.
*   **RSL-RL 연동**: RSL-RL 라이브러리(PPO 알고리즘 등)와 Isaac Lab 환경을 연결해 주는 역할을 합니다.

### 2. 코드 실행 흐름

1.  **라이브러리 세팅 및 앱 실행 (Init)**
    *   필요한 파이썬 패키지(`argparse`, `sys` 등)를 불러오고, `AppLauncher` 인수를 설정합니다.
    *   `AppLauncher`를 통해 Isaac Sim 애플리케이션을 **가장 먼저** 실행합니다. (시뮬레이터가 켜져야 이후 작업 가능)

2.  **커스텀 태스크 등록**
    *   **Line 65**: `import custom_quadruped_isaac`을 통해 사용자가 정의한 로봇/환경 설정을 레지스트리에 등록합니다.

3.  **버전 체크**
    *   설치된 `rsl-rl` 라이브러리가 최소 요구 버전(3.0.1) 이상인지 확인합니다.

4.  **메인 함수 (`main`) - 학습 준비**
    *   `@hydra_task_config`: Hydra를 사용하여 설정 파일(`agent_cfg.py`, `env_cfg.py`)을 로드합니다.
    *   **시드(Seed) 설정**: 재현 가능한 학습을 위해 난수 시드를 고정합니다.
    *   **로그 경로 설정**: `logs/rsl_rl/실험이름/날짜_시간` 형식으로 로그 저장소를 만듭니다.

5.  **환경(Environment) 생성**
    *   `gym.make(args_cli.task, ...)`: 설정된 태스크 이름(예: `Isaac-Velocity-Flat-Custom-Quad-v0`)으로 시뮬레이션 환경을 만듭니다.
    *   **비디오 녹화**: `--video` 옵션이 있으면 `gym.wrappers.RecordVideo`로 환경을 감싸 간헐적으로 영상을 저장합니다.
    *   **RSL-RL 래퍼**: `RslRlVecEnvWrapper`를 사용하여 Gym 환경을 RSL-RL 트레이너가 이해할 수 있는 형태로 변환합니다.

6.  **학습 실행 (Training)**
    *   **Runner 생성**: `OnPolicyRunner` (주로 PPO) 객체를 생성합니다.
    *   **체크포인트 로드**: `--resume` 옵션이 있다면 이전 학습 모델을 불러옵니다.
    *   **설정 저장**: 현재 사용된 환경 및 에이전트 설정을 `env.yaml`, `agent.yaml`로 저장합니다.
    *   **`runner.learn()`**: 실제로 학습 루프를 돌며 에이전트를 훈련시킵니다.

7.  **종료 (Cleanup)**
    *   학습이 끝나면 환경과 시뮬레이션 앱을 안전하게 종료합니다.

### 3. 원본 `train.py`와의 차이점

`scripts/train.py` (원본)와 `scripts/local_train.py` (로컬 수정본)의 결정적인 차이는 **커스텀 모듈 인식 여부**입니다.

| 구분                         | 원본 (`train.py`)              | 로컬 수정본 (`local_train.py`)       | 비고                                                              |
| :--------------------------- | :----------------------------- | :----------------------------------- | :---------------------------------------------------------------- |
| **시스템 경로 (`sys.path`)** | 수정 없음                      | `sys.path.append(...)` 추가          | 현재 스크립트 위치를 경로에 추가하여 로컬 폴더 import 가능하게 함 |
| **커스텀 태스크 등록**       | 없음                           | `import custom_quadruped_isaac`      | `gym.make`가 커스텀 환경 ID를 인식하도록 레지스트리에 등록        |
| **목적**                     | 패키지로 설치된 표준 환경 학습 | 개발 중인 로컬 사용자 지정 환경 학습 |                                                                   |

**코드 상세 비교:**

```python
# [원본] imports
import argparse
import sys
from isaaclab.app import AppLauncher

# ... (중략) ...

# [로컬 수정본] imports 및 경로 추가
import argparse
import sys
import os  # 추가됨

# [차이점 1] 현재 디렉토리를 시스템 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from isaaclab.app import AppLauncher

# ... (AppLauncher 실행 후) ...

# [차이점 2] 커스텀 태스크 모듈 import
import custom_quadruped_isaac 
```

이외의 RSL-RL 실행 로직, Hydra 설정 로드, 학습 루프 등은 **100% 동일**합니다.

### 요약
이 파일은 **"설정 로드 -> 시뮬레이터 켜기 -> 환경 만들기 -> PPO 학습기 붙이기 -> 학습 시작"**의 표준적인 절차를 수행하는 스크립트이며, 특히 **로컬 파일들을 바로 import 할 수 있도록 경로 설정이 추가된 점**이 핵심입니다.
