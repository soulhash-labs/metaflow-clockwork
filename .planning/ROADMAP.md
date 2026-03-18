# Roadmap: MetaFlow Clockwork

**Project:** MetaFlow Clockwork
**Date:** 2026-03-17
**Planning Basis:** `PROJECT.md`, visible package sources, Aurora control-boundary ADRs
**Milestone Intent:** Make MetaFlow Clockwork a small, testable, ledger-compatible Aurora package that integrates with QRBT without bypassing existing authority.

## Phase 1: Repo Hygiene And Planning Baseline

**Goal:** Establish repo-local planning state, basic project intent, and explicit constraints before expanding runtime or bridge behavior.

**Observable success criteria:**
- Standard `.planning` files exist in the repo.
- Current package seams are documented.
- The next work items are phase-scoped instead of ad hoc.

## Phase 2: Engine And Event Determinism

**Goal:** Validate recursive engine behavior and event emission semantics so local runs are predictable and testable.

**Observable success criteria:**
- `MetaTag.tick()` behavior is covered by unit tests.
- Recursive spawn depth and exhaustion behavior are deterministic under test.
- Event emission paths are observable without relying on stdout inspection alone.

## Phase 3: Ledger Compatibility And Auditability

**Goal:** Ensure the ledger sink remains compatible with Aurora run-ledger expectations and produces durable event-chain artifacts.

**Observable success criteria:**
- `events.jsonl` and `events.sha256` emission is covered by tests.
- Event payload shape is documented and stable.
- Failure paths preserve useful audit evidence.

## Phase 4: QRBT Bridge Contract Hardening

**Goal:** Align bridge payloads and target endpoints with current live QRBT authority instead of stale assumptions.

**Observable success criteria:**
- Bridge contract is mapped against live QRBT surfaces.
- Any stale endpoint assumptions are corrected.
- Bridge behavior preserves QRBT and gateway authority boundaries.

## Phase 5: Packaging, Tests, And Release Readiness

**Goal:** Make the package easy to validate, install, and reuse inside Aurora workflows.

**Observable success criteria:**
- Package metadata and test entry points exist.
- Local validation steps are documented.
- Release/readiness notes exist for Aurora operators.
