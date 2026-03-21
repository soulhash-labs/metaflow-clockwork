# Self-Contained Execution Doctrine for MetaFlow Clockwork

## Purpose

This document defines how work should execute when it claims to be
self-contained inside MetaFlow Clockwork.

It is a public-safe adaptation of Aurora's execution discipline for a local,
deterministic package context.

## Core Principle

Self-contained execution means:

- explicit inputs
- explicit local resources
- explicit boundaries
- explicit artifacts
- no hidden control plane

The package should not depend on ambient authority that is not declared in the
prompt or contract.

## Working Law

Trusted progress is strongest when:

- inputs are explicit
- execution is bounded
- state is local and inspectable
- outputs are replayable
- proof is concrete

Trusted progress collapses when:

- state is hidden
- authority is implicit
- scope widens mid-slice
- execution depends on ambient services
- outputs cannot be replayed or verified

## MetaFlow Operating Model

Good self-contained work looks like:

- inspect local inputs
- validate contracts before execution
- execute one bounded local slice
- emit ledger or validation artifacts
- verify the result

Bad self-contained work looks like:

- hidden background services
- undeclared network dependencies
- broad multi-plane missions
- mutable global state with no receipt
- no proof beyond "it seems fine"

## Sequence Discipline

Default sequence:

`inspect -> validate inputs -> execute -> emit artifacts -> verify -> report`

Do not skip the inspect step.  
Do not skip the verification step.  
Do not claim self-contained execution if the slice actually requires an
undeclared external service.

## Rules

1. One slice, one seam.
2. Declare exact inputs before execution.
3. Keep state local to the run, repo, or declared artifact path.
4. Bound recursion, iteration, and tool use explicitly.
5. Emit evidence for every material result.
6. Prefer deterministic local execution over ambient orchestration.
7. If external authority is required, declare it instead of hiding it.
8. Keep public docs aligned to what the repo actually implements.

## What Counts As A Hard Artifact

Acceptable artifacts include:

- a validated run spec
- a ledger file
- a verification result
- a deterministic summary
- a checked example prompt or contract file
- an explicit blocker with evidence

## Public Boundary

MetaFlow Clockwork is:

- a deterministic local runtime
- a contract surface
- a replayable ledger system

MetaFlow Clockwork is not:

- a hosted orchestrator
- a hidden swarm runtime
- a broker-backed control plane
- a wrapper around undeclared private infrastructure

## When External Authority Is Real

If a task genuinely requires external authority:

- name it explicitly
- narrow the boundary
- do not pretend the slice is self-contained

The honest output in that case is a declared dependency or blocker, not a vague
success claim.
