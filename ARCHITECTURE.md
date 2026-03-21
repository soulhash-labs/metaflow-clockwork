# MetaFlow Clockwork Architecture

## Overview

MetaFlow Clockwork is a deterministic local Python runtime for tagged execution, append-only event ledgers, and spec-driven local runs.

The current public package is intentionally small:

- no daemon
- no broker
- no worker pool
- no second hosted orchestration layer

## Runtime Components

### Clockwork Engine

`metaflow_clockwork.engine` executes `MetaTag` graphs in deterministic ticks and emits structured events.

### Event Sinks

`metaflow_clockwork.events` provides in-memory, stdout, and ledger-backed event sinks.

### Ledger Persistence

`metaflow_clockwork.ledger_sink` writes append-only `events.jsonl` and `events.sha256` artifacts for local audit and replay.

### Run-Spec Contract

`metaflow_clockwork.run_spec` validates and executes checked-in JSON run specs through registered functions and known tag types only.

### Replay And Verification

`metaflow_clockwork.ledger_replay` supports summary, replay, and hash-chain verification of recorded runs.

### Prompt And Doctrine Surface

The public prompt-framework surface lives under `prompts/` and includes:

- prompt hygiene guidance
- a reusable prompt template
- a self-contained execution doctrine
- a machine-readable role contract example
- a concrete example prompt

These files are authoring and governance assets, not a runtime orchestration
layer.

## Execution Model

Default usage is local and no-network:

1. validate or load a run spec
2. execute deterministic ticks
3. persist events to a local ledger
4. replay or verify the resulting artifacts

## Self-Contained Execution

MetaFlow's public execution posture is intentionally self-contained:

- explicit inputs
- explicit local resources
- explicit artifacts
- no hidden broker
- no second hosted control plane

If a task genuinely requires external authority, that dependency should be
declared instead of hidden behind a "local-first" claim.

## Public Boundaries

- The public package is a local runtime and contract surface, not a hosted orchestration service.
- Internal research and private integrations are intentionally excluded from this public repo.
- Legacy QRBT import and CLI names are retained only as compatibility notices. Live bridge execution is not part of the public package.
- Prompt and doctrine assets are public documentation and contracts, not autonomous runtime behavior.

## Naming

- distribution name: `metaflow-clockwork`
- import path: `metaflow_clockwork`
- CLI name: `metaflow-clockwork`

This project is not affiliated with Netflix Metaflow or the `metaflow` project on PyPI.
