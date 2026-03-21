# MetaFlow Clockwork Prompt Template v1

## Purpose

This template turns MetaFlow prompt hygiene and the Self-Contained Execution
Doctrine into a reusable prompt shape for public repo work.

Use it for:

- one bounded runtime slice
- one bounded docs slice
- one bounded contract or example slice
- one bounded validation slice

Do not use it to hide a broad, multi-plane mission.

## Minimal Header

```text
Read first:
- <exact repo docs>
- <exact package files if needed>

Apply MetaFlow prompt hygiene and the Self-Contained Execution Doctrine for
planning, edits, validation, and reporting in this thread.
```

## Reusable Template

```text
Role:
<one role name>

Mission:
<one sentence naming the one missing seam>

Lane type:
- <choose one>

Read first:
- <exact repo files only>

Current state:
- <only proven facts>

Input contract:
- required:
  - <input>
- optional:
  - <input>
- accepted formats:
  - <path, JSON shape, scalar form, or exact enum>
- missing-input behavior:
  - <stop and report, or exact fallback if allowed>
- rejected:
  - <input or shape>

Allowed resources:
- read files:
  - <exact read paths or classes of paths>
- write files:
  - <exact write paths or classes of paths>
- network:
  - <allowed or disallowed>
- external authority:
  - <none or exact dependency>
- state scope:
  - <where state may live>

Execution doctrine:
- local-first
- explicit contracts
- bounded tools and state
- no hidden broker or control plane
- emit verifiable artifacts
- depth limit:
  - <max recursion, iteration, or tool-call depth>
- stop condition:
  - <exact condition that ends the lane cleanly>
- allowed completion states:
  - completed
  - already complete
  - blocked by missing local input

Steps:
1. <inspect>
2. <patch or author>
3. <validate>
4. <report>

Output contract:
- touched_files
- completion_state
- run_id
- request_id
- tick_limit
- events_path
- chain_path
- validation_performed
- verification_result
- residual_risk

Validation:
- <exact command>
- <exact expected result>

Explicit non-goals:
- <what must not widen in this slice>
```

## Fill Rules

### 1. One seam only

If the prompt touches multiple independent seams, split it.

### 2. Current state must be proven

Only include facts already visible in the repo or validated workspace.

### 3. Boundaries must be operationally real

If network, daemons, or external authority are disallowed, say so plainly.

### 4. Validation must be executable

Do not say only "tests green".
Name the exact command and the seam it proves.

### 5. Non-goals are mandatory

Every prompt should say what this slice does not do.
