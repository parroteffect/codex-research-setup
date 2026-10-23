# GOAL-HARDEN-20261022 / R1

Status: IMPLEMENTATION_AUTHORIZED. 실제 연구 goal·설치·본 실험: NOT_RUN / 범위 밖.
Owner: Main. Engineer: `/root/goal_hardening_impl`, actual effort xhigh.
Target: `/workspace/_nas/_shared/codex-research-setup`.
User authorization: 독립 검수의 다섯 항목에 대해 “오케이 수정해봐”.
Baseline: 현재 v5.3.0 uncommitted 구현을 보존한다. Git HEAD만으로 되돌리지 않는다.
Evidence: `research/notes/goal-workflow-independent-review-20261022.md` F1–F5.

## Purpose and ownership

Fix the five reviewed defects while preserving the KOBS-inspired research loop, orthogonal
goal/monk overlays, Main's scientific responsibility, single engineering writer, role/effort
policy, and USER_ONLY heavy work. This is ordinary workflow engineering, monk off; the KOBS
survey remains paused. No new research idea, goal, global Codex setup, or executor is authorized.

Engineer is the sole writer of the shared distribution (code/tests/docs/manifests/version and
new small validation artifacts) plus this task's REPORT.md and RUNBOOK.md. Main owns this SPEC,
research/STATE.md and review notes. Other reviewers are read-only. You are not alone in the
codebase: preserve existing edits and original evidence; never revert or overwrite others' work.

Read common policy `/workspace/_nas/_shared/init/settings_prompt/**/*.txt`, distribution
AGENTS.md, `/workspace/kvcprs/.codex/guides/implementation.md`, this SPEC and the independent
review. Small source/metadata/fixtures stay local. No model/data/cache work is required;
project identity is kvcprs and existing large-storage policy remains unchanged.

## F1 — conservative managed-block provenance

Always check the provenance of an existing marked AGENTS block, even when install metadata or
agents_block_hash is absent. Automatic replacement is allowed only when it exactly matches the
current payload, the recorded installed block, or an independently verifiable pristine legacy
release. Unknown/customized blocks must raise Conflict without changing the target. Preserve
outside-block content and existing backup behavior. No force option or fabricated metadata.
Conservative conflict for an unprovable older block is acceptable; document the manual merge.

Regressions must cover missing metadata, missing block-hash key, unchanged current block,
tracked clean upgrade and custom-block preservation. Preserve existing install/update behavior.

## F2 — explicitly budgeted setup prerequisite

Choose the review's smaller design option: preparing and independently reviewing a proxy is a
**separately budgeted prerequisite** to the frozen goal run. Do not add a generic SETUP execution
engine, new OS runner or complex mutable-contract migration in this patch.

- Provide a concise managed Markdown setup-budget/record template and integrate it in the guide,
  example, user-form explanation and manifest. User specifies finite SETUP allocation before
  preparation starts. Main records start time, per-work upper-bound reservations, actual/unknown
  usage, pending work, failure/retry cost and remaining allocation. Main/Engineer/QA calls count.
- SETUP and RUN allocations are explicit. Existing RUN limits in the goal TOML begin at init;
  they must not be presented as including unrecorded setup. If the user gives a single total,
  an explicitly authorized split is required; agents cannot grant extra setup resources or
  silently reset an end-to-end deadline. Separate ceilings are not fresh money/time on resume.
- Missing setup authorization means no new proxy preparation. Reusing an already prepared proxy
  records its provenance and any newly required checks under a valid allocation. No automatic
  unlimited setup loop. Finish or hand off the bounded preparation before freezing the run.
- Startup requires a completed setup record / documented pre-existing reviewed prerequisite,
  QA review and unchanged referenced artifacts; carry a link to setup costs into goal progress
  so the combined cost remains visible. No transfer of unused allocation unless authorized.
- State clearly this prerequisite's Markdown accounting is reviewed operationally, not enforced
  or metered by goal_guard. Heavy/unknown work and unobservable required caps remain USER_ONLY /
  NEEDS_USER_RUN. Post-init preparation still consumes ordinary ledger reservations.
- Keep schema-1 RUN config compatibility; no silent rewrite of the installed user's form.

The fix must make the preparation/initialization order and budget ownership unambiguous across
all changed docs. Do not claim new machine enforcement for the manual setup record.

## F3 — latch stagnation stop

Once the recorded consecutive stagnation limit is reached, late meaningful PROGRESS must not
permit new reservations. Progress before the limit still resets the consecutive counter.
Late evidence and pending FINISH records remain allowed within metadata capacity. Recover the
latched stop from durable history, including old ledgers containing a past crossing followed
by meaningful progress; do not require a mutable side-file to remember it.

No automatic resume or budget reset. Existing no-amendment policy applies: explicit user
authorization plus reviewed migration preserving past use/start time is required for a new
budget/continuation. Document this rather than adding an unreviewed resume command.

## F4 — progress commit and result under one lock

Compute the returned status from the same locked state after appending PROGRESS. Do not release
and reacquire the state lock or reload potentially changed state for the response. A collision
before commit must leave the ledger unchanged; a committed event must return its correct state.
Small deterministic contention/call-boundary regression must exercise the actual guard path.
No broad locking rewrite or automatic stale-lock recovery. Progress idempotency is optional,
not required if no new retry interface is introduced.

## F5 — reserve completion metadata capacity

Guarantee bounded space for one valid FINISH record per pending reservation. New RESERVE and
PROGRESS cannot consume that space. Define and validate finite serialized metadata limits so
the guarantee has a real upper bound (including JSON escaping/envelope/ID/numeric sizes).
Reject oversized metadata before mutating the ledger; do not truncate evidence silently.

FINISH must remain recordable at new-work capacity exhaustion and must update actual usage /
breach accounting. STATUS and refusal responses must consistently expose capacity exhaustion
and its scope; never claim a failed completion was recorded. Treat a large single event that
does not fit separately from true global inability to append bounded required records.

Existing ledgers must remain readable without losing costs/history. If old pending reservations
lack completion headroom, block new work and provide an honest manual handoff; allow any bounded
FINISH that still fits rather than making repair impossible. Do not auto-delete/rotate/reset a
ledger. Any persistent budget stop must preserve completion-space guarantees.

Regressions: insufficient headroom refuses reservation without mutation; multiple pending
reservations retain FINISH slots; PROGRESS cannot steal them; completing all pending at the
boundary succeeds; actual overshoot still records breach; metadata size/escaping edge; STATUS
agrees with exhaustion; old/cap-tight state fails conservatively. Tiny patched ledger cap is
appropriate; no multi-MiB fill or stress benchmark required.

## Packaging and validation

- Patch release v5.3.1; update VERSION/manifest/relevant docs and preserve previous payload hashes
  for safe upgrades. Preserve v5.3.0 validation/artifacts and all historical review results.
- Save a pre-edit source fingerprint/small snapshot outside source payload in a new validation
  directory for this task. Record actual final hashes and executed tests in REPORT.
- Engineer effort xhigh: cross-module lifecycle, persistent-state and accounting invariants.
  Reuse this writer for fixes; no child agents or extra Codex sessions.
- Only reviewed stdlib tiny temporary fixtures. At most 4 test invocations, each <=15 seconds,
  aggregate <=45 seconds. Full existing suite (~1–2 seconds previously) plus focused tests are
  permitted within this bound. Adjust tests only when the intended contract changed; never lower
  assertions to conceal failures. If budget is exhausted or tests become non-light, report Main.
- No GPU, model/data load/download, API experiment, actual goal loop, current-project install,
  global config change, external publish/commit, CI, scheduler, or user-job control.
- Do not duplicate another reviewer's tests. Final checks include payload hashes, meaningful
  regressions through actual functions, installer temporary fixtures and diff whitespace.
- Return changed files, exact commands/status/time, old/new behavior, remaining limitations,
  REPORT/RUNBOOK and evidence paths. Main reviews core code/diff and actual logs before completion.

Done means all five contracts above are implemented and light checks pass. It does not mean
runtime roles, external enforcement, goal-loop autonomy or full research performance is verified.
