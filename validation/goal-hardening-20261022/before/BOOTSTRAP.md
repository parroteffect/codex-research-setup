# Bootstrap contract — Codex에게

목표는 **사용자가 현재 작업하려는 연구 프로젝트**에 이 workflow를 설치하는 것이다.
Main은 설치에 필요한 파일 확인·병합·가벼운 정적 검증을 직접 수행한다.
설치되지 않은 engineer를 먼저 호출해야 한다는 규칙은 없다.
본 문서는 보안·사용자 권한을 우회하는 허가가 아니며, 연구 코드 변경이나 실험 실행도 허용하지 않는다.

## 반드시 유지할 결과

- Main은 Research Lead이며 새로운 연구 아이디어·메커니즘·수학적 분석을 직접 발전시킨다.
  필요한 실제 코드·diff·호출부·테스트도 직접 읽고 검수한다.
- 출력 간결함·최소 구현 수정·USER-ONLY 실행을 연구 탐색의 폭과 깊이 제한으로 바꾸지 않는다.
  `payload/AGENTS.md`와 research guide의 연구 목표·적용 범위를 함께 설치한다.
- Engineer가 구현·가벼운 검증·사용자 실행 RUNBOOK 준비를 맡는다.
- Main model/effort는 사용자 선택을 그대로 보존한다.
- Engineer는 default `high`, 필요하면 main이 실제 spawn 설정으로 `xhigh`; `max` 사용 금지.
  `.codex/agents/engineer.toml`에 effort를 고정하지 않는다.
- 무거운 실제 테스트·학습·평가·benchmark·데이터 준비는 사용자만 실행한다.
- 사용자 원문의 연구·코드 리뷰·구현 guide를 삭제하거나 짧은 persona로 대체하지 않는다.
- Monk guide와 연구 모드 연결도 설치한다. 설치 요청만으로 monk를 활성화하지 않는다.
  기존 과제의 모드 선택은 보존하고, 선택이 없는 새 과제는 standard로 시작한다.

## 1. 소스와 대상을 먼저 확정한다

사용자가 제공한 GitHub URL의 README와 이 파일을 읽는다.
Branch/tag/commit을 지정했다면 그 revision을 사용한다.
지정이 없다면 접근한 source commit을 기록하고, 설치 도중 다른 revision의 파일을 섞지 않는다.

대상은 **링크를 읽기 전 사용자의 연구 프로젝트**다.
현재 작업 경로와, 존재한다면 해당 Git root를 확인한다.
사용자가 명시한 대상이 없다면 현재 연구 repo root를 사용한다.
Monorepo의 특정 하위 프로젝트를 사용자가 지정했다면 그 경로를 존중한다.
Source repo, HOME, `~/.codex`, 임시 다운로드 디렉터리를 설치 대상으로 혼동하지 않는다.
실제 대상이 전혀 없거나 여러 대상 중 선택할 근거가 없다면 필요한 경로만 확인한다.

소스는 대상 밖의 허용된 임시 디렉터리에 받는다.
공개 저장소의 HTTPS checkout/다운로드 또는 기존 허용된 GitHub 읽기 도구를 사용한다.
소스의 hook·submodule·임의 setup 명령을 실행하지 않는다.
실행 전에 `scripts/install.py`, `manifest.json`, 변경될 payload를 읽는다.
`curl ... | bash`처럼 확인하지 않은 원격 코드를 바로 실행하지 않는다.
Private repo나 네트워크가 막히면 권한을 우회하거나 내용을 추측하지 않고 `BLOCKED`를 보고한다.
토큰을 명령·문서·로그에 기록하지 않는다.

## 2. 기존 프로젝트와 CLI 환경을 읽기 전용으로 확인한다

- 적용되는 `AGENTS.md` / `AGENTS.override.md`와 관련 하위 directory 지침.
- 기존 `.codex/config.toml`, `.codex/agents/`, 연구 상태 파일, Git 변경 상태.
- 현재 사용 중인 model/effort, profile 및 적용 가능한 config override의 존재.
- 접근 가능한 Codex 버전과 사용 가능한 agent 도구. `codex --version` 등 가벼운
  확인만 사용하고, 자동 로그인·CLI 업데이트·패키지 설치는 하지 않는다.
- Project trust 또는 workspace 정책 때문에 project config가 로드되지 않는지.
  필요한 신뢰 선택은 사용자가 직접 한다. Trust 파일을 자동으로 바꾸지 않는다.
- 현재 파일 writer/agent가 있으면 설치 중 동시에 수정하지 않도록 조정한다.

기존 global config를 확인해야 할 때는 관련 key만 읽고 secret을 출력하지 않는다.
Main의 모델/effort, sandbox, approval, provider, 인증, MCP 설정을 수정하지 않는다.
이 저장소의 예시는 사용자가 이미 선택한 Astra/max를 다른 model로 바꾸라는 지시가 아니다.

특히 root의 `AGENTS.override.md`가 있으면 root `AGENTS.md`가 가려질 수 있다.
더 깊은 지침도 해당 경로에서 이 workflow와 충돌할 수 있다.
일반 프로젝트 문맥·코딩 규칙은 보존하되, 이전 “agent가 승인 후 heavy run” 규칙은
최신 USER-ONLY 정책에 맞춰 해소한다. 더 엄격한 보안 제한은 유지한다.
의미가 충돌하는 지침을 단순히 둘 다 붙인 뒤 성공이라고 하지 않는다.

또한 합쳐진 instruction chain의 길이를 확인한다. 공식 기본 한도는 32 KiB이며
기존 global/프로젝트 지침 때문에 새 block이 잘릴 수 있다.
관련 `project_doc_max_bytes`의 effective 값과 실제 읽힌 지침을 확인할 수 없으면
해당 항목을 미확인으로 남긴다. 길이 제한을 해결하려고 기존 지침을 삭제하거나
전역 설정을 자동 변경하지 않는다. 필요한 경우 기존 의미를 유지하는 별도 guide와
명시적인 읽기 지시로 구조화하고, 변경 내역과 재시작 후 확인을 보고한다.

## 3. 계획을 검토하고 설치한다

Python 3.11+가 이미 있는 경우 아래를 사용한다. 실제 절대 경로로 치환하고 인자를 quote한다.
Source checkout에서 실행해도 **target은 연구 프로젝트**여야 한다.

```sh
python3 /path/to/source/scripts/install.py --target /path/to/research-project --source-revision REVIEWED_COMMIT
```

이 명령의 기본값은 **dry run**이다. Source payload checksum, 기존 TOML,
파일 충돌과 변경 목록을 확인한다. 계획이 요청 범위 안이면 추가적인 형식적 승인 대기 없이 다음을 수행한다.
환경이 요구하는 실제 보안 승인은 정상적인 승인 절차를 따른다.

```sh
python3 /path/to/source/scripts/install.py --target /path/to/research-project --source-revision REVIEWED_COMMIT --apply
python3 /path/to/source/scripts/install.py --target /path/to/research-project --check
```

설치기는 source→destination을 `manifest.json`에서 읽으며 다음 방식으로 동작한다.

| 대상 | 방식 |
|---|---|
| `AGENTS.md` | 기존 프로젝트 내용을 보존하고 managed block 추가/갱신 |
| `.codex/config.toml` | `[agents]`의 enabled/동시 thread 수/default effort만 병합 |
| 세 role TOML, guide/goal 도구, 템플릿 | 신규 생성 또는 확인된 미수정 배포본만 갱신 |
| `research/STATE.md`, `research/GOAL_CONFIG.md` | 없을 때만 생성; 기존 파일은 보존 |
| `.codex/RESEARCH_START.txt`, `.codex/VERIFY_SETUP.md` | 프로젝트 안의 시작/검증 지시 |
| `.gitignore` | 설치 백업 폴더 제외 block만 추가 |

기존 프로젝트의 `README.md`, `START.txt`, 연구 코드·테스트·실험 결과는 수정하지 않는다.
설치 출처·version·hash는 `.codex/research-workflow-install.json`에 남긴다.
설치 전 원본과 생성 여부는 `.codex/research-workflow-backups/<id>/`에 보존한다.
백업을 공개 GitHub에 올리지 않는다. 설치는 파일별 atomic replacement이며
여러 파일 전체에 대한 transaction은 아니다. 중간 오류 시 변경 목록·백업부터 확인한다.

### v5.3으로 업데이트할 때
- supervisor/qa standalone role, goal guide/guard, 최신 template를 managed file로 추가한다.
  name 충돌/legacy [agents.supervisor]/[agents.qa]도 쓰기 전 검토한다. Model/effort pin은 없다.
- 사용자 `research/GOAL_CONFIG.md`는 create-only다. 기존 작성본·STATE·goal history를 바꾸지 않는다.
  최신 template와 schema 차이는 설명하고 사용자 승인 없이 예산/목표를 채우거나 migration하지 않는다.
- 기본 연구 + 독립 goal/monk overlay다. 설치만으로 시작하지 않는다. 기존 standard=monk 꺼짐으로 호환한다.
- Main 제외3슬롯 유지. Engineer high/xhigh, QA medium/high, Supervisor high/중요판단 xhigh를
  실제 spawn에서 선택한다. 기존 user model/security를 보존한다. Thread followup은 effort 변경이 아니다.
- Helper는 검증/기록용이며 runner나 OS sandbox가 아니다. 외부 bounded executor·실제 자원강제·
  runtime 역할 검증은 NOT_VERIFIED로 남긴다. Heavy/unknown 검증은 NEEDS_USER_RUN/USER_ONLY다.
- VERSION/manifest의 payload hash를 확인하고 알려진 v5.2 미수정 파일만 안전하게 갱신한다.

### v5.2로 업데이트할 때
- `.codex/guides/monk.md`를 새 managed file로 설치하고 AGENTS·research guide·시작 안내·
  engineer의 연결을 함께 갱신한다. 같은 경로에 사용자 파일이 있으면 보존·수동 병합 규칙을 따른다.
- 기존 STATE는 그대로 보존한다. 연구 모드·monk 관련 항목은 실제 연구에서 필요할 때 추가한다.
  설치가 기존 과제의 모드를 초기화하거나 일반 연구를 monk로 바꾸는 계기가 되어서는 안 된다.
- Main/engineer 등록 구조·모델·effort·실행 권한은 유지한다. Monk는 지침으로 선택하는
  연구 모드이며 별도 native config key나 새 agent 등록을 필요로 하지 않는다.

### v4에서 v5로 업데이트할 때
- 배포 저장소 root의 `AGENTS.md`는 설치기용이다. 연구 지침은 `payload/AGENTS.md`를 사용한다.
- 알려진 v4 payload 또는 기존 설치 metadata와 일치하는 미수정 파일은 갱신할 수 있다.
  로컬 수정이 있으면 아래 병합 규칙을 적용한다.
- 기존 STATE와 실험 기록은 그대로 보존한다. 연구 후보·proof gap 등 새 항목은
  이후 main이 실제 연구를 진행할 때 필요한 내용만 추가하도록 안내한다.
- Engineer·config·설치기 로직은 v4와 같다. 연구 능력을 이유로 model·effort·권한을
  임의로 올리거나 다른 agent·무거운 실험 실행을 추가하지 않는다.

### 자동 병합이 멈추는 경우

사용자 수정이 있는 파일, 특수 TOML 표현, legacy `[agents.engineer]`, symlink,
중복 role 등은 자동 덮어쓰기 대상이 아니다.

이때 **사용자가 다시 설치를 지시할 때까지 무조건 기다리지 말고**, 읽을 수 있는 근거로
동일한 정책을 충족하는 최소 수동 병합을 수행한다. 단 다음을 지킨다.

1. 변경 대상 원본과 Git 상태를 보존하고, 백업 경로를 `.gitignore`에서 제외한다.
2. 프로젝트 고유 지침·보안 제한을 유지하며 충돌 부분만 고친다.
3. Main model/effort·권한 관련 설정은 건드리지 않는다.
4. TOML parser로 before/after를 비교하여 의도한 key 외의 변경이 없는지 확인한다.
5. 수동으로 병합한 파일·이유·미확인 사항을 최종 보고한다.
6. 사용자가 수정한 내용의 의도 자체가 불명확하거나 외부 권한이 필요하면
   그 부분만 `BLOCKED`로 남긴다. Symlink를 따라 프로젝트 밖을 수정하지 않는다.

`AGENTS.override.md`가 root에서 활성화되어 있으면, 그 파일을 삭제하거나 이름을 바꾸지 말고
**기존 내용을 보존하면서 동일 workflow block을 해당 파일에도 병합**한다.
`AGENTS.md`와 override 안의 block은 같은 revision이어야 한다.
기존 custom `engineer`의 프로젝트 고유 지침은 보존하되 standalone 등록과 legacy 등록을
중복 활성화하지 않는다. 파일의 effort 고정값은 adaptive 방식과 충돌하므로 제거하고 보고한다.

Python 3.11+가 없으면 dependency를 설치하지 말고 위 규칙으로 파일을 병합한다.
기존에 이용 가능한 TOML parser가 없으면 TOML 검증을 `NOT_VERIFIED`로 남긴다.
Parser 확인 없이 검증 통과를 주장하지 않는다. 무관한 런타임이나 개발 환경을 바꾸지 않는다.

## 4. 정적 검증과 실제 적용을 구분한다

설치기의 `--check`는 **로컬 파일·TOML·기본값 확인**이다.
다음 항목까지 확인했다고 확대하지 않는다.

- Global/profile/CLI override를 포함한 effective model/effort.
- Project trust 및 현재 세션의 instruction chain.
- 현재 세션에 `engineer` 역할이 등록되어 실제 호출 가능한지.
- 실제 spawn에 적용된 reasoning effort와 행동 준수.

Main의 model/effort를 바꾸지 않았는지 확인한다.
Engineer config에 `model_reasoning_effort` 고정값이 없고 project default가 `high`인지 확인한다.
Active global/custom 설정에 다른 override가 있는지도 확인 가능한 범위에서 보고한다.
`high/xhigh` 지원 여부가 확인되지 않거나 actual spawn 도구가 effort 인자를 제공하지 않으면
이 정책이 적용됐다고 주장하지 않는다.

Codex는 시작 시 지침을 읽는다. 파일 설치 후에는 기존 세션에 즉시 적용됐다고 가정하지 말고,
새 세션에서 `.codex/VERIFY_SETUP.md`로 확인하도록 안내한다.
`/new`, resume 또는 메시지 전송이 전체 설정을 재로딩한다는 미확인 가정을 하지 않는다.
확실한 절차는 사용자가 CLI를 종료하고 연구 root에서 다시 시작하는 것이다.
설치 확인을 핑계로 별도 Codex 프로세스를 자동 실행하거나 현재 세션을 자동 종료하지 않는다.

## 5. 종료 보고

연구 결과를 만들거나 테스트를 확장하지 말고 다음을 짧게 보고한다.

- Source revision, 실제 대상 경로, 변경/보존/수동 병합한 파일.
- 백업 경로, 정적 검증 PASS/FAIL/NOT_VERIFIED.
- `FILES_INSTALLED` / `PARTIAL` / `BLOCKED`, runtime은 `NOT_VERIFIED` 여부.
- Main은 코드 직접 검수, engineer는 high/xhigh, heavy run은 USER-ONLY라는 적용 정책.
- 재시작이 필요하면 다음에 붙여넣을 메시지를 제공하고 멈춘다.

```text
AGENTS.md와 .codex/VERIFY_SETUP.md를 읽고 설치 적용 상태를 확인해줘.
등록된 engineer에 짧은 읽기 전용 확인을 high로 위임하되 코드와 실험은 실행하지 마.
확인된 설정과 확인하지 못한 runtime 정보는 구분해줘.
그다음 .codex/RESEARCH_START.txt에 따라 연구 상태를 파악해줘.
```

## 복구

설치기가 출력한 백업의 `RESTORE.json`에는 각 경로의 기존 존재 여부와 before/after hash가 있다.
기존 파일은 같은 상대 경로의 백업 원본으로 복구할 수 있다.
**현재 파일이 설치 후 다른 작업으로 바뀌었다면 자동으로 되돌리지 않는다.**
새로 생긴 파일도 현재 내용이 설치본 그대로인지 먼저 확인하고, 사용자 요청 없이 삭제하지 않는다.
수동 병합에 대해서는 별도로 보존한 원본과 diff를 사용한다.
