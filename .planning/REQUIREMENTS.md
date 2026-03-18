# Requirements: MetaFlow Clockwork

**Defined:** 2026-03-18
**Core Value:** Provide a small Aurora-local execution package that emits deterministic events, writes ledger-compatible records, and integrates with QRBT through approved bridge semantics.

## v1.1 Requirements

### Run Specs

- [x] **SPEC-01**: Operator can define root tags, static tag data, and registered function names in a local run-spec file.
- [x] **SPEC-02**: Package validates run-spec files and rejects unknown tag types or unknown function bindings before execution starts.
- [x] **SPEC-03**: Spec parsing preserves deterministic defaults for `run_id`, `request_id`, recursive depth, and tick limits.

### Local Execution

- [x] **EXEC-01**: CLI can execute a validated run-spec into a named local run directory without contacting QRBT.
- [x] **EXEC-02**: Spec-driven execution writes Aurora-style ledger artifacts for the resulting run.
- [x] **EXEC-03**: Operator can bound execution by an explicit tick limit from the CLI or run spec.

### Replay And Verification

- [x] **REPL-01**: Operator can inspect a run ledger and get summary information including run id, event count, and event kinds.
- [x] **REPL-02**: Operator can replay ledger events in recorded order from the CLI.
- [x] **REPL-03**: Package can verify `events.sha256` against `events.jsonl` and report mismatches clearly.

### Release Readiness

- [x] **OPS-01**: Unit tests cover run-spec validation, spec-driven execution, and replay/verification behavior.
- [x] **OPS-02**: CLI help and README examples cover the new spec and replay commands accurately.

## v1.2 Requirements

### Snapshot And Resume

- **SNAP-01**: Operator can persist engine state snapshots and resume execution from them.
- **SNAP-02**: Snapshot contents preserve enough state to reproduce subsequent ticks deterministically.

### QRBT Runtime Integration

- **QINT-01**: MetaFlow can submit validated local run artifacts into QRBT review or run workflows without bypassing authority boundaries.
- **QINT-02**: Host-level integration tests cover the MetaFlow-to-QRBT handoff against a live Aurora host.

## Out Of Scope

| Feature | Reason |
|---------|--------|
| Arbitrary Python code embedded in run-spec files | Would weaken deterministic execution and auditability. |
| Direct QRBT or gateway execution during spec runs | This milestone stays local-first and does not widen authority boundaries. |
| Federation or remote orchestration | Deferred until spec execution and replay are stable locally. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SPEC-01 | Phase 6: Run-Spec Contract And Validation | Completed |
| SPEC-02 | Phase 6: Run-Spec Contract And Validation | Completed |
| SPEC-03 | Phase 6: Run-Spec Contract And Validation | Completed |
| EXEC-01 | Phase 7: Spec-Driven Local Execution | Completed |
| EXEC-02 | Phase 7: Spec-Driven Local Execution | Completed |
| EXEC-03 | Phase 7: Spec-Driven Local Execution | Completed |
| REPL-01 | Phase 8: Ledger Replay And Verification | Completed |
| REPL-02 | Phase 8: Ledger Replay And Verification | Completed |
| REPL-03 | Phase 8: Ledger Replay And Verification | Completed |
| OPS-01 | Phase 9: Operator Docs And Hardening | Completed |
| OPS-02 | Phase 9: Operator Docs And Hardening | Completed |

**Coverage:**
- v1.1 requirements: 11 total
- Completed: 11
- Pending: 0
- Unmapped: 0
