# MetaFlow Clockwork Quickstart

This quickstart assumes a repository checkout and matches the current public
package surface:

- package: `metaflow-clockwork`
- import path: `metaflow_clockwork`
- CLI: `metaflow-clockwork`

This project is not affiliated with Netflix Metaflow.

If you only want to smoke-test an installed wheel, use `metaflow-clockwork
validate --run-root /tmp/metaflow-runs` from outside the source checkout.

## Install

From a local checkout:

```bash
pip install .
```

For development:

```bash
pip install -e .
```

To build distribution artifacts from a working tree:

```bash
python -m pip install --upgrade build twine
rm -rf build dist metaflow_clockwork.egg-info
python -m build --sdist --wheel
python -m twine check dist/*
```

## First Python Run

```python
from metaflow_clockwork import ClockworkEngine, MetaTag, MetaTagType, RecordingEventSink

sink = RecordingEventSink()
engine = ClockworkEngine(event_sink=sink, run_id="quickstart-run", request_id="quickstart-request")

root = MetaTag(tag_id="root", tag_type=MetaTagType.GEAR, event_sink=sink)

def spawn_once(tag: MetaTag):
    if tag.data.get("spawned"):
        return []
    tag.data["spawned"] = True
    child = tag.spawn_child(MetaTagType.COG, tag_id="child-1")
    return [child] if child else []

root.add_function("spawn_once", spawn_once)
engine.add_root_gear(root)

summary = engine.tick()

print(summary)
print([event.kind for event in sink.events])
```

What to expect:

- a deterministic tick summary
- a `metaflow.spawn` event in the recording sink
- no network calls

## First CLI Run

Validate the local package behavior:

```bash
python -m metaflow_clockwork validate --run-root /tmp/metaflow-runs
```

Run the checked-in spec:

```bash
python -m metaflow_clockwork spec-validate ./examples/basic_harmonics.json
python -m metaflow_clockwork spec-run ./examples/basic_harmonics.json --run-root /tmp/metaflow-runs
python -m metaflow_clockwork ledger-verify /tmp/metaflow-runs/example_harmonics
```

## Next Steps

- read [ARCHITECTURE.md](../ARCHITECTURE.md)
- read [prompts/README.md](../prompts/README.md)
- read [ROADMAP.md](../ROADMAP.md)
- inspect [examples/basic_clockwork.py](../examples/basic_clockwork.py)
- inspect [examples/basic_harmonics.json](../examples/basic_harmonics.json)
