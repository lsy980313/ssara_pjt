

# Docker commands

| 설명                   | 명령어                                                                                                          | 실사용 명령어                                |
| :--------------------- | :-------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| 도커 파일명 체크       | `docker ps`                                                                                                     |                                              |
| **도커 이미지 저장**   | `docker commit <도커파일명> <저장할 도커 이미지 파일명>`<br> - 동일한 이름으로 저장하면 덮어쓰기로 동작         | `docker commit isaac-sim isaac-sim-img`      |
| **저장된 이미지 확인** | `docker images`                                                                                                 | `docker images \| grep isaac`                |
| 도커 전체삭제          | `docker image prune`                                                                                            |                                              |
| **도커 이미지 삭제**   | `docker rmi <컨테이너명>`                                                                                       |                                              |
| **컨테이너 삭제**      | `docker stop isaac`, `docker rm isaac`                                                                          |                                              |
| **Isaac Sim 실행**     | `/isaac-sim/runapp.sh`                                                                                          |                                              |
| **볼륨 마운트**        | `-v 호스트경로:컨테이너경로[:옵션]`                                                                             | `-v /home/ssafy/scripts:/home/ssafy/scripts` |
| **컨테이너 시작**      | `docker start <컨테이너명>`<br> - `docker ps -a` 등으로 확인되는 stopped container 재시작 가능                  |                                              |
| **컨테이너 진입**      | `docker exec -it <컨테이너명> bash`                                                                             |                                              |
| **UID/GID 확인**       | `sudo docker run --rm --entrypoint bash <docker image name> \`<br>`-c "id -u <컨테이너명>; id -g <컨테이너명>"` |                                              |
| <br>                   |                                                                                                                 |                                              |
- Volume mount?
	호스트의 경로를 컨테이너 내부 경로와 1:1로 매핑. **Bind Mount는 본질적으로 '동기화'가 아니라 '동일한 디렉터리 공유'**이기 때문에 양방향으로 즉시 반영

# Run Isaac sim in docker container
## 실행 스크립트(일반)
```bash
  sudo docker run --name <container name> -it --gpus all --network=host \
  --user `<UID>`:`<GID>` \
  -e ACCEPT_EULA=Y -e PRIVACY_CONSENT=Y \
  -e DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /home/ssafy/isaac-sim/cache:/isaac-sim/.cache \
  -v /home/ssafy/isaac-sim/ov:/isaac-sim/.local/share/ov \
  -v /home/ssafy/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs \
  <-v 호스트경로:컨테이너경로[:옵션]>
  <docker image name>
```
위 스크립트에 대한 상세한 설명은 아래와 같다.
- `sudo docker run`: 도커 데몬은 기본적으로 root 권한으로 실행되므로 관리자 권한이 필요
- `--name <container name>`: 컨테이너에 이름표를 붙인다. `docker stop`, `restart` 등 관리 용이
- `-it` (Interactive + TTY): 터미널에 접속해서 명령어를 입력해야 할 때 필수
    - `-i` (interactive): 표준 입력(stdin)을 활성화하여 키보드 입력을 컨테이너로 보냄
    - `-t` (tty): 가상 터미널(pseudo-tty)을 할당하여 콘솔 화면이 보이게 함
- `--gpus all`: 호스트 컴퓨터에 장착된 모든 NVIDIA GPU를 컨테이너가 사용할 수 있게 허용 (딥러닝 학습 시 필수). *NVIDIA Container Toolkit 설치 필요*
- `--network=host`: 컨테이너와 호스트 간의 네트워크 격리를 없앰. 호스트의 IP와 포트를 컨테이너가 그대로 공유
- `--user <UID>:<GID>`: 컨테이너 내부 프로세스를 root가 아닌 특정 사용자(호스트의 나와 같은 ID)로 실행. Bind Mount 사용 시 권한 문제(Permission Denied)를 예방하는 가장 좋은 방법.
- - e: 
- -v: 볼륨 마운트
## 실행 스크립트(실사용 명령)
```bash
xhost +local:
docker run --name isaac-sim --entrypoint bash -it --gpus all -e "ACCEPT_EULA=Y" --rm --network=host \
-e "PRIVACY_CONSENT=Y" \
-v $HOME/.Xauthority:/isaac-sim/.Xauthority \
-e DISPLAY \
-v ~/docker/isaac-sim/cache/main:/isaac-sim/.cache:rw \
-v ~/docker/isaac-sim/cache/computecache:/isaac-sim/.nv/ComputeCache:rw \
-v ~/docker/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs:rw \
-v ~/docker/isaac-sim/config:/isaac-sim/.nvidia-omniverse/config:rw \
-v ~/docker/isaac-sim/data:/isaac-sim/.local/share/ov/data:rw \
-v ~/docker/isaac-sim/pkg:/isaac-sim/.local/share/ov/pkg:rw \
-v /home/actuating/workspaces/spotMicroIsaac:/home/actuating/workspaces/spotMicroIsaac \
-u 1234:1234 \
isaac_sim
```
위 실사용 스크립트에 대한 상세 설명은 다음과 같습니다.

- `xhost +local:`: 로컬 사용자(non-network)가 X11 서버(그래픽 화면)에 접근할 수 있도록 허용합니다. GUI 프로그램을 띄우기 위해 필수입니다.
- `--entrypoint bash`: 컨테이너의 기본 실행 명령을 무시하고 `bash` 쉘을 실행합니다.
- `--rm`: 컨테이너가 종료되면 자동으로 삭제합니다 (일회성 실행 시 유용).
- `-e "ACCEPT_EULA=Y"`, `-e "PRIVACY_CONSENT=Y"`: NVIDIA Isaac Sim 라이선스 및 개인정보 동의를 환경 변수로 자동 수락합니다.
- `-v $HOME/.Xauthority:/isaac-sim/.Xauthority` 및 `-e DISPLAY`: 호스트의 디스플레이 설정과 권한을 공유하여 컨테이너 안에서 실행되는 Isaac Sim의 화면을 호스트 모니터에 띄웁니다.
- **캐시 및 데이터 마운트 (-v 옵션들)**:
    - `cache/main`, `cache/computecache`: 셰이더 컴파일 결과 등을 저장하여 다음 실행 시 로딩 속도를 높입니다.
    - `logs`: 로그 파일을 호스트에 저장하여 디버깅을 용이하게 합니다.
    - `data`, `pkg`: Isaac Sim의 데이터와 패키지를 호스트에 저장하여 컨테이너 재시작 시에도 데이터를 유지합니다.
- `-v .../spotMicroIsaac:...`: **사용자 워크스페이스 마운트**. 로컬에서 작성한 코드가 컨테이너 내부에서도 동일한 경로로 접근 가능하게 합니다.
- `-u 1234:1234`: 호스트 사용자와 동일한 UID/GID로 실행하여, 생성되는 파일의 권한 문제를 방지합니다.