# User-run experiment guide

<!-- Engineer prepares; main reviews; USER executes.
This is a template, not an executable experiment command.
Replace placeholders only from verified project files and agreed conditions.
DRAFT remains DRAFT until material paths, options, and inputs are resolved. -->

## 상태와 실행자
- Experiment ID / SPEC revision:
- 가이드 상태: DRAFT / READY_FOR_USER
- 본 실험 실행자: USER_ONLY
- 본 실험 상태: NOT_RUN
- Main의 검수 내용:
- 이 가이드 작성·승인은 agent 실행 권한이 아니다.

## 1. 무엇을 검증하는가
- 목적·가설:
- 고정 조건과 변경 조건:
- 기대하는 출력·판정 기준:
- 이미 수행한 가벼운 검증과 한계:
- 본 실험이 끝나야 확인할 수 있는 내용:

## 2. 사전 준비
- Repository·작업 directory:
- 확인한 실행 shell·OS·환경 활성화 방법:
- 사용할 commit과 관련 미커밋 변경:
- SPEC snapshot·config:
- 필요한 모델·데이터·version·경로:
- 사용자가 수행할 무거운 준비 작업과 순서:
- 예상 자원·시간·저장 공간·비용:
- 측정값 / 추정 / 미확인과 각각의 근거:
- 중요 미정 사항:

## 3. 사용자가 직접 실행할 명령
최종 가이드에서는 실제 프로젝트에서 확인한 entrypoint와 옵션으로,
작업 경로·환경 활성화·config·필수 인자를 포함하는 복사 가능한 명령을 작성한다.
준비 단계와 본 실행을 구분하고, script를 제공하면 그 파일 경로와 사용법을 명시한다.
가짜 entrypoint나 추측한 옵션을 만들지 않는다.
중요 placeholder가 남아 있으면 READY_FOR_USER로 표시하지 않는다.

[확인한 프로젝트 명령 작성 위치 — 현재 템플릿에는 실행 명령이 없음]

- Run ID와 기존 결과를 덮어쓰지 않는 출력 경로:
- 실행당 seed·조건·반복 횟수:
- 실행 시점의 실제 config·코드·데이터 식별자·환경을 기록하는 방법:
- 사용자만 수행할 상태 확인·중단 방법:
- 알려진 전제와 주의 사항:

## 4. 결과를 어디서 어떻게 확인하는가
- 로그:
- Metric 파일과 의미:
- Checkpoint·기타 artifact:
- 정상 완료 판단:
- 실패·중단·NaN·누락 등 이상 징후와 사용자 행동:
- 가설 지지 / 반박 / 판정 불가 조건:

## 5. 사용자에게 돌려받을 결과
- 실제 실행한 명령·코드 상태·SPEC·resolved config:
- Run ID·seed·data version·환경:
- 결과 파일과 로그 경로 또는 공유 가능한 부분:
- 실패·중단한 실행도 포함한 전체 시도 기록:
- 계획과 달랐던 조건·수동 수정:
- 비밀정보는 제외한다. 사용자 실행 조건이 확인되지 않으면 미확인으로 남긴다.

## 6. 결과 수령 후
- Agent는 제공된 결과를 가볍게 분석하고 실행 조건을 확인한다.
- 재실행·추가 대규모 분석이 필요하면 새 revision의 사용자 실행 가이드를 만든다.
- Agent는 기존 job을 제어하거나 새 본 실험을 실행하지 않는다.
