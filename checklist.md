# 배포 뼈대 체크리스트

- [x] 기존 `runcoach.service`, `shadowtrack.service` 구조를 읽기 전용으로 확인한다.
- [x] 최소 서비스 프로세스와 의존성 파일을 작성한다.
- [x] 비밀정보와 로컬 데이터를 제외하는 `.gitignore`를 작성한다.
- [x] 기존 구조를 미러링한 systemd 유닛을 작성한다.
- [x] SSH 기반 GitHub Actions CD 워크플로를 작성한다.
- [x] 문서와 환경변수 예시를 작성한다.
- [x] 로컬 실행 및 정적 검증을 완료한다.
