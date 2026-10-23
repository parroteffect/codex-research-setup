#!/usr/bin/env python3
"""Offline goal configuration and conservative bookkeeping. NEVER executes a plan.

Python 3.11+, stdlib only. Locks are not silently recovered after interruption.
A valid reservation is not execution permission or physical resource enforcement.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import tomllib

TEXT_LIMIT = 262_144
LEDGER_LIMIT = 4_194_304
MANIFEST_FILE_LIMIT = 524_288
MAX_MANIFEST_FILES = 32
# Reserve bounded snapshots + full ledger + small lock/directory bookkeeping upfront.
METADATA_RESERVATION = 3 * TEXT_LIMIT + LEDGER_LIMIT + 65_536
DIMENSIONS = ("cpu_seconds", "gpu_seconds", "disk_bytes", "agent_calls", "reviews", "tokens", "cost")
INTEGER_DIMENSIONS = {"disk_bytes", "agent_calls", "reviews", "tokens"}
LIMIT_KEYS = {"total_elapsed_seconds", "per_attempt_seconds", "total_cpu_seconds", "total_gpu_seconds",
              "cpu_cores", "ram_mib", "gpu_ids", "vram_mib", "disk_bytes", "max_attempts",
              "max_retries", "concurrency", "max_agent_calls", "max_reviews", "max_stagnation"}
CONTRACT_KEYS = {"revision", "objective", "scope", "validity_envelope", "baseline", "evaluator",
                 "data_manifests", "splits", "dev_policy", "heldout_policy", "metrics", "aggregation",
                 "comparison_conditions", "acceptance_gates", "allowed_candidate_changes", "files"}


class GuardError(Exception):
    def __init__(self, message, status="BLOCKED_CONFIG"):
        super().__init__(message)
        self.status = status


def result(status, **fields):
    return {"status": status, "execution_authorization": "NOT_GRANTED",
            "enforcement": "NOT_PROVIDED", "automatic_execution": "NOT_DETERMINED",
            "proxy_requirement": "REVIEWED_EXTERNAL_BOUNDED_EXECUTOR_OR_NEEDS_USER_RUN",
            "scientific_decision": "NOT_COMPUTED", "goal_achievement": "NOT_COMPUTED", **fields}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def exact_keys(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise GuardError(f"{label}: expected fields {sorted(keys)}")


def number(value, label, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GuardError(f"{label}: expected a nonnegative number; unset is not unlimited")
    if value < 0 or value > 10**18 or (isinstance(value, float) and not math.isfinite(value)) or (integer and not isinstance(value, int)):
        raise GuardError(f"{label}: expected a finite nonnegative {'integer' if integer else 'number'}")
    return value


def string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise GuardError(f"{label}: required value is unset (NOT_READY)")
    return value


def strings(value, label, allow_empty=False):
    if not isinstance(value, list) or (not value and not allow_empty):
        raise GuardError(f"{label}: expected {'a' if allow_empty else 'a nonempty'} string list")
    for item in value:
        string(item, label)
    if len(set(value)) != len(value):
        raise GuardError(f"{label}: duplicate values")
    return value


def safe_path(value):
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts:
        raise GuardError(f"Expected an absolute path without traversal: {value}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise GuardError(f"Symlink paths are not allowed: {current}")
    return path


def within(path, roots):
    if not any(path.is_relative_to(root) for root in roots):
        raise GuardError(f"Path is outside declared roots: {path}")
    return path


def read_small(path, limit=TEXT_LIMIT):
    path = safe_path(str(path))
    if not path.is_file() or path.stat().st_size > limit:
        raise GuardError(f"Missing or oversized small metadata file: {path}")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise GuardError(f"Metadata grew beyond size limit: {path}")
    return data


def parse_markdown(data):
    try:
        text = data.decode("utf-8")
        # One TOML block is the complete machine configuration; prose is explanatory.
        blocks = re.findall(r"^```toml[ \t]*\r?\n(.*?)^```[ \t]*\r?$", text, re.M | re.S)
        if len(blocks) != 1 or len(re.findall(r"^```toml\b", text, re.M)) != 1:
            raise GuardError("Expected exactly one fenced TOML block")
        return tomllib.loads(blocks[0])
    except (UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise GuardError(f"Invalid UTF-8/TOML: {exc}") from exc


def parse_json(data):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise GuardError(f"Duplicate JSON field: {key}")
            value[key] = item
        return value
    try:
        return json.loads(data, object_pairs_hook=pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(GuardError(f"Nonfinite JSON: {value}")))
    except (ValueError, UnicodeError) as exc:
        raise GuardError(f"Invalid JSON: {exc}") from exc


def config_from(path):
    raw = read_small(path)
    cfg = parse_markdown(raw)
    exact_keys(cfg, {"schema_version", "goal", "paths", "proxy", "limits", "accounting"}, "config")
    if type(cfg["schema_version"]) is not int or cfg["schema_version"] != 1:
        raise GuardError("Unsupported schema_version")
    goal = cfg["goal"]
    exact_keys(goal, {"enabled", "monk", "objective", "success_criteria", "target_directions", "accepted_evidence", "stop_conditions"}, "goal")
    for key in ("enabled", "monk"):
        if type(goal[key]) is not bool:
            raise GuardError(f"goal.{key}: expected boolean")
    for key in ("objective", "success_criteria"):
        string(goal[key], "goal." + key)
    number(goal["target_directions"], "target_directions", True)
    strings(goal["accepted_evidence"], "accepted_evidence")
    strings(goal["stop_conditions"], "stop_conditions", True)
    paths = cfg["paths"]
    exact_keys(paths, {"workspace", "environment", "read_roots", "write_roots", "artifact_root"}, "paths")
    string(paths["environment"], "environment")
    for key in ("workspace", "artifact_root"):
        safe_path(string(paths[key], key))
    if not Path(paths["workspace"]).is_dir():
        raise GuardError("workspace must be an existing directory")
    for key in ("read_roots", "write_roots"):
        for root in strings(paths[key], key):
            safe_path(root)
    within(Path(paths["artifact_root"]), [Path(p) for p in paths["write_roots"]])
    proxy = cfg["proxy"]
    exact_keys(proxy, {"contract_path", "revision"}, "proxy")
    string(proxy["revision"], "proxy.revision")
    within(safe_path(string(proxy["contract_path"], "contract_path")), [Path(p) for p in paths["read_roots"]])
    limits = cfg["limits"]
    exact_keys(limits, LIMIT_KEYS, "limits")
    for key, value in limits.items():
        if key == "gpu_ids":
            strings(value, key, True)
        else:
            number(value, key, key in {"disk_bytes", "max_attempts", "max_retries", "concurrency", "max_agent_calls", "max_reviews", "max_stagnation"})
    if limits["total_elapsed_seconds"] == 0:
        raise GuardError("total_elapsed_seconds=0 prohibits starting a goal (NOT_READY)")
    if not limits["gpu_ids"] and (limits["vram_mib"] or limits["total_gpu_seconds"]):
        raise GuardError("No GPU IDs requires zero VRAM and GPU work budget")
    accounting = cfg["accounting"]
    exact_keys(accounting, {"token_cap", "cost_cap", "tokens_metered", "tokens_enforced", "cost_metered", "cost_enforced"}, "accounting")
    for key in ("tokens_metered", "tokens_enforced", "cost_metered", "cost_enforced"):
        if type(accounting[key]) is not bool:
            raise GuardError(f"{key}: expected boolean")
    for key in ("token_cap", "cost_cap"):
        if accounting[key] != "unselected":
            number(accounting[key], key, key == "token_cap")
    return cfg, raw


def accounting_gaps(cfg):
    a = cfg["accounting"]
    return [prefix for prefix, cap in (("tokens", "token_cap"), ("cost", "cost_cap"))
            if a[cap] != "unselected" and not (a[prefix + "_metered"] and a[prefix + "_enforced"])]


def contract_from(cfg):
    path = Path(cfg["proxy"]["contract_path"])
    raw = read_small(path)
    contract = parse_markdown(raw)
    exact_keys(contract, CONTRACT_KEYS, "contract")
    for key in CONTRACT_KEYS - {"files", "data_manifests"}:
        string(contract[key], "contract." + key)
    strings(contract["data_manifests"], "data_manifests")
    if contract["revision"] != cfg["proxy"]["revision"]:
        raise GuardError("Contract revision differs from config", "BLOCKED_CONTRACT")
    files = contract["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_MANIFEST_FILES:
        raise GuardError("Contract needs 1..32 explicit small evaluator/baseline files")
    observed = []
    for entry in files:
        exact_keys(entry, {"path", "sha256"}, "contract.files")
        path = within(safe_path(string(entry["path"], "manifest path")), [Path(p) for p in cfg["paths"]["read_roots"]])
        if not isinstance(entry["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
            raise GuardError("Invalid manifest SHA256")
        actual = sha(read_small(path, MANIFEST_FILE_LIMIT))
        if actual != entry["sha256"]:
            raise GuardError(f"Evaluator/baseline fingerprint changed: {path}", "BLOCKED_CONTRACT")
        observed.append({"path": str(path), "sha256": actual})
    if len({entry["path"] for entry in observed}) != len(observed):
        raise GuardError("Duplicate contract file path")
    return raw, observed


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n").encode()


def create_file(path, data):
    # O_EXCL and NOFOLLOW fail rather than replacing prior state.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def locked(state):
    lock = safe_path(str(state / ".lock"))
    try:
        create_file(lock, json_bytes({"pid": os.getpid()}))
    except FileExistsError as exc:
        raise GuardError("State is locked; do not recover or rerun automatically", "BLOCKED_CONTRACT") from exc
    try:
        yield
    finally:
        lock.unlink()


def state_path(cfg, value):
    state = within(safe_path(str(value)), [Path(p) for p in cfg["paths"]["write_roots"]])
    if state == Path(cfg["paths"]["workspace"]) or state in [Path(p) for p in cfg["paths"]["write_roots"]]:
        raise GuardError("Use a new goal-specific child directory for state")
    return state


def envelope(kind, payload, seq, previous, timestamp):
    event = {"seq": seq, "previous": previous, "time": timestamp, "kind": kind, "payload": payload}
    event["hash"] = sha(json_bytes(event))
    return event


def append_event(state, events, kind, payload):
    event = envelope(kind, payload, len(events), events[-1]["hash"] if events else "", time.time())
    path = safe_path(str(state / "ledger.jsonl"))
    data = json_bytes(event)
    existing = read_small(path, LEDGER_LIMIT)
    if len(existing) + len(data) > LEDGER_LIMIT:
        raise GuardError("Ledger size cap reached; preserve state and stop", "BUDGET_EXHAUSTED")
    if events and event["time"] < events[-1]["time"]:
        raise GuardError("Clock moved backwards", "BLOCKED_CONTRACT")
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return event


def init(config_path, state_value):
    cfg, raw = config_from(config_path)
    if not cfg["goal"]["enabled"]:
        raise GuardError("goal.enabled=false; goal is not activated")
    contract, files = contract_from(cfg)
    if accounting_gaps(cfg):
        return result("NEEDS_USER_RUN", reason="Requested billing cap lacks declared metering/enforcement")
    if cfg["limits"]["disk_bytes"] < METADATA_RESERVATION:
        return result("BUDGET_EXHAUSTED", reason="Disk budget cannot cover bounded guard metadata", goal_achieved=False)
    state = state_path(cfg, state_value)
    # Parent must already exist: no implicit storage/mount creation.
    if not state.parent.is_dir() or state.exists():
        raise GuardError("State must be a new directory under an existing approved parent")
    frozen = {"schema_version": 1, "config_sha256": sha(raw), "contract_sha256": sha(contract), "files": files}
    if len(json_bytes(frozen)) > TEXT_LIMIT:
        raise GuardError("Frozen metadata exceeds size cap")
    state.mkdir(mode=0o700)
    with locked(state):
        create_file(state / "config.md", raw)
        create_file(state / "contract.md", contract)
        create_file(state / "frozen.json", json_bytes(frozen))
        create_file(state / "ledger.jsonl", b"")
        append_event(state, [], "INIT", {"fingerprint": sha(json_bytes(frozen))})
    return result("READY_FOR_LIGHT_REVIEW", state=str(state), reservation_is_execution=False)


def check_plan(plan):
    exact_keys(plan, {"id", "kind", "retry_of", "light", "cost_known", "duration_seconds", "cpu_cores", "ram_mib", "gpu_ids", "vram_mib", "bounds"}, "plan")
    if not isinstance(plan["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", plan["id"]):
        raise GuardError("Invalid attempt ID")
    if plan["kind"] not in ("experiment", "agent", "review"):
        raise GuardError("kind must be experiment, agent, or review")
    if plan["retry_of"] is not None:
        string(plan["retry_of"], "retry_of")
    for key in ("light", "cost_known"):
        if type(plan[key]) is not bool:
            raise GuardError(f"{key}: expected boolean")
    for key in ("duration_seconds", "cpu_cores", "ram_mib", "vram_mib"):
        number(plan[key], key)
    strings(plan["gpu_ids"], "gpu_ids", True)
    exact_keys(plan["bounds"], DIMENSIONS, "bounds")
    for key, value in plan["bounds"].items():
        number(value, key, key in INTEGER_DIMENSIONS)
    if plan["duration_seconds"] == 0:
        raise GuardError("A work reservation needs positive elapsed duration")
    if plan["kind"] == "experiment" and (not plan["cpu_cores"] or not plan["ram_mib"]):
        raise GuardError("Local experiment needs positive CPU and RAM bounds")
    if plan["bounds"]["cpu_seconds"] < plan["cpu_cores"] * plan["duration_seconds"]:
        raise GuardError("CPU work must cover duration times allocated cores")
    if plan["bounds"]["gpu_seconds"] < len(plan["gpu_ids"]) * plan["duration_seconds"]:
        raise GuardError("GPU work must cover duration times device count")
    if not plan["gpu_ids"] and (plan["vram_mib"] or plan["bounds"]["gpu_seconds"]):
        raise GuardError("No GPU IDs requires zero GPU bounds")
    if plan["gpu_ids"] and (not plan["vram_mib"] or not plan["bounds"]["gpu_seconds"]):
        raise GuardError("GPU reservation requires positive VRAM and GPU work")
    if plan["kind"] in ("agent", "review") and not plan["bounds"]["agent_calls"]:
        raise GuardError("Agent/review work must reserve agent calls")
    if plan["kind"] == "review" and not plan["bounds"]["reviews"]:
        raise GuardError("Review work must reserve a review")


def check_usage(usage):
    exact_keys(usage, {"outcome", "actual", "duration_seconds", "cpu_cores", "ram_mib", "gpu_ids", "vram_mib", "evidence"}, "usage")
    if usage["outcome"] not in ("VALID", "INVALID", "OOM", "TIMEOUT", "INFRA_ERROR", "NEEDS_USER_RUN"):
        raise GuardError("Invalid execution outcome; scientific decisions are separate")
    exact_keys(usage["actual"], DIMENSIONS, "actual")
    for key, value in usage["actual"].items():
        if value is not None:
            number(value, key, key in INTEGER_DIMENSIONS)
    for key in ("duration_seconds", "cpu_cores", "ram_mib", "vram_mib"):
        if usage[key] is not None:
            number(usage[key], key)
    if usage["gpu_ids"] is not None:
        strings(usage["gpu_ids"], "gpu_ids", True)
    exact_keys(usage["evidence"], {"executor", "code_revision", "config_revision", "artifact_ids"}, "evidence")
    for key in ("executor", "code_revision", "config_revision"):
        string(usage["evidence"][key], key)
    strings(usage["evidence"]["artifact_ids"], "artifact_ids", True)


def replay(events, cfg):
    attempts = {}
    used = {key: 0 for key in DIMENSIONS}
    used["disk_bytes"] = METADATA_RESERVATION
    breach = False
    stagnant = 0
    for event in events[1:]:
        payload = event["payload"]
        if event["kind"] == "RESERVE":
            check_plan(payload)
            if payload["id"] in attempts:
                raise GuardError("Duplicate attempt in ledger", "BLOCKED_CONTRACT")
            attempts[payload["id"]] = {"plan": payload, "usage": None}
            for key in DIMENSIONS:
                used[key] += payload["bounds"][key]
        elif event["kind"] == "FINISH":
            exact_keys(payload, {"id", "usage"}, "finish event")
            if payload["id"] not in attempts or attempts[payload["id"]]["usage"] is not None:
                raise GuardError("Unmatched or duplicate finish", "BLOCKED_CONTRACT")
            check_usage(payload["usage"])
            attempt = attempts[payload["id"]]
            attempt["usage"] = usage = payload["usage"]
            plan = attempt["plan"]
            for key in DIMENSIONS:
                actual = usage["actual"][key]
                if actual is not None and actual > plan["bounds"][key]:
                    used[key] += actual - plan["bounds"][key]
                    breach = True
            for key in ("duration_seconds", "cpu_cores", "ram_mib", "vram_mib"):
                if usage[key] is not None and usage[key] > plan[key]:
                    breach = True
            if usage["gpu_ids"] is not None and not set(usage["gpu_ids"]).issubset(plan["gpu_ids"]):
                breach = True
        elif event["kind"] == "PROGRESS":
            exact_keys(payload, {"meaningful", "evidence"}, "progress")
            if type(payload["meaningful"]) is not bool:
                raise GuardError("Invalid progress boolean")
            string(payload["evidence"], "progress evidence")
            stagnant = 0 if payload["meaningful"] else stagnant + 1
        else:
            raise GuardError("Unknown ledger event", "BLOCKED_CONTRACT")
    return attempts, used, breach, stagnant


def load_state(config_path, state_value):
    cfg, raw = config_from(config_path)
    state = state_path(cfg, state_value)
    frozen = parse_json(read_small(state / "frozen.json"))
    exact_keys(frozen, {"schema_version", "config_sha256", "contract_sha256", "files"}, "frozen")
    contract, files = contract_from(cfg)
    expected = {"schema_version": 1, "config_sha256": sha(raw), "contract_sha256": sha(contract), "files": files}
    if frozen != expected or read_small(state / "config.md") != raw or read_small(state / "contract.md") != contract:
        raise GuardError("Frozen config/contract changed; preserve this run and authorize a new revision", "BLOCKED_CONTRACT")
    raw_ledger = read_small(state / "ledger.jsonl", LEDGER_LIMIT)
    if not raw_ledger or not raw_ledger.endswith(b"\n"):
        raise GuardError("Missing or interrupted ledger; do not silently repair", "BLOCKED_CONTRACT")
    events = []
    for line in raw_ledger.splitlines():
        event = parse_json(line)
        exact_keys(event, {"seq", "previous", "time", "kind", "payload", "hash"}, "ledger event")
        number(event["seq"], "seq", True)
        number(event["time"], "event time")
        check = {k: v for k, v in event.items() if k != "hash"}
        if event["hash"] != sha(json_bytes(check)) or event["seq"] != len(events) or event["previous"] != (events[-1]["hash"] if events else ""):
            raise GuardError("Corrupt ledger sequence/hash", "BLOCKED_CONTRACT")
        if events and event["time"] < events[-1]["time"]:
            raise GuardError("Nonmonotonic ledger time", "BLOCKED_CONTRACT")
        events.append(event)
    if events[0]["kind"] != "INIT" or events[0]["payload"] != {"fingerprint": sha(json_bytes(frozen))}:
        raise GuardError("Ledger does not match frozen contract", "BLOCKED_CONTRACT")
    if time.time() < events[-1]["time"]:
        raise GuardError("Clock moved backwards", "BLOCKED_CONTRACT")
    attempts, used, breach, stagnant = replay(events, cfg)
    return cfg, state, events, attempts, used, breach, stagnant


def caps(cfg):
    l, a = cfg["limits"], cfg["accounting"]
    return {"cpu_seconds": l["total_cpu_seconds"], "gpu_seconds": l["total_gpu_seconds"],
            "disk_bytes": l["disk_bytes"], "agent_calls": l["max_agent_calls"], "reviews": l["max_reviews"],
            "tokens": a["token_cap"], "cost": a["cost_cap"]}


def exhausted(cfg, events, breach, stagnant):
    if breach:
        return "Recorded resource breach; no further reservations"
    if time.time() - events[0]["time"] >= cfg["limits"]["total_elapsed_seconds"]:
        return "Total elapsed budget expired; pauses/interruption are included"
    if stagnant >= cfg["limits"]["max_stagnation"]:
        return "Stagnation limit reached; goal remains unmet"
    return None


def reserve(config_path, state_value, plan):
    check_plan(plan)
    cfg, _ = config_from(config_path)
    state = state_path(cfg, state_value)
    with locked(state):
        cfg, state, events, attempts, used, breach, stagnant = load_state(config_path, state)
        l = cfg["limits"]
        reason = exhausted(cfg, events, breach, stagnant)
        if len(attempts) >= l["max_attempts"]:
            reason = reason or "Attempt budget exhausted"
        if reason:
            return result("BUDGET_EXHAUSTED", reason=reason, scope="GOAL", goal_achieved=False,
                          remaining={key: (cap-used[key] if cap != "unselected" else "unselected") for key, cap in caps(cfg).items()})
        if not plan["light"] or not plan["cost_known"] or accounting_gaps(cfg):
            return result("NEEDS_USER_RUN", scope="ATTEMPT", reason="Heavy/unknown work or unsupported requested accounting")
        pending = [a["plan"] for a in attempts.values() if a["usage"] is None]
        if plan["id"] in attempts:
            raise GuardError("Attempt ID already exists; pending work must not rerun", "BLOCKED_CONTRACT")
        if plan["retry_of"] is not None:
            parent = attempts.get(plan["retry_of"])
            if parent is None or parent["usage"] is None:
                raise GuardError("Retry requires a finished existing attempt", "BLOCKED_CONTRACT")
            # Global retry cap prevents renaming/chaining attempts to reset the allowance.
            if sum(a["plan"]["retry_of"] is not None for a in attempts.values()) >= l["max_retries"]:
                reason = "Retry budget exhausted"
        if len(pending) >= l["concurrency"]:
            reason = "Concurrent reservation slots unavailable"
        remaining_time = l["total_elapsed_seconds"] - (time.time() - events[0]["time"])
        if plan["duration_seconds"] > min(l["per_attempt_seconds"], remaining_time):
            reason = "Worst-case duration exceeds remaining/per-attempt time"
        for key in ("cpu_cores", "ram_mib"):
            if sum(p[key] for p in pending) + plan[key] > l[key]:
                reason = f"Concurrent {key} exceeds declared limit"
        if not set(plan["gpu_ids"]).issubset(l["gpu_ids"]):
            reason = "GPU ID outside declared allocation"
        for gpu in plan["gpu_ids"]:
            if plan["vram_mib"] + sum(p["vram_mib"] for p in pending if gpu in p["gpu_ids"]) > l["vram_mib"]:
                reason = "Concurrent per-device VRAM exceeds declared limit"
        for key, cap in caps(cfg).items():
            if cap != "unselected" and used[key] + plan["bounds"][key] > cap:
                reason = f"Cumulative {key} budget exhausted"
        if reason:
            return result("BUDGET_EXHAUSTED", reason=reason, scope="ATTEMPT",
                          remaining={key: (cap-used[key] if cap != "unselected" else "unselected") for key, cap in caps(cfg).items()},
                          goal_achieved=False)
        append_event(state, events, "RESERVE", plan)
    return result("READY_FOR_LIGHT_REVIEW", attempt_id=plan["id"], reservation_is_execution=False,
                  warning="Bookkeeping only; independently reviewed bounded executor is still required")


def finish(config_path, state_value, attempt_id, usage):
    check_usage(usage)
    cfg, _ = config_from(config_path)
    state = state_path(cfg, state_value)
    with locked(state):
        cfg, state, events, attempts, used, breach, stagnant = load_state(config_path, state)
        if attempt_id not in attempts or attempts[attempt_id]["usage"] is not None:
            raise GuardError("Attempt is missing or already finished", "BLOCKED_CONTRACT")
        event = append_event(state, events, "FINISH", {"id": attempt_id, "usage": usage})
        _, _, breach, _ = replay(events + [event], cfg)
        reason = exhausted(cfg, events + [event], breach, stagnant)
        if len(attempts) >= cfg["limits"]["max_attempts"]:
            reason = reason or "Attempt budget exhausted"
    return result("BUDGET_EXHAUSTED" if reason else "READY_FOR_LIGHT_REVIEW", breach=breach,
                  scope="GOAL" if reason else "ATTEMPT", reason=reason,
                  outcome=usage["outcome"], evidence_is_metadata_only=True)


def progress(config_path, state_value, meaningful, evidence):
    if type(meaningful) is not bool:
        raise GuardError("meaningful must be boolean")
    string(evidence, "progress evidence")
    cfg, _ = config_from(config_path)
    state = state_path(cfg, state_value)
    with locked(state):
        cfg, state, events, attempts, used, breach, stagnant = load_state(config_path, state)
        append_event(state, events, "PROGRESS", {"meaningful": meaningful, "evidence": evidence})
    return status(config_path, state)


def status(config_path, state_value):
    cfg, _ = config_from(config_path)
    state = state_path(cfg, state_value)
    with locked(state):
        cfg, _, events, attempts, used, breach, stagnant = load_state(config_path, state)
        reason = exhausted(cfg, events, breach, stagnant)
        if len(attempts) >= cfg["limits"]["max_attempts"]:
            reason = reason or "Attempt budget exhausted; no further reservations"
        remaining = {key: (cap - used[key] if cap != "unselected" else "unselected") for key, cap in caps(cfg).items()}
        return result("BUDGET_EXHAUSTED" if reason else "READY_FOR_LIGHT_REVIEW", reason=reason,
                      scope="GOAL" if reason else "STATUS", charged=used, remaining=remaining, remaining_attempts=max(0, cfg["limits"]["max_attempts"] - len(attempts)), attempts=len(attempts), pending=[k for k, a in attempts.items() if a["usage"] is None],
                      elapsed_seconds=time.time() - events[0]["time"], stagnant_reviews=stagnant,
                      goal_achievement="NOT_COMPUTED", accounting_coverage="Recorded events only; not automatic provider/conversation metering")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "init", "reserve", "finish", "status", "progress"))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--record", type=Path, help="Small JSON plan/usage metadata, never a command")
    parser.add_argument("--attempt")
    parser.add_argument("--meaningful", choices=("yes", "no"))
    parser.add_argument("--evidence")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            cfg, _ = config_from(args.config)
            contract_from(cfg)
            output = result("NEEDS_USER_RUN" if accounting_gaps(cfg) else "READY_FOR_LIGHT_REVIEW",
                            goal_enabled=cfg["goal"]["enabled"], monk=cfg["goal"]["monk"])
        else:
            if args.state is None:
                raise GuardError("--state is required")
            if args.command in ("reserve", "finish") and args.record is None:
                raise GuardError("--record is required")
            if args.command == "init":
                output = init(args.config, args.state)
            elif args.command == "reserve":
                output = reserve(args.config, args.state, parse_json(read_small(args.record)))
            elif args.command == "finish":
                output = finish(args.config, args.state, args.attempt, parse_json(read_small(args.record)))
            elif args.command == "progress":
                if args.meaningful is None:
                    raise GuardError("--meaningful is required")
                output = progress(args.config, args.state, args.meaningful == "yes", args.evidence)
            else:
                output = status(args.config, args.state)
        print(json.dumps(output, sort_keys=True, allow_nan=False))
        return 0 if output["status"] == "READY_FOR_LIGHT_REVIEW" else 2
    except (GuardError, OSError, ValueError, TypeError) as exc:
        print(json.dumps(result(getattr(exc, "status", "BLOCKED_CONFIG"), reason=str(exc))))
        return 2


if __name__ == "__main__":
    sys.exit(main())
