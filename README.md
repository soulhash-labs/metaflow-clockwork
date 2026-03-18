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
- `metaflow-clockwork validate`
- `metaflow-clockwork bridge-envelope --profile-id <profile> --op <op>`
- `metaflow-clockwork spec-validate <path-to-spec.json>`

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
python -m metaflow_clockwork spec-validate ./spec.json
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

## Test Commands

```bash
python3 -m py_compile metaflow_clockwork/*.py tests/test_engine_phase2.py tests/test_ledger_sink_phase3.py tests/test_qrbt_bridge_phase4.py tests/test_cli_phase5.py tests/test_run_spec_phase6.py
python3 -m unittest -v tests.test_engine_phase2 tests.test_ledger_sink_phase3 tests.test_qrbt_bridge_phase4 tests.test_cli_phase5 tests.test_run_spec_phase6
python3 -m metaflow_clockwork validate
python3 -m metaflow_clockwork spec-validate ./spec.json
```

## Authority Boundaries

- MetaFlow does not bypass QRBT or the gateway.
- Live QRBT invocation is formed as `/qrbtrun <profile_id> <op>`.
- The package-level validation path does not perform live network calls.
