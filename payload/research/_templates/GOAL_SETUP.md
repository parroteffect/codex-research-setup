# Goal SETUP budget and prerequisite record

DRAFT · Main 기록 / 사용자 예산 승인 / 독립 QA 검수.
이 Markdown은 운영상 검토하는 회계 기록이다. goal_guard가 강제·자동 계측하지 않는다.
복사 위치: `research/goals/<id>/SETUP.md`. 작성본은 재설치로 초기화하지 않는다.
이 과제 root는 문서 부모이며 guard의 --state가 아니다. RUN init는 아직 없는 별도 child
`research/goals/<id>/run-state/`를 사용하고 이후 helper 명령도 같은 child를 참조한다.

- Goal ID / 사용자 요청·승인 근거 / 기록 revision:
- 상태: NOT_AUTHORIZED / PREPARING / COMPLETED / HANDOFF / EXHAUSTED
- SETUP 목적·완료 기준 / proxy 준비 또는 기존 검수본 재사용:
- 사용자 SETUP 배정 / 별도 RUN 배정 / 단일 총액이면 명시적으로 승인한 분할:
- SETUP 최초 시작 UTC / 유한 elapsed 한도 / deadline UTC / 중단·재개 이력:
- End-to-end deadline이 있으면 원래 시각 / RUN 시작 시 남은 시간과 승인된 RUN 한도:
- 환경·허용 경로·CPU/RAM/GPU/VRAM/동시성 peak 한도 / heavy·unknown USER_ONLY:

아래 모든 필수 한도는 사용자가 유한 값으로 정한다. 빈칸은 미정, 0은 금지다.
Token/cost cap만 명시적 미선택을 허용한다. 필수 관측/강제가 불가능하면 dependent work는
NEEDS_USER_RUN이다. SETUP 승인 누락 시 새 proxy 준비를 시작하지 않는다.

| 차원·단위 | 승인 SETUP 상한 | 누적 보수적 부과 | pending 예약 포함 | 잔여량·미확인 |
|---|---|---|---|---|
| elapsed seconds (pause 포함) | 미정 | 미정 | 미정 | 미정 |
| CPU core-seconds / GPU device-seconds | 미정 | 미정 | 미정 | 미정 |
| 신규 disk bytes | 미정 | 미정 | 미정 | 미정 |
| Main·Engineer·QA·Supervisor calls / reviews | 미정 | 미정 | 미정 | 미정 |
| work attempts / failures·retries 한도 | 미정 | 미정 | 미정 | 미정 |
| tokens / monetary cost (명시적 미선택 가능) | 미정 | 미정 | 미정 | 미정 |

각 작업 **전에** Main이 startup/work/cleanup/save까지 upper bound를 예약한다.
각 작업 **후** actual 또는 UNKNOWN, 실패/재시도 비용, evidence와 잔여량을 추가한다.
누적 차원은 max(reserved, known actual); UNKNOWN과 pending은 예약량을 계속 부과한다.
Main의 유의미한 작업 단위·subagent turn·교체·QA도 포함하며 실패 비용을 환불하지 않는다.
원래 시작시간/소모량은 재개 후에도 유지한다. 상한 초과·미확인 비용은 새 작업 중단/handoff다.

| 작업 ID·담당·retry_of | 사전 예약 시각·상한 (각 차원·peak) | 실제 시작/종료·actual/UNKNOWN | 상태·실패비용·pending | artifact·잔여량 |
|---|---|---|---|---|
| 작성 필요 | 준비 전 기록 | 준비 후 기록 | NOT_RUN | 미확인 |

RUN init 이전 완료 gate (Main과 독립 QA가 근거를 확인):

- SETUP 승인·원래 시작시각·소모·잔여·실패 기록 완비; pending 준비 작업 없음:
- 기존 reviewed proxy 재사용이면 원본 revision/검수/provenance와 과거 비용 또는 UNKNOWN:
- 재사용에서도 새 revision/hash/QA 확인 비용은 위 유효한 배정으로 예약·부과:
- 최종 proxy contract/evaluator/baseline/config/artifact 경로·revision·SHA256:
- 독립 QA의 validity·변경 없음 확인과 bounded executor/enforcement 또는 NEEDS_USER_RUN:
- COMPLETED 승인 근거 또는 미완료 HANDOFF (미완료면 RUN init 금지):
- `GOAL_PROGRESS.md`의 SETUP 비용 링크·RUN 예산·합산 비용/UNKNOWN·남은 end-to-end 시간:

준비 완료 → QA 및 참조 artifact 불변 확인 → RUN init(freeze) → RUN 예약 순서를 따른다.
Helper READY는 이 운영 gate의 확인을 대신하지 않는다. 완료 전 한도가 끝나면 handoff하며
새 init/재개/이름 변경으로 SETUP이나 RUN 예산·deadline을 초기화하지 않는다.
미사용 배정의 이전, 추가 배정, 총액의 분할은 사용자 명시 승인 없이는 금지한다.
Init 이후 허용된 준비/preflight는 RUN ledger에 예약한다. Frozen artifact를 바꾸는 준비는
별도 승인·검토된 migration 없이는 금지하며 과거 비용과 시작시간을 보존한다.
