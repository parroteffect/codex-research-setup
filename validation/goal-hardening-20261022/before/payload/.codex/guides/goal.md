# Goal overlay — 목표까지 연구와 검증을 이어간다

연구는 기본 동작이다. Goal은 연구 → 작은 판별 검증 → 채택/기각/보강 → 다음 연구를
사용자의 ultimate goal까지 이어가는 자율 진행 overlay다. Monk는 관련 방법론 조사 제한으로
goal과 독립이다. 새 양식은 goal.enabled와 goal.monk만 사용한다. 기존 STATE의 standard는
monk=false, monk는 monk=true로 호환해서 읽는다. 새 native Codex mode key를 만들지 않는다.
설치·양식 작성만으로 goal이 시작되지 않는다. Main은 기존 research guide의 발명·깊은 수학적
분석·반례 점검을 직접 수행하며 dispatcher로만 행동하지 않는다.

## 시작과 고정 계약

사용자가 `research/GOAL_CONFIG.md`의 하나의 TOML block에 목표·범위·예산·경로를 작성하고
시작을 요청한다. Agent는 입력을 해석·검사하고 별도 과제 문서에 미정 사항을 기록한다.
사용자 authorization field를 임의로 채우지 않는다. 0은 금지, 빈칸은 미정이다.
선택되지 않은 token/cost cap 외 모든 한도는 유한해야 한다. 누락된 중요한 조건은 SETUP이다.

자동 실험 순환 전 과제별 proxy를 선정하고 `research/_templates/PROXY_CONTRACT.md`로
범위·baseline/evaluator revision·data manifest/split·fit/tune/DEV·heldout 접근·metric/unit·
aggregation·precision/storage/runtime 조건·acceptance gate를 고정한다. 반복 DEV 노출과
multiplicity를 기록한다. 적응적 탐색의 최고 DEV를 독립 confirmation이라고 부르지 않는다.
Sealed confirmation은 사전 접근 규칙 안에서만 사용하며 그 결과로 반복 tuning하지 않는다.
Candidate/hyperparameter만 계약 안에서 바꾼다. 후보를 살리려고 evaluator/data/gate를 바꾸지 않는다.
계약 변경은 새 revision, 필요한 사용자 승인과 과거 결과·남은 예산 보존을 요구한다.
부적합 proxy의 점수로 유망한 외부 범위 후보를 기각하지 않는다. 별도 설계 질문 또는
NEEDS_USER_RUN으로 보존하며 매 아이디어에 새 full evaluator를 만들지는 않는다.

## 역할과 실제 effort

| 역할 | 책임 | 실제 spawn effort |
|---|---|---|
| Main Research Lead | 메커니즘·유도·반례·실험설계·직접 코드 검수·연구 학습 | 사용자 설정 유지 |
| Engineer | 단일 코드 writer, 구현·debug·tiny local checks·RUNBOOK | high, 복잡한 수식/수치 정합성은 xhigh |
| QA | 독립적으로 계약/코드/config/비교/누수/실제revision/비용/출력 검수 | 반복조건·로그는 medium; 최초 evaluator·metric/split 변경·수학적 유효성은 high |
| Supervisor | 기여 가능성·근거·경쟁설명·실패조건·목표 적합성 판단 | routine high; 중요한 판단 xhigh |

Supervisor의 중요한 판단은 최종 shortlist 채택, 유망 연구 방향의 기각, 논쟁적 과학 기각,
중요한 연구 방향 변경, 결정적 수학 판단이다. 모든 반복을 xhigh로 만들지는 않는다.
Model은 사용자 선택을 보존하며 역할 TOML에 effort를 pin하지 않는다. 기본 subagent effort는 high,
QA medium은 실제 spawn 인자로 지정한다. Requested와 observed/resolved effort를 구분한다.
Followup으로 thread effort가 바뀌었다고 가정하지 않는다. 변경이 필요하면 근거를 보존하고
기존 thread를 정리한 뒤 도구 지원을 확인해 replacement를 생성한다. 교체 비용도 계산한다.
기계적 검사는 낮은 effort agent보다 deterministic check를 우선한다. 이 정책은 정확도 실측 주장이 아니다.

`max_concurrent_threads_per_session=3`은 Main을 제외한 공유 슬롯이다. Goal에서는
Engineer1+QA1+Supervisor1이 이를 공유한다. 일반 상황의 최대3 Engineer 규칙을
3 Engineer+2 reviewer 허용으로 해석하지 않는다. 코드 writer는 언제나 하나다.
QA/Supervisor는 자식 agent·별도 Codex를 생성하지 않는다. QA는 연구 코드를 수정하거나
판정 중 evaluator를 조용히 고치지 않는다. 작은 검수 artifact만 소유할 수 있다.
Main/QA가 수정을 요청하면 Engineer가 수행한다. 누락된 역할을 Main의 self-review로 대체해
독립 검수 완료라고 하지 않는다. Runtime 지원 실패는 해당 gate UNVERIFIED로 남긴다.

## 반복과 독립 검수

1. Main은 중요한 병목·핵심 insight·기여·성립 가정·경쟁 설명을 발전시킨다. 후보 family와 lineage를 남긴다.
2. 가장 경제적인 판별 질문을 정하고 계약 적합성을 확인한다. Engineer가 필요한 최소 구현과 tiny 검증을 맡는다.
3. 새 method/evaluator/data 경로나 검수 envelope 밖 변경은 독립 QA를 받는다. 동일 검수 경로는 exact
   code/config/pipeline hash에 연결된 자동 검사를 재사용할 수 있다. 매 반복 전체 역할의 full review를 요구하지 않는다.
4. 실행 전 권한·비용/예산 검사와 QA validity를 따로 확인한다. 예약 후 검수된 bounded executor로만
   허용된 light proxy를 실행한다. 실행자는 시도마다 한 명, 보통 QA; tiny 구현 검사는 Engineer다.
   QA는 Engineer의 검증을 자동 재실행하지 않는다. 한 번의 실행을 중복 계측/실행하지 않는다.
5. QA-valid 근거를 Supervisor가 사용자 기준에 따라 검토한다. 고정 novelty/performance 가중 점수로
   명시적 논증을 대체하지 않는다. Main은 기각/보강 이유를 다음 연구에 환류한다.
6. 유망 후보를 보존하고 다른 메커니즘을 탐색한다. 목표까지 반복하거나 명시적 경계에서 멈춘다.

실행 상태: NOT_RUN / RUNNING / VALID / INVALID / OOM / TIMEOUT / INFRA_ERROR / NEEDS_USER_RUN.
가설 상태: PROPOSED / REFINE / REJECTED / ACCEPTED / DEFERRED. QA-valid execution은 가설 채택과 다르다.
결함·invalid comparison·timeout·OOM·예산 부족·proxy 부적합은 과학적 기각이 아니다.
유효한 negative evidence는 검사한 가정 아래 특정 mechanism을 반박할 수 있다. 전체 family의
기각에는 그 범위의 근거가 필요하다. 배포 overhead가 연구 제약을 위반한다는 증거와 검증 비용은 다르다.
논쟁은 Main의 근거/수정 후 한 번의 bounded re-review로 다룬다. 미해결이면 두 rationale를 남겨
DEFERRED로 보존한다. 끝없는 논쟁이나 자동 overrule을 하지 않는다.

## 성공과 중단

ACCEPTED는 사용자의 다음 선택에 필요한 사전 근거/품질 기준을 만족했다는 뜻이다.
독립 QA-valid 근거와 Supervisor rationale, mechanism/lineage 중복 제거가 필요하다.
이름 변경·hyperparameter 변형으로 quota를 채우지 않는다. 최종 실규모 성능/논문 novelty/채택 증명은 아니다.
Proxy-supported, theory-supported, decisive-evidence-deferred를 구분한다. 결정적 검증을 미룬 후보는
처음 목표가 그 evidence class를 허용한 경우에만 quota에 포함하며 proxy-supported로 포장하지 않는다.
Monk에서 문헌상 novelty는 UNVERIFIED이며 자동 실패나 최초성 주장이 아니다. 모든 역할에 같은
monk 조사 경계를 전달한다. 우연한 방법론 노출·기존 지식·수학 자료의 확인 범위를 보존한다.

처음 ultimate-goal predicate의 **모든 조건**을 확인해야 GOAL_MET이다. 예컨대 다른 방향3개가
목표이면 기준 충족+중복 제거된3개가 필요하다. 후보수만 맞거나 예산이 끝났다고 성공이 아니다.
유한 trial/retry/review/stagnation 한도, 사용자 pause/stop, serious integrity failure,
허용된 유용한 진전 불가능에 도달하면 목표 미달을 명시하고 checkpoint한다.
짧은 shortlist·기각 mechanism의 교훈·pending user-run 검증·잔여 불확실성을 전달한다.
사용자가 최종 테스트 대상을 고른다. 자원 경계 때문에 검증이 남은 후보는 NEEDS_USER_RUN이다.

## 실행과 자원 경계

USER_ONLY heavy run은 goal에서도 유지한다. 모델/데이터 준비·import·초기화·저장·cleanup·실패·
재시도·병렬 합계를 포함한다. 할당 예산은 무거운 작업의 실행 허가가 아니다. 비용 미확인도 시작하지 않는다.
필요하면 실제 entrypoint/옵션·환경·출력·판정 기준·추정 자원과 불확실성을 RUNBOOK에 남긴다.

`.codex/tools/goal_guard.py`는 stdlib **기록/검증 도구이며 실행 runner나 OS sandbox가 아니다**.
Config command 실행, project import, 모델 로딩, scheduler/API, job control을 하지 않는다.
한도 숫자와 예약 성공은 권한·강제의 증거가 아니다. 별도 과제의 bounded executor를 QA가
contract/hash/capability 근거로 검수하면 그 경로로 light proxy 반복이 가능하다. 필수 한도 강제가
미지원이면 해당 실험은 NEEDS_USER_RUN이다. Executor가 없는 상태에도 독립적으로 허용된
연구·수학 분석·리뷰는 finite calls/time 안에서 진행할 수 있다. 모든 연구를 사용자 실행으로 돌리지 않는다.
실험을 안 하는 순수 연구 목표라면 실제 proxy 실행 gate는 사용하지 않으며, 기준과 평가 근거를
명시한 계약을 사용한다. 본 도구는 Codex가 없는 동안 자율 실행하거나 provider billing을 강제하지 못한다.

Main의 작업/각 subagent turn/교체/검토도 유한 agent-call/time 예산에 넣는다. Token/cost cap은
선택 사항이며 요구한 cap을 관측/강제하지 못하면 dependent automatic work를 진행하지 않는다.
Self-reported capability boolean은 실제 강제 증명이 아니다. Ledger는 기록한 이벤트만 계측한다.
준비/preflight에 필요한 agent/CPU 비용도 별도 예약에 포함하고 무상 반복으로 제외하지 않는다.

## Helper 사용과 재개

Python3.11+가 이미 있는 환경에서 사용한다. 새로운 환경이나 패키지를 설치하지 않는다.
아래 경로는 실제 과제 경로로 바꾼다. 이 명령은 작은 metadata만 읽고 쓴다.

```sh
python3 .codex/tools/goal_guard.py validate --config /project/research/GOAL_CONFIG.md
python3 .codex/tools/goal_guard.py init --config /project/research/GOAL_CONFIG.md --state /project/research/goals/g1
python3 .codex/tools/goal_guard.py reserve --config /project/research/GOAL_CONFIG.md --state /project/research/goals/g1 --record /project/research/plan.json
python3 .codex/tools/goal_guard.py finish --config /project/research/GOAL_CONFIG.md --state /project/research/goals/g1 --attempt toy-001 --record /project/research/usage.json
python3 .codex/tools/goal_guard.py progress --config /project/research/GOAL_CONFIG.md --state /project/research/goals/g1 --meaningful no --evidence review-R2
python3 .codex/tools/goal_guard.py status --config /project/research/GOAL_CONFIG.md --state /project/research/goals/g1
```

`init`가 freeze이며 부모는 이미 존재해야 한다. 기존 state는 덮어쓰지 않는다. 각 RESERVE는
startup+work+cleanup+save upper bound를 먼저 차감한다. Agent/review/experiment 종류를 구분한다.
FINISH는 unknown(null)을0으로 바꾸지 않고 각 누적 차원에서 max(reserved, actual)을 부과한다.
실패/재시도도 같은 비용을 지며 overshoot는 breach로 남겨 새 예약을 차단한다. Pending 예약은
계속 차감·동시 점유하며 미해결 시도를 재개라는 이름으로 다시 실행하지 않는다.
`progress`는 의미 있는 결정의 근거 또는 정체를 기록한다. 정체 카운트는 main의 기록에 의존한다.
실제 progress가 없는데 counter만 초기화하지 않는다. Helper는 연구 품질·목표 달성을 계산하지 않는다.

Config 전체 byte hash, contract와 작은 explicit evaluator/baseline file hash를 묶는다.
변경된 코드에 옛 결과를 재사용하지 않는다. 입력/계약은256KiB, manifest file은512KiB×최대32개,
ledger는4MiB로 제한한다. 대형 data/model은 기존 manifest ID를 사용한다. Symlink·traversal 쓰기 금지.
Lock 충돌, 일부만 기록된 ledger, hash 불일치는 중단하며 자동 복구/삭제/수정하지 않는다.
이는 우발적 충돌·손상 검출이며 악의적 변경을 막는 security boundary나 reviewer 독립성의 증명이 아니다.

Init 시 wall clock부터 pause/interrupt를 포함한다. Compaction·thread·retry·계약 개정으로 예산을
초기화하지 않는다. Helper에는 budget amendment 기능이 없다. 개정이 필요하면 사용자 승인과
이전 소모/예약·시작시간을 보존한 검토된 migration이 별도 필요하며, 새 init로 우회하지 않는다.
Checkpoint에 config/contract/ledger/evidence revision과 pending attempt를 남기고 재개 때 대조한다.
Executor가 관리할 수 있는 것은 자신의 goal job뿐이며 사용자 job은 중단·변경·재시작하지 않는다.

Templates: `research/_templates/{GOAL_CONFIG,PROXY_CONTRACT,CANDIDATE,GOAL_PROGRESS}.md`.
작성 예시는 `.codex/GOAL_EXAMPLE.md`이며 실행 허가가 아니다. 실험 SPEC/REPORT/RUNBOOK은
기존 `experiments/_templates/`를 재사용한다. 무거운 실제 검증은 NOT_RUN/USER_ONLY로 남긴다.

단일 plan의 초과나 일시적 concurrency 부족은 helper의 `scope=ATTEMPT` 예약 거부다.
그 후보의 필요한 실험은 NEEDS_USER_RUN/보류로 남기고, 잔여 예산 안의 다른 유용한 연구를 이어간다.
이는 goal 전체 종료가 아니다. `scope=GOAL`은 elapsed/attempt/stagnation 소진·breach 등
전체 경계이며 과학적 성공을 뜻하지 않는다. 비교 의미를 훼손하는 임의 축소는 하지 않는다.

Guard metadata는 init 전에 `METADATA_RESERVATION` bytes를 디스크 예산에서 보수적으로 예약한다
(3×256KiB snapshot 상한 +4MiB ledger +64KiB bookkeeping). 이보다 작은 disk cap/0은
디렉터리를 만들기 전에 거부한다. 이후 plan의 disk_bytes는 이 metadata 외 신규 쓰기 상한이다.
Filesystem physical block 사용량을 자동 측정하지 않으므로 실제 disk 강제는 외부 executor 검수 대상이다.
Local 실험 CPU work는 duration×allocated cores, GPU work는 duration×device count 이상 예약한다.
Agent/review의 원격 LLM 작업은 local CPU/GPU 소비와 다르다. Local 자원 사용이 없으면0으로,
agent_calls/reviews와 elapsed 및 선택한 token/cost로 기록한다. 가짜 local RAM/CPU를 채우지 않는다.
모든 수치는 유한·비음수이며 구현상 최대10^18이다. Remote provider 자원을 계측했다고 주장하지 않는다.
