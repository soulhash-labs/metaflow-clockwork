# MetaFlow Ledger Contract

**Date:** 2026-03-18
**Status:** Phase 3 baseline

## Goal

Align MetaFlow Clockwork ledger emission with Aurora / QRBT run-ledger expectations closely enough that downstream tooling can reason about run state from `events.jsonl` and `events.sha256`.

## Run Layout

MetaFlow writes to:

```text
<run_root>/<run_id>/
  events.jsonl
  events.sha256
  emit_failures.jsonl   # best-effort failure audit evidence
```

Default `run_root`:

```text
/opt/aurora/var/ledger/runs
```

## Event Entry Shape

Each `events.jsonl` line is a single JSON object:

```json
{
  "ts": 1773799999.123,
  "type": "metaflow.tick.summary",
  "payload": {
    "run_id": "run_meta_1",
    "request_id": "req-1",
    "level": "info",
    "data": {
      "tick": 1,
      "spawned": 0
    }
  },
  "prev": "<previous hash or 64 zeroes>",
  "hash": "<sha256 of the event object before hash insertion>"
}
```

Rules:
- `type` is the canonical event type.
- `payload.run_id` must match the sink-configured `run_id`.
- `payload.request_id` and `payload.level` are always preserved.
- event-specific fields live under `payload.data`.
- `prev` is the previous chain hash, or 64 zeroes for the first event.
- `hash` is computed from the canonical JSON of the event before `hash` is inserted.

## Chain File Shape

Each `events.sha256` line is:

```text
<hash> <ts> <type>
```

This preserves the Aurora/QRBT pattern where run state can be inferred from the last event type in the chain.

## Failure Audit

If MetaFlow cannot serialize or persist an event, it writes a best-effort failure record to `emit_failures.jsonl`.

Failure records include:
- timestamp
- stage (`serialize`, `write`, `run_id_mismatch`)
- configured `run_id`
- requested `run_id`
- `request_id`
- `level`
- error string
- truncated `data_preview`
- `event_hash` when available

## Phase 3 Coverage

Covered by tests:
- event file emission
- chain continuation across sink reopen
- run-id drift rejection
- serialization failure audit evidence
