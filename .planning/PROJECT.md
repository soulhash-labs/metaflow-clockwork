# MetaFlow Clockwork

## What This Is

MetaFlow Clockwork is a small Aurora-local runtime package that models recursive clockwork-style execution with typed tags, event emission, ledger persistence, and QRBT trigger bridging.

The current codebase centers on four seams:

- `engine.py`: recursive tag execution and event emission
- `events.py`: event sink protocol and no-op/stdout implementations
- `ledger_sink.py`: append-only run ledger writer under `/opt/aurora/var/ledger/runs`
- `qrbt_bridge.py`: async QRBT trigger bridge for run submission

## Core Value

Aurora gets a lightweight programmable execution engine that can emit deterministic event traces, write ledger-compatible run records, and hand off controlled work into QRBT without inventing a new operator shell.

## Requirements

### Validated

- `MetaTag` and `ClockworkEngine` exist and support recursive ticking with event emission.
- Event sink protocol exists with no-op and stdout implementations.
- Ledger sink writes `events.jsonl` plus chain metadata in the Aurora run-ledger layout.
- QRBT bridge code exists for async run-trigger handoff.

### Active

- Stabilize package shape and repo hygiene for ongoing Aurora use.
- Define the intended QRBT handoff contract clearly enough to avoid drift from live QRBT APIs.
- Add basic test coverage for engine behavior, ledger emission, and bridge payload construction.
- Bring repo-local planning state in line with Aurora canonical `.planning` posture.

### Out Of Scope

- New QRBT authority or bypass paths.
- A standalone operator UI for MetaFlow.
- Host federation or remote orchestration beyond existing QRBT seams.

## Constraints

- Keep the package read-only with respect to QRBT authority except through approved bridge semantics.
- Preserve Aurora run-ledger compatibility.
- Do not invent a second control plane.
- Keep planning repo-local and explicit.
