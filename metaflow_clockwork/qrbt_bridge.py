from __future__ import annotations

from typing import Any


REMOVAL_DETAIL = (
    "QRBT bridge functionality is not shipped in the public MetaFlow Clockwork package. "
    "Legacy QRBT names remain only as compatibility notices."
)


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
    """Compatibility shim for the removed private QRBT bridge surface."""

    def __init__(
        self,
        qrbt_url: str | None = None,
        *,
        bridge_token: str | None = None,
        command_path: str = "/api/openclaw/command",
        timeout: float = 60.0,
        transport: Any | None = None,
    ) -> None:
        self.qrbt_url = qrbt_url
        self.bridge_token = bridge_token
        self.command_path = command_path
        self.timeout = timeout
        self.transport = transport

    @staticmethod
    def _build_command(profile_id: str | None, op: str | None) -> str | None:
        clean_profile_id = (profile_id or "").strip()
        clean_op = (op or "").strip()
        if not clean_profile_id or not clean_op:
            return None
        return f"/qrbtrun {clean_profile_id} {clean_op}"

    def emit_pending_confirm(self, tag_data: dict[str, Any]) -> dict[str, Any]:
        qrbt_spec = tag_data.get("qrbt") or {}
        profile_id = str(qrbt_spec.get("profile_id") or "").strip()
        op = str(qrbt_spec.get("op") or "").strip()
        return {
            "ok": False,
            "removed": True,
            "reason": "qrbt_bridge_removed",
            "detail": REMOVAL_DETAIL,
            "tag_id": tag_data.get("tag_id"),
            "request_id": tag_data.get("request_id"),
            "actor": (tag_data.get("actor") or "metaflow").strip() or "metaflow",
            "qrbt": {
                "profile_id": profile_id,
                "op": op,
                "command": self._build_command(profile_id, op),
            },
        }

    async def trigger_run(
        self,
        profile_id: str,
        op: str,
        args: dict[str, Any] | None,
        request_id: str,
        actor: str = "metaflow",
    ) -> dict[str, Any]:
        del args, request_id, actor
        raise QRBTBridgeError(
            "qrbt_bridge_removed",
            command=self._build_command(profile_id, op),
            detail=REMOVAL_DETAIL,
        )
