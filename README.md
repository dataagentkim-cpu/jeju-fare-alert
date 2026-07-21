# Agent Service

기존 EC2 서버에서 `runcoach.service`, `shadowtrack.service`와 나란히 실행할 세 번째 Python 프로세스의 최소 배포 뼈대입니다. AWS API, AWS CLI, SDK 또는 신규 AWS 리소스를 사용하지 않습니다.

## 저장소 구조

```text
.
├── .github/workflows/deploy.yml
├── deploy/agent-service.service
├── src/main.py
├── .env.example
├── .gitignore
└── requirements.txt
```

## 최초 서버 설치

아래 작업은 서버에서 한 번만 수행합니다. `REPOSITORY_NAME`은 실제 GitHub 저장소명으로 바꿉니다.

```bash
ssh -i ~/Downloads/runcoach_key.pem ubuntu@3.35.236.206
git clone https://github.com/dataagentkim-cpu/REPOSITORY_NAME.git /home/ubuntu/agent-service
cd /home/ubuntu/agent-service
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
sudo cp deploy/agent-service.service /etc/systemd/system/agent-service.service
sudo systemctl daemon-reload
sudo systemctl enable --now agent-service.service
systemctl status agent-service.service --no-pager
```

`.env`에는 서버에서 직접 비밀값을 넣습니다. 이 파일과 DB 파일은 `.gitignore`에 포함되어 저장소로 올라가지 않습니다.

## GitHub Actions 설정

GitHub 저장소의 `Settings → Secrets and variables → Actions`에 다음 Repository secret을 추가합니다.

- `EC2_HOST` 값은 `3.35.236.206`입니다.
- `EC2_SSH_KEY` 값은 `runcoach_key.pem`의 전체 내용입니다.

이후 `main` 브랜치에 push하면 워크플로가 SSH로 접속해 `git pull --ff-only` 후 `agent-service.service`만 재시작합니다.

## 로컬 실행

```bash
python3 -m src.main
```

현재 프로세스는 시작 후 종료 신호를 기다리는 최소 진입점뿐입니다. 정기 작업이 생기면 별도 cron이나 systemd timer보다 애플리케이션 내부 스케줄러를 우선 사용합니다.
