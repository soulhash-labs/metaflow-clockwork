# MetaFlow Clockwork

## Current Milestone: v1.1 Spec-Driven Execution And Replay

**Goal:** Make MetaFlow Clockwork runnable from declarative local specs and inspectable from its own Aurora-style ledgers without widening QRBT authority.

**Target features:**
- Load root tags and registered function bindings from local run-spec files.
- Execute spec-defined runs through the package CLI into deterministic ledger-backed run directories.
- Replay and verify existing run ledgers for local debugging and audit.

## What This Is

MetaFlow Clockwork is a small Aurora-local runtime package that models recursive clockwork-style execution with typed tags, event emission, ledger persistence, and QRBT trigger bridging. The validated v1.0 baseline is now packaged and testable; the next milestone extends it into a practical operator runtime with declarative run specs and replay tooling.

The current codebase centers on five seams:

- `engine.py`: recursive tag execution and event emission
- `events.py`: event sink protocol and recording/no-op/stdout implementations
- `ledger_sink.py`: append-only run ledger writer under `/opt/aurora/var/ledger/runs`
- `qrbt_bridge.py`: async QRBT trigger bridge for run submission
- `cli.py`: local package validation and bridge-envelope entry points

## Core Value

Aurora gets a lightweight programmable execution engine that can emit deterministic event traces, write ledger-compatible run records, and hand off controlled work into QRBT without inventing a new operator shell.

## Requirements

### Validated

- ✓ `MetaTag` and `ClockworkEngine` support deterministic recursive ticking with structured event emission — v1.0
- ✓ Event sink protocol supports no-op, stdout, recording, and ledger-backed execution paths — v1.0
- ✓ Ledger sink writes `events.jsonl` and `events.sha256` in the Aurora run-ledger layout with failure audit evidence — v1.0
- ✓ QRBT bridge aligns to the live `/api/openclaw/command` seam without bypassing QRBT or gateway authority — v1.0
- ✓ Package metadata, CLI entry points, and local release-readiness validation are documented and tested — v1.0

### Active

- Add declarative run-spec loading for root tags, tag data, and registered function names.
- Add CLI execution from run-spec files into deterministic local ledger directories.
- Add ledger replay and chain-verification tooling for local debugging and audit.

### Out Of Scope

- New QRBT authority or bypass paths.
- A standalone operator UI for MetaFlow.
- Host federation or remote orchestration beyond existing QRBT seams.
- Arbitrary executable code embedded in run-spec files.

## Context

- v1.0 shipped as a bounded package milestone on 2026-03-18 with phases 1-5 complete.
- The runtime can now execute deterministic tags, write Aurora-style ledgers, and form live QRBT bridge envelopes, but it still requires handwritten Python construction for most runs.
- The next practical gap is operator usability: local declarative run setup and first-class replay/inspection of emitted ledgers.

## Constraints

- Keep the package read-only with respect to QRBT authority except through approved bridge semantics.
- Preserve Aurora run-ledger compatibility.
- Do not invent a second control plane.
- Keep planning repo-local and explicit.
- Keep spec execution limited to registered functions and known tag types.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| v1.0 remains the validated baseline | Prevents new runtime scope from rewriting the closed foundation milestone | ✓ Good |
| v1.1 focuses on local spec execution and replay, not new authority surfaces | Highest operator payoff without widening QRBT control boundaries | — Pending |
| Run specs will bind only to registered functions | Keeps local execution deterministic and auditable | — Pending |

---
*Last updated: 2026-03-18 after milestone v1.1 start*
