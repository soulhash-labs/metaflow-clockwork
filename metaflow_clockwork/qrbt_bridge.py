#!/usr/bin/env python3
"""
QRBT Bridge for MetaFlow Clockwork
Allows MetaFlow to trigger QRBT runs via policy.pending_confirm
"""

import httpx
from typing import Dict, Any, Optional

class QRBTBridge:
    def __init__(self, qrbt_url: str = "http://127.0.0.1:9130"):
        self.qrbt_url = qrbt_url
    
    async def trigger_run(self, profile_id: str, op: str, args: Dict[str, Any], request_id: str, actor: str = "metaflow") -> Dict[str, Any]:
        """Trigger a QRBT run - returns policy.pending_confirm style response"""
        payload = {
            "request_id": request_id,
            "actor": actor,
            "profile_id": profile_id,
            "op": op,
            "args": args,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{self.qrbt_url}/run", json=payload)
            r.raise_for_status()
            return r.json()
    
    def emit_pending_confirm(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Emit a pending confirm event for QRBT trigger"""
        qrbt_spec = tag_data.get("qrbt", {})
        return {
            "action": "qrbt.run",
            "payload": {
                "repo_id": qrbt_spec.get("repo_id"),
                "mode": qrbt_spec.get("mode", "audit"),
                "cycles": qrbt_spec.get("cycles", 2),
            },
            "tag_id": tag_data.get("tag_id"),
        }
