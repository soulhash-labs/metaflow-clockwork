from __future__ import annotations

import unittest

from metaflow_clockwork import QRBTBridge, QRBTBridgeError


class QRBTBridgeCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_trigger_run_raises_removed_error(self) -> None:
        bridge = QRBTBridge(qrbt_url="http://qrbt.test")

        with self.assertRaises(QRBTBridgeError) as ctx:
            await bridge.trigger_run(
                profile_id="profile-1",
                op="audit",
                args={},
                request_id="req-1",
            )

        self.assertIn("qrbt_bridge_removed", str(ctx.exception))
        self.assertIn("/qrbtrun profile-1 audit", str(ctx.exception))


class QRBTBridgePendingConfirmTests(unittest.TestCase):
    def test_emit_pending_confirm_returns_removed_notice(self) -> None:
        bridge = QRBTBridge(qrbt_url="http://qrbt.test")

        event = bridge.emit_pending_confirm(
            {
                "tag_id": "tag-1",
                "request_id": "req-5",
                "actor": "metaflow-worker",
                "qrbt": {
                    "profile_id": "profile-1",
                    "op": "audit",
                },
            }
        )

        self.assertTrue(event["removed"])
        self.assertEqual(event["reason"], "qrbt_bridge_removed")
        self.assertEqual(event["tag_id"], "tag-1")
        self.assertEqual(event["actor"], "metaflow-worker")
        self.assertEqual(event["qrbt"]["command"], "/qrbtrun profile-1 audit")
