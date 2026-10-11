# Fresh-session setup verification

이 문서는 연구 프로젝트 root에서 **재시작한 Codex main**이 수행하는 작은 설치 확인이다.
설치 파일의 존재와 실제 runtime 적용을 구분한다.
확인 작업은 사용자 코드 실행·모델 로딩·학습·평가를 포함하지 않는다.

## Main의 확인
1. 실제로 적용되는 AGENTS.md와 override, 프로젝트 config, engineer 역할 파일을 읽는다.
   전역/profile/CLI override는 관련 key만 확인하고 secret을 출력하지 않는다.
2. Main model/effort는 사용자의 기존 선택을 유지한다. 이번 검증을 위해 변경하지 않는다.
3. 사용할 수 있는 실제 agent 도구에서 `engineer` 등록과 effort 선택 방법을 확인한다.
   등록되지 않았거나 도구가 해당 선택을 지원하지 않으면 그 항목은 BLOCKED/NOT_VERIFIED다.
4. 사용자가 이 문서의 검증을 요청했다면 아래 읽기 전용 작업을 **한 번만** high로 위임한다.
   이는 작은 agent 호출 비용이 드는 확인이며 heavyweight 연구 테스트가 아니다.

## 연구 지침의 적용 범위
- Main은 `.codex/guides/research.md`를 읽고 연구 발굴·아이디어 발전·수학적 분석이
  자신의 책임임을 확인한다. 간결함은 설명, 최소 수정은 구현, USER-ONLY는 무거운 실행에 적용한다.
- 연구 guide를 읽었다는 보고는 로딩 확인일 뿐 연구 품질·novelty·수학적 정확성의 검증이 아니다.
  이 설치 확인을 위해 연구 아이디어를 억지로 생성하거나 별도 평가 실험을 실행하지 않는다.

## Engineer에 보낼 작업
- Mode: inspect. 파일 수정·코드 실행·추가 agent 생성 금지.
- Read: AGENTS.md, .codex/agents/engineer.toml.
- Return: (a) heavy final tests의 실행 주체, (b) main의 직접 코드 읽기/검수 권한,
  (c) 명세 변경의 결정 주체를 짧게 답하고 해당 파일/절을 가리킨다.
- Effort는 위임 문자열이 아니라 main이 **실제 spawn 설정**에서 high로 선택한다.

## 판단
- Main이 실제 engineer spawn/결과 수신을 확인했으면 delegation 확인으로 기록한다.
- 실제 호출 metadata나 도구 반환에서 effort가 확인되면 관찰된 적용값을 기록한다.
- 도구에 high를 보냈지만 최종 resolved effort가 보이지 않으면
  `requested=high; resolved=NOT_VERIFIED`라고 적는다.
- Engineer가 “나는 high다”라고 말한 것은 runtime 설정 증거가 아니다.
- xhigh 호출을 수행하지 않았다면 xhigh runtime 검증은 NOT_RUN이다.
  high가 통과했다는 이유로 둘 다 검증됐다고 하지 않는다.
- 짧은 정책 답변은 지침 이해의 제한적인 증거이지, 장기 행동 준수의 보장이 아니다.
- 다른 업무가 없으면 확인용 thread를 정리하고 상태를 짧게 보고한다.

결과는 FILES / DELEGATION / EFFORT / LIMITATIONS로 간단히 정리한다.
설정 실패를 해결하려고 model·권한·trust를 임의 변경하거나 무거운 실험을 실행하지 않는다.
이후 사용자가 연구 시작까지 요청했다면 .codex/RESEARCH_START.txt에 따른다.
