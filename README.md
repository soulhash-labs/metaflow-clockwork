# MetaFlow Clockwork

<div align="center">

```text
  deterministic local runtime for AI agents
  self-executing tags  ·  bounded recursion
  spec-driven runs     ·  append-only ledgers
```

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](./LICENSE)
[![Import](https://img.shields.io/badge/import-metaflow__clockwork-5C6AC4)](#install)
[![Runtime](https://img.shields.io/badge/runtime-local--first-2EA44F)](#design-principles)

**[Quickstart](./docs/quickstart.md)** · **[Architecture](./ARCHITECTURE.md)** · **[Prompt Assets](./prompts/README.md)** · **[Roadmap](./ROADMAP.md)** · **[Contributing](./CONTRIBUTING.md)** · **[Changelog](./CHANGELOG.md)**

</div>

---

> **`pip install metaflow-clockwork`** once published &nbsp;·&nbsp; `import metaflow_clockwork` &nbsp;·&nbsp; `metaflow-clockwork`
>
> Not affiliated with Netflix Metaflow or the `metaflow` package on PyPI.

---

## What Is It?

MetaFlow Clockwork is the public open-source package distributed as `metaflow-clockwork` and imported as `metaflow_clockwork`.

It is a deterministic local runtime for building and testing AI agents with:

- explicit tagged execution units
- bounded recursive workflows
- spec-driven local runs
- append-only ledgers for replay and verification

Most agent frameworks optimize for speed of experimentation.
MetaFlow Clockwork optimizes for clarity of execution.

Built for teams who want to:

- model behavior as explicit execution units
- bound recursion deliberately
- validate runs before they execute
- produce replayable, verifiable ledgers
- stay local-first without a broker, daemon, or hidden orchestration layer

## What Ships Today

| Feature | Description |
|---|---|
| `MetaTag` execution | Deterministic execution units that describe and run behavior |
| `ClockworkEngine` | Bounded recursive ticking with explicit depth control |
| Event sinks | In-memory and append-only ledger backends |
| Run-spec validation | Validate a spec before a single tick fires |
| Ledger tools | Summary, replay, and verification |
| CLI | `validate`, `spec-validate`, `spec-run`, `ledger-verify` for local development |
| Repository prompt assets | Public prompt hygiene, template, doctrine, and example role contract |

## Install

Once published:

```bash
pip install metaflow-clockwork
```

From a repo checkout:

```bash
pip install .

# Editable / dev install
pip install -e .

# Build distribution artifacts
python -m pip install --upgrade build twine
rm -rf build dist metaflow_clockwork.egg-info
python -m build --sdist --wheel
python -m twine check dist/*
```

## Python Quickstart

```python
from metaflow_clockwork import ClockworkEngine, MetaTag, MetaTagType, RecordingEventSink

sink = RecordingEventSink()
engine = ClockworkEngine(
    event_sink=sink,
    run_id="demo-run",
    request_id="demo-request",
)

root = MetaTag(
    tag_id="root-gear",
    tag_type=MetaTagType.GEAR,
    event_sink=sink,
)

def spawn_once(tag: MetaTag):
    if tag.data.get("spawned"):
        return []
    tag.data["spawned"] = True
    child = tag.spawn_child(MetaTagType.COG, tag_id="child-cog")
    return [child] if child else []

root.add_function("spawn_once", spawn_once)
engine.add_root_gear(root)

summary = engine.tick()
print(summary)
print([event.kind for event in sink.events])
```

## CLI Quickstart

```bash
# Installed-package smoke check
metaflow-clockwork validate --run-root /tmp/metaflow-runs
```

From a repo checkout:

```bash
# Validate a run spec
metaflow-clockwork spec-validate ./examples/basic_harmonics.json

# Execute locally and verify the resulting ledger
metaflow-clockwork spec-run ./examples/basic_harmonics.json --run-root /tmp/metaflow-runs
metaflow-clockwork ledger-verify /tmp/metaflow-runs/example_harmonics

# Module invocation also works
python -m metaflow_clockwork spec-validate ./examples/basic_harmonics.json
```

If you want to validate the installed wheel rather than the checked-out source
tree, run those commands from outside the repository root and pass an absolute
path to the example spec.

## Design Principles

```text
PROMPT HYGIENE FIRST     Keep instructions, contracts, and boundaries explicit.
SELF-CONTAINED          Explicit inputs. Explicit local resources. No hidden control plane.
DETERMINISTIC            Same input -> inspectable, repeatable behavior.
BOUNDED RECURSION        Recursion is useful when deliberate and constrained.
LEDGERED EXECUTION       Every meaningful run leaves a replayable trace.
LOCAL-FIRST              No broker. No daemon. No hidden mesh to get started.
```

## Prompt Framework & Doctrine

The public prompt and doctrine surface lives under [`prompts/`](./prompts/README.md).

It currently includes:

- [Prompt Hygiene](./prompts/PROMPT_HYGIENE.md)
- [Prompt Template v1](./prompts/PROMPT_TEMPLATE_V1.md)
- [Self-Contained Execution Doctrine](./prompts/SELF_CONTAINED_EXECUTION_DOCTRINE.md)
- [Example role contract](./prompts/contracts/local_runtime_agent.v1.json)
- [Example prompt](./prompts/examples/local_runtime_agent.prompt.md)

These assets are public docs and contracts. They describe how MetaFlow work
should be framed and bounded. They do not add a hidden runtime loader, broker,
or second orchestration surface.

Legacy QRBT bridge names remain only as compatibility notices for migration.
Live QRBT bridge execution is not part of the public package.

## Examples

| Example | Description |
|---|---|
| [`examples/basic_harmonics.json`](./examples/basic_harmonics.json) | Minimal JSON run spec to validate and execute |
| [`examples/basic_clockwork.py`](./examples/basic_clockwork.py) | Python example wiring tags and the engine |
| [`docs/quickstart.md`](./docs/quickstart.md) | Hands-on walkthrough from zero to ledger |

## Validation

Run the same checks used during release hardening:

```bash
# Syntax check
python3 -m py_compile metaflow_clockwork/*.py tests/test_*.py examples/basic_clockwork.py

# Unit tests
python3 -m unittest discover -s tests -p 'test_*.py' -v

# Build and distribution check
python3 -m pip install --upgrade build twine
rm -rf build dist metaflow_clockwork.egg-info
python3 -m build --sdist --wheel
python3 -m twine check dist/*

# End-to-end spec run
metaflow-clockwork spec-validate ./examples/basic_harmonics.json
metaflow-clockwork spec-run ./examples/basic_harmonics.json --run-root /tmp/metaflow-runs
metaflow-clockwork ledger-verify /tmp/metaflow-runs/example_harmonics
```

## Docs & Community

| | |
|---|---|
| [Architecture](./ARCHITECTURE.md) | How the engine, tags, and ledgers fit together |
| [Prompt Assets](./prompts/README.md) | Public prompt hygiene, doctrine, and role contract examples |
| [Roadmap](./ROADMAP.md) | Where the public package is headed |
| [Contributing](./CONTRIBUTING.md) | How to contribute |
| [Security](./SECURITY.md) | Reporting vulnerabilities |
| [Support](./SUPPORT.md) | Getting help |
| [Trademarks](./TRADEMARKS.md) | Trademark and branding notice |
| [Code of Conduct](./CODE_OF_CONDUCT.md) | Community standards |
| [Changelog](./CHANGELOG.md) | What changed |

## License

Licensed under [Apache 2.0](./LICENSE).

Trademark and branding guidance lives in [TRADEMARKS.md](./TRADEMARKS.md).

---

*Build agent systems that are inspectable, replayable, and auditable.*

MetaFlow Clockwork™ is an open-source runtime by SoulHash®. The Apache 2.0
license covers the code; branding rights are reserved.
