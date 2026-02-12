# Install ubuntu 22.04 in newer environments

## Nvidia 40XX, 50XX Driver issue
### 부팅 드라이브 설치 시
usb로 설치시에 grub 메뉴에서 try or install ubuntu가 하이라이트 된 상태에서 e를 눌러 설정으로 들어간 뒤 'quiet splash ---' 에 nomodeset 붙이기. 안되면 계속 뒤의 매개변수들 추가`'quiet splash ---' -> 'quiet splash nomodeset ---' -> 'quiet splash nomodeset acpi=off ---'

### 설치 후 첫 부팅 시
첫 부팅에 ubuntu를 고르기 전에 e를 눌러 다시 nomodeset 넣기
우분투로 들어가서 인터넷 연결 후 아래 명령어를 순서대로 입력

```bash
sudo apt update
sudo apt install linux-oem-22.04d -y
sudo apt install nvidia-driver-550 -y
```

- `sudo nano /etc/gdm3/custom.conf`
- `#WaylandEnable=false` 에서 # 지우기
- Ctrl+O, Enter 저장 -> Ctrl +X 로 종료

- `sudo nano /etc/default/grub` 아래 라인 찾아서 똑같이 만들기
- `GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nouveau.modeset=0 ibt=off"`
- 맨 아랫줄에 `#GRUB_TERMINAL=console` 에서 # 지우기
- Ctrl+O, Enter 저장 -> Ctrl +X 로 종료

`sudo reboot`로 재시작

## Grub install fatal error
재부팅 시 USB 연결한 상태로 `Try/Install ubuntu ...`로 진입

```bash
sudo add-apt-repository ppa:yannubuntu/boot-repair
sudo apt-get update
sudo apt-get install boot-repair
```

앱 서랍에서 `boot-repair`앱 실행

## 유선랜 인식 안 될때.
휴대폰을 USB를 통해 연결하면 인터넷이 연결되지 않은 PC에 연결하면, `USB 테더링`으로 인터넷 접속 가능
이 상태에서 랜카드 드라이버를 다시 까는 등 상황에 맞는 조치를 취한다.

> 추후에 랜카드 드라이버, grub 맞는 버전, 그래픽 드라이버(ver. 570 open)가 설치된 ubuntu 22.04 custom 이미지 만들어 보기

## User agent  변경하기
>Project.ssafy.com 안들어가지는 문제의 해결책이다.

