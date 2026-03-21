"""Public package surface for MetaFlow Clockwork."""

from typing import TextIO

from .engine import MetaTag, MetaTagType, ClockworkEngine
from .events import EventSink, NoOpEventSink, RecordingEventSink, RecordedEvent, StdoutEventSink
from .ledger_replay import (
    LedgerReplayError,
    LedgerReplayResult,
    LedgerSummary,
    LedgerVerificationResult,
    replay_ledger,
    summarize_ledger,
    verify_ledger,
)
from .ledger_sink import LedgerEmitError, LedgerEventSink
from .qrbt_bridge import QRBTBridge, QRBTBridgeError
from .run_spec import RunExecutionResult, RunSpec, RunSpecError, TagSpec, execute_run_spec, instantiate_run_spec, load_run_spec

__version__ = "0.1.0"


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    from .cli import main as _main

    return _main(argv, stdout)

__all__ = [
    "MetaTag",
    "MetaTagType",
    "ClockworkEngine",
    "EventSink",
    "NoOpEventSink",
    "RecordedEvent",
    "RecordingEventSink",
    "StdoutEventSink",
    "LedgerReplayError",
    "LedgerReplayResult",
    "LedgerSummary",
    "LedgerVerificationResult",
    "LedgerEmitError",
    "LedgerEventSink",
    "QRBTBridge",
    "QRBTBridgeError",
    "replay_ledger",
    "summarize_ledger",
    "verify_ledger",
    "RunExecutionResult",
    "RunSpec",
    "RunSpecError",
    "TagSpec",
    "execute_run_spec",
    "instantiate_run_spec",
    "load_run_spec",
    "main",
]
