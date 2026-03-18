from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

from metaflow_clockwork import replay_ledger, summarize_ledger, verify_ledger
from metaflow_clockwork.cli import main
from metaflow_clockwork.run_spec import execute_run_spec, load_run_spec


class LedgerReplayPhase8Tests(unittest.TestCase):
    def _write_spec(self, root: Path, *, run_id: str = "run-phase8", request_id: str = "req-phase8") -> Path:
        path = root / "phase8_spec.json"
        path.write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "request_id": request_id,
                    "tick_limit": 2,
                    "root_tags": [
                        {
                            "tag_type": "gear",
                            "functions": ["spawn_harmonics"],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return path

    def _execute_sample_run(self, root: Path, *, run_id: str = "run-phase8") -> str:
        spec_path = self._write_spec(root, run_id=run_id, request_id=f"{run_id}-request")
        spec = load_run_spec(spec_path)
        result = execute_run_spec(spec, run_root=str(root))
        return result.run_dir

    def test_summarize_ledger_reports_run_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = self._execute_sample_run(Path(tmpdir))
            summary = summarize_ledger(run_dir)

        self.assertEqual(summary.run_id, "run-phase8")
        self.assertGreaterEqual(summary.event_count, 4)
        self.assertIn("metaflow.run.start", summary.event_kinds)
        self.assertIn("metaflow.run.complete", summary.event_kinds)
        self.assertEqual(summary.first_event_type, "metaflow.run.start")
        self.assertEqual(summary.last_event_type, "metaflow.run.complete")
        self.assertTrue(summary.last_hash)

    def test_replay_ledger_filters_by_kind_and_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = self._execute_sample_run(Path(tmpdir))
            replay = replay_ledger(run_dir, kind="metaflow.tick.summary", limit=1)

        self.assertEqual(replay.run_id, "run-phase8")
        self.assertEqual(replay.filtered_event_count, 1)
        self.assertEqual(replay.events[0]["type"], "metaflow.tick.summary")
        self.assertGreaterEqual(replay.event_count, replay.filtered_event_count)

    def test_verify_ledger_accepts_valid_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = self._execute_sample_run(Path(tmpdir))
            verification = verify_ledger(run_dir)

        self.assertTrue(verification.ok)
        self.assertEqual(verification.event_count, verification.chain_line_count)
        self.assertEqual(verification.verified_count, verification.event_count)
        self.assertEqual(verification.errors, [])

    def test_verify_ledger_detects_tampered_event_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(self._execute_sample_run(Path(tmpdir)))
            events_path = run_dir / "events.jsonl"
            events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            events[0]["payload"]["data"]["tick_limit"] = 999
            events_path.write_text("\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n", encoding="utf-8")

            verification = verify_ledger(run_dir)

        self.assertFalse(verification.ok)
        self.assertTrue(any("ledger_event_hash_mismatch" in error for error in verification.errors))

    def test_ledger_verify_cli_reports_tamper_clearly(self) -> None:
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(self._execute_sample_run(Path(tmpdir), run_id="run-phase8-cli"))
            chain_path = run_dir / "events.sha256"
            chain_lines = [line for line in chain_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            chain_lines[-1] = chain_lines[-1].replace("metaflow.run.complete", "metaflow.run.done")
            chain_path.write_text("\n".join(chain_lines) + "\n", encoding="utf-8")

            rc = main(["ledger-verify", str(run_dir)], stdout=output)

        self.assertEqual(rc, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["entry_point"], "ledger-verify")
        self.assertFalse(payload["verification"]["ok"])
        self.assertTrue(
            any("ledger_chain_kind_mismatch" in error for error in payload["verification"]["errors"])
        )

    def test_ledger_summary_cli_accepts_events_file_path(self) -> None:
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(self._execute_sample_run(Path(tmpdir), run_id="run-phase8-summary"))
            rc = main(["ledger-summary", str(run_dir / "events.jsonl")], stdout=output)

        self.assertEqual(rc, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["entry_point"], "ledger-summary")
        self.assertEqual(payload["summary"]["run_id"], "run-phase8-summary")
        self.assertGreaterEqual(payload["summary"]["event_count"], 4)


if __name__ == "__main__":
    unittest.main()
