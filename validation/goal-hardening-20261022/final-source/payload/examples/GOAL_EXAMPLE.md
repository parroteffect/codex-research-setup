# 작은 예시 — 실행 허가 또는 완성된 설정이 아님

목표 예: 작은 합성 선형계에서 서로 다른 세 가지 안정적인 근사 메커니즘을 찾는다.
`goal.enabled=true`, `goal.monk=false`면 기본 연구+goal, monk를 true로 바꾸면 goal+monk다.
예시의 `target_directions=3`은 전역 quota가 아니다. 독립 QA-valid 근거와 Supervisor의
사전 기준 충족 판단, mechanism/lineage 중복 제거를 모두 거친 3개가 있어야 목표가 달성된다.

작성 순서:

1. 사용자가 유한 **SETUP 배정**과 `research/GOAL_CONFIG.md`의 **RUN 배정**을 별도로 정한다.
   단일 총액이면 사용자가 분할을 명시적으로 승인한다. Main은 `research/_templates/GOAL_SETUP.md`로
   `SETUP.md`에 승인·최초 시작 UTC·deadline·작업 전 예약·actual/UNKNOWN·실패/재시도·잔여를 기록한다.
   SETUP 미승인 시 준비 금지다. 예를 들어 RUN이 CPU 전용이면 `gpu_ids=[]`, `vram_mib=0`,
   `total_gpu_seconds=0`; token cap을 안 쓰면 `"unselected"`. 예시는 예산이나 실행을 승인하지 않는다.
2. 승인된 SETUP 범위에서 Main/Engineer가 PROXY_CONTRACT와 작은 known-answer evaluator를 준비한다.
   모든 비교는 같은 frozen 데이터/metric/aggregation을 사용한다. 실제 파일의 SHA256만 적는다.
   Main/Engineer/QA calls와 tiny 검사도 SETUP 비용이다. 기존 proxy 재사용이면 provenance와 이전
   검수·비용/UNKNOWN을 보존하고 새 확인 비용을 유효한 SETUP 배정에서 부과한다.
3. 독립 QA가 계약/코드/비교와 외부 executor를 검수한다. SETUP 완료·pending 없음·참조 artifact
   불변 확인 후에만 RUN init한다. 한도 안에서 미완료면 handoff다. SETUP Markdown은 운영상 검수하며
   guard가 강제/계측하지 않는다. Executor/필수 hard limit가 없으면 실험은 NEEDS_USER_RUN이다.
4. SETUP 비용 링크·RUN 배정·합산 비용/UNKNOWN을 GOAL_PROGRESS에 남긴다. SETUP.md/progress가 있는
   `research/goals/<id>/`는 부모로 유지하고, init의 --state는 아직 없는 child
   `research/goals/<id>/run-state/`로 지정해 RUN을 freeze한다. 이후 모든 helper도 같은 child를 쓴다.
   RUN elapsed는 이때 시작한다. 원래 end-to-end deadline과 과거 사용량은 초기화하지 않는다.
   미사용 배정 자동 이전은 금지다. Init 이후 허용된 preflight도 RUN ledger에 예약한다.
5. 아래는 **freeze 이후 파일에 기록할 JSON 예약 예시**다. 명령이나 실제 실행 요청이 아니다.

```json
{"id":"toy-001","kind":"experiment","retry_of":null,"light":true,"cost_known":true,"duration_seconds":2,"cpu_cores":1,"ram_mib":32,"gpu_ids":[],"vram_mib":0,"bounds":{"cpu_seconds":2,"gpu_seconds":0,"disk_bytes":4096,"agent_calls":0,"reviews":0,"tokens":0,"cost":0}}
```

`finish`의 usage JSON은 `outcome`, `actual`(같은7개누적차원), `duration_seconds`, `cpu_cores`,
`ram_mib`, `gpu_ids`, `vram_mib`, `evidence`를 포함한다. 미계측 actual/peak는 JSON null이다.
`evidence`는 `executor`, `code_revision`, `config_revision`, `artifact_ids`를 기록한다.
실패도 finish하며 unknown은 예약량을 유지한다. 실제량이 예약을 넘으면 breach로 중단한다.

KOBS의 설명용 흐름은 fixed-K/fixed-layer-input V readout에서 baseline·analytic initialization·
trained space를 비교하고, 기각한 메커니즘에서 다음 축을 배우고, 별도 사용자 full-model PPL로
이어진 것이다. 기존 KOBS pilot의 큰 RAM·여러 분 실행을 agent-light로 간주하지 않는다.
이 배포본은 Qwen·layer·임계값이나 KOBS 실제 실험을 포함하지 않는다.
