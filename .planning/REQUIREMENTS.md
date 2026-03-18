# Requirements: MetaFlow Clockwork

**Defined:** 2026-03-17
**Core Value:** Provide a small Aurora-local execution package that emits deterministic events, writes ledger-compatible records, and integrates with QRBT through approved bridge semantics.

## v1 Requirements

### Engine Behavior

- [x] **ENG-01**: `MetaTag` execution and child spawning behave deterministically under test.
- [x] **ENG-02**: Recursive depth and exhaustion behavior are bounded and observable.
- [x] **ENG-03**: Engine tick summaries include enough structured data for debugging and audit use.

### Event And Ledger Compatibility

- [ ] **LED-01**: Event sink protocol supports no-op, stdout, and ledger-backed implementations without changing engine behavior.
- [ ] **LED-02**: Ledger sink writes `events.jsonl` and `events.sha256` in an Aurora-compatible run directory layout.
- [ ] **LED-03**: Event payloads preserve `run_id`, `request_id`, type, level, and payload data consistently.

### QRBT Integration

- [ ] **BRG-01**: Bridge payloads align with current live QRBT authority surfaces.
- [ ] **BRG-02**: Bridge integration does not bypass QRBT or gateway control boundaries.
- [ ] **BRG-03**: Bridge failure paths return actionable errors instead of silent drift.

### Repo Readiness

- [x] **REP-01**: Repo-local `.planning` remains canonical for future work.
- [ ] **REP-02**: Basic unit tests cover engine, ledger sink, and bridge payload formation.
- [ ] **REP-03**: Package entry points and validation steps are documented.

## Out Of Scope

| Feature | Reason |
|---------|--------|
| New operator shell | Violates Aurora control-boundary posture. |
| Direct gateway/daemon bypass | Must remain under QRBT and gateway authority. |
| Federation or remote orchestration | Deferred until local package behavior is stable. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ENG-01 | Phase 2: Engine And Event Determinism | Completed |
| ENG-02 | Phase 2: Engine And Event Determinism | Completed |
| ENG-03 | Phase 2: Engine And Event Determinism | Completed |
| LED-01 | Phase 3: Ledger Compatibility And Auditability | Planned |
| LED-02 | Phase 3: Ledger Compatibility And Auditability | Planned |
| LED-03 | Phase 3: Ledger Compatibility And Auditability | Planned |
| BRG-01 | Phase 4: QRBT Bridge Contract Hardening | Planned |
| BRG-02 | Phase 4: QRBT Bridge Contract Hardening | Planned |
| BRG-03 | Phase 4: QRBT Bridge Contract Hardening | Planned |
| REP-01 | Phase 1: Repo Hygiene And Planning Baseline | Completed |
| REP-02 | Phase 5: Packaging, Tests, And Release Readiness | Planned |
| REP-03 | Phase 5: Packaging, Tests, And Release Readiness | Planned |
