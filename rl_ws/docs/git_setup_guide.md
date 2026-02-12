# Git 자격 증명 설정 및 푸시 가이드

이 가이드는 GitLab 자격 증명을 이 머신에 영구적으로 저장하고, 현재 로컬 워크스페이스의 내용으로 원격 브랜치를 덮어쓰는 방법을 설명합니다.

## 1. 자격 증명 영구 저장 설정 (Credential Storage)

매번 사용자 이름과 비밀번호를 입력하지 않도록, Git이 `store` credential helper를 사용하도록 설정합니다.

### 1단계: Helper 활성화
터미널에서 다음 명령어를 실행하세요:
```bash
git config --global credential.helper store
```

### 2단계: 자격 증명 추가
`~/.git-credentials` 파일을 생성(또는 편집)하여 GitLab 인증 정보를 추가합니다.

**실행할 명령어:**
`<USERNAME>`과 `<ACCESS_TOKEN>` 부분을 실제 본인의 정보로 변경하여 실행하세요.
```bash
echo "https://<USERNAME>:<ACCESS_TOKEN>@lab.ssafy.com" >> ~/.git-credentials
```

또는 `vi`나 `nano` 편집기를 사용하여 수동으로 작성할 수도 있습니다:
```bash
nano ~/.git-credentials
```
파일에 다음 내용을 한 줄로 추가하고 저장하세요:
`https://your_username:your_token@lab.ssafy.com`

> **참고**: Personal Access Token이 없다면 GitLab의 **User Settings > Access Tokens** 메뉴에서 생성할 수 있습니다.

## 2. 원격 브랜치로 푸시 (Push)

인증 설정이 완료되면 작업을 업로드할 수 있습니다.

### 2.1단계: 강제 푸시 (Force Push)
이 명령어는 원격 `feature/RL` 브랜치의 내용을 사용자의 로컬 `develop` 브랜치 내용으로 덮어씁니다.

```bash
cd /home/actuating/workspaces/spotmicro
git push -u origin develop:feature/RL --force
```

---
**확인**:
푸시 명령 실행 후, 업데이트가 완료되었다는 메시지(예: `Branch 'develop' set up to track remote branch 'feature/RL' from 'origin'.`)가 나오면 성공한 것입니다.
