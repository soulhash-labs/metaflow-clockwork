# QRBT Bridge Contract

## Scope

Phase 4 hardens MetaFlow's QRBT bridge against the current live QRBT authority surface.

MetaFlow does not call the gateway directly. It calls QRBT's OpenClaw bridge, and QRBT remains responsible for any downstream gateway confirmation behavior.

## Live Contract

- Base URL default: `http://127.0.0.1:7799`
- Method: `POST`
- Endpoint: `/api/openclaw/command`
- Request body:

```json
{
  "command": "/qrbtrun <profile_id> <op>"
}
```

- Request headers:
  - `X-Request-ID`
  - `X-QRBT-ACTOR`
  - optional `X-QRBT-BRIDGE-TOKEN`

## Accepted Inputs

- `profile_id` is required
- `op` is required
- non-empty `args` are rejected by MetaFlow before any HTTP call

This is deliberate. The current live `/qrbtrun` command accepts only `<profile_id> <op>`. Allowing silent extra arguments would create bridge drift.

## Success Normalization

`QRBTBridge.trigger_run(...)` preserves the top-level QRBT response and adds:

- `result_data`

`result_data` is the parsed JSON form of the QRBT `result` string. `run_id` and `qrbt_run_id` are backfilled from `result_data` when QRBT does not provide them at the top level.

## Failure Behavior

Bridge failures raise `QRBTBridgeError` with actionable context:

- transport failures
- non-200 HTTP responses
- non-JSON top-level payloads
- non-JSON `/qrbtrun` result payloads
- unsupported argument usage

This keeps Phase 4 aligned with:

- `BRG-01`: live QRBT contract alignment
- `BRG-02`: no direct gateway bypass
- `BRG-03`: actionable failures instead of silent drift
