# MetaFlow Clockwork

MetaFlow Clockwork is a small Aurora-local Python package for deterministic tag execution, Aurora-compatible ledger emission, and QRBT bridge payload formation.

## Package Surface

Import surface:

- `metaflow_clockwork.ClockworkEngine`
- `metaflow_clockwork.MetaTag`
- `metaflow_clockwork.MetaTagType`
- `metaflow_clockwork.RecordingEventSink`
- `metaflow_clockwork.LedgerEventSink`
- `metaflow_clockwork.QRBTBridge`

Executable entry points:

- `python -m metaflow_clockwork validate`
- `python -m metaflow_clockwork bridge-envelope --profile-id <profile> --op <op>`
- `python -m metaflow_clockwork spec-validate <path-to-spec.json>`
- `python -m metaflow_clockwork spec-run <path-to-spec.json>`
- `python -m metaflow_clockwork ledger-summary <run-dir-or-ledger-file>`
- `python -m metaflow_clockwork ledger-replay <run-dir-or-ledger-file>`
- `python -m metaflow_clockwork ledger-verify <run-dir-or-ledger-file>`
- `metaflow-clockwork validate`
- `metaflow-clockwork bridge-envelope --profile-id <profile> --op <op>`
- `metaflow-clockwork spec-validate <path-to-spec.json>`
- `metaflow-clockwork spec-run <path-to-spec.json>`
- `metaflow-clockwork ledger-summary <run-dir-or-ledger-file>`
- `metaflow-clockwork ledger-replay <run-dir-or-ledger-file>`
- `metaflow-clockwork ledger-verify <run-dir-or-ledger-file>`

## Install

Editable install:

```bash
pip install -e .
```

## Local Validation

The validation path is intentionally local and no-network by default.

Run:

```bash
python -m metaflow_clockwork validate
```

This validates:

- deterministic engine tick execution
- Aurora-style ledger file creation
- QRBT bridge envelope generation against the live `/api/openclaw/command` contract

To inspect the QRBT bridge envelope directly:

```bash
python -m metaflow_clockwork bridge-envelope --profile-id default --op audit
```

## Run-Spec Validation

Validate a local JSON run spec:

```bash
python -m metaflow_clockwork spec-validate ./examples/basic_harmonics.json
```

Example spec:

```json
{
  "version": 1,
  "tick_limit": 3,
  "root_tags": [
    {
      "tag_type": "gear",
      "functions": ["spawn_harmonics"],
      "data": {
        "frequency": 528
      }
    }
  ]
}
```

The validator applies defaults for:

- `run_id`
- `request_id`
- `tick_limit`
- `max_recursive_depth`

## Spec-Driven Local Execution

Execute a validated run spec into a local ledger-backed run directory:

```bash
python -m metaflow_clockwork spec-run ./examples/basic_harmonics.json --run-root /tmp/metaflow-runs
```

Optional execution overrides:

- `--tick-limit`
- `--run-id`
- `--request-id`

The command writes:

- `events.jsonl`
- `events.sha256`
- `emit_failures.jsonl`

under `<run_root>/<run_id>/`.

## Ledger Summary, Replay, And Verification

Summarize an emitted run ledger:

```bash
python -m metaflow_clockwork ledger-summary /tmp/metaflow-runs/run-phase7
```

Replay recorded events in ledger order:

```bash
python -m metaflow_clockwork ledger-replay /tmp/metaflow-runs/run-phase7 --kind metaflow.tick.summary --limit 2
```

Verify that `events.sha256` matches `events.jsonl`:

```bash
python -m metaflow_clockwork ledger-verify /tmp/metaflow-runs/run-phase7
```

These commands accept either:

- the run directory
- `events.jsonl`
- `events.sha256`
- `emit_failures.jsonl`

## Test Commands

```bash
python3 -m py_compile metaflow_clockwork/*.py tests/test_engine_phase2.py tests/test_ledger_sink_phase3.py tests/test_qrbt_bridge_phase4.py tests/test_cli_phase5.py tests/test_run_spec_phase6.py tests/test_ledger_replay_phase8.py tests/test_operator_phase9.py
python3 -m unittest -v tests.test_engine_phase2 tests.test_ledger_sink_phase3 tests.test_qrbt_bridge_phase4 tests.test_cli_phase5 tests.test_run_spec_phase6 tests.test_ledger_replay_phase8 tests.test_operator_phase9
python3 -m metaflow_clockwork validate
python3 -m metaflow_clockwork spec-validate ./examples/basic_harmonics.json
python3 -m metaflow_clockwork spec-run ./examples/basic_harmonics.json --run-root /tmp/metaflow-runs
python3 -m metaflow_clockwork ledger-summary /tmp/metaflow-runs/<run_id>
python3 -m metaflow_clockwork ledger-replay /tmp/metaflow-runs/<run_id> --kind metaflow.tick.summary
python3 -m metaflow_clockwork ledger-verify /tmp/metaflow-runs/<run_id>
```

## Operator Reference

Operator walkthrough and expected outcomes:

- [.planning/OPERATOR_GUIDE.md](/opt/aurora/repos/metaflow/.planning/OPERATOR_GUIDE.md)

## Authority Boundaries

- MetaFlow does not bypass QRBT or the gateway.
- Live QRBT invocation is formed as `/qrbtrun <profile_id> <op>`.
- The package-level validation path does not perform live network calls.
