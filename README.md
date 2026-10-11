# Codex Research Workflow

**Main = Research Lead · Engineer = 구현/가벼운 검증 · 무거운 최종 실험 = 사용자 직접 실행**

이 저장소는 연구 코드가 아니라, **현재 연구 프로젝트에 설치하는 Codex 지침과 설정 패키지**입니다.
Main의 model/effort는 사용자가 관리합니다. Engineering은 기본 `high`,
깊은 추론이 필요한 작업은 main이 spawn 시 `xhigh`를 선택합니다.
Main은 소스 코드·diff·호출부·테스트를 직접 읽고 검수합니다.
연구에서는 새로운 문제·방법·메커니즘과 핵심 수학적 분석을 직접 발전시킵니다.

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
| `payload/` | 설치 대상 AGENTS.md, engineer, 세 guide, 상태·실험 템플릿 |
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

v5는 v4의 Codex 설정·등록 형식을 변경하지 않습니다. 특정 로컬 CLI 버전에서의 성공을 보장하지 않습니다.
이번 연구 지침 설계에서는 아래 공식 안내도 참고했습니다.
- [Astra prompts and decision boundaries](https://learn.chatgpt.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [Reasoning prompting](https://developers.openai.com/api/docs/guides/reasoning-best-practices)
- [Concise AGENTS.md and task-specific guides](https://learn.chatgpt.com/guides/best-practices)

이 문서들은 일반적인 지침 설계의 근거이지 이 패키지의 연구 성능 개선 증거가 아닙니다.
프롬프트가 잠재력을 몇 % 사용하게 한다거나 novel한 결과를 보장한다고 주장하지 않습니다.
설치기의 정적 성공은 Codex runtime·행동 준수의 검증이 아닙니다.
USER-ONLY와 `high/xhigh` 허용 범위는 지침이며, GPU 접근이나 effort를 기술적으로 차단하는 sandbox/allowlist는 아닙니다.
