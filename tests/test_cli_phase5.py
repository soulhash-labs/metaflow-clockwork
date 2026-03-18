from __future__ import annotations

import io
import json
import tempfile
import unittest

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
                    "--profile-id",
                    "profile-1",
                    "--op",
                    "audit",
                ],
                stdout=output,
            )

            self.assertEqual(rc, 0)
            data = json.loads(output.getvalue())
            self.assertTrue(data["ok"])
            self.assertEqual(data["engine"]["summary"]["tick"], 1)
            self.assertFalse(data["temporary_run_root"])
            self.assertEqual(
                data["bridge"]["payload"]["body"]["command"],
                "/qrbtrun profile-1 audit",
            )

    def test_bridge_envelope_command_returns_live_contract_shape(self) -> None:
        output = io.StringIO()

        rc = main(
            [
                "bridge-envelope",
                "--profile-id",
                "profile-2",
                "--op",
                "review",
                "--request-id",
                "req-cli-2",
                "--actor",
                "metaflow-test",
                "--tag-id",
                "tag-cli-2",
            ],
            stdout=output,
        )

        self.assertEqual(rc, 0)
        data = json.loads(output.getvalue())
        self.assertEqual(data["action"], "qrbt.openclaw.command")
        self.assertEqual(data["tag_id"], "tag-cli-2")
        self.assertEqual(
            data["payload"]["body"]["command"],
            "/qrbtrun profile-2 review",
        )
        self.assertEqual(data["payload"]["headers"]["X-QRBT-ACTOR"], "metaflow-test")


if __name__ == "__main__":
    unittest.main()
