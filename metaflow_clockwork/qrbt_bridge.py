from __future__ import annotations

import json
import os
from typing import Any

import httpx


DEFAULT_QRBT_URL = "http://127.0.0.1:7799"
DEFAULT_COMMAND_PATH = "/api/openclaw/command"


class QRBTBridgeError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        command: str | None = None,
        status_code: int | None = None,
        detail: str | None = None,
    ) -> None:
        self.message = message
        self.command = command
        self.status_code = status_code
        self.detail = detail
        parts = [message]
        if status_code is not None:
            parts.append(f"status={status_code}")
        if command:
            parts.append(f"command={command}")
        if detail:
            parts.append(f"detail={detail}")
        super().__init__(" ".join(parts))


class QRBTBridge:
    """MetaFlow bridge that uses QRBT's live OpenClaw authority surface."""

    def __init__(
        self,
        qrbt_url: str | None = None,
        *,
        bridge_token: str | None = None,
        command_path: str = DEFAULT_COMMAND_PATH,
        timeout: float = 60.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.qrbt_url = (qrbt_url or os.environ.get("METAFLOW_QRBT_URL") or DEFAULT_QRBT_URL).rstrip("/")
        self.bridge_token = bridge_token if bridge_token is not None else os.environ.get("QRBT_BRIDGE_TOKEN")
        self.command_path = command_path
        self.timeout = timeout
        self.transport = transport

    def _build_qrbtrun_command(
        self,
        profile_id: str,
        op: str,
        args: dict[str, Any] | None,
    ) -> str:
        clean_profile_id = (profile_id or "").strip()
        clean_op = (op or "").strip()
        if not clean_profile_id:
            raise QRBTBridgeError("missing_profile_id")
        if not clean_op:
            raise QRBTBridgeError("missing_op")
        if args:
            raise QRBTBridgeError(
                "unsupported_qrbtrun_args",
                command=f"/qrbtrun {clean_profile_id} {clean_op}",
                detail=(
                    "live QRBT /qrbtrun accepts only <profile_id> <op>; "
                    f"got args={json.dumps(args, sort_keys=True)}"
                ),
            )
        return f"/qrbtrun {clean_profile_id} {clean_op}"

    def _command_headers(self, request_id: str, actor: str) -> dict[str, str]:
        headers = {
            "X-Request-ID": request_id,
            "X-QRBT-ACTOR": actor,
        }
        if self.bridge_token:
            headers["X-QRBT-BRIDGE-TOKEN"] = self.bridge_token
        return headers

    @staticmethod
    def _error_detail(response: httpx.Response) -> str:
        try:
            data = response.json()
        except Exception:
            text = response.text.strip()
            return text or "unknown_response"
        if isinstance(data, dict):
            detail = data.get("detail")
            if detail:
                return str(detail)
        return json.dumps(data, sort_keys=True)

    async def trigger_run(
        self,
        profile_id: str,
        op: str,
        args: dict[str, Any] | None,
        request_id: str,
        actor: str = "metaflow",
    ) -> dict[str, Any]:
        """Trigger a QRBT run via QRBT's live OpenClaw bridge."""

        command = self._build_qrbtrun_command(profile_id, op, args)
        payload = {"command": command}
        headers = self._command_headers(request_id, actor)

        try:
            async with httpx.AsyncClient(
                base_url=self.qrbt_url,
                timeout=self.timeout,
                transport=self.transport,
            ) as client:
                response = await client.post(self.command_path, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise QRBTBridgeError(
                "bridge_transport_error",
                command=command,
                detail=str(exc),
            ) from exc

        if response.status_code != 200:
            raise QRBTBridgeError(
                "bridge_http_error",
                command=command,
                status_code=response.status_code,
                detail=self._error_detail(response),
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise QRBTBridgeError(
                "bridge_invalid_json",
                command=command,
                detail=response.text.strip() or "empty_response",
            ) from exc

        if not isinstance(data, dict):
            raise QRBTBridgeError(
                "bridge_invalid_payload",
                command=command,
                detail=f"type={type(data).__name__}",
            )
        if not data.get("ok", False):
            raise QRBTBridgeError(
                "bridge_not_ok",
                command=command,
                detail=json.dumps(data, sort_keys=True),
            )

        raw_result = data.get("result")
        if not isinstance(raw_result, str):
            raise QRBTBridgeError(
                "unexpected_qrbtrun_result_type",
                command=command,
                detail=f"type={type(raw_result).__name__}",
            )
        try:
            result_data = json.loads(raw_result)
        except ValueError as exc:
            raise QRBTBridgeError(
                "unparseable_qrbtrun_result",
                command=command,
                detail=raw_result,
            ) from exc
        if not isinstance(result_data, dict):
            raise QRBTBridgeError(
                "unexpected_qrbtrun_result_shape",
                command=command,
                detail=f"type={type(result_data).__name__}",
            )

        normalized = dict(data)
        normalized["result_data"] = result_data
        if not normalized.get("run_id"):
            normalized["run_id"] = result_data.get("run_id")
        qrbt = result_data.get("qrbt")
        if isinstance(qrbt, dict) and not normalized.get("qrbt_run_id"):
            normalized["qrbt_run_id"] = qrbt.get("run_id")
        return normalized

    def emit_pending_confirm(self, tag_data: dict[str, Any]) -> dict[str, Any]:
        """Emit the live QRBT/OpenClaw command envelope for review."""

        qrbt_spec = tag_data.get("qrbt") or {}
        command = self._build_qrbtrun_command(
            str(qrbt_spec.get("profile_id") or ""),
            str(qrbt_spec.get("op") or ""),
            qrbt_spec.get("args"),
        )
        actor = (tag_data.get("actor") or "metaflow").strip() or "metaflow"
        request_id = (tag_data.get("request_id") or "").strip()
        return {
            "action": "qrbt.openclaw.command",
            "payload": {
                "method": "POST",
                "endpoint": self.command_path,
                "body": {"command": command},
                "headers": {
                    "X-Request-ID": request_id,
                    "X-QRBT-ACTOR": actor,
                },
            },
            "tag_id": tag_data.get("tag_id"),
        }
