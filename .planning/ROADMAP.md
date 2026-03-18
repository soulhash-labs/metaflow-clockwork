# Roadmap: MetaFlow Clockwork

**Project:** MetaFlow Clockwork
**Date:** 2026-03-18
**Planning Basis:** `PROJECT.md`, `MILESTONES.md`, visible package sources, Aurora control-boundary ADRs
**Current Milestone:** v1.1 Spec-Driven Execution And Replay
**Milestone Intent:** Make MetaFlow Clockwork practical for operators by supporting declarative local run specs and first-class replay/verification of emitted ledgers without widening QRBT authority.

## Shipped Baseline

**v1.0 Foundation Package:** completed in Phases 1-5

Delivered:
- deterministic engine and event observation
- Aurora-compatible ledger writing
- live QRBT bridge alignment
- package metadata and local validation entry points

## Phase 6: Run-Spec Contract And Validation

**Goal:** Define a stable local run-spec contract that binds only to known tag types and registered functions.

**Observable success criteria:**
- A run-spec file format is documented.
- Spec validation rejects unknown tag types and unknown function names.
- Deterministic execution defaults are explicit and testable.

## Phase 7: Spec-Driven Local Execution

**Goal:** Execute MetaFlow runs directly from validated run-spec files into local Aurora-style run directories.

**Observable success criteria:**
- CLI can run a spec file with a bounded tick count.
- Spec-driven runs write `events.jsonl` and `events.sha256`.
- Execution stays local and does not contact QRBT by default.

## Phase 8: Ledger Replay And Verification

**Goal:** Add first-class replay and chain-verification tooling for emitted run ledgers.

**Observable success criteria:**
- CLI can summarize and replay ledger events in recorded order.
- Chain verification can detect mismatches between `events.jsonl` and `events.sha256`.
- Replay behavior is covered by local tests.

**Status:** Completed

## Phase 9: Operator Docs And Hardening

**Goal:** Close the milestone with operator-facing docs, examples, and test coverage for the new runtime surface.

**Observable success criteria:**
- README examples match the shipped CLI behavior.
- Tests cover run-spec validation, local execution, and replay/verification.
- Release/readiness notes are updated for the new commands.

**Status:** Completed
