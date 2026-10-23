# Candidate evidence and decision

작은 시도는 같은 파일의 표/행으로 기록해도 된다. 매번 긴 문서를 요구하지 않는다.

- ID / revision / parent lineage / mechanism family:
- 성공하면 남는 기여 / 중요한 제약 / 구체적 메커니즘:
- 정의·가정·유도·반례 / 증명과 conjecture / proof gap:
- 경쟁 설명과 최소 판별 질문 / proxy envelope 적합성:
- SPEC·code/config·contract hash / data manifest·seed / attempt IDs:
- 실행: NOT_RUN / RUNNING / VALID / INVALID / OOM / TIMEOUT / INFRA_ERROR / NEEDS_USER_RUN
- 근거 class: proxy-supported / theory-supported / decisive-evidence-deferred
- 관찰과 해석 / DEV 노출 횟수 / confirmation 접근 기록:
- 독립 QA: VALID / INVALID / UNVERIFIED, 실제 reviewer thread·revision·근거:
- Supervisor: PROPOSED / REFINE / REJECTED / ACCEPTED / DEFERRED, rationale·사용자 기준 대응:
- Novelty: 확인한 범위 / UNVERIFIED (monk 후속 대조 대기):
- 채택 quota에 포함 가능한지 / 중복과 다른 작동 메커니즘:
- 기각의 적용 가정·범위 / 배운 점 / 재검토 조건:
- 다음 판별 행동 / NEEDS_USER_RUN이면 experiments/<id>/RUNBOOK.md 링크:

결함·실행 실패·비용·부적합 proxy는 과학적 기각이 아니다. 유효한 negative result도
실제로 검사한 주장에 한정한다. 논쟁은 근거 보완 후 한 번의 bounded re-review;
미해결이면 두 rationale를 보존하고 DEFERRED로 남긴다.
