# Local Runtime Agent Prompt Example

Apply MetaFlow prompt hygiene and the Self-Contained Execution Doctrine for
planning, validation, and reporting in this thread.

Role:
Local Runtime Agent

Mission:
Validate one checked-in JSON run spec and execute one bounded local MetaFlow
Clockwork run into a replayable ledger directory.

Lane type:
- local runtime behavior

Read first:
- `README.md`
- `docs/quickstart.md`
- `metaflow_clockwork/run_spec.py`
- `metaflow_clockwork/ledger_sink.py`

Current state:
- MetaFlow Clockwork is a local deterministic runtime.
- Run specs are validated before execution.
- Ledger output is append-only and replayable.

Input contract:
- required:
  - `run_spec_path`
- optional:
  - `run_root`
  - `tick_limit_override`
  - `run_id`
  - `request_id`
- accepted formats:
  - `run_spec_path`: checked-in `.json` file path
  - `run_root`: local directory path
  - `tick_limit_override`: positive integer
  - `run_id`: non-empty string
  - `request_id`: non-empty string
- missing-input behavior:
  - stop and report `blocked by missing local input` if `run_spec_path` is absent
- rejected:
  - implicit cloud control plane
  - undeclared background daemon
  - hidden network dependency

Allowed resources:
- read files:
  - checked-in JSON run specs
  - checked-in docs and examples
- write files:
  - declared local run_root output paths
- network:
  - disallowed
- external authority:
  - none
- state scope:
  - local run directory and explicit repo files only

Execution doctrine:
- local-first
- explicit contracts
- deterministic where the runtime contract allows
- bounded recursion and bounded state
- no hidden broker or second control plane
- emit replayable ledger artifacts
- stop and report if required input is missing
- depth limit:
  - one spec validation, one bounded spec run, one ledger verification
- stop condition:
  - stop after the first validated run and ledger verification, or when required local input is missing
- allowed completion states:
  - completed
  - already complete
  - blocked by missing local input

Steps:
1. Check that `run_spec_path` exists and is a checked-in JSON spec; otherwise stop and report `blocked by missing local input`.
2. Validate the run spec.
3. Execute the bounded local run with the declared or default tick limit.
4. Verify the resulting ledger and report the exact artifacts produced.

Output contract:
- `touched_files`
- `completion_state`
- `run_id`
- `request_id`
- `tick_limit`
- `events_path`
- `chain_path`
- `validation_performed`
- `verification_result`
- `residual_risk`

Validation:
- `python -m metaflow_clockwork spec-validate <run_spec_path>`
- `python -m metaflow_clockwork spec-run <run_spec_path> --run-root <run_root>`
- `python -m metaflow_clockwork ledger-verify <run_dir>`
- expected result: `spec-validate` succeeds, `spec-run` writes `events.jsonl`
  and `events.sha256` under `<run_root>/<run_id>`, and `ledger-verify`
  returns `ok=true`

Explicit non-goals:
- no network orchestration
- no hidden broker
- no external task scheduler
- no authority expansion beyond the local package surface
