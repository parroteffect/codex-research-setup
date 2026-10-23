# Codex Research Workflow

**Main = Research Lead · Engineer = 구현/가벼운 검증 · 무거운 최종 실험 = 사용자 직접 실행**

이 저장소는 연구 코드가 아니라, **현재 연구 프로젝트에 설치하는 Codex 지침과 설정 패키지**입니다.
Main의 model/effort는 사용자가 관리합니다. Engineering은 기본 `high`,
깊은 추론이 필요한 작업은 main이 spawn 시 `xhigh`를 선택합니다.
Main은 소스 코드·diff·호출부·테스트를 직접 읽고 검수합니다.
연구에서는 새로운 문제·방법·메커니즘과 핵심 수학적 분석을 직접 발전시킵니다.

## v5.3.1: Goal overlay와 독립 Supervisor / QA

연구는 기본 동작입니다. **Goal**은 연구→작은 판별 검증→채택/기각/보강→다음 연구를
사용자의 ultimate goal까지 이어가는 자율 진행 옵션이고, **monk**는 독립적인 조사 제한입니다.
사용자가 `research/GOAL_CONFIG.md`의 한 TOML block을 작성합니다. CLI 문답은 없습니다.
새 양식은 `goal.enabled`, `goal.monk`를 쓰며 기존 standard/monk STATE는 호환합니다.

Main은 발명·깊은 수학적 분석과 직접 검수를 계속 수행합니다. Engineer는 단일 writer,
QA는 비교/evidence 유효성, Supervisor는 기여·근거·목표 적합성을 독립 검토합니다.
Engineer high/xhigh 유지; QA 반복 검토 medium·최초 evaluator/metric/split/수학 검토 high;
Supervisor routine high, 중요한 최종 채택·유망 방향 기각·논쟁적 기각·방향변경·수학 판단 xhigh.
실제 spawn에서 선택하며 model/effort를 role 파일에 pin하지 않습니다.
Main 제외3 subagent 슬롯을 세 역할이 공유합니다. 모든 반복을 full review하거나 xhigh로 만들지 않습니다.

**설정·기록 도구가 포함되며 experiment runner는 포함되지 않습니다.**
Guard는 stdlib로 config 검증·frozen proxy·보수적 budget ledger를 제공합니다.
RAM/VRAM/disk/provider token을 물리적으로 강제하거나 Codex가 없는 동안 실행하지 않습니다.
QA가 검수한 별도 bounded executor가 있을 때만 허용된 light proxy를 자동 반복할 수 있습니다.
Heavy/unknown/over-budget/필수 enforcement 미지원은 NEEDS_USER_RUN이며 과학적 기각이 아닙니다.
그와 독립인 연구/리뷰는 유한 예산 안에서 계속합니다. USER_ONLY heavy 실행은 유지합니다.

처음 목표의 모든 기준, 독립 evidence와 mechanism 중복 제거를 충족해야 GOAL_MET입니다.
예산 종료나 후보수 미달은 성공이 아닙니다. 최종 shortlist는 사용자에게 최종 테스트 선택권을 남깁니다.
Monk에서는 문헌 novelty 미확인을 유지합니다. 반복 DEV 최적값을 독립 confirmation으로 부르지 않습니다.

- [Goal 운영/명령/한계](payload/.codex/guides/goal.md)
- [별도 SETUP 예산·기록](payload/research/_templates/GOAL_SETUP.md)
- [사용자 작성 양식](payload/research/GOAL_CONFIG.md), [proxy 계약](payload/research/_templates/PROXY_CONTRACT.md)
- [작은 설명용 예시](payload/examples/GOAL_EXAMPLE.md)

v5.3.1은 준비 비용을 별도 사용자 SETUP 배정으로 명시합니다. SETUP 예약/준비/QA→완료·artifact
확인→RUN init→RUN 예약 순서이며 RUN TOML/schema1은 그대로입니다. SETUP 기록은 운영상 검수하며
helper가 강제·계측하지 않습니다. 단일 총액은 사용자 승인 분할이 필요하고 deadline/예산을 임의로 늘리지 않습니다.
정체 stop은 이력에서 유지하고 progress 응답은 같은 lock에서 계산합니다. Pending마다 bounded FINISH
공간을 보존하며 metadata 공간 부족과 영구 budget stop을 구분합니다. 상세 한계는 goal guide를 따릅니다.

업데이트는 기존 user config/STATE/goal history를 보존합니다. 새 역할명 충돌·사용자 수정은
자동 덮어쓰지 않습니다. 설치는 goal을 시작하지 않으며 runtime role 활성화는 새 세션에서 별도 확인합니다.

## v5.2: Monk mode (이전 변경)

Main Research Lead가 연구 과제별로 선택하는 `standard` / `monk` 연구 모드를 추가했습니다.
기본은 기존 standard이며, monk는 사용자의 선택으로 활성화합니다.
연구 논의·리뷰·구현·결과 해석이라는 작업 모드와 별개로 유지하고 STATE에서 복원합니다.
별도 monk agent나 Codex 설정 key를 추가하지 않습니다.

Monk의 목표는 **유연하고 기발한 발상과 깊은 수학적 분석으로 영향력 있는 연구의 축과
novelty가 있을 법한 방법론을 발전시키는 것**입니다.
초기 직감·가정의 반전·문제 재정의·먼 수학적 연결·창의적인 결합을 발전시키고,
유망한 후보의 메커니즘·핵심 유도·반례·proof gap을 실제로 검토합니다.
완성된 증명이나 쉬운 구현을 발상의 선행 조건으로 요구하지 않습니다.

- 목표 문제의 관련 방법론 survey는 발표 연도와 관계없이 제한합니다.
  웹·로컬 자료·요약·다른 agent의 보고에도 같은 범위를 적용합니다.
- 수학적 기법·관점·사고·정리·proof 조사는 허용합니다.
  이미 정한 증명의 빈틈뿐 아니라 새로운 수학적 표현을 찾는 탐색에도 사용할 수 있습니다.
- 독립적인 유도와 문헌상 novelty는 별개입니다. 관련 선행연구 대조는 후속 검증으로 남기며,
  사용자가 요청하면 후보 기록을 보존하고 해당 과제를 standard로 전환해 대조합니다.
- Main의 직접 검수, engineer의 high/xhigh, single-writer와 USER-ONLY 실행 경계를 유지합니다.

설치 후 연구 프로젝트에서 다음처럼 사용합니다.

```text
이 문제는 monk mode로 연구하자.
문제: [연구할 질문과 중요한 제약]
```

선행연구 대조를 시작하려면 `이 후보를 이제 선행연구와 비교하자`라고 요청합니다.
대조 없이 일반 연구로 돌아가려면 `이 과제는 standard mode로 전환하자`라고 요청합니다.
모드는 agent가 자동 해제하지 않으며, 같은 과제를 구현으로 넘겨도 engineer에게 전달됩니다.

상세 지침은 [monk guide](payload/.codex/guides/monk.md)에 있습니다.
기존 STATE는 업데이트 시 보존하고 필요한 새 항목만 이후 연구에서 병합합니다.
이 모드는 지침 수준의 정보 사용 정책이며, 완전한 문맥 격리·검색 차단이나
연구 성능·novelty의 향상을 보장하지 않습니다.

## v5.1: 기여를 중심으로 하는 novelty 탐색

새 연구 방향을 만들 때 성공 시 남을 기여와 중요한 한계를 구체화하고,
그 한계를 넘게 할 insight·메커니즘을 발전시키도록 research guide를 보완했습니다.
가까운 선행 대비 차이를 일찍 확인하되, 알려진 요소의 창의적인 결합과
잠재력이 큰 미완성 후보도 발전시킵니다. 기여의 가치와 현재 근거·불확실성은 따로 판단합니다.
AGENTS와 시작 안내에도 연결했고, 새 STATE 템플릿에 기대 기여 항목을 추가했습니다.
기존 STATE는 보존합니다. 고정된 후보 수·사고 절차·novelty 점수는 요구하지 않으며,
이 지침 변경의 실제 연구 성과 개선은 아직 검증하지 않았습니다.

## v5: 능동적인 연구 기여

핵심 변경은 `payload/AGENTS.md`와 `payload/.codex/guides/research.md`입니다.
Main의 목표를 연구 발굴·아이디어 발전·수학적 분석까지 명시하고,
출력 간결함·최소 구현 수정·USER-ONLY 실행을 연구 탐색의 제한과 분리했습니다.
초기 아이디어에서 멈추지 않고 검토 가능한 근거까지 발전시키되,
고정된 아이디어 수나 사고 절차, 근거 없는 novelty·성공률은 요구하지 않습니다.

`payload/START.txt`, `payload/research/STATE.md`와 설치 확인 문서도 연결했습니다.
Engineer·config·설치기 로직과 코드 리뷰·구현 guide·실험 템플릿은 v4와 동일합니다.
기존 STATE는 자동으로 바꾸지 않습니다. 새 연구 항목은 이후 main이 필요할 때
기존 기록을 보존하며 추가합니다.
구체적인 수정 의도와 파일별 변경은 [docs/RESEARCH_UPGRADE.md](docs/RESEARCH_UPGRADE.md)를 참조하세요.

## Codex에게 링크 하나로 설치시키기

**설치할 연구 프로젝트에서 Codex CLI를 실행**하고 다음 메시지를 보내세요.
`<이 저장소의 GitHub URL>`은 실제 URL로 바꿉니다. 저장소 이름은 자유롭게 정해도 됩니다.

```text
<이 저장소의 GitHub URL>

이 저장소의 README.md와 BOOTSTRAP.md를 읽고,
현재 연구 프로젝트에 Research Lead + engineer workflow를 설치해줘.
기존 프로젝트 지침·코드·연구 상태·main의 모델/effort·권한 설정은 보존해.
설정 설치와 가벼운 정적 검증까지만 진행하고, 무거운 테스트·실험은 실행하지 마.
설치 상태와 runtime 적용 여부를 구분해서 보고하고,
재시작이 필요하면 새 세션에 붙여넣을 메시지를 알려줘.
```

**For Codex / 설치를 맡은 agent:** 먼저 [BOOTSTRAP.md](BOOTSTRAP.md)를 읽고 실행하세요.
`payload/`를 통째로 덮어쓰거나 이 배포 저장소 자체를 설치 대상으로 삼지 마세요.
설치 작업은 main이 직접 진행해도 됩니다. 등록 전 engineer를 먼저 호출할 필요는 없습니다.

## 설치 흐름

`링크 읽기 → 대상·기존 설정 확인 → 소스/설치기 검토 → dry run → 안전한 병합 → 정적 검증 → 재시작 후 runtime 확인`

네트워크 접근, 현재 프로젝트에 대한 쓰기 권한, 필요한 보안 승인, 접근 가능한 저장소가 전제입니다.
Private GitHub 저장소는 해당 Codex 환경에서 접근 가능한 인증이 필요합니다.
링크를 읽는 것만으로 파일이 자동 설치되거나 현재 세션에 새 agent가 활성화되는 것은 아닙니다.
CLI 버전·workspace 정책 때문에 지원되지 않으면 이를 `BLOCKED` 또는 `NOT_VERIFIED`로 보고합니다.
설치기가 Python 3.11+를 필요로 하지만, 없으면 Codex가 BOOTSTRAP의 동일한 병합 규칙으로 처리할 수 있습니다.
Python·패키지·Codex 자체를 자동 설치/업데이트하지 않습니다.

## 주요 파일

| 파일 | 역할 |
|---|---|
| `BOOTSTRAP.md` | Codex가 읽고 따르는 설치 절차·충돌 처리·종료 조건 |
| `scripts/install.py` | 네트워크/외부 dependency 없는 설치기. 기본 dry run, `--apply`, `--check` |
| `payload/` | 설치 대상 AGENTS.md, engineer/supervisor/qa, guide와 goal 도구, 상태·실험 템플릿 |
| `payload/.codex/guides/monk.md` | 독립적인 발상·수학적 연구와 과제별 조사 범위·전환 기준 |
| `payload/.codex/VERIFY_SETUP.md` | 재시작 후 실제 등록·위임·effort 확인 절차 |
| `manifest.json` | source→destination, 설치 방식, payload checksum |
| `tests/` | 임시 폴더에서만 실행하는 설치기·갱신·연구 지침 연결 테스트 |

설치 대상에는 `AGENTS.md`, `.codex/config.toml`, `.codex/agents/engineer.toml`,
`.codex/guides/`, `.codex/RESEARCH_START.txt`, `.codex/VERIFY_SETUP.md`,
`research/STATE.md`, `experiments/_templates/` 등이 생깁니다.
연구 프로젝트의 `README.md`는 변경하지 않습니다.

## 보존·업데이트 원칙

- `AGENTS.md`의 기존 프로젝트 지침은 남기고 **managed block**으로 추가합니다.
- `.codex/config.toml`은 `[agents]`의 3개 설정만 병합합니다.
  같은 설정의 legacy alias `max_threads`는 중복 충돌을 피하려고 제거합니다.
  Main model/effort, sandbox, approval, provider 등 다른 설정은 유지합니다.
- 기존 `research/STATE.md`, 실제 `experiments/<id>/`, 코드·테스트·데이터는 덮어쓰지 않습니다.
- 기존 파일 변경 전에 `.codex/research-workflow-backups/`에 백업합니다.
  이 경로를 프로젝트 `.gitignore`에 추가합니다. 백업에는 로컬 설정이 포함될 수 있으므로 공개하지 마세요.
- 이전 설치본과 같은 파일은 갱신할 수 있지만, 사용자가 수정한 파일은 임의로 덮어쓰지 않습니다.
  이런 경우 Codex가 로컬 지침을 보존해 검토·병합하고 변경 내역을 보고합니다.
- Managed AGENTS marker만으로 원본을 인정하지 않습니다. Metadata/block hash가 없어도 현재 payload,
  기록된 block 또는 검증 가능한 pristine legacy 본문과 일치해야 자동 갱신합니다. 출처 미확인 block은
  conflict로 보존하며 원본 백업과 diff를 두고 수동 병합합니다. Metadata를 위조하거나 force로 우회하지 않습니다.
- 같은 상태에 다시 설치하면 중복 block/table을 만들지 않습니다.
- `~/.codex`, 로그인 정보, Git remote, 프로젝트 trust, 권한 설정은 변경하지 않습니다.
  자동 commit/push, 실험 실행, CI/scheduler 제출도 하지 않습니다.

원문 guide의 연구 태도, 단계별 대화형 코드 리뷰, 간결한 phase별 구현과 의미 있는 작은 테스트는 유지했습니다.
단, 이전의 “승인받으면 agent가 무거운 작업 실행” 경로는
**“사용자가 직접 실행하고 agent는 RUNBOOK을 준비”**하는 규칙으로 교체되어 있습니다.

## 재시작 후

새 Codex 세션을 **연구 프로젝트 root**에서 시작한 뒤 아래 메시지를 사용합니다.

```text
AGENTS.md와 .codex/VERIFY_SETUP.md를 읽고 설치 적용 상태를 확인해줘.
등록된 engineer에 짧은 읽기 전용 확인을 high로 위임하되 코드와 실험은 실행하지 마.
확인된 설정과 확인하지 못한 runtime 정보는 구분해줘.
그다음 .codex/RESEARCH_START.txt에 따라 연구 상태를 파악해줘.
```

이 확인은 작은 agent 호출 비용이 발생하며, 무거운 연구 실험과는 다릅니다.
Agent가 자기 effort를 말하는 것만으로 실제 적용값을 검증했다고 간주하지 않습니다.

## 이 패키지를 GitHub에 올릴 때

압축을 푼 **내용물**을 저장소 root에 올려 `README.md`, `BOOTSTRAP.md`, `payload/`가 바로 보이게 하세요.
ZIP 파일 하나만 업로드하지 마세요. `payload/.codex/` 같은 숨김 디렉터리도 포함해야 합니다.
실제 연구 코드·데이터·설치 백업은 이 배포 저장소에 넣지 마세요.
재현 가능한 설치가 필요하면 게시한 commit 또는 release를 지정합니다.

## 공식 문서와 한계

2026-10-11 확인:
- [AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Custom subagents and effort precedence](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

v5.3은 기존 standalone 역할 형식을 유지하고 supervisor/qa를 추가합니다. 특정 로컬 CLI 버전에서의 성공을 보장하지 않습니다.
이번 연구 지침 설계에서는 아래 공식 안내도 참고했습니다.
- [Astra prompts and decision boundaries](https://learn.chatgpt.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [Reasoning prompting](https://developers.openai.com/api/docs/guides/reasoning-best-practices)
- [Concise AGENTS.md and task-specific guides](https://learn.chatgpt.com/guides/best-practices)

이 문서들은 일반적인 지침 설계의 근거이지 이 패키지의 연구 성능 개선 증거가 아닙니다.
프롬프트가 잠재력을 몇 % 사용하게 한다거나 novel한 결과를 보장한다고 주장하지 않습니다.
설치기의 정적 성공은 Codex runtime·행동 준수의 검증이 아닙니다.
USER-ONLY와 `high/xhigh` 허용 범위는 지침이며, GPU 접근이나 effort를 기술적으로 차단하는 sandbox/allowlist는 아닙니다.
