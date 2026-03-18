# Operator Guide

## Scope

This guide freezes the minimum operator workflow for MetaFlow Clockwork v1.1.

The workflow is local-first and does not bypass QRBT authority.

## Recommended Flow

1. validate the package locally
2. validate a run spec
3. execute the run spec into a local run directory
4. summarize the emitted ledger
5. verify the emitted ledger chain
6. only then decide whether a separate QRBT handoff is needed

## Example Commands

Use the checked-in example spec:

```bash
python3 -m metaflow_clockwork validate
python3 -m metaflow_clockwork spec-validate ./examples/basic_harmonics.json
python3 -m metaflow_clockwork spec-run ./examples/basic_harmonics.json --run-root /tmp/metaflow-runs
python3 -m metaflow_clockwork ledger-summary /tmp/metaflow-runs/example_harmonics
python3 -m metaflow_clockwork ledger-verify /tmp/metaflow-runs/example_harmonics
```

Optional focused replay:

```bash
python3 -m metaflow_clockwork ledger-replay /tmp/metaflow-runs/example_harmonics --kind metaflow.tick.summary --limit 2
```

## Expected Outputs

`spec-run` writes:

- `events.jsonl`
- `events.sha256`
- `emit_failures.jsonl`

under `<run_root>/<run_id>/`.

`ledger-summary` should report:

- `run_id`
- `event_count`
- `event_kinds`
- `first_event_type`
- `last_event_type`
- `last_hash`

`ledger-verify` should report:

- `ok=true`
- matching `event_count` and `chain_line_count`
- no `errors`

## Failure Interpretation

If `ledger-verify` fails:

- treat the run ledger as suspect
- inspect the returned `errors`
- inspect `emit_failures.jsonl` if present
- do not assume the run is safe to hand off downstream without understanding the chain drift

## Boundary Reminder

- MetaFlow remains local-first in this milestone.
- QRBT remains the sovereign runtime boundary for live controlled execution.
- Example specs are deterministic package fixtures, not policy grants.
