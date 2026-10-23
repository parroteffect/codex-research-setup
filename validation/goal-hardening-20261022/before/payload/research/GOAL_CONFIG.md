# Goal 설정 — 사용자가 작성

Schema 1 · DRAFT · 기본 연구에 선택적으로 goal과 monk를 적용한다.
이 파일은 설치 시 없을 때만 생성된다. Agent는 사용자 입력을 임의로 채우거나 바꾸지 않는다.
아래 **하나의 TOML block**만 기계 설정이다. CLI 문답은 없다.

- `enabled=false`: goal 시작 안 함. `monk=false`: 기본 연구, `true`: monk 조사 제한.
- 빈 문자열은 미정이다. 숫자 0은 사용 금지이며 무제한이 아니다. 예시 값은 실행 허가가 아니다.
- 목표 후보 수는 목표의 일부다. 실제 성공 기준·허용 근거·중복 제거까지 만족해야 GOAL_MET이다.
- 각 비용은 준비/import/초기화/저장/실패/재시도/하위 프로세스를 포함한 전체 상한이다.
- CPU/GPU work 단위는 core·second/device·second, RAM/VRAM은 MiB, 저장은 bytes다.
  CPU/RAM은 동시 합계, VRAM은 지정 GPU마다 동시 합계, 저장은 누적 신규 쓰기 보수적 합계다.
- GPU 미사용: `gpu_ids=[]`, VRAM/GPU seconds=0. Token/cost cap 미선택은 문자열 `unselected`다.
  선택한 cap의 계측·강제가 불가능하면 dependent automatic work는 NEEDS_USER_RUN이다.
- Agent calls는 Main의 유의미한 작업 단위와 subagent 생성/후속 turn/교체를 모두 포함해 예약한다.
  Ledger는 기록된 이벤트만 센다. Provider token/billing이나 대화 전체를 자동 계측하지 않는다.
- `max_attempts`는 모든 experiment/agent/review 예약, `max_retries`는 전체 재시도,
  `concurrency`는 미완료 예약 수다. 재사용 thread도 새 작업 비용을 기록한다.
- 허용 경로는 절대 real path로 작성한다. 대용량 artifact root는 프로젝트 storage 정책을 따른다.
- 양식 작성/검증/init는 실행 허가가 아니다. 사용자의 시작 요청, frozen proxy, 독립 QA,
  실제 검수된 bounded executor가 있어야 허용된 light proxy를 반복할 수 있다.

```toml
schema_version = 1

[goal]
enabled = false
monk = false
objective = ""
success_criteria = ""
target_directions = 0
accepted_evidence = []
stop_conditions = []

[paths]
workspace = ""
environment = ""
read_roots = []
write_roots = []
artifact_root = ""

[proxy]
contract_path = ""
revision = ""

[limits]
total_elapsed_seconds = 0
per_attempt_seconds = 0
total_cpu_seconds = 0
total_gpu_seconds = 0
cpu_cores = 0
ram_mib = 0
gpu_ids = []
vram_mib = 0
disk_bytes = 0
max_attempts = 0
max_retries = 0
concurrency = 0
max_agent_calls = 0
max_reviews = 0
max_stagnation = 0

[accounting]
token_cap = "unselected"
cost_cap = "unselected"
tokens_metered = false
tokens_enforced = false
cost_metered = false
cost_enforced = false
```

Agent가 작성할 계약·검수·설정 해석은 `research/goals/<id>/`의 별도 문서에 남긴다.
현재 schema는 `research/_templates/GOAL_CONFIG.md`를 참고한다. 작성본을 덮어써 갱신하지 않는다.
