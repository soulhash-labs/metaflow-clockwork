from __future__ import annotations

import unittest

from metaflow_clockwork import ClockworkEngine, MetaTag, MetaTagType, RecordingEventSink


class EnginePhase2Tests(unittest.TestCase):
    def test_meta_tag_tick_defers_new_child_execution_until_next_tick(self) -> None:
        sink = RecordingEventSink()
        parent = MetaTag(tag_id="root", tag_type=MetaTagType.GEAR, event_sink=sink)

        def spawn_once(tag: MetaTag):
            if tag.data.get("spawned"):
                return []
            tag.data["spawned"] = True
            child = tag.spawn_child(MetaTagType.COG, tag_id="child-1")
            return [child] if child else []

        parent.add_function("spawn_once", spawn_once)

        spawned = parent.tick()

        self.assertEqual(parent.execution_count, 1)
        self.assertEqual([tag.tag_id for tag in spawned], ["child-1"])
        self.assertEqual(parent.children[0].execution_count, 0)
        self.assertEqual([evt.kind for evt in sink.events], ["metaflow.spawn"])

        parent.tick()

        self.assertEqual(parent.children[0].execution_count, 1)

    def test_spawn_child_respects_recursive_depth_limit(self) -> None:
        sink = RecordingEventSink()
        tag = MetaTag(
            tag_id="limit-root",
            tag_type=MetaTagType.GEAR,
            recursive_depth=1,
            max_recursive_depth=1,
            event_sink=sink,
        )

        child = tag.spawn_child(MetaTagType.COG, tag_id="blocked-child")

        self.assertIsNone(child)
        self.assertEqual(tag.children, [])
        self.assertEqual(sink.events, [])

    def test_engine_tick_returns_and_emits_structured_summary(self) -> None:
        sink = RecordingEventSink()
        engine = ClockworkEngine(event_sink=sink, run_id="run-1", request_id="req-1")
        engine.add_root_gear(MetaTag(tag_id="root-1", tag_type=MetaTagType.GEAR))

        summary = engine.tick()

        self.assertEqual(
            summary,
            {
                "tick": 1,
                "time": 1.0 / 60,
                "active_tags": 1,
                "active_tag_ids": ["root-1"],
                "spawned": 0,
                "spawned_tag_ids": [],
                "root_gears": 1,
                "exhausted": 0,
            },
        )
        summary_events = [evt for evt in sink.events if evt.kind == "metaflow.tick.summary"]
        self.assertEqual(len(summary_events), 1)
        self.assertEqual(summary_events[0].data, summary)

    def test_engine_cleanup_emits_single_exhaustion_event(self) -> None:
        sink = RecordingEventSink()
        engine = ClockworkEngine(event_sink=sink, run_id="run-2", request_id="req-2")
        root = MetaTag(tag_id="root-2", tag_type=MetaTagType.GEAR)
        child = MetaTag(
            tag_id="child-2",
            tag_type=MetaTagType.SPRING,
            parent=root,
            energy=0.05,
        )
        root.children.append(child)
        engine.add_root_gear(root)

        summary = engine.tick()

        self.assertEqual(summary["exhausted"], 1)
        self.assertEqual(summary["active_tag_ids"], ["root-2"])
        self.assertEqual([c.tag_id for c in root.children], [])
        exhausted_events = [
            evt for evt in sink.events
            if evt.kind == "metaflow.tag.exhausted" and evt.data.get("tag_id") == "child-2"
        ]
        self.assertEqual(len(exhausted_events), 1)

    def test_recursive_spawning_stays_bounded_across_ticks(self) -> None:
        sink = RecordingEventSink()
        engine = ClockworkEngine(event_sink=sink, run_id="run-3", request_id="req-3")
        root = MetaTag(
            tag_id="chain-root",
            tag_type=MetaTagType.GEAR,
            data={"spawned": False},
            max_recursive_depth=2,
        )

        def chain_once(tag: MetaTag):
            if tag.data.get("spawned"):
                return []
            tag.data["spawned"] = True
            child = tag.spawn_child(
                MetaTagType.COG,
                tag_id=f"chain-{tag.recursive_depth + 1}",
                data={"spawned": False},
            )
            if child:
                child.add_function("chain_once", chain_once)
                return [child]
            return []

        root.add_function("chain_once", chain_once)
        engine.add_root_gear(root)

        summary1 = engine.tick()
        summary2 = engine.tick()
        summary3 = engine.tick()

        self.assertEqual(summary1["active_tags"], 2)
        self.assertEqual(summary2["active_tags"], 3)
        self.assertEqual(summary3["active_tags"], 3)
        self.assertEqual(sorted(tag.recursive_depth for tag in engine.all_tags.values()), [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
