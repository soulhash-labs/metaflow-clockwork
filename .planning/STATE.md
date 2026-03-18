# Planning State: MetaFlow Clockwork

**Date:** 2026-03-18
**Project:** MetaFlow Clockwork
**Current phase:** Phase 9 - Operator Docs And Hardening
**Overall status:** v1.0 foundation milestone is complete; v1.1 run-spec validation, spec-driven local execution, and replay/verification are complete, and final operator hardening is next.

## Phase Status

| Phase | Name | Status |
|------:|------|--------|
| 1 | Repo Hygiene And Planning Baseline | Completed |
| 2 | Engine And Event Determinism | Completed |
| 3 | Ledger Compatibility And Auditability | Completed |
| 4 | QRBT Bridge Contract Hardening | Completed |
| 5 | Packaging, Tests, And Release Readiness | Completed |
| 6 | Run-Spec Contract And Validation | Completed |
| 7 | Spec-Driven Local Execution | Completed |
| 8 | Ledger Replay And Verification | Completed |
| 9 | Operator Docs And Hardening | Planned |

## Notes

- Repo-local `.planning` remains the canonical planning baseline for the repo.
- `v1.0 Foundation Package` is recorded in `.planning/MILESTONES.md` as the closed baseline milestone.
- Deterministic engine behavior, ledger compatibility, live QRBT bridge alignment, and package entry points are validated baseline capabilities from v1.0.
- `.planning/RUN_SPEC_CONTRACT.md` now records the JSON run-spec schema, defaults, and function-binding rules for v1.1.
- `spec-validate` now validates local run specs and instantiates them against the registered function catalog without contacting QRBT.
- `spec-run` now executes validated run specs into local Aurora-style run directories without contacting QRBT.
- CLI execution can override `tick_limit`, `run_id`, and `request_id` while still preserving deterministic defaults from the spec contract.
- `tests/test_run_spec_phase6.py` now covers execution output, ledger artifact creation, and tick-limit override behavior in addition to Phase 6 validation cases.
- Replay and verification now exist as first-class local CLI commands over emitted Aurora-style run ledgers.
- `.planning/LEDGER_REPLAY_CONTRACT.md` records accepted input paths, replay filters, and verification semantics.
- `ledger-summary` reports run shape without mutating any files.
- `ledger-replay` returns recorded events in ledger order with optional event-type and limit filters.
- `ledger-verify` now recomputes event hashes and checks chain drift against `events.sha256`.
- The repo still has untracked local noise and `.srclight` artifacts that were intentionally left untouched.

## Next Action

- Start Phase 9 by tightening operator docs, examples, and final hardening around the v1.1 runtime surface.
