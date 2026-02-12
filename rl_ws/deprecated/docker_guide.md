# Run Isaac Sim in container
## save/load docker
- 도커 파일명 체크하기 `docker ps`
- 도커 이미지 저장하기 `docker commit <도커파일명> <저장할 도커 이미지 파일명>`
  - 동일한 이름으로 저장하면 덮어쓰기로 동작한다
  > 예시)  `docker commit isaac_sim isaac_sim`, `docker commit a1b2c3d4e5f6 isaac-sim:5.1.0-installed`
- 저장된 도커 이미지 확인하기: `docker images | grep isaac`
- 도커 이미지 관리: `docker image prune`
- 도커 이미지 삭제: `docker rmi <컨테이너명>`
- remove docker container: `docker stop isaac` `docker rm isaac`
- isaac sim 실행 스크립트: `/isaac-sim/runapp.sh`
- 컨테이너에 볼륨 마운트: `-v 호스트경로:컨테이너경로[:옵션]`
  > 예시)  `-v /home/ssafy/scripts:/home/ssafy/scripts`
- 도커 컨테이너 시작: `docker start <컨테이너명>`
  - `docker ps -a`, `docker rm`으로 확인되는 stopped container는 이 명령으로 다시 살릴 수 있다
- go inside docker container:`docker exec -it <컨테이너명> bash`
- check UID/GID:
  ``` bash
    sudo docker run --rm --entrypoint bash <docker image name> \
    -c "id -u <컨테이너명>; id -g <컨테이너명>"
  ```
- ~~change  host mount dir: `sudo chown -R <UID>:<GID> /home/ssafy/isaac-sim`~~
- 저장된 도커 이미지 로드하기:
  - ~~권한 문제 발생 시 UID, GID 확인 후 아래 명령으로 실행한다.~~
  - 그냥 <UID>, <GID>에 0,0 넣고 루트로 실행해버리면 도커 안에서 편집하는 등의 절차에서 권한 문제를 완전히 해소할 수 있다.
```bash
sudo docker run --name <container name> -it --gpus all --network=host \
--user <UID>:<GID> \
-e ACCEPT_EULA=Y -e PRIVACY_CONSENT=Y \
-e DISPLAY \
-v /tmp/.X11-unix:/tmp/.X11-unix \
-v /home/ssafy/isaac-sim/cache:/isaac-sim/.cache \
-v /home/ssafy/isaac-sim/ov:/isaac-sim/.local/share/ov \
-v /home/ssafy/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs \
<-v 호스트경로:컨테이너경로[:옵션]>
<docker image name>
```

예시(Real command)
> spotMicroIsaac 경로로 이동한 후 `./scripts/run_isaac_sim.sh` 로 구성해 두었다.
```bash
sudo docker run --name isaac_sim -it --gpus all --network=host \
--user 0:0 \
-e ACCEPT_EULA=Y -e PRIVACY_CONSENT=Y \
-e DISPLAY=$DISPLAY \
-e XAUTHORITY=/root/.Xauthority \
-v $XAUTHORITY:/root/.Xauthority:ro \
-v /tmp/.X11-unix:/tmp/.X11-unix \
-v /home/ssafy/isaac-sim/cache:/isaac-sim/.cache \
-v /home/ssafy/isaac-sim/ov:/isaac-sim/.local/share/ov \
-v /home/ssafy/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs \
-v /home/ssafy/workspace/spotMicroIssac/scripts:/home/ssafy/workspace/spotMicroIssac/scripts \
isaac_sim
```
공식 문서에서 나온 대로
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
-u 1234:1234 \
isaac_sim
```