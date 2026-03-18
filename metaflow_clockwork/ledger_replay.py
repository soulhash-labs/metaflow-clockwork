from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ZERO_HASH = "0" * 64


class LedgerReplayError(RuntimeError):
    pass


@dataclass(frozen=True)
class LedgerSummary:
    run_id: str
    run_dir: str
    events_path: str
    chain_path: str
    failures_path: str
    event_count: int
    event_kinds: dict[str, int]
    first_event_type: str | None
    last_event_type: str | None
    last_hash: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "events_path": self.events_path,
            "chain_path": self.chain_path,
            "failures_path": self.failures_path,
            "event_count": self.event_count,
            "event_kinds": dict(self.event_kinds),
            "first_event_type": self.first_event_type,
            "last_event_type": self.last_event_type,
            "last_hash": self.last_hash,
        }


@dataclass(frozen=True)
class LedgerVerificationResult:
    ok: bool
    run_id: str
    run_dir: str
    events_path: str
    chain_path: str
    failures_path: str
    event_count: int
    chain_line_count: int
    verified_count: int
    last_hash: str | None
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "events_path": self.events_path,
            "chain_path": self.chain_path,
            "failures_path": self.failures_path,
            "event_count": self.event_count,
            "chain_line_count": self.chain_line_count,
            "verified_count": self.verified_count,
            "last_hash": self.last_hash,
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class LedgerReplayResult:
    run_id: str
    run_dir: str
    events_path: str
    chain_path: str
    failures_path: str
    filtered_event_count: int
    event_count: int
    events: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "events_path": self.events_path,
            "chain_path": self.chain_path,
            "failures_path": self.failures_path,
            "filtered_event_count": self.filtered_event_count,
            "event_count": self.event_count,
            "events": list(self.events),
        }


@dataclass(frozen=True)
class _LedgerPaths:
    run_dir: Path
    events_path: Path
    chain_path: Path
    failures_path: Path


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _resolve_ledger_paths(path: str | Path) -> _LedgerPaths:
    candidate = Path(path)
    if candidate.is_dir():
        run_dir = candidate
    elif candidate.name in {"events.jsonl", "events.sha256", "emit_failures.jsonl"}:
        run_dir = candidate.parent
    else:
        raise LedgerReplayError(f"ledger_path_invalid path={candidate}")

    events_path = run_dir / "events.jsonl"
    chain_path = run_dir / "events.sha256"
    failures_path = run_dir / "emit_failures.jsonl"

    if not events_path.exists():
        raise LedgerReplayError(f"ledger_events_not_found path={events_path}")

    return _LedgerPaths(
        run_dir=run_dir,
        events_path=events_path,
        chain_path=chain_path,
        failures_path=failures_path,
    )


def _load_events(events_path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for index, raw_line in enumerate(events_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise LedgerReplayError(f"ledger_events_invalid_json line={index} detail={exc}") from exc
        if not isinstance(event, dict):
            raise LedgerReplayError(f"ledger_events_invalid_record line={index} type={type(event).__name__}")
        events.append(event)
    return events


def _load_chain_lines(chain_path: Path) -> list[str]:
    if not chain_path.exists():
        return []
    return [line.strip() for line in chain_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _derive_run_id(run_dir: Path, events: list[dict[str, Any]]) -> str:
    if not events:
        return run_dir.name
    payload = events[0].get("payload")
    if isinstance(payload, dict):
        candidate = str(payload.get("run_id") or "").strip()
        if candidate:
            return candidate
    return run_dir.name


def summarize_ledger(path: str | Path) -> LedgerSummary:
    paths = _resolve_ledger_paths(path)
    events = _load_events(paths.events_path)
    run_id = _derive_run_id(paths.run_dir, events)
    event_kinds = Counter(str(event.get("type") or "") for event in events)
    filtered_kinds = {kind: count for kind, count in sorted(event_kinds.items()) if kind}
    last_hash = None
    if events:
        last_hash = str(events[-1].get("hash") or "") or None

    return LedgerSummary(
        run_id=run_id,
        run_dir=str(paths.run_dir),
        events_path=str(paths.events_path),
        chain_path=str(paths.chain_path),
        failures_path=str(paths.failures_path),
        event_count=len(events),
        event_kinds=filtered_kinds,
        first_event_type=(str(events[0].get("type") or "") or None) if events else None,
        last_event_type=(str(events[-1].get("type") or "") or None) if events else None,
        last_hash=last_hash,
    )


def replay_ledger(path: str | Path, *, kind: str | None = None, limit: int | None = None) -> LedgerReplayResult:
    if limit is not None and limit <= 0:
        raise LedgerReplayError(f"ledger_replay_invalid_limit value={limit!r}")

    paths = _resolve_ledger_paths(path)
    events = _load_events(paths.events_path)
    run_id = _derive_run_id(paths.run_dir, events)

    filtered = [
        event for event in events
        if kind is None or str(event.get("type") or "") == kind
    ]
    if limit is not None:
        filtered = filtered[:limit]

    return LedgerReplayResult(
        run_id=run_id,
        run_dir=str(paths.run_dir),
        events_path=str(paths.events_path),
        chain_path=str(paths.chain_path),
        failures_path=str(paths.failures_path),
        filtered_event_count=len(filtered),
        event_count=len(events),
        events=filtered,
    )


def verify_ledger(path: str | Path) -> LedgerVerificationResult:
    paths = _resolve_ledger_paths(path)
    events = _load_events(paths.events_path)
    chain_lines = _load_chain_lines(paths.chain_path)
    run_id = _derive_run_id(paths.run_dir, events)

    errors: list[str] = []
    previous_hash = ZERO_HASH
    verified_count = 0

    if len(chain_lines) != len(events):
        errors.append(
            f"ledger_chain_length_mismatch expected_events={len(events)} actual_chain_lines={len(chain_lines)}"
        )

    for index, event in enumerate(events):
        event_type = str(event.get("type") or "")
        event_hash = str(event.get("hash") or "")
        event_prev = str(event.get("prev") or "")
        event_payload = event.get("payload")
        event_ts = event.get("ts")

        if not isinstance(event_payload, dict):
            errors.append(f"ledger_event_invalid_payload index={index} type={type(event_payload).__name__}")
            continue
        if not isinstance(event_ts, (int, float)):
            errors.append(f"ledger_event_invalid_ts index={index} value={event_ts!r}")
            continue

        expected_raw = {
            "ts": event_ts,
            "type": event_type,
            "payload": event_payload,
            "prev": event_prev,
        }
        expected_hash = _sha256_hex(
            json.dumps(expected_raw, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )

        if event_hash != expected_hash:
            errors.append(
                f"ledger_event_hash_mismatch index={index} expected={expected_hash} actual={event_hash}"
            )
        if event_prev != previous_hash:
            errors.append(
                f"ledger_prev_hash_mismatch index={index} expected={previous_hash} actual={event_prev}"
            )

        if index < len(chain_lines):
            parts = chain_lines[index].split(" ", 2)
            if len(parts) != 3:
                errors.append(f"ledger_chain_invalid_line index={index} value={chain_lines[index]!r}")
            else:
                chain_hash, chain_ts, chain_kind = parts
                if chain_hash != event_hash:
                    errors.append(
                        f"ledger_chain_hash_mismatch index={index} expected={event_hash} actual={chain_hash}"
                    )
                if chain_ts != str(event_ts):
                    errors.append(
                        f"ledger_chain_ts_mismatch index={index} expected={event_ts} actual={chain_ts}"
                    )
                if chain_kind != event_type:
                    errors.append(
                        f"ledger_chain_kind_mismatch index={index} expected={event_type} actual={chain_kind}"
                    )

        payload_run_id = str(event_payload.get("run_id") or "").strip()
        if payload_run_id and payload_run_id != run_id:
            errors.append(
                f"ledger_run_id_mismatch index={index} expected={run_id} actual={payload_run_id}"
            )

        previous_hash = event_hash or previous_hash
        verified_count += 1

    return LedgerVerificationResult(
        ok=not errors,
        run_id=run_id,
        run_dir=str(paths.run_dir),
        events_path=str(paths.events_path),
        chain_path=str(paths.chain_path),
        failures_path=str(paths.failures_path),
        event_count=len(events),
        chain_line_count=len(chain_lines),
        verified_count=verified_count,
        last_hash=(str(events[-1].get("hash") or "") or None) if events else None,
        errors=errors,
    )
