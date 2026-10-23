# Research state

<!-- Main owns this file. Ground factual context in evidence; label hypotheses explicitly.
Never overwrite an existing state file with this template.
Use only fields relevant to continuing the research; link to longer research notes.
Preserve old decisions, rejected alternatives, and evidence by linking to them. -->

## 현재 질문과 범위
- 질문:
- 사용자가 승인한 목표·수정 범위:
- 현재 모드: 연구 논의 / 대화형 리뷰 / 구현 / 결과 해석
- 연구 모드: standard
- 연구 모드의 적용 과제 / 사용자 선택·전환 근거: (monk 선택 시 기록하고 재개 때 복원)
- 이번 요청의 종료 조건:

## 현재 판단
- 확인한 사실·관찰과 증거:
- 해석·가설·경쟁 설명:
- 결정과 근거:
- 미해결 사항:
- 리뷰 중이라면 현재 step / 다음 step 진행에 대한 사용자 동의:

## 연구 후보와 수학적 상태
<!-- Keep brief; add/update only when useful. These are not fixed output quotas.
Hypothesis status, novelty status, and user approval are separate judgments. -->
- 유망한 후보 / 서로 다른 작동 메커니즘 / 현재 선호와 이유:
- 성공 시 기대하는 기여와 중요성 / 현재 성공을 뒷받침하는 근거·핵심 불확실성:
- 중요한 대안 / 기각·보류 이유 / 다시 검토할 조건:
- 핵심 정의·가정 / 도출한 결과 / proof sketch 또는 conjecture / 남은 proof gap:
- 가장 가까운 선행 접근 / 실제 확인한 차이 / 미확인 novelty:
- 결론을 바꿀 수 있는 다음 계산·증거·판별 실험:
- 상세 연구 노트 링크: (필요할 때만 research/notes/<topic>.md 사용)

## Monk 연구 맥락
<!-- Fill only for a monk task or its follow-up comparison.
Keep the mode separate from the task type and preserve earlier exposure and findings. -->
- 출발 문제·제약·관찰 / 이미 제공되거나 확인한 자료:
- 유망한 연구의 축·기발한 발상 / 발전시킨 메커니즘·핵심 불확실성:
- 활용한 수학적 관점·기법·출처와 성립 조건:
- 중요한 관련 방법론 노출과 후보에 준 영향:
- 선행연구 대조 상태·확인 범위: (미확인은 monk 후속 대조 대기로 남김)
- 대조 전 후보의 주장·유도·proof gap snapshot 또는 revision:
- 사용자가 요청한 전환·대조 범위 / 다음 행동:

## 실행 경계와 가벼운 검증
- 본 실험 실행자: USER_ONLY
- Agent는 무거운 최종 테스트·실험을 실행·제출·재시도·재개하지 않는다.
- 허용한 가벼운 검증의 범위·자원·시간·실행 수·재시도 한도:
- 고정 조건·수정 금지 대상:
- 사용자 실행 계획의 자원 요구와 불확실성: (agent 실행 권한과 별개)

## 활성 engineering 작업
- Task ID / 실제 확인한 engineer thread 식별자:
- Mode / SPEC 경로와 revision:
- 수정 가능한 경로:
- 작업 상태: DONE / PARTIAL / BLOCKED
- 마지막으로 확인한 내용과 시각:

## 사용자 실행 handoff
- RUNBOOK 경로 / DRAFT 또는 READY_FOR_USER:
- 본 실험 상태: NOT_RUN / USER_RUNNING / USER_COMPLETED / USER_FAILED / USER_ABORTED / UNKNOWN
- 사용자에게 전달한 명령·config·SPEC·code revision:
- 사용자 실행 후 실제로 확인한 조건: (예정 조건과 구분)
- 사용자 보고 / 직접 확인한 artifact:
- 제공받은 run·job ID와 로그 경로: (미제공이면 미확인, job 제어 금지)
- 최종 실행 없이는 판단할 수 없는 항목:
- 다음 책임자와 행동:

## 기록
- SPEC / REPORT / RUNBOOK:
- Raw artifact와 재현 정보:
- 과거 결정·실험 기록:

## 선택적 Goal 상태
- Goal enabled / monk boolean: (기존 standard는 monk=false로 호환)
- 사용자 시작 요청 / ultimate-goal predicate / config·frozen proxy·ledger revision:
- 독립 QA/Supervisor thread·requested/resolved effort / 남은 호출·검토 예산:
- Shortlist·mechanism/lineage 중복 제거 / 사용자 기준 충족 근거:
- GOAL_MET 여부 / 미달 중단 사유 / pending NEEDS_USER_RUN:
- 상세 progress·candidate evidence 링크 / pending reservations와 다음 책임자:
