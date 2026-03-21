from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from metaflow_clockwork import LedgerEmitError, LedgerEventSink


class LedgerSinkPhase3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.run_root = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_emit_writes_ledger_and_chain(self) -> None:
        sink = LedgerEventSink(run_root=str(self.run_root), run_id="run_meta_1")

        sink.emit(
            kind="metaflow.tick.summary",
            run_id="run_meta_1",
            request_id="req-1",
            level="info",
            data={"tick": 1, "spawned": 0},
        )

        events_path = self.run_root / "run_meta_1" / "events.jsonl"
        chain_path = self.run_root / "run_meta_1" / "events.sha256"
        self.assertTrue(events_path.exists())
        self.assertTrue(chain_path.exists())

        event = json.loads(events_path.read_text(encoding="utf-8").strip())
        self.assertEqual(event["type"], "metaflow.tick.summary")
        self.assertEqual(event["prev"], "0" * 64)
        self.assertEqual(
            event["payload"],
            {
                "run_id": "run_meta_1",
                "request_id": "req-1",
                "level": "info",
                "data": {"tick": 1, "spawned": 0},
            },
        )

        raw_without_hash = {
            "ts": event["ts"],
            "type": event["type"],
            "payload": event["payload"],
            "prev": event["prev"],
        }
        expected_hash = hashlib.sha256(
            json.dumps(raw_without_hash, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()
        self.assertEqual(event["hash"], expected_hash)

        chain_line = chain_path.read_text(encoding="utf-8").strip()
        self.assertEqual(chain_line, f"{expected_hash} {event['ts']} metaflow.tick.summary")

    def test_sink_resumes_previous_hash_chain(self) -> None:
        sink1 = LedgerEventSink(run_root=str(self.run_root), run_id="run_meta_2")
        sink1.emit("metaflow.tick", "run_meta_2", "req-1", "info", {"tick": 1})

        sink2 = LedgerEventSink(run_root=str(self.run_root), run_id="run_meta_2")
        sink2.emit("metaflow.tick.summary", "run_meta_2", "req-2", "info", {"tick": 2})

        events = [
            json.loads(line)
            for line in (self.run_root / "run_meta_2" / "events.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(events), 2)
        self.assertEqual(events[1]["prev"], events[0]["hash"])

    def test_run_id_mismatch_is_rejected_and_audited(self) -> None:
        sink = LedgerEventSink(run_root=str(self.run_root), run_id="run_meta_3")

        with self.assertRaises(LedgerEmitError) as ctx:
            sink.emit("metaflow.tick", "other_run", "req-1", "warn", {"tick": 1})

        self.assertIn("run_id_mismatch", str(ctx.exception))
        failure_lines = (
            self.run_root / "run_meta_3" / "emit_failures.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        failure = json.loads(failure_lines[-1])
        self.assertEqual(failure["stage"], "run_id_mismatch")
        self.assertEqual(failure["configured_run_id"], "run_meta_3")
        self.assertEqual(failure["run_id"], "other_run")

    def test_serialization_failure_preserves_audit_evidence(self) -> None:
        sink = LedgerEventSink(run_root=str(self.run_root), run_id="run_meta_4")

        with self.assertRaises(LedgerEmitError) as ctx:
            sink.emit("metaflow.tick", "run_meta_4", "req-1", "error", {"bad": {1, 2, 3}})

        self.assertIn("serialize", str(ctx.exception))
        failure_lines = (
            self.run_root / "run_meta_4" / "emit_failures.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        failure = json.loads(failure_lines[-1])
        self.assertEqual(failure["stage"], "serialize")
        self.assertEqual(failure["request_id"], "req-1")
        self.assertIn("{1, 2, 3}", failure["data_preview"])

    def test_default_run_root_honors_environment_override(self) -> None:
        with tempfile.TemporaryDirectory() as env_root:
            with mock.patch.dict(os.environ, {"METAFLOW_CLOCKWORK_RUN_ROOT": env_root}, clear=False):
                sink = LedgerEventSink(run_id="run_meta_5")

        self.assertEqual(sink.run_root, Path(env_root))


if __name__ == "__main__":
    unittest.main()
