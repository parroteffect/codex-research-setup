# Frozen proxy contract — agent 작성, 사용자 목표/권한 변경은 사용자 결정

DRAFT. 빈칸을 실제 코드/자료와 사전 합의로 채운다. 하나의 TOML block을 사용한다.
모든 field는 필수다. `files`에는 evaluator/baseline의 **작은 명시적 소스 파일**만 넣는다.
최대32개, 각512KiB; raw data/model을 hash하거나 디렉터리를 재귀 탐색하지 않는다.
큰 데이터는 이미 있는 manifest ID/version으로 식별한다. SHA256은 과학적 진실의 증명이 아니다.

```toml
revision = ""
objective = ""
scope = ""
validity_envelope = ""
baseline = ""
evaluator = ""
data_manifests = []
splits = ""
dev_policy = ""
heldout_policy = ""
metrics = ""
aggregation = ""
comparison_conditions = ""
acceptance_gates = ""
allowed_candidate_changes = ""

[[files]]
path = ""
sha256 = ""
```

Freeze 전에 확인할 내용:

- `baseline/evaluator`: exact version, entrypoint, 필수 옵션, baseline 재현/독립 정답 예제.
- `splits/dev_policy/heldout_policy`: fit/tune/DEV 구분, 반복 DEV 노출·multiplicity,
  confirmation 접근 횟수/조건. 본 데이터를 미사용 TEST로 부르지 않는다.
- `metrics/aggregation/comparison_conditions`: 단위·분모·정규화·seed·선택규칙,
  precision·storage bytes·runtime overhead·모델/입력 조건을 고정한다.
- `acceptance_gates`: 사용자 success criteria에 대응하는 근거 기준과 후보 중복 판별.
- `validity_envelope`: 무엇을 판별할 수 있고 어떤 가설에는 부적합한지 명시한다.
- QA: contract/code/config/data와 독립 기준의 일치, thread·requested/resolved effort·근거 링크.
- 외부 bounded executor: exact code/config hash, 검수된 실행 경로·자원별 capability 증거,
  초기화/cleanup/저장 포함 사전 upper bound, 미지원 한도, 단일 실행자와 job ownership.
  Numeric config만으로 강제됐다고 쓰지 않는다. 미지원 필수 한도면 NEEDS_USER_RUN.

Candidate 코드/hyperparameter는 허용 범위 안에서만 바꾼다. Evaluator/data/gates 변경은 새 revision,
필요한 사용자 승인, 기존 결과와 잔여 예산 보존이 필요하다. 새 ledger로 예산을 초기화하지 않는다.
