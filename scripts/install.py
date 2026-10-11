#!/usr/bin/env python3
"""Install the local workflow payload. No network, subprocesses, or package installs.

Python 3.11+ is required. Default: plan only. Use --apply to write; --check
performs static checks only and does not claim a running Codex session is ready.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import uuid
from datetime import datetime, timezone

try:
    import tomllib
except ImportError:
    sys.exit("Python 3.11+ is required. Do not install dependencies automatically; see BOOTSTRAP.md.")

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- BEGIN CODEX RESEARCH WORKFLOW -->"
END = "<!-- END CODEX RESEARCH WORKFLOW -->"
META = ".codex/research-workflow-install.json"
BACKUPS = ".codex/research-workflow-backups"
SETTINGS = {"enabled": True, "max_concurrent_threads_per_session": 3,
            "default_subagent_reasoning_effort": "high"}
IGNORE_BEGIN = "# BEGIN CODEX RESEARCH WORKFLOW"
IGNORE_END = "# END CODEX RESEARCH WORKFLOW"
IGNORE = f"{IGNORE_BEGIN}\n/{BACKUPS}/\n{IGNORE_END}"


class Conflict(Exception):
    """An input needs review; do not guess or overwrite it."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or any(p in ("..", ".git") for p in rel.parts):
        raise Conflict(f"Unsafe path: {relative!r}")
    p = root
    for part in rel.parts:
        p = p / part
        if p.is_symlink():
            raise Conflict(f"Refusing a symlink: {p}")
    if not p.resolve().is_relative_to(root.resolve()):
        raise Conflict(f"Path escapes the target: {relative}")
    return p


def read_bytes(path: Path) -> bytes | None:
    if not path.exists():
        return None
    if not path.is_file():
        raise Conflict(f"Expected a file: {path}")
    if path.stat().st_size > 2_000_000:
        raise Conflict(f"Unexpectedly large configuration file: {path}")
    return path.read_bytes()


def decode(data: bytes | None) -> str:
    try:
        return (data or b"").decode("utf-8")
    except UnicodeError as exc:
        raise Conflict("Expected UTF-8 configuration text") from exc


def load_toml(text: str, label: str) -> dict:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise Conflict(f"Invalid TOML in {label}: {exc}") from exc


def block(text: str, begin: str, end: str) -> tuple[int, int] | None:
    n, m = text.count(begin), text.count(end)
    if n == m == 0:
        return None
    if n != 1 or m != 1 or text.index(begin) >= text.index(end):
        raise Conflict(f"Malformed or repeated managed block: {begin}")
    return text.index(begin), text.index(end) + len(end)


def append_or_replace(text: str, content: str, begin: str, end: str) -> str:
    span = block(text, begin, end)
    if span:
        return text[:span[0]] + content + text[span[1]:]
    return text + ("\n\n" if text and not text.endswith("\n\n") else "") + content + "\n"


def merge_config(text: str) -> str:
    """Conservative text edit, followed by a full semantic TOML comparison.

    Unusual inline/dotted encodings fail closed instead of being reformatted.
    A Codex bootstrap session may perform a reviewed manual merge in that case.
    """
    before = load_toml(text, ".codex/config.toml")
    agents = before.get("agents", {})
    if not isinstance(agents, dict):
        raise Conflict("[agents] is not a table")
    if "engineer" in agents:
        raise Conflict("Legacy [agents.engineer] registration exists; review it before installing a standalone engineer")
    desired = copy.deepcopy(before)
    desired.setdefault("agents", {}).update(SETTINGS)
    desired["agents"].pop("max_threads", None)
    if before == desired:
        return text
    lines = text.splitlines(keepends=True)
    headers = [i for i, line in enumerate(lines)
               if re.match(r'^\s*\[\s*(?:agents|"agents"|\'agents\')\s*\]\s*(?:#.*)?$', line.rstrip())]
    if len(headers) > 1:
        raise Conflict("Ambiguous [agents] text; use a reviewed manual TOML merge")
    literals = {"enabled": "true", "max_concurrent_threads_per_session": "3",
                "default_subagent_reasoning_effort": '"high"'}
    if headers:
        start = headers[0] + 1
        stop = next((i for i in range(start, len(lines))
                     if re.match(r'^\s*\[', lines[i])), len(lines))
        section = lines[start:stop]
        for key in (*SETTINGS, "max_threads"):
            pattern = re.compile(r"^(\s*)" + re.escape(key) + r"\s*=\s*([^\r\n]*)(\r?\n)?$")
            indexes = [i for i, line in enumerate(section) if pattern.match(line)]
            if len(indexes) > 1 or (key in agents and not indexes):
                raise Conflict(f"Cannot safely edit agents.{key}; use a reviewed manual TOML merge")
            if key == "max_threads":
                if indexes:
                    section.pop(indexes[0])
                continue
            if indexes:
                i = indexes[0]
                old = section[i]
                comment = " #" + old.split("#", 1)[1].rstrip("\r\n") if "#" in old else ""
                section[i] = f"{key} = {literals[key]}{comment}\n"
            else:
                if section and not section[-1].endswith("\n"):
                    section[-1] += "\n"
                section.append(f"{key} = {literals[key]}\n")
        merged = "".join(lines[:start] + section + lines[stop:])
    else:
        if any(k in agents for k in (*SETTINGS, "max_threads")):
            raise Conflict("Inline/dotted agents settings need a reviewed manual merge")
        merged = text + ("\n\n" if text else "") + "[agents]\n"
        merged += "".join(f"{k} = {v}\n" for k, v in literals.items())
    after = load_toml(merged, "merged .codex/config.toml")
    if after != desired:
        raise Conflict("TOML merge would change unrelated settings; nothing was installed")
    return merged


def read_package() -> tuple[dict, dict, dict[str, bytes]]:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    legacy = json.loads((ROOT / "legacy-hashes.json").read_text(encoding="utf-8"))
    files = {}
    for item in manifest["files"]:
        data = safe_path(ROOT, item["source"]).read_bytes()
        if digest(data) != item["sha256"]:
            raise Conflict(f"Payload checksum mismatch: {item['source']}")
        safe_path(ROOT, item["destination"])
        files[item["destination"]] = data
    return manifest, legacy, files


def target_root(value: str) -> Path:
    raw = Path(value).expanduser().absolute()
    if raw.is_symlink():
        raise Conflict("Use a real project directory, not a symlink")
    target = raw.resolve()
    if not target.is_dir():
        raise Conflict("Target must be an existing project directory")
    homes = {Path.home().resolve(), Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).resolve()}
    if target == Path(target.anchor) or target in homes or target == Path.home().resolve() / ".codex":
        raise Conflict("Refusing a filesystem root, home, or Codex home as installation target")
    if target == ROOT or target.is_relative_to(ROOT) or ROOT.is_relative_to(target):
        raise Conflict("Keep this source checkout outside the target project")
    return target


def make_plan(target: Path, revision: str) -> tuple[list[tuple[str, bytes | None, bytes]], list[str]]:
    manifest, legacy, payload = read_package()
    previous_data = read_bytes(safe_path(target, META))
    previous = json.loads(decode(previous_data)) if previous_data else {}
    if previous and previous.get("package") != manifest["package"]:
        raise Conflict("Existing install metadata belongs to a different package")
    agents_dir = safe_path(target, ".codex/agents")
    if agents_dir.is_dir():
        for file in agents_dir.glob("*.toml"):
            if file.name == "engineer.toml":
                continue
            other = load_toml(decode(read_bytes(safe_path(target, str(file.relative_to(target))))), str(file))
            if other.get("name") == "engineer":
                raise Conflict(f"Duplicate project-scoped engineer role: {file.name}")
    tracked = previous.get("installed_hashes", {})
    changes, notices, hashes = [], [], {}
    for item in manifest["files"]:
        rel, mode = item["destination"], item["mode"]
        path = safe_path(target, rel)
        old = read_bytes(path)
        new = payload[rel]
        known = set(legacy.get(item.get("legacy_path", rel), []))
        if rel in tracked:
            known.add(tracked[rel])
        if mode == "agents-block":
            text = decode(old)
            content = BEGIN + "\n" + decode(new).rstrip() + "\n" + END
            span = block(text, BEGIN, END)
            if old is not None and digest(old) in known and not span:
                new = (content + "\n").encode()
            elif not span and text.startswith("# Research workflow"):
                raise Conflict("Unmanaged edited legacy AGENTS.md; migrate it manually, preserving project rules")
            else:
                if span and previous.get("agents_block_hash"):
                    actual = digest(text[span[0]:span[1]].encode())
                    if actual != previous["agents_block_hash"] and text[span[0]:span[1]] != content:
                        raise Conflict("Managed AGENTS.md block has local edits; review them before update")
                new = append_or_replace(text, content, BEGIN, END).encode()
        elif mode == "toml-merge":
            new = merge_config(decode(old)).encode() if old is not None else new
        elif mode == "create-only" and old is not None:
            new = old
            notices.append(f"PRESERVED existing {rel}")
        elif old is not None and old != new and digest(old) not in known:
            raise Conflict(f"Locally customized file: {rel}. Preserve and merge it manually; no force overwrite is provided")
        hashes[rel] = digest(new)
        if old != new:
            changes.append((rel, old, new))
    ignore_old = read_bytes(safe_path(target, ".gitignore"))
    ignore_new = append_or_replace(decode(ignore_old), IGNORE, IGNORE_BEGIN, IGNORE_END).encode()
    if ignore_old != ignore_new:
        changes.append((".gitignore", ignore_old, ignore_new))
    agents_new = next((new for rel, _, new in changes if rel == "AGENTS.md"),
                      read_bytes(safe_path(target, "AGENTS.md")) or b"")
    span = block(decode(agents_new), BEGIN, END)
    assert span is not None
    marker_hash = digest(decode(agents_new)[span[0]:span[1]].encode())
    metadata = {"package": manifest["package"], "version": manifest["version"],
                "source_revision": revision or previous.get("source_revision", "UNSPECIFIED"),
                "installed_hashes": hashes, "agents_block_hash": marker_hash,
                "runtime_status": "NOT_VERIFIED"}
    metadata_bytes = (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode()
    if previous_data != metadata_bytes:
        changes.append((META, previous_data, metadata_bytes))
    if read_bytes(safe_path(target, "AGENTS.override.md")):
        notices.append("ATTENTION: root AGENTS.override.md can mask AGENTS.md. BOOTSTRAP.md requires a reviewed merge into the active file")
    config = load_toml(decode(next((n for r, _, n in changes if r == ".codex/config.toml"),
                                  read_bytes(safe_path(target, ".codex/config.toml")) or b"")), "config")
    if config.get("agents", {}).get("default_subagent_model"):
        notices.append("ATTENTION: an existing default_subagent_model was preserved; inspect the effective engineer model")
    return changes, notices


def atomic_write(path: Path, data: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".workflow-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply_plan(target: Path, changes: list[tuple[str, bytes | None, bytes]]) -> str | None:
    if not changes:
        return None
    # Check the entire plan before any write, and recheck each file at replacement.
    for rel, old, _ in changes:
        if read_bytes(safe_path(target, rel)) != old:
            raise Conflict(f"File changed after planning: {rel}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    backup = safe_path(target, BACKUPS + "/" + stamp)
    backup.mkdir(parents=True, mode=0o700)
    os.chmod(backup, 0o700)
    records = []
    for rel, old, new in changes:
        records.append({"path": rel, "existed": old is not None,
                        "before_sha256": digest(old) if old is not None else None,
                        "after_sha256": digest(new)})
        if old is not None:
            dest = safe_path(backup, rel)
            atomic_write(dest, old, 0o600)
    atomic_write(backup / "RESTORE.json", (json.dumps(records, indent=2) + "\n").encode(), 0o600)
    print(f"BACKUP {backup}", flush=True)
    for rel, old, new in changes:
        path = safe_path(target, rel)
        if read_bytes(path) != old:
            raise Conflict(f"Concurrent edit at {rel}; some earlier files may be installed. Review backup {backup}")
        mode = stat.S_IMODE(path.stat().st_mode) if old is not None else 0o644
        atomic_write(path, new, mode)
    return str(backup)


def check(target: Path) -> int:
    manifest, _, payload = read_package()
    errors, notes = [], []
    for item in manifest["files"]:
        data = read_bytes(safe_path(target, item["destination"]))
        if data is None:
            errors.append(f"Missing {item['destination']}")
    config = load_toml(decode(read_bytes(safe_path(target, ".codex/config.toml"))), "project config")
    for key, desired in SETTINGS.items():
        if config.get("agents", {}).get(key) != desired:
            errors.append(f"agents.{key} must equal {desired!r}")
    if "max_threads" in config.get("agents", {}) or "engineer" in config.get("agents", {}):
        errors.append("Legacy agents.max_threads / agents.engineer registration requires review")
    agent = load_toml(decode(read_bytes(safe_path(target, ".codex/agents/engineer.toml"))), "engineer")
    for key in ("name", "description", "developer_instructions"):
        if not agent.get(key):
            errors.append(f"Missing custom-agent field {key}")
    if agent.get("name") != "engineer":
        errors.append("Custom-agent name must be engineer")
    if "model_reasoning_effort" in agent:
        errors.append("Remove pinned engineer.model_reasoning_effort to allow main's spawn selection")
    text = decode(read_bytes(safe_path(target, "AGENTS.md")))
    span = block(text, BEGIN, END)
    if span is None:
        errors.append("AGENTS.md managed workflow block is missing")
    else:
        content = text[span[0]:span[1]]
        expected = BEGIN + "\n" + decode(payload["AGENTS.md"]).rstrip() + "\n" + END
        if content != expected:
            notes.append("Local workflow block differs from payload; review its meaning manually")
    override = decode(read_bytes(safe_path(target, "AGENTS.override.md")))
    if override and decode(payload["AGENTS.md"]).strip() not in override:
        errors.append("Root AGENTS.override.md masks AGENTS.md; manually merge the workflow into the active override, preserving its restrictions")
    agents_dir = safe_path(target, ".codex/agents")
    if agents_dir.is_dir():
        for file in agents_dir.glob("*.toml"):
            if file.name == "engineer.toml":
                continue
            other = load_toml(decode(read_bytes(safe_path(target, str(file.relative_to(target))))), str(file))
            if other.get("name") == "engineer":
                errors.append(f"Duplicate project-scoped engineer role: {file.name}")
    for note in notes:
        print("REVIEW " + note)
    for error in errors:
        print("FAIL " + error)
    if errors:
        return 2
    print("PASS local file presence, TOML, role name, project defaults, and unpinned engineer effort")
    print("NOT_CHECKED effective global/profile overrides, trust, active instruction chain, runtime agent registration or actual spawn effort")
    print("NEXT restart Codex in the target project, then read .codex/VERIFY_SETUP.md")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Existing research project directory, not the source checkout")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="Write the reviewed installation plan")
    group.add_argument("--check", action="store_true", help="Static verification only")
    parser.add_argument("--source-revision", default="", help="Reviewed source commit or release identifier; never credentials")
    args = parser.parse_args()
    try:
        if args.source_revision and not re.fullmatch(r"[A-Za-z0-9._/+:-]{1,128}", args.source_revision):
            raise Conflict("Source revision must be a short commit/tag identifier without credentials or whitespace")
        target = target_root(args.target)
        if args.check:
            return check(target)
        changes, notes = make_plan(target, args.source_revision)
        for note in notes:
            print(note)
        for rel, old, _ in changes:
            print(("CREATE " if old is None else "UPDATE ") + rel)
        print(f"PLAN {len(changes)} changed files")
        if not args.apply:
            print("DRY_RUN no files written; review BOOTSTRAP.md and use --apply when ready")
            return 0
        apply_plan(target, changes)
        print("FILES_INSTALLED; runtime is NOT_VERIFIED")
        return check(target)
    except (Conflict, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"BLOCKED {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
