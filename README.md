# 제주 항공권 알림

Google Flights 검색 결과를 SerpApi로 조회하고 Telegram으로 보내는 개인용 가격 알림 서비스입니다.

## 조회 조건

- 김포 `GMP` → 제주 `CJU` 왕복.
- 2026년 9월 24일 출발, 9월 27일 귀국.
- 성인 4명, 일반석, 직항만 조회.
- Asia/Seoul 기준 매일 09시, 15시, 21시 알림.
- 최저가 조합의 가는 편과 오는 편 출발·도착 시각 및 항공사를 함께 알림.

## 환경변수

`.env.example`을 `.env`로 복사하고 서버에서만 값을 입력합니다.

- `SERPAPI_API_KEY`.
- `TELEGRAM_BOT_TOKEN`.
- `TELEGRAM_CHAT_ID`.

`.env`, DB 파일, 로그 및 가상환경은 Git에서 제외됩니다.

## 최초 서버 설치

```bash
git clone https://github.com/dataagentkim-cpu/jeju-fare-alert.git /home/ubuntu/jeju-fare-alert
cd /home/ubuntu/jeju-fare-alert
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
sudo cp deploy/jeju-fare-alert.service /etc/systemd/system/jeju-fare-alert.service
sudo systemctl daemon-reload
sudo systemctl enable --now jeju-fare-alert.service
```

시험 알림은 아래 명령으로 한 번 실행합니다.

```bash
venv/bin/python -m src.main --once
```

## GitHub Actions

Repository secret으로 `EC2_HOST`와 `EC2_SSH_KEY`를 등록합니다. `main` push 시 SSH로 서버에 접속해 `git pull --ff-only` 후 서비스만 재시작합니다.
