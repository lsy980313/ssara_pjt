- ~~reply, review in korean~~
- use sequential-thinking
- use context7
- 파일을 수정할 경우, always ask.
- 파일을 생성할 경우, 경로에 대한 언급이 없는 한 ./scripts/ai_gen 폴더에 생성한다.다른 경로에 생성해야 할 경우, always ask.
- always propose `implementation plan`, `walkthrough` and `review request` in korean.

프로젝트의 환경은 아래와 같다
- ~~ubuntu 22.04~~
- isaac Sim version: 5.1.0, container에서 구동
- isaac lab version: 2.3.0
- 사용하는 컨테이너에 대한 정보는 /home/actuating/workspaces/spotMicroIsaac/scripts/run_container.sh를 참고한다
- isaac lab의 설치 경로는 컨테이너 내부에서 `~/IsaacLab`이다
- 파일을 수정할 경우, 대화 당 1번 수정하기 전 파일을 `파일명_backup.확장자`로 저장한다.