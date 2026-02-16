#!/usr/bin/env python3
"""
MetaFlow Clockwork - Event Sink Protocol
"""

from typing import Protocol, Dict, Any, Optional
from datetime import datetime

class EventSink(Protocol):
    """Protocol for emitting events to ledger/stream"""
    def emit(self, kind: str, run_id: str, request_id: str, level: str, data: Dict[str, Any]) -> None:
        ...

class NoOpEventSink:
    """No-op implementation for when no sink is configured"""
    def emit(self, kind: str, run_id: str, request_id: str, level: str, data: Dict[str, Any]) -> None:
        pass

class StdoutEventSink:
    """Print events to stdout for debugging"""
    def emit(self, kind: str, run_id: str, request_id: str, level: str, data: Dict[str, Any]) -> None:
        ts = datetime.now().isoformat()
        print(f"[{ts}] {kind} | run={run_id} | level={level} | data={data}")
