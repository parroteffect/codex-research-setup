# Goal progress and user shortlist

- Goal ID / 사용자 시작 요청 / config·contract·ledger 경로와 hash:
- Ultimate-goal predicate / 목표수와 추가 기준 / 허용 evidence class:
- Monk 선택과 기존 standard/monk STATE 대응 / 방법론 노출:
- 현재 상태: SETUP / ACTIVE / GOAL_MET / BUDGET_EXHAUSTED / STALLED / USER_PAUSED / INTEGRITY_BLOCKED
- Goal 달성: YES / NO / UNVERIFIED, 처음 목표의 각 조건에 대한 증거:
- 현재 elapsed/attempt/retry/review/stagnation/agent-call 예약·잔여량 / 미계측 항목:
- 미완료 예약·실패·중단 기록 / 다음 실행자와 확인할 revision:

| 후보·lineage·mechanism | 근거 class·QA | Supervisor rationale | 기준 충족·중복 제거 | 사용자 최종 검증 |
|---|---|---|---|---|
| 작성 필요 | UNVERIFIED | 미검토 | 미확인 | NOT_RUN |

Proxy로 지지된 후보, 이론 근거 후보와 결정적 검증이 남은 후보를 구분한다.
예산 종료·후보수 부족은 GOAL_MET가 아니다. 사용자 목표가 허용하지 않는 근거 class는 quota에 세지 않는다.
Main이 처음 predicate와 모든 근거를 직접 확인하고 최종 shortlist 판단을 Supervisor xhigh에 맡긴다.

- 기각/보강한 메커니즘과 다음 연구에 반영할 교훈:
- Pending user-run tests: 질문·우선순위·RUNBOOK DRAFT/READY_FOR_USER·예상 자원·불확실성:
- 실제 확인한 결과 / 사용자 보고 / 미확인 결과 구분:
- 재개 조건 / 다음 책임자 / unresolved scientific disagreement:

Checkpoint 후 같은 config/contract/ledger와 모든 pending reservation을 복원한다.
예산/목표 변경은 사용자 승인과 과거 기록·소모량을 보존하는 명시적 개정이다.
Helper가 자동 판정한 scientific success나 자원 sandbox를 주장하지 않는다.
