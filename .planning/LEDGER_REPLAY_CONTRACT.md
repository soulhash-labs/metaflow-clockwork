# Ledger Replay Contract

## Scope

Phase 8 adds read-side inspection over Aurora-style local run ledgers emitted by `LedgerEventSink`.

The contract is intentionally strict:

- replay reads exactly the files written by the Phase 3 sink
- verification recomputes event hashes using the same serialized fields as the sink
- chain drift is reported explicitly instead of being repaired or ignored

## Accepted Input Paths

Replay and verification commands accept any of:

- a run directory containing `events.jsonl`
- the `events.jsonl` file directly
- the `events.sha256` file directly
- the `emit_failures.jsonl` file directly

All paths resolve to the containing run directory.

## Commands

### `ledger-summary`

Returns summary information for a run ledger:

- `run_id`
- `event_count`
- `event_kinds`
- `first_event_type`
- `last_event_type`
- `last_hash`
- resolved ledger paths

### `ledger-replay`

Returns recorded events in ledger order.

Optional filters:

- `--kind <event-type>` limits output to a single event type
- `--limit <n>` bounds the number of returned events after filtering

Replay does not mutate ledger state.

### `ledger-verify`

Verifies:

- every `events.jsonl` record is valid JSON
- every record payload is hashable under the Phase 3 serialization contract
- `event.hash` matches the recomputed hash of `{ts,type,payload,prev}`
- `prev` fields form a continuous chain
- `events.sha256` line count matches event count
- each chain line matches the event hash, timestamp, and type at the same index
- all event payload `run_id` values match the ledger run id

## Failure Semantics

Verification returns a structured result with:

- `ok`
- `event_count`
- `chain_line_count`
- `verified_count`
- `last_hash`
- `errors`

Examples of explicit error strings:

- `ledger_event_hash_mismatch`
- `ledger_prev_hash_mismatch`
- `ledger_chain_length_mismatch`
- `ledger_chain_kind_mismatch`
- `ledger_run_id_mismatch`

## Non-Goals

- automatic repair of damaged chains
- partial recovery from malformed event records
- remote ledger reads
- QRBT submission or live execution during replay
