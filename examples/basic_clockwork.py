#!/usr/bin/env python3
"""Basic MetaFlow Clockwork example using the current public API."""

from metaflow_clockwork import ClockworkEngine, MetaTag, MetaTagType, RecordingEventSink


def main() -> None:
    sink = RecordingEventSink()
    engine = ClockworkEngine(event_sink=sink, run_id="basic-clockwork", request_id="example-request")

    root = MetaTag(
        tag_id="root-gear",
        tag_type=MetaTagType.GEAR,
        data={"label": "basic-clockwork"},
        event_sink=sink,
    )

    def spawn_once(tag: MetaTag):
        if tag.data.get("spawned"):
            return []
        tag.data["spawned"] = True
        child = tag.spawn_child(
            MetaTagType.COG,
            tag_id="child-cog",
            data={"label": "worker"},
        )
        return [child] if child else []

    root.add_function("spawn_once", spawn_once)
    engine.add_root_gear(root)

    for _ in range(2):
        summary = engine.tick()
        print(summary)

    print([event.kind for event in sink.events])


if __name__ == "__main__":
    main()
