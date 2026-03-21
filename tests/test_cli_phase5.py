from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from metaflow_clockwork.cli import main


class CLIPhase5Tests(unittest.TestCase):
    def test_validate_command_writes_summary_and_artifacts(self) -> None:
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmpdir:
            rc = main(
                [
                    "validate",
                    "--run-root",
                    tmpdir,
                    "--run-id",
                    "run_cli_1",
                    "--request-id",
                    "req-cli-1",
                ],
                stdout=output,
            )

            self.assertEqual(rc, 0)
            data = json.loads(output.getvalue())
            self.assertTrue(data["ok"])
            self.assertEqual(data["engine"]["summary"]["tick"], 1)
            self.assertFalse(data["temporary_run_root"])
            self.assertIn("ledger", data)
            self.assertIn("bridge", data)
            self.assertTrue(data["bridge"]["removed"])
            self.assertEqual(data["bridge"]["reason"], "qrbt_bridge_removed")
            self.assertEqual(data["bridge"]["qrbt"]["profile_id"], "default")
            self.assertEqual(data["bridge"]["qrbt"]["op"], "audit")

    def test_bridge_envelope_returns_removed_notice(self) -> None:
        output = io.StringIO()
        rc = main(
            [
                "bridge-envelope",
                "--profile-id",
                "profile-1",
                "--op",
                "audit",
                "--request-id",
                "req-bridge",
                "--actor",
                "metaflow",
                "--tag-id",
                "tag-bridge",
            ],
            stdout=output,
        )

        self.assertEqual(rc, 0)
        data = json.loads(output.getvalue())
        self.assertEqual(data["entry_point"], "bridge-envelope")
        self.assertTrue(data["removed"])
        self.assertEqual(data["reason"], "qrbt_bridge_removed")
        self.assertEqual(data["qrbt"]["profile_id"], "profile-1")
        self.assertEqual(data["qrbt"]["op"], "audit")

    def test_module_invocation_bridge_envelope_emits_json_notice(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "metaflow_clockwork.cli",
                "bridge-envelope",
                "--profile-id",
                "profile-1",
                "--op",
                "audit",
            ],
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        data = json.loads(result.stdout)
        self.assertEqual(data["entry_point"], "bridge-envelope")
        self.assertEqual(data["reason"], "qrbt_bridge_removed")


if __name__ == "__main__":
    unittest.main()
