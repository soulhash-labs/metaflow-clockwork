# Contributing to MetaFlow Clockwork

## Scope

MetaFlow Clockwork is a small deterministic Python runtime with append-only ledgers and spec-driven local execution.

Please keep contributions aligned to the public repo surface:

- deterministic local execution
- run-spec validation and execution
- ledger replay and verification
- docs, packaging, and test improvements

## Local setup

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

## Validation

Run the same checks used by CI:

```bash
python -m py_compile metaflow_clockwork/*.py tests/test_*.py examples/basic_clockwork.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Optional CLI smoke checks:

```bash
python -m metaflow_clockwork validate
python -m metaflow_clockwork spec-validate ./examples/basic_harmonics.json
python -m metaflow_clockwork spec-run ./examples/basic_harmonics.json --run-root /tmp/metaflow-runs
python -m metaflow_clockwork ledger-verify /tmp/metaflow-runs/example_harmonics
```

## Packaging validation

Clean local build artifacts before calling `python -m build`. A leftover
repo-root `build/` directory can shadow the packaging frontend.

```bash
python -m pip install --upgrade pip build twine
rm -rf build dist *.egg-info
python -m build --sdist --wheel
python -m twine check dist/*
```

## Boundaries

- Do not add a second hosted orchestration layer.
- Keep prompts and role contracts explicit and versioned if you add them.
- Keep public prompt assets under `prompts/`.
- Keep public-facing docs in the repo root instead of relying on private planning material.
- Keep internal research and private integrations out of the public repo.

## Archive posture

`site-archive/` is archival input only. It can inform naming or brand discussions, but it is not the source of truth for runtime, packaging, or governance decisions.

## Issues and pull requests

Once the public GitHub repository is live, use GitHub Issues and Pull Requests for normal bug reports, feature proposals, and contribution review.

## Security

Do not report vulnerabilities in public issues. Follow [SECURITY.md](SECURITY.md).
