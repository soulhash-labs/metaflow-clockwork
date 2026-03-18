#!/usr/bin/env python3
"""
MetaFlow Clockwork - Event Sink Protocol
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Dict, Any, List

class EventSink(Protocol):
    """Protocol for emitting events to ledger/stream"""
    def emit(self, kind: str, run_id: str, request_id: str, level: str, data: Dict[str, Any]) -> None:
        ...


@dataclass
class RecordedEvent:
    kind: str
    run_id: str
    request_id: str
    level: str
    data: Dict[str, Any]

class NoOpEventSink:
    """No-op implementation for when no sink is configured"""
    def emit(self, kind: str, run_id: str, request_id: str, level: str, data: Dict[str, Any]) -> None:
        pass


class RecordingEventSink:
    """Collect events in memory so engine behavior is testable without stdout."""
    def __init__(self):
        self.events: List[RecordedEvent] = []

    def emit(self, kind: str, run_id: str, request_id: str, level: str, data: Dict[str, Any]) -> None:
        self.events.append(
            RecordedEvent(
                kind=kind,
                run_id=run_id,
                request_id=request_id,
                level=level,
                data=dict(data),
            )
        )

class StdoutEventSink:
    """Print events to stdout for debugging"""
    def emit(self, kind: str, run_id: str, request_id: str, level: str, data: Dict[str, Any]) -> None:
        ts = datetime.now().isoformat()
        print(f"[{ts}] {kind} | run={run_id} | level={level} | data={data}")
