# Release Readiness

## Scope

Phase 5 closes the current MetaFlow Clockwork roadmap by documenting package entry points and the local validation path.

## Package Entry Points

- Module entry point:
  - `python -m metaflow_clockwork`
- Console script:
  - `metaflow-clockwork`

## Supported Commands

### `validate`

Runs a local package validation pass without making live network calls.

It verifies:

- engine import and single-tick execution
- ledger sink creation and Aurora-style run artifact writing
- QRBT bridge envelope formation against the live OpenClaw contract

### `bridge-envelope`

Outputs the exact QRBT/OpenClaw command envelope MetaFlow would form for:

- `/qrbtrun <profile_id> <op>`

### `spec-validate`

Validates a local JSON run spec, applies deterministic defaults, and confirms the spec can be instantiated against the current registered function catalog.

### `spec-run`

Executes a validated local JSON run spec into a ledger-backed run directory under the selected `run_root`.

## Validation Commands

```bash
python3 -m py_compile metaflow_clockwork/*.py tests/test_engine_phase2.py tests/test_ledger_sink_phase3.py tests/test_qrbt_bridge_phase4.py tests/test_cli_phase5.py
python3 -m py_compile metaflow_clockwork/*.py tests/test_engine_phase2.py tests/test_ledger_sink_phase3.py tests/test_qrbt_bridge_phase4.py tests/test_cli_phase5.py tests/test_run_spec_phase6.py
python3 -m unittest -v tests.test_engine_phase2 tests.test_ledger_sink_phase3 tests.test_qrbt_bridge_phase4 tests.test_cli_phase5 tests.test_run_spec_phase6
python3 -m metaflow_clockwork validate
python3 -m metaflow_clockwork spec-validate ./spec.json
python3 -m metaflow_clockwork spec-run ./spec.json --run-root /tmp/metaflow-runs
python3 -m metaflow_clockwork bridge-envelope --profile-id default --op audit
```

## Rollback Posture

This phase changes only local package metadata, entry points, and documentation.

Rollback is straightforward:

- revert `pyproject.toml`
- revert `README.md`
- revert `metaflow_clockwork/cli.py`
- revert `metaflow_clockwork/__main__.py`
- revert the related docs and tests

No live QRBT service configuration is changed by this phase.
