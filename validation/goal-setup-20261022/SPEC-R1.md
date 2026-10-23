# GOAL-SETUP-20261022 — shared workflow 5.3.0 / R1

Status: IMPLEMENTATION_AUTHORIZED. Research experiment: NOT_RUN / not part of this task.
R1: user asked for cheaper QA and appropriate Supervisor effort; role-specific dispatch policy added.
Owner: Main (Research Lead). Engineer: `/root/goal_setup_impl`, actual spawn effort xhigh.
Source baseline: `/workspace/_nas/_shared/codex-research-setup`, git `688bb6c`, version 5.2.0.

## Objective and scope

Implement portable goal-mode **settings and support**, based on the KOBS discovery flow:
research → discriminating small validation → accept/reject/refine → research, until the user's
ultimate goal is met or an explicit resource/permission/stop boundary is reached. Research is the
default activity, not an extra user-selectable mode. Goal is an autonomy overlay; monk independently
restricts methodology survey. The user may enable goal alone or goal + monk.

User example: find three distinct promising research directions. Three is an example, not a global
quota. Accepted means meeting the predeclared evidence/quality criteria for the user's next decision,
not proof of full-scale performance, publication novelty, or final scientific adoption. Exhausting
resources before collecting the requested directions is **not goal achievement**.

Update only the shared distribution, plus this task's REPORT/RUNBOOK. Do not install it into KVCPRS,
change global Codex settings, resume the paused KOBS survey, or launch any research goal/experiment.
No automatic Codex sessions, subprocess agent orchestration, scheduler, API experiments, model/data
loading, downloads, GPU use, package installation, or real project command execution in this task.

## Ownership and preserved contracts

- Engineer is the sole writer of all shared distribution files and this task's REPORT/RUNBOOK.
  You are not alone in the codebase: preserve others' changes; never revert unrelated work.
- Main owns this SPEC and KVCPRS research/STATE.md. Do not edit KVCPRS research code/config/results.
- Read source AGENTS.md, shared policy `/workspace/_nas/_shared/init/settings_prompt/**/*.txt`,
  and the KVCPRS implementation guide. This task is ordinary workflow engineering, monk off.
- Preserve the original research depth/invention/math standards, direct Main code access,
  single engineering writer, existing user's model/effort/security, and USER_ONLY heavy execution.
- Agent budgets do not grant permission for heavy runs. All four roles follow the same boundary.
- No additional agents or Codex sessions from Engineer. Report scientific/spec ambiguities to Main.

## Package integration

1. Bump package VERSION/manifest/docs to **5.3.0**, with correct payload hashes. Preserve v5.2
   hashes for safe legacy migration. Existing STATE, user goal forms and goal run history survive
   reinstall/upgrade unchanged. No automatic destructive migrations or forced overwrites.
2. Add `.codex/guides/goal.md`, standalone `supervisor.toml` and `qa.toml` alongside Engineer.
   Required TOML role fields remain name/description/developer_instructions; no model/effort pin.
   Keep `[agents]` settings and max concurrent subagents=3. These roles run only when relevant.
   Generalize installer duplicate-name, legacy registration, static role and effort checks to all
   three managed roles; preserve unrelated roles and project/global configurations.
3. Link the new workflow from AGENTS, RESEARCH_START, VERIFY_SETUP, Engineer, research and monk
   guides, README and BOOTSTRAP without replacing existing guidance with a new framework.
   User-facing terminology: default research, optional monk, optional goal. Existing recorded
   `standard`/`monk` states remain compatible (standard means monk disabled), not a third overlay.
4. Provide a human-readable **Markdown form containing one fenced TOML block**, parsed with stdlib
   tomllib, at `research/GOAL_CONFIG.md` with create-only install semantics. A separate managed copy
   under templates gives the current schema. No CLI questionnaire. A fresh template cannot start
   automatically; unset fields/disabled defaults must be explicit and safe. User edits goal/budgets;
   agents fill a separate proxy contract/reviews, not the user's authorization fields.
5. Add concise reusable templates for a frozen proxy contract, candidate evidence/decisions,
   goal progress/shortlist and validation/handoff as needed. Avoid redundant copies of SPEC/REPORT
   and RUNBOOK or mandatory essay paperwork per trivial trial. Include one clearly marked small
   illustrative example/config to make the schema understandable; examples are not authorizations.

## Goal loop and roles (instructions are operational, not an OS security boundary)

Main remains Research Lead: develops mechanisms, mathematical derivation/counterexamples, designs
the most economical discriminating test and learns from failed hypotheses. It does not become just
a dispatcher. Supervisor independently assesses contribution potential, evidence, alternatives,
failure conditions, fit to the goal and whether to deepen/refine/reject/accept/park. No fixed
performance/novelty weighted score may replace explicit reasoning about the declared criteria.

Engineer owns implementation, debugging, tiny local checks and preparation of exact commands.
QA is an independent reader of SPEC/code/config/evaluation/evidence and checks valid comparisons,
data leakage, actual revision, costs and output integrity. QA may own small validation artifacts,
but may not edit research code or quietly fix the evaluator while judging it. Main/QA can request
Engineer fixes. Supervisor and QA do not spawn children or run heavy work.

Reasoning effort is chosen in the actual spawn arguments, not pinned in role TOML. Keep the same
model unless the user selects another. Engineer retains high/xhigh. QA defaults to medium for an
already-reviewed pipeline's conditions/logs/evidence; use high for first evaluator review, changed
metrics/splits or substantive numerical/mathematical validity questions. Prefer deterministic
checks over paying a low-effort agent for mechanical assertions. Supervisor defaults to high;
use xhigh for final shortlist acceptance, rejection of a promising research direction, contested
scientific rejection, substantive research-direction changes or decisive mathematical analysis.
The user explicitly endorsed xhigh for these important Supervisor judgments. Do not make every
routine iteration xhigh. Main's own settings remain user controlled.
`[agents].default_subagent_reasoning_effort = high` stays compatible; QA medium is an explicit
per-spawn selection. Check runtime support and record requested vs observed effort. Reusing a
thread does not change its effort; if different effort is necessary, preserve its evidence and
close/stop it before starting its replacement. Count the replacement and all reviewer work in
the goal's agent-call budget. These defaults are operational judgment, not measured accuracy claims.

One named executor per attempt (normally QA for the pre-reviewed light proxy; Engineer for tiny
implementation checks); no duplicate runs. QA does not automatically rerun Engineer evidence.
New method/evaluator/data paths or changes beyond the reviewed envelope require independent QA.
Identical reviewed paths may reuse automatic checks keyed to exact code/config/pipeline revisions;
do not pay for all-agent full reviews every iteration. No fake role independence through Main
claiming to have reviewed itself. Missing role/runtime support must be reported and the dependent
gate left unverified; don't silently erase the check or alter permissions/models.

Before each execution, resource/permission gate and QA validity are separate from scientific
judgment. Result states distinguish NOT_RUN, RUNNING, VALID, INVALID, OOM/TIMEOUT/INFRA_ERROR,
NEEDS_USER_RUN. Hypothesis states distinguish PROPOSED, REFINE, REJECTED, ACCEPTED, DEFERRED.
A bug, timeout, invalid comparison, lack of budget or out-of-scope proxy is not scientific rejection.
Negative valid evidence can reject a precise mechanism under tested assumptions. Rejecting the
whole family requires adequate support. Method deployment overhead violating the actual research
constraint is different from high cost to validate it.

Accepted directions need independent QA-valid evidence and Supervisor rationale for user criteria.
Track lineage/mechanism so renamed duplicates and hyperparameter variants do not fill the quota.
Literature novelty under monk remains UNVERIFIED and is neither auto-failure nor a claimed first.
An accepted direction may still require full user-run validation; a candidate with only deferred
decisive evidence does not count as proxy-supported unless the user's initial goal explicitly
permits that evidence class. Show these classes separately in the shortlist.

Completion is checked against the initial ultimate-goal predicate, not merely candidate count or
running out of ideas. Budget exhaustion/stalled exploration/user interruption preserve an unmet
goal and evidence. Stop on explicit user pause/stop, serious integrity failure, or inability to make
permitted useful progress. Use finite trial, retry, review and stagnation limits. On a disputed
review, Main may provide evidence/correction, then seek one bounded re-review; unresolved scientific
disagreement remains deferred with both rationales, not an endless argument or auto-overrule.

Checkpoint after meaningful decisions; resume from config/pipeline/ledger/evidence revisions,
including failed/pending attempts and resource reservations. Do not reset history/budgets on
compaction, new thread, retry or plan revision. Do not adopt an old result as validation of changed
code. Stop/cancel only jobs owned by the goal executor; never touch user's jobs. Deliver a concise
shortlist, rejected-mechanism lessons, pending user-run tests and remaining uncertainties at stop.

## Fixed proxy contract and scientific validity

Goal cannot start automatic experimental cycling until a task-specific proxy is selected/reviewed.
Freeze scope, baseline/version, evaluator, data manifests/splits, fit/tune/DEV rules, heldout access,
metrics/units/aggregation, precision/storage/runtime comparison conditions and acceptance gates.
Candidate implementation/hyperparameters may change inside this contract. Evaluator/data/gates
must not drift to rescue a candidate. A needed change is a new contract revision with explicit
authorization when it changes user goals or test policy; retain old results and remaining budgets.

Record repeated DEV exposure and multiplicity. An adaptive search's best DEV is not independent
confirmation. A sealed confirmation set is accessed only under the predeclared rule; no repeated
tuning on it. Proxy validity envelope and failures to extrapolate are explicit. Don't reject an
interesting out-of-envelope proposal using an incapable proxy. Preserve it as NEEDS_USER_RUN or a
separate design question. Avoid demanding a brand-new full evaluator for each idea automatically.

KOBS flow is an explanatory example: fixed-K, fixed-layer-input V readout proxy compared baseline,
analytic initialization and trained space; feedback/rejected earlier mechanisms led to a new axis;
later full-model PPL was a separate user-run stage. Do not hard-code Qwen/layers/thresholds or imply
the original multi-minute, large-memory KOBS pilot was an agent-light test.

## Resources and deterministic helper

Implement a **small stdlib helper**, e.g. `.codex/tools/goal_guard.py`, for structured config
validation, immutable contract snapshot/check, and an append-only budget/attempt ledger. It is
deliberately **not an experiment runner or automatic OS sandbox** and executes no config commands,
project imports, model loads, schedulers or APIs. A separate task-specific bounded executor must be
available/reviewed before automatic proxy execution. Unsupported hard enforcement → NEEDS_USER_RUN;
never label a plan's numeric limits as physically enforced. This release supplies the agent workflow
and deterministic bookkeeping; it cannot itself run while Codex is absent or enforce provider billing.

Config captures objective and success criteria/target, monk boolean, workspace/environment,
allowed read/write/artifact roots, proxy contract path/revision, finite total elapsed time,
per-run time, aggregate CPU/GPU work, CPU/RAM/GPU IDs/VRAM/disk, attempts/retries/concurrency,
finite agent-call/review/stagnation limits, and optional token/cost caps with explicit accounting
availability. Required values missing/empty means NOT_READY; zero means prohibited. Do not require
GPU/token spending when unused. Optional token/cost caps can be explicitly unselected; then finite
agent calls/time still apply. If a requested cap cannot be metered/enforced, don't promise it or
start dependent automatic work. Reject NaN/inf/negative, bool-as-number, unknown fields, duplicate
fields/blocks and malformed TOML. Avoid configuration aliases with conflicting meanings.

Provide documented commands to validate, freeze/init, reserve an attempt, finish/record usage,
and report status. Exact CLI names/schema are Engineer's implementation choice. Keep it small.
Machine output must distinguish logical readiness, execution authorization (never granted by
this helper), actual enforcement status and scientific decision (not computed by resource gate).
The helper may report READY_FOR_LIGHT_REVIEW, NEEDS_USER_RUN, BLOCKED_CONFIG/CONTRACT or BUDGET_EXHAUSTED.

Ledger rules:
- Reserve declared worst-case startup+work+cleanup+save resource bounds **before** work. Every
  attempt, failure and retry consumes its reservation; no free preflight runs or repeat loopholes.
- Default conservative accounting: charge max(reserved, reported actual) for each cumulative
  dimension. Unknown usage/pending attempts keep the reservation, not zero. No refunds based on
  unverifiable self-reports. Overshoot is recorded as breach and blocks further reservations.
- Concurrent reservations count collectively; finite retry/attempt/concurrency limits are checked.
  Handle sequential/colliding writers with a lock and atomic/append semantics; don't overwrite or
  silently repair partial/corrupt state. An interrupted unresolved attempt must not rerun on resume.
- Ledger persists fingerprints of config/contract and small explicit evaluator/baseline manifests;
  changed contracts block reuse. Limit input/snapshot/ledger size and avoid hashing big raw data,
  model weights or recursively traversing datasets. Existing artifact manifest IDs suffice.
- Refuse unsafe state paths/symlink writes; never infer authorization from a relative traversal.
  Validate evidence provenance as metadata; a checksum is not proof of scientific truth or
  cryptographic independence of reviewers. Reserve/finish are serialized, no duplicate IDs/finishes.
- Wall-clock age starts with init, includes interruption/pause until an explicitly authorized budget
  amendment. No reset on reload. Data files/user results are read-only; helper never controls jobs.
- Include agent work in accounting instructions; calls/time are a finite fallback if provider tokens
  aren't observable. Do not pretend an experimental-attempt ledger automatically meters the main
  conversation or all subagent usage. Explain capability/coverage gaps explicitly.

No generic experiment shell runner in this release: portable hard VRAM/RAM/disk/token enforcement
cannot be honestly supplied by a configuration-only helper. Make this limitation prominent in
README/guide/VERIFY_SETUP and handoff. Existing tiny development checks remain allowed under the
project's original policy; that is not permission for an unbounded goal proxy loop.

## Verification and completion

Use only offline stdlib unittests in temporary fixtures. No existing experiment test suites or
model imports. Up to 4 targeted/full unittest invocations total, <=60 seconds each, <=180 seconds
aggregate; single process/small temporary files, no GPU/network/installs. Stop and report if more is
needed; Main may revise the light-validation allowance based on actual failures.

Meaningful checks: existing installer behavior, fresh install/upgrade from v5.2/idempotence,
config/STATE/goal history preservation, role conflict/pinned effort validation, checksums;
real helper parsing for monk off/on, blanks/zero/unknown/duplicate/nonfinite/bool cases,
frozen contract mutation, path/symlink limits, reserve/fail/pending/retry/concurrency/cumulative
budget and elapsed expiry, usage overshoot, corrupted/interrupted ledger, no execution side effects.
Guide/template contract checks should assert important invariants, not reproduce implementation.
No actual research outcome or runtime role activation is validated by these static/unit tests.

Return REPORT.md and RUNBOOK.md at this task directory: files, schema/CLI examples, actual tests
and revisions/hashes, limitations, migration behavior, static vs runtime status and how a future
project owner fills and validates the form. This task is done when source artifacts are complete,
Main reviews core paths/evidence and appropriate lightweight checks pass. No research goal is
started; fresh-session role activation and real proxy executor integration remain NOT_VERIFIED.
