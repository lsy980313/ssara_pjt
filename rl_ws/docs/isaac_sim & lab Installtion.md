# isaac sim 5.1.0 Installation issues(Container)

NVIDIA-SMI version: 580.95.05

See Setting the Default Nucleus Server to set the default Nucleus server.

See Setting the Default Username and Password for Connecting to the Nucleus Server to set the default credentials for any Nucleus server.

## System checking result: FAILED troubleshooting

- Change CPU governance from powersave to performance

```bash
powerprofilesctl set performance
powerprofilesctl get
```

## isaac lab installation
### installtion commands
> 컨테이너 내부의 `/home/<사용자명>` 디렉토리에 설치하는 기준의 설명이다
``` bash
docker exec -it isaac_sim bash
cd /home/<사용자명>
git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

export ISAACSIM_PATH=/isaac-sim
rm -f _isaac_sim
ln -s ${ISAACSIM_PATH} _isaac_sim

./isaaclab.sh -i
```

### 깃 설치 에러 발생시
루트 사용자(UID 0, GID 0)로 접속 후,
``` bash
apt-get update
apt-get install -y git
```
### 설치 확인
```bash
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py
```

```bash
cd /isaac-sim/IsaacLab
cat VERSION
```
## Read Setup tips in documents!!

## 설치 테스트 코드
```bash
cd /isaac-sim/IsaacLab
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py
```

## Start Container
[[docs/docker/docker_guide|docker_guide 문서 참조]]

# Edit files
## 1. 마운트를 통한 개발환경 구축 [[docs/docker/docker_guide]]
> 자동완성이 안 된다는 **치명적인** 단점이 있기는 하지만, Antigravity 등 CLI 기반 AI를 활용하기에 가장 적합하다 판단.

local 파일에 container가 접근할 수 있을 뿐 아니라, **Container의 파일을 local에서 접근**하는 것도 가능하다. 이 방식을 활용하면 설치 시 따라오는 nvidia asset에 CLI기반 LLM으로 접근  가능하다.

## 2. Dev-container 확장을 통한 개발환경 구축
>VScode Dev container 확장 설치. 자동완성이 된다는 장점이 있다.
- 좌측 하단 원격 아이콘 Click
- `Attach to Running Container` 선택
- isaac-sim container에 연결하면, 컨테이너 내부의 파일에 접근해 편집할 수 있다.

# Run files
## 1. Run by IsaacSim
아이작 심 설치 디렉토리(일반적으로`~`, `~` = 컨테이너의 홈 디렉토리)에서 `./python.sh <실행할 파이썬 파일 경로>`로 실행한다. Isaac sim 앱 실행은 동일 경로에서 `./runapp.sh`

## 2. Run by IsaacLab
아이작 랩 설치 디렉토리(일반적으로 `~/IsaacLab`, `~` = 컨테이너의 홈 디렉토리)
예시) 
```bash
cd ~/IsaacLab
./isaaclab.sh -p /home/ssafy/workspace/spotMicroIssac/scripts/train.py \
  --task Isaac-Velocity-Flat-Unitree-A1-v0 \
  --num_envs 128
```

# Useful Tutorials
## Isaac Sim Basic Usage Tutorials
- Add Physics and Collision Properties
  - Rigid Body with Colliders Preset
  
## Basic Robot Tutorial
- Physics inspector: move joints
- Omnigraph: move joints
- Action graph: omnigraph 값의 의미들을 시각화


# references

- [Exploring Autonomous Navigation with Isaac SIM and NVIDIA Carter | ROS Nav2 Tutorial](https://www.youtube.com/watch?v=2LDMub6-v5M)
- [nvidia robotics tutorials](https://www.nvidia.com/en-us/learn/learning-path/robotics/)
- [How to command Simulated Issac Robot](https://moveit.picknik.ai/main/doc/how_to_guides/isaac_panda/isaac_panda_tutorial.html)
- [Dockerized ROS2를 사용하여 IsaacSim 시작하기 튜토리얼](https://www.youtube.com/watch?v=9EkkdjW4N54)
- [issac sim requirements](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/installation/requirements.html)

# others
- maniskill?
- Running ROS in Docker?
