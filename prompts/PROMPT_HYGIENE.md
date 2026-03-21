# MetaFlow Clockwork Prompt Hygiene

## Purpose

This document defines how prompts should be authored for MetaFlow Clockwork.

Prompt hygiene governs how work is described before execution starts.
Execution doctrine governs how work is carried out once the prompt is in hand.

Use this file to prevent:

- prompt drift
- hidden prerequisites
- accidental authority expansion
- cross-repo artifact confusion
- ambiguous inputs and outputs
- unbounded recursion or tool use

## Prompt Law

A MetaFlow prompt must describe one bounded, self-contained execution slice
grounded in current repo reality, with explicit inputs, explicit local
resources, explicit boundaries, and explicit proof of completion.

If those are not concrete, the prompt is not ready.

## Prompt Authoring Rules

### 1. Verify repo reality first

Do not write prompts from memory alone.

Verify:

- touched files
- touched examples
- touched tests
- whether the seam already exists
- whether the required artifact is actually in this repo

### 2. Separate current state from requested delta

Every prompt should distinguish:

- current state
- requested change

Do not blend them together.

### 3. Lock the lane type up front

Declare one primary lane type:

- local runtime behavior
- docs only
- contract/schema only
- example only
- test only

Do not mix unrelated lanes in one prompt.

### 4. Use real files and contracts only

Prefer exact repo paths and real package surfaces.

Do not present invented names, guessed helpers, or speculative interfaces as if
they already exist.

### 5. Declare the exact input contract

Prompts should state:

- required inputs
- optional inputs
- accepted formats
- missing-input behavior

### 6. Declare allowed resources and tool boundaries

Prompts should state:

- what local files may be read
- what local files may be written
- whether network access is allowed
- whether external authority is required

### 7. Keep execution self-contained

If a prompt claims to be local-first, it must not rely on:

- hidden brokers
- ambient daemons
- implicit cloud services
- undeclared external control planes

### 8. Require proof, not vibes

Every prompt should name:

- the exact validation command
- the exact artifact or output
- the exact condition that proves the slice is done

### 9. Bound recursion, state, and scope

If recursion, iteration, or tool use exists, the prompt should define:

- depth limit
- state scope
- stop condition
- non-goals

### 10. Allow already-complete or blocked outcomes

If a seam may already exist, the prompt must allow:

- `already complete`
- `blocked by missing local input`

Do not force unnecessary code change.

### 11. Keep prompts versioned and inspectable

Prompt assets should be:

- checked into the repo
- versioned
- human-readable

### 12. Keep public and private material separate

Public prompt assets must not depend on private/internal research or internal
service behavior that is intentionally out of scope for this repo.

## Mandatory Prompt Sections

Every substantial MetaFlow prompt should include:

- Role
- Mission
- Lane type
- Read first
- Current state
- Input contract
- Allowed resources
- Execution doctrine
- Steps
- Output contract
- Validation
- Explicit non-goals
