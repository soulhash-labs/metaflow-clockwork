# MetaFlow Clockwork Prompt Assets

This directory contains the public prompt-framework and doctrine surface for
MetaFlow Clockwork.

These files are:

- public docs and contracts
- local-first and repo-scoped
- versioned and inspectable
- safe to publish with the public package

These files are not:

- a hidden control plane
- a runtime autonomy layer
- a private Aurora/SoulHash/Starlight research surface
- a replacement for the package's explicit runtime contracts

## What Lives Here

- [PROMPT_HYGIENE.md](PROMPT_HYGIENE.md)
  - public prompt-authoring rules for MetaFlow Clockwork
- [PROMPT_TEMPLATE_V1.md](PROMPT_TEMPLATE_V1.md)
  - reusable prompt authoring template
- [SELF_CONTAINED_EXECUTION_DOCTRINE.md](SELF_CONTAINED_EXECUTION_DOCTRINE.md)
  - public-safe execution doctrine for local-first, bounded execution
- [contracts/local_runtime_agent.v1.json](contracts/local_runtime_agent.v1.json)
  - machine-readable role contract example
- [examples/local_runtime_agent.prompt.md](examples/local_runtime_agent.prompt.md)
  - concrete prompt example using the template and doctrine

## Current Status

MetaFlow Clockwork ships these assets as authoring and governance material.
They document how prompts should be written and how execution should be
bounded, but they do not add a hidden runtime loader or a second orchestration
surface.

## Validation

The public repo validates these assets through:

- `tests/test_prompt_assets_public.py`

That test checks:

- required prompt and doctrine files exist
- the example role contract is well-formed JSON
- the contract points to a real prompt example
- the example prompt contains the required sections

## Public Boundary

Keep this directory public-safe.

Allowed:

- explicit prompt hygiene
- explicit role contracts
- bounded execution doctrine
- local-first prompt examples

Disallowed:

- private enforcement research
- internal-only licensing controls
- private orchestration surfaces
- undeclared external authority assumptions
