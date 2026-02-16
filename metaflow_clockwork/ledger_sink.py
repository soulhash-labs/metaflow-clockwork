#!/usr/bin/env python3
"""Ledger Event Sink for MetaFlow - writes to the same ledger format as Gateway"""
from __future__ import annotations
import os
import json
import time
import hashlib
from typing import Dict, Any

def _sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

class LedgerEventSink:
    """EventSink that writes to /opt/aurora/var/ledger/runs/<run_id>/events.jsonl"""
    
    def __init__(self, run_root: str = "/opt/aurora/var/ledger/runs", run_id: str = "metaflow"):
        self.run_root = run_root
        self.run_id = run_id
        self._last_hash = "0" * 64
        self._events_path = None
        self._chain_path = None
        self._ensure_init()
    
    def _ensure_init(self):
        run_dir = os.path.join(self.run_root, self.run_id)
        os.makedirs(run_dir, exist_ok=True)
        self._events_path = os.path.join(run_dir, "events.jsonl")
        self._chain_path = os.path.join(run_dir, "events.sha256")
        
        if os.path.exists(self._chain_path):
            with open(self._chain_path, "r") as f:
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]
                if lines:
                    self._last_hash = lines[-1].split(" ", 1)[0]
    
    def emit(self, kind: str, run_id: str, request_id: str, level: str, data: Dict[str, Any]) -> None:
        evt = {
            "ts": time.time(),
            "type": kind,
            "run_id": run_id,
            "request_id": request_id,
            "level": level,
            "payload": data,
            "prev": self._last_hash,
        }
        raw = json.dumps(evt, separators=(",", ":"), sort_keys=True).encode("utf-8")
        h = _sha256_hex(raw)
        self._last_hash = h
        evt["hash"] = h
        
        with open(self._events_path, "a") as f:
            f.write(json.dumps(evt) + "\n")
        with open(self._chain_path, "a") as f:
            f.write(f"{h} {evt['ts']} {kind}\n")
