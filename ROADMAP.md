# MetaFlow Clockwork Roadmap

## Current Baseline

The current public baseline already includes:

- deterministic recursive tag execution
- append-only event ledgers
- run-spec validation and execution
- ledger replay and verification
- local test and CLI smoke coverage
- public prompt hygiene, template, and self-contained execution doctrine docs

## Near-Term Priorities

### 1. Public Release Hardening

- finalize repository metadata once the public GitHub destination is known
- keep community-health and security files current
- maintain source and artifact validation in CI

### 2. Agent Contract Baseline

- define explicit role contracts
- define task/result schemas
- define bounded tool and state rules

This phase is docs/contracts first. It should not add runtime autonomy.

### 3. Prompt Contract Expansion

- add more role-specific prompt assets where the public package truly needs them
- keep prompt contracts explicit, versioned, and local-first
- do not expand execution authority while adding prompt assets

### 4. Website Relaunch

- publish a small public site or docs landing page for MetaFlow Clockwork
- keep historical lore separate from public product copy

## Non-Goals For The First Public Cut

- no second hosted orchestration layer
- no hidden memory or autonomous swarm runtime
- no public release under the bare `metaflow` package/repo name
- no internal research or private integrations
