# Milestones: MetaFlow Clockwork

## v1.0 Foundation Package

**Status:** Completed on 2026-03-18

**Shipped scope:**
- deterministic engine behavior and structured tick summaries
- recording and ledger-backed event sinks
- Aurora-style `events.jsonl` / `events.sha256` ledger output
- live QRBT bridge alignment to `/api/openclaw/command`
- package metadata, CLI entry points, and local release-readiness validation

**Phases:**
- Phase 1: Repo Hygiene And Planning Baseline
- Phase 2: Engine And Event Determinism
- Phase 3: Ledger Compatibility And Auditability
- Phase 4: QRBT Bridge Contract Hardening
- Phase 5: Packaging, Tests, And Release Readiness

## v1.1 Spec-Driven Execution And Replay

**Status:** Completed on 2026-03-18

**Goal:** Add declarative local run specs, deterministic spec execution, and first-class replay/verification tooling without widening QRBT authority.

**Shipped scope:**
- run-spec schema and validation
- CLI execution from run-spec files
- ledger replay and chain verification
- tests and docs for the new operator-facing runtime surface
- checked-in example spec and operator guide
