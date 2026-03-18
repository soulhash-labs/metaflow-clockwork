from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

from metaflow_clockwork.cli import build_parser, main


class OperatorPhase9Tests(unittest.TestCase):
    def test_top_level_help_lists_operator_commands(self) -> None:
        help_text = build_parser().format_help()

        self.assertIn("spec-validate", help_text)
        self.assertIn("spec-run", help_text)
        self.assertIn("ledger-summary", help_text)
        self.assertIn("ledger-replay", help_text)
        self.assertIn("ledger-verify", help_text)

    def test_ledger_replay_help_lists_filter_flags(self) -> None:
        parser = build_parser()
        replay_parser = parser._subparsers._group_actions[0].choices["ledger-replay"]
        help_text = replay_parser.format_help()

        self.assertIn("--kind", help_text)
        self.assertIn("--limit", help_text)

    def test_checked_in_example_spec_runs_end_to_end(self) -> None:
        example_path = Path(__file__).resolve().parent.parent / "examples" / "basic_harmonics.json"
        self.assertTrue(example_path.exists())

        with tempfile.TemporaryDirectory() as tmpdir:
            validate_output = io.StringIO()
            run_output = io.StringIO()
            verify_output = io.StringIO()

            rc_validate = main(["spec-validate", str(example_path)], stdout=validate_output)
            self.assertEqual(rc_validate, 0)
            validate_output.seek(0)
            validate_payload = json.loads(validate_output.read())
            self.assertEqual(validate_payload["spec"]["run_id"], "example_harmonics")

            rc_run = main(["spec-run", str(example_path), "--run-root", tmpdir], stdout=run_output)
            self.assertEqual(rc_run, 0)
            run_output.seek(0)
            run_payload = json.loads(run_output.read())
            run_dir = Path(run_payload["execution"]["run_dir"])
            self.assertTrue((run_dir / "events.jsonl").exists())
            self.assertTrue((run_dir / "events.sha256").exists())

            rc_verify = main(["ledger-verify", str(run_dir)], stdout=verify_output)
            self.assertEqual(rc_verify, 0)
            verify_output.seek(0)
            verify_payload = json.loads(verify_output.read())
            self.assertTrue(verify_payload["verification"]["ok"])


if __name__ == "__main__":
    unittest.main()
