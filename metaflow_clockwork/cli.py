from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import TextIO

from .engine import ClockworkEngine, MetaTag, MetaTagType
from .events import RecordingEventSink
from .ledger_replay import replay_ledger, summarize_ledger, verify_ledger
from .ledger_sink import LedgerEventSink
from .qrbt_bridge import QRBTBridge
from .run_spec import execute_run_spec, instantiate_run_spec, load_run_spec


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="metaflow-clockwork")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate",
        help="Run a local no-network package validation pass",
    )
    validate.add_argument("--run-root", help="Ledger run root for validation output")
    validate.add_argument("--run-id", default="metaflow_validation")
    validate.add_argument("--request-id", default="validation-local")
    validate.add_argument("--profile-id", default="default")
    validate.add_argument("--op", default="audit")
    validate.set_defaults(handler=_handle_validate)

    bridge = subparsers.add_parser(
        "bridge-envelope",
        help="Emit a compatibility notice for the removed legacy QRBT bridge surface",
    )
    bridge.add_argument("--profile-id", required=True)
    bridge.add_argument("--op", required=True)
    bridge.add_argument("--request-id", default="validation-local")
    bridge.add_argument("--actor", default="metaflow")
    bridge.add_argument("--tag-id", default="tag-validation")
    bridge.set_defaults(handler=_handle_bridge_envelope)

    spec_validate = subparsers.add_parser(
        "spec-validate",
        help="Validate a local JSON run-spec and print the normalized contract",
    )
    spec_validate.add_argument("path", help="Path to the JSON run-spec file")
    spec_validate.set_defaults(handler=_handle_spec_validate)

    spec_run = subparsers.add_parser(
        "spec-run",
        help="Execute a validated local JSON run-spec into a ledger-backed run directory",
    )
    spec_run.add_argument("path", help="Path to the JSON run-spec file")
    spec_run.add_argument("--run-root", help="Ledger run root for execution output")
    spec_run.add_argument("--tick-limit", type=int, help="Override the spec tick limit")
    spec_run.add_argument("--run-id", help="Override the spec run id")
    spec_run.add_argument("--request-id", help="Override the spec request id")
    spec_run.set_defaults(handler=_handle_spec_run)

    ledger_summary = subparsers.add_parser(
        "ledger-summary",
        help="Summarize an emitted local ledger run",
    )
    ledger_summary.add_argument("path", help="Run directory or ledger file path")
    ledger_summary.set_defaults(handler=_handle_ledger_summary)

    ledger_replay = subparsers.add_parser(
        "ledger-replay",
        help="Replay recorded ledger events in order",
    )
    ledger_replay.add_argument("path", help="Run directory or ledger file path")
    ledger_replay.add_argument("--kind", help="Optional event type filter")
    ledger_replay.add_argument("--limit", type=int, help="Optional maximum number of events to return")
    ledger_replay.set_defaults(handler=_handle_ledger_replay)

    ledger_verify = subparsers.add_parser(
        "ledger-verify",
        help="Verify a ledger hash chain against emitted events",
    )
    ledger_verify.add_argument("path", help="Run directory or ledger file path")
    ledger_verify.set_defaults(handler=_handle_ledger_verify)

    return parser


def _resolve_run_root(value: str | None) -> tuple[str, bool]:
    if value:
        return value, False
    return tempfile.mkdtemp(prefix="metaflow_clockwork_"), True


def _legacy_qrbt_notice(*, profile_id: str, op: str, request_id: str, actor: str, tag_id: str) -> dict[str, object]:
    bridge = QRBTBridge()
    return bridge.emit_pending_confirm(
        {
            "tag_id": tag_id,
            "request_id": request_id,
            "actor": actor,
            "qrbt": {
                "profile_id": profile_id,
                "op": op,
            },
        }
    )


def _handle_validate(args: argparse.Namespace, stdout: TextIO) -> int:
    run_root, temporary_root = _resolve_run_root(args.run_root)
    run_id = str(args.run_id).strip() or "metaflow_validation"
    request_id = str(args.request_id).strip() or "validation-local"

    event_sink = RecordingEventSink()
    engine = ClockworkEngine(event_sink=event_sink, run_id=run_id, request_id=request_id)
    root = MetaTag(
        tag_id="validation-root",
        tag_type=MetaTagType.GEAR,
        data={"mode": "validation"},
    )
    engine.add_root_gear(root)
    summary = engine.tick()

    ledger_sink = LedgerEventSink(run_root=run_root, run_id=run_id)
    ledger_sink.emit(
        kind="metaflow.validation",
        run_id=run_id,
        request_id=request_id,
        level="info",
        data={"summary": summary},
    )

    result = {
        "ok": True,
        "entry_point": "validate",
        "run_id": run_id,
        "request_id": request_id,
        "temporary_run_root": temporary_root,
        "run_root": run_root,
        "engine": {
            "summary": summary,
            "recorded_events": len(event_sink.events),
        },
        "ledger": {
            "run_dir": str(ledger_sink.run_dir),
            "events_path": str(ledger_sink.events_path),
            "chain_path": str(ledger_sink.chain_path),
            "failures_path": str(ledger_sink.failures_path),
        },
        "bridge": _legacy_qrbt_notice(
            profile_id=args.profile_id,
            op=args.op,
            request_id=request_id,
            actor="metaflow",
            tag_id="validation-tag",
        ),
    }
    json.dump(result, stdout, indent=2, sort_keys=True)
    stdout.write("\n")
    return 0


def _handle_bridge_envelope(args: argparse.Namespace, stdout: TextIO) -> int:
    payload = _legacy_qrbt_notice(
        profile_id=args.profile_id,
        op=args.op,
        request_id=args.request_id,
        actor=args.actor,
        tag_id=args.tag_id,
    )
    payload["entry_point"] = "bridge-envelope"
    json.dump(payload, stdout, indent=2, sort_keys=True)
    stdout.write("\n")
    return 0


def _handle_spec_validate(args: argparse.Namespace, stdout: TextIO) -> int:
    engine = ClockworkEngine()
    spec = load_run_spec(args.path, engine=engine)
    root_tags = instantiate_run_spec(spec, engine=engine)
    payload = {
        "ok": True,
        "entry_point": "spec-validate",
        "spec": spec.to_dict(),
        "instantiated_root_tags": [tag.tag_id for tag in root_tags],
        "known_functions": sorted(engine.function_registry.keys()),
    }
    json.dump(payload, stdout, indent=2, sort_keys=True)
    stdout.write("\n")
    return 0


def _handle_spec_run(args: argparse.Namespace, stdout: TextIO) -> int:
    run_root, temporary_root = _resolve_run_root(args.run_root)
    spec = load_run_spec(args.path)
    result = execute_run_spec(
        spec,
        run_root=run_root,
        tick_limit=args.tick_limit,
        run_id=args.run_id,
        request_id=args.request_id,
    )
    payload = {
        "ok": True,
        "entry_point": "spec-run",
        "temporary_run_root": temporary_root,
        "spec_path": str(Path(args.path)),
        "execution": result.to_dict(),
    }
    json.dump(payload, stdout, indent=2, sort_keys=True)
    stdout.write("\n")
    return 0


def _handle_ledger_summary(args: argparse.Namespace, stdout: TextIO) -> int:
    summary = summarize_ledger(args.path)
    payload = {
        "ok": True,
        "entry_point": "ledger-summary",
        "summary": summary.to_dict(),
    }
    json.dump(payload, stdout, indent=2, sort_keys=True)
    stdout.write("\n")
    return 0


def _handle_ledger_replay(args: argparse.Namespace, stdout: TextIO) -> int:
    replay = replay_ledger(args.path, kind=args.kind, limit=args.limit)
    payload = {
        "ok": True,
        "entry_point": "ledger-replay",
        "replay": replay.to_dict(),
    }
    json.dump(payload, stdout, indent=2, sort_keys=True)
    stdout.write("\n")
    return 0


def _handle_ledger_verify(args: argparse.Namespace, stdout: TextIO) -> int:
    verification = verify_ledger(args.path)
    payload = {
        "ok": verification.ok,
        "entry_point": "ledger-verify",
        "verification": verification.to_dict(),
    }
    json.dump(payload, stdout, indent=2, sort_keys=True)
    stdout.write("\n")
    return 0


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    out = stdout or sys.stdout
    return args.handler(args, out)


if __name__ == "__main__":
    raise SystemExit(main())
