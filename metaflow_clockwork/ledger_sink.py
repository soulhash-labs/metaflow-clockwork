#!/usr/bin/env python3
"""Append-only ledger sink for MetaFlow Clockwork."""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utc_iso(ts: float | None = None) -> str:
    return datetime.fromtimestamp(ts or time.time(), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _default_run_root() -> Path:
    explicit = os.environ.get("METAFLOW_CLOCKWORK_RUN_ROOT")
    if explicit and explicit.strip():
        return Path(explicit).expanduser()
    xdg_state_home = os.environ.get("XDG_STATE_HOME")
    if xdg_state_home and xdg_state_home.strip():
        return Path(xdg_state_home).expanduser() / "metaflow_clockwork" / "runs"
    return Path.home() / ".local" / "state" / "metaflow_clockwork" / "runs"


@dataclass
class LedgerEmitError(RuntimeError):
    message: str
    audit_record: Dict[str, Any] | None = None

    def __str__(self) -> str:
        return self.message


class LedgerEventSink:
    """Write MetaFlow events to local run ledgers."""

    def __init__(self, run_root: str | None = None, run_id: str = "metaflow"):
        self.run_root = Path(run_root).expanduser() if run_root else _default_run_root()
        self.run_id = str(run_id).strip() or "metaflow"
        self._last_hash = "0" * 64
        self._run_dir: Path | None = None
        self._events_path: Path | None = None
        self._chain_path: Path | None = None
        self._failures_path: Path | None = None
        self._ensure_init()

    @property
    def run_dir(self) -> Path:
        assert self._run_dir is not None
        return self._run_dir

    @property
    def events_path(self) -> Path:
        assert self._events_path is not None
        return self._events_path

    @property
    def chain_path(self) -> Path:
        assert self._chain_path is not None
        return self._chain_path

    @property
    def failures_path(self) -> Path:
        assert self._failures_path is not None
        return self._failures_path

    def _ensure_init(self) -> None:
        self._run_dir = self.run_root / self.run_id
        self._run_dir.mkdir(parents=True, exist_ok=True)
        self._events_path = self._run_dir / "events.jsonl"
        self._chain_path = self._run_dir / "events.sha256"
        self._failures_path = self._run_dir / "emit_failures.jsonl"
        self._last_hash = self._load_last_hash()

    def _load_last_hash(self) -> str:
        if not self.chain_path.exists():
            return "0" * 64
        try:
            lines = [line.strip() for line in self.chain_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        except Exception:
            return "0" * 64
        if not lines:
            return "0" * 64
        return lines[-1].split(" ", 1)[0]

    def _record_failure(
        self,
        *,
        stage: str,
        kind: str,
        run_id: str,
        request_id: str,
        level: str,
        data: Dict[str, Any],
        error: str,
        event_hash: str | None = None,
    ) -> Dict[str, Any]:
        record = {
            "ts_unix": time.time(),
            "ts_iso": _utc_iso(),
            "stage": stage,
            "kind": kind,
            "configured_run_id": self.run_id,
            "run_id": run_id,
            "request_id": request_id,
            "level": level,
            "error": error,
            "event_hash": event_hash,
            "data_preview": repr(data)[:1000],
        }
        try:
            with self.failures_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
        except Exception:
            pass
        return record

    def _build_event(
        self,
        *,
        kind: str,
        run_id: str,
        request_id: str,
        level: str,
        data: Dict[str, Any],
    ) -> tuple[dict, bytes, str]:
        event = {
            "ts": time.time(),
            "type": kind,
            "payload": {
                "run_id": run_id,
                "request_id": request_id,
                "level": level,
                "data": data,
            },
            "prev": self._last_hash,
        }
        raw = json.dumps(event, separators=(",", ":"), sort_keys=True).encode("utf-8")
        event_hash = _sha256_hex(raw)
        event["hash"] = event_hash
        return event, raw, event_hash

    def emit(self, kind: str, run_id: str, request_id: str, level: str, data: Dict[str, Any]) -> None:
        normalized_run_id = str(run_id).strip()
        if normalized_run_id != self.run_id:
            audit = self._record_failure(
                stage="run_id_mismatch",
                kind=kind,
                run_id=normalized_run_id,
                request_id=request_id,
                level=level,
                data=data,
                error=f"configured sink for run_id={self.run_id}, got run_id={normalized_run_id}",
            )
            raise LedgerEmitError("ledger_emit_failed:run_id_mismatch", audit)

        try:
            event, _, event_hash = self._build_event(
                kind=kind,
                run_id=normalized_run_id,
                request_id=request_id,
                level=level,
                data=data,
            )
        except Exception as exc:
            audit = self._record_failure(
                stage="serialize",
                kind=kind,
                run_id=normalized_run_id,
                request_id=request_id,
                level=level,
                data=data,
                error=str(exc),
            )
            raise LedgerEmitError(f"ledger_emit_failed:serialize:{exc}", audit) from exc

        try:
            with self.events_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, sort_keys=True) + "\n")
            with self.chain_path.open("a", encoding="utf-8") as handle:
                handle.write(f"{event_hash} {event['ts']} {kind}\n")
        except Exception as exc:
            audit = self._record_failure(
                stage="write",
                kind=kind,
                run_id=normalized_run_id,
                request_id=request_id,
                level=level,
                data=data,
                error=str(exc),
                event_hash=event_hash,
            )
            raise LedgerEmitError(f"ledger_emit_failed:write:{exc}", audit) from exc

        self._last_hash = event_hash
