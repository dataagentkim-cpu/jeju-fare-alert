# 작업 컨텍스트 기록

- AWS API, AWS CLI, AWS SDK, IAM 변경 및 신규 AWS 리소스 생성은 사용하지 않는다.
- 기존 EC2 `3.35.236.206`의 `runcoach.service`, `shadowtrack.service`를 읽기 전용으로 조사한다.
- 배포 서버 사용자는 `ubuntu`이며 SSH 키는 로컬 `~/Downloads/runcoach_key.pem`을 재사용한다.
- 서비스 이름이 지정되지 않아 임시 이름을 `agent-service`로 가정한다. 최종 이름 확정 시 경로와 유닛명을 함께 변경할 수 있게 단순하게 유지한다.
- 서버 배포 또는 systemd 변경은 이번 단계 범위가 아니다. 저장소에 배포 뼈대만 작성한다.
- 기존 두 유닛 모두 `After=network.target`, `Restart=always`, `RestartSec=10`, `WantedBy=multi-user.target`을 사용한다.
- 새 배포 경로는 `/home/ubuntu/agent-service`, 유닛명은 `agent-service.service`로 정했다.
- CD는 최초 설치가 완료됐다는 전제에서 `git pull --ff-only origin main`과 서비스 재시작만 수행한다.
- Python 진입점의 컴파일과 SIGTERM 정상 종료, `deploy.yml` YAML 파싱, `.env` 및 DB 패턴의 Git 제외를 검증했다.
