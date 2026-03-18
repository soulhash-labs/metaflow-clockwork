from __future__ import annotations

import json
import unittest

import httpx

from metaflow_clockwork import QRBTBridge, QRBTBridgeError


class QRBTBridgePhase4Tests(unittest.IsolatedAsyncioTestCase):
    async def test_trigger_run_posts_live_openclaw_command(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.method, "POST")
            self.assertEqual(str(request.url), "http://qrbt.test/api/openclaw/command")
            self.assertEqual(request.headers["X-Request-ID"], "req-1")
            self.assertEqual(request.headers["X-QRBT-ACTOR"], "metaflow")
            self.assertEqual(request.headers["X-QRBT-BRIDGE-TOKEN"], "bridge-token")
            self.assertEqual(
                json.loads(request.content.decode("utf-8")),
                {"command": "/qrbtrun profile-1 audit"},
            )
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "request_id": "req-1",
                    "command": "/qrbtrun profile-1 audit",
                    "result": json.dumps(
                        {
                            "state": "accepted",
                            "run_id": "run-1",
                            "qrbt": {"run_id": "qrbt-run-1"},
                        }
                    ),
                },
            )

        bridge = QRBTBridge(
            qrbt_url="http://qrbt.test",
            bridge_token="bridge-token",
            transport=httpx.MockTransport(handler),
        )

        result = await bridge.trigger_run(
            profile_id="profile-1",
            op="audit",
            args={},
            request_id="req-1",
        )

        self.assertEqual(result["request_id"], "req-1")
        self.assertEqual(result["run_id"], "run-1")
        self.assertEqual(result["qrbt_run_id"], "qrbt-run-1")
        self.assertEqual(result["result_data"]["state"], "accepted")

    async def test_trigger_run_rejects_non_empty_args(self) -> None:
        bridge = QRBTBridge(qrbt_url="http://qrbt.test")

        with self.assertRaises(QRBTBridgeError) as ctx:
            await bridge.trigger_run(
                profile_id="profile-1",
                op="audit",
                args={"cycles": 2},
                request_id="req-2",
            )

        self.assertIn("unsupported_qrbtrun_args", str(ctx.exception))

    async def test_trigger_run_surfaces_http_detail(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(423, json={"detail": "Council approval pending"})

        bridge = QRBTBridge(
            qrbt_url="http://qrbt.test",
            transport=httpx.MockTransport(handler),
        )

        with self.assertRaises(QRBTBridgeError) as ctx:
            await bridge.trigger_run(
                profile_id="profile-1",
                op="audit",
                args={},
                request_id="req-3",
            )

        self.assertIn("bridge_http_error", str(ctx.exception))
        self.assertIn("status=423", str(ctx.exception))
        self.assertIn("Council approval pending", str(ctx.exception))

    async def test_trigger_run_rejects_unparseable_qrbtrun_result(self) -> None:
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "ok": True,
                    "request_id": "req-4",
                    "command": "/qrbtrun profile-1 audit",
                    "result": "not-json",
                },
            )

        bridge = QRBTBridge(
            qrbt_url="http://qrbt.test",
            transport=httpx.MockTransport(handler),
        )

        with self.assertRaises(QRBTBridgeError) as ctx:
            await bridge.trigger_run(
                profile_id="profile-1",
                op="audit",
                args={},
                request_id="req-4",
            )

        self.assertIn("unparseable_qrbtrun_result", str(ctx.exception))


class QRBTBridgePendingConfirmTests(unittest.TestCase):
    def test_emit_pending_confirm_uses_live_command_contract(self) -> None:
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

        self.assertEqual(
            event,
            {
                "action": "qrbt.openclaw.command",
                "payload": {
                    "method": "POST",
                    "endpoint": "/api/openclaw/command",
                    "body": {"command": "/qrbtrun profile-1 audit"},
                    "headers": {
                        "X-Request-ID": "req-5",
                        "X-QRBT-ACTOR": "metaflow-worker",
                    },
                },
                "tag_id": "tag-1",
            },
        )


if __name__ == "__main__":
    unittest.main()
