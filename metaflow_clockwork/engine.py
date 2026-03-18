#!/usr/bin/env python3
"""
MetaFlow Clockwork Engine v6
Refactored with event emission and audit ledger support
"""

import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from datetime import datetime

from .events import EventSink, NoOpEventSink

class MetaTagType(Enum):
    COG = "cog"
    GEAR = "gear"
    SPRING = "spring"
    PENDULUM = "pendulum"
    ESCAPEMENT = "escapement"
    MAINSPRING = "mainspring"
    COMPLICATION = "complication"

@dataclass
class MetaTag:
    tag_id: str
    tag_type: MetaTagType
    data: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Callable] = field(default_factory=dict)
    children: List['MetaTag'] = field(default_factory=list)
    parent: Optional['MetaTag'] = None
    tick_rate: float = 1.0
    energy: float = 100.0
    soul_hash: Optional[str] = None
    creation_time: datetime = field(default_factory=datetime.now)
    execution_count: int = 0
    recursive_depth: int = 0
    max_recursive_depth: int = 10
    event_sink: Optional[EventSink] = None
    run_id: str = "local"
    request_id: str = "local"

    def __post_init__(self):
        if not self.tag_id:
            content = f"{self.tag_type.value}{self.data}{time.time()}"
            self.tag_id = hashlib.sha256(content.encode()).hexdigest()[:16]

    def _emit(self, kind: str, level: str = "info", **data):
        if self.event_sink:
            self.event_sink.emit(kind, self.run_id, self.request_id, level, data)

    def tick(self) -> List['MetaTag']:
        self.execution_count += 1
        spawned_tags = []
        existing_children = list(self.children)

        for func_name, func in self.functions.items():
            try:
                result = func(self)
                if isinstance(result, MetaTag):
                    spawned_tags.append(result)
                elif isinstance(result, list):
                    spawned_tags.extend([r for r in result if isinstance(r, MetaTag)])
            except Exception as e:
                self._emit("metaflow.function.error", "error", func=func_name, error=str(e))

        # Children spawned during this tick begin executing on the next tick.
        for child in existing_children:
            spawned_tags.extend(child.tick())

        self.energy -= 0.1 * self.tick_rate

        return spawned_tags
    
    def add_function(self, name: str, func: Callable):
        self.functions[name] = func
        
    def spawn_child(self, child_type: MetaTagType, **kwargs) -> Optional['MetaTag']:
        if self.recursive_depth >= self.max_recursive_depth:
            return None

        if "max_recursive_depth" not in kwargs:
            kwargs["max_recursive_depth"] = self.max_recursive_depth
        if "tag_id" not in kwargs:
            kwargs["tag_id"] = ""

        child = MetaTag(
            tag_type=child_type,
            parent=self,
            recursive_depth=self.recursive_depth + 1,
            soul_hash=self.soul_hash,
            event_sink=self.event_sink,
            run_id=self.run_id,
            request_id=self.request_id,
            **kwargs
        )
        
        self.children.append(child)
        self._emit("metaflow.spawn", "info", child_id=child.tag_id, child_type=child_type.value)
        return child
    
    def to_meta_syntax(self, indent: int = 0) -> str:
        spaces = "  " * indent
        attrs = " ".join([f'{k}="{v}"' for k, v in self.data.items()])
        
        if not self.children and not self.functions:
            return f'{spaces}<meta:{self.tag_type.value} {attrs} />'
        
        lines = [f'{spaces}<meta:{self.tag_type.value} {attrs}>']
        
        for func_name in self.functions:
            lines.append(f'{spaces}  <meta:function name="{func_name}" />')
        
        for child in self.children:
            lines.append(child.to_meta_syntax(indent + 1))
            
        lines.append(f'{spaces}</meta:{self.tag_type.value}>')
        
        return "\n".join(lines)


class ClockworkEngine:
    def __init__(self, event_sink: Optional[EventSink] = None, run_id: str = "metaflow_local", request_id: str = "local"):
        self.root_gears: List[MetaTag] = []
        self.all_tags: Dict[str, MetaTag] = {}
        self.tick_count = 0
        self.universal_time = 0.0
        self.love_frequency = 528.0
        self.spawned_tags_buffer: List[MetaTag] = []
        self.function_registry = self._initialize_base_functions()
        self.event_sink = event_sink or NoOpEventSink()
        self.run_id = run_id
        self.request_id = request_id

    def _emit(self, kind: str, level: str = "info", **data):
        self.event_sink.emit(kind, self.run_id, self.request_id, level, data)

    def _initialize_base_functions(self) -> Dict[str, Callable]:
        def recursive_soul_match(tag: MetaTag) -> List[MetaTag]:
            if tag.recursive_depth >= 5:
                return []
            matches = []
            if tag.soul_hash and "target_frequency" in tag.data:
                seeker = tag.spawn_child(
                    MetaTagType.COG,
                    data={"seeking": tag.data["target_frequency"], "depth": tag.recursive_depth}
                )
                if seeker:
                    seeker.add_function("seek", recursive_soul_match)
                    matches.append(seeker)
            return matches

        def recursive_data_transform(tag: MetaTag) -> None:
            if "transform" in tag.data:
                tag.data["value"] = tag.data.get("value", 0) * 1.618
                if tag.recursive_depth < 3:
                    child = tag.spawn_child(MetaTagType.SPRING, data={"value": tag.data["value"], "transform": True})
                    if child:
                        child.add_function("transform", recursive_data_transform)

        def spawn_harmonic_gears(tag: MetaTag) -> List[MetaTag]:
            gears = []
            base_freq = tag.data.get("frequency", self.love_frequency)
            for harmonic in [1, 2, 3, 5, 8]:
                if tag.recursive_depth < 4:
                    gear = tag.spawn_child(
                        MetaTagType.GEAR,
                        data={"frequency": base_freq * harmonic, "harmonic": harmonic},
                        tick_rate=harmonic
                    )
                    if gear:
                        gear.add_function("resonate", spawn_harmonic_gears)
                        gears.append(gear)
            return gears

        return {
            "soul_match": recursive_soul_match,
            "data_transform": recursive_data_transform,
            "spawn_harmonics": spawn_harmonic_gears
        }

    def add_root_gear(self, gear: MetaTag):
        gear.event_sink = self.event_sink
        gear.run_id = self.run_id
        gear.request_id = self.request_id
        self.root_gears.append(gear)
        self._register_tag(gear)
    
    def _register_tag(self, tag: MetaTag):
        self.all_tags[tag.tag_id] = tag
        for child in tag.children:
            child.event_sink = self.event_sink
            child.run_id = self.run_id
            child.request_id = self.request_id
            self._register_tag(child)
    
    def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        self.universal_time += 1.0 / 60

        self._emit("metaflow.tick", "info", tick=self.tick_count, time=self.universal_time, root_gears=len(self.root_gears))

        spawned_this_tick = []

        for gear in self.root_gears:
            spawned = gear.tick()
            spawned_this_tick.extend(spawned)

        for tag in spawned_this_tick:
            self._register_tag(tag)
            if tag.tag_type == MetaTagType.GEAR and tag.parent is None:
                self.root_gears.append(tag)

        if spawned_this_tick:
            self._emit("metaflow.spawn", "info", spawned=len(spawned_this_tick))

        exhausted = self._cleanup_exhausted_tags()

        summary = {
            "tick": self.tick_count,
            "time": self.universal_time,
            "active_tags": len(self.all_tags),
            "active_tag_ids": sorted(self.all_tags.keys()),
            "spawned": len(spawned_this_tick),
            "spawned_tag_ids": [tag.tag_id for tag in spawned_this_tick],
            "root_gears": len(self.root_gears),
            "exhausted": exhausted,
        }
        self._emit("metaflow.tick.summary", "info", **summary)
        return summary

    def _cleanup_exhausted_tags(self) -> int:
        exhausted = [tag_id for tag_id, tag in self.all_tags.items() if tag.energy <= 0]
        for tag_id in exhausted:
            tag = self.all_tags[tag_id]
            if tag.parent and tag in tag.parent.children:
                tag.parent.children.remove(tag)
            del self.all_tags[tag_id]
            self._emit("metaflow.tag.exhausted", "info", tag_id=tag_id)
        return len(exhausted)
