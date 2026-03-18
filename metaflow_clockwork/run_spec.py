from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from .engine import ClockworkEngine, MetaTag, MetaTagType
from .ledger_sink import LedgerEventSink


DEFAULT_RUN_ID_PREFIX = "metaflow_spec"
DEFAULT_REQUEST_ID_SUFFIX = "-request"
DEFAULT_TICK_LIMIT = 1


class RunSpecError(RuntimeError):
    pass


@dataclass(frozen=True)
class TagSpec:
    tag_type: MetaTagType
    tag_id: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    functions: list[str] = field(default_factory=list)
    children: list["TagSpec"] = field(default_factory=list)
    tick_rate: float = 1.0
    energy: float = 100.0
    max_recursive_depth: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tag_type": self.tag_type.value,
            "data": self.data,
            "functions": list(self.functions),
            "children": [child.to_dict() for child in self.children],
            "tick_rate": self.tick_rate,
            "energy": self.energy,
        }
        if self.tag_id:
            payload["tag_id"] = self.tag_id
        if self.max_recursive_depth is not None:
            payload["max_recursive_depth"] = self.max_recursive_depth
        return payload


@dataclass(frozen=True)
class RunSpec:
    version: int
    run_id: str
    request_id: str
    tick_limit: int
    max_recursive_depth: int
    root_tags: list[TagSpec]
    source_path: str
    known_functions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "tick_limit": self.tick_limit,
            "max_recursive_depth": self.max_recursive_depth,
            "root_tags": [tag.to_dict() for tag in self.root_tags],
            "source_path": self.source_path,
            "known_functions": list(self.known_functions),
        }


@dataclass(frozen=True)
class RunExecutionResult:
    run_id: str
    request_id: str
    tick_limit: int
    run_root: str
    run_dir: str
    events_path: str
    chain_path: str
    failures_path: str
    root_tag_ids: list[str]
    tick_summaries: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "request_id": self.request_id,
            "tick_limit": self.tick_limit,
            "run_root": self.run_root,
            "run_dir": self.run_dir,
            "events_path": self.events_path,
            "chain_path": self.chain_path,
            "failures_path": self.failures_path,
            "root_tag_ids": list(self.root_tag_ids),
            "tick_summaries": list(self.tick_summaries),
        }


def _load_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RunSpecError(f"run_spec_not_found path={path}") from exc
    except json.JSONDecodeError as exc:
        raise RunSpecError(f"run_spec_invalid_json path={path} detail={exc}") from exc
    if not isinstance(raw, dict):
        raise RunSpecError(f"run_spec_invalid_root type={type(raw).__name__}")
    return raw


def _normalize_run_id(value: str | None, path: Path) -> str:
    candidate = str(value or "").strip()
    if candidate:
        return candidate
    stem = path.stem.strip().replace(" ", "_") or "default"
    return f"{DEFAULT_RUN_ID_PREFIX}_{stem}"


def _normalize_request_id(value: str | None, run_id: str) -> str:
    candidate = str(value or "").strip()
    if candidate:
        return candidate
    return f"{run_id}{DEFAULT_REQUEST_ID_SUFFIX}"


def _validate_tick_limit(value: Any) -> int:
    if value is None:
        return DEFAULT_TICK_LIMIT
    if not isinstance(value, int) or value <= 0:
        raise RunSpecError(f"run_spec_invalid_tick_limit value={value!r}")
    return value


def _validate_max_recursive_depth(value: Any, *, field_name: str) -> int:
    if value is None:
        return 10
    if not isinstance(value, int) or value < 0:
        raise RunSpecError(f"run_spec_invalid_{field_name} value={value!r}")
    return value


def _validate_tag_spec(
    raw: Any,
    *,
    known_functions: set[str],
    inherited_depth_limit: int,
    path: str,
) -> TagSpec:
    if not isinstance(raw, dict):
        raise RunSpecError(f"run_spec_invalid_tag path={path} type={type(raw).__name__}")

    raw_tag_type = str(raw.get("tag_type") or "").strip().lower()
    try:
        tag_type = MetaTagType(raw_tag_type)
    except ValueError as exc:
        raise RunSpecError(f"run_spec_unknown_tag_type path={path} value={raw_tag_type!r}") from exc

    raw_functions = raw.get("functions", [])
    if not isinstance(raw_functions, list) or not all(isinstance(name, str) for name in raw_functions):
        raise RunSpecError(f"run_spec_invalid_functions path={path}")
    for function_name in raw_functions:
        if function_name not in known_functions:
            raise RunSpecError(
                f"run_spec_unknown_function path={path} value={function_name!r} known={sorted(known_functions)}"
            )

    raw_children = raw.get("children", [])
    if not isinstance(raw_children, list):
        raise RunSpecError(f"run_spec_invalid_children path={path}")

    raw_data = raw.get("data", {})
    if raw_data is None:
        raw_data = {}
    if not isinstance(raw_data, dict):
        raise RunSpecError(f"run_spec_invalid_data path={path}")

    max_recursive_depth = raw.get("max_recursive_depth")
    resolved_depth = (
        inherited_depth_limit if max_recursive_depth is None
        else _validate_max_recursive_depth(max_recursive_depth, field_name="max_recursive_depth")
    )

    children = [
        _validate_tag_spec(
            child,
            known_functions=known_functions,
            inherited_depth_limit=resolved_depth,
            path=f"{path}.children[{index}]",
        )
        for index, child in enumerate(raw_children)
    ]

    tick_rate = raw.get("tick_rate", 1.0)
    energy = raw.get("energy", 100.0)
    if not isinstance(tick_rate, (int, float)) or tick_rate <= 0:
        raise RunSpecError(f"run_spec_invalid_tick_rate path={path} value={tick_rate!r}")
    if not isinstance(energy, (int, float)) or energy <= 0:
        raise RunSpecError(f"run_spec_invalid_energy path={path} value={energy!r}")

    return TagSpec(
        tag_type=tag_type,
        tag_id=str(raw.get("tag_id") or "").strip(),
        data=dict(raw_data),
        functions=[name.strip() for name in raw_functions],
        children=children,
        tick_rate=float(tick_rate),
        energy=float(energy),
        max_recursive_depth=resolved_depth,
    )


def load_run_spec(path: str | Path, *, engine: ClockworkEngine | None = None) -> RunSpec:
    spec_path = Path(path)
    raw = _load_json(spec_path)
    engine_for_validation = engine or ClockworkEngine()
    known_functions = set(engine_for_validation.function_registry.keys())

    version = raw.get("version", 1)
    if version != 1:
        raise RunSpecError(f"run_spec_unsupported_version value={version!r}")

    run_id = _normalize_run_id(raw.get("run_id"), spec_path)
    request_id = _normalize_request_id(raw.get("request_id"), run_id)
    tick_limit = _validate_tick_limit(raw.get("tick_limit"))
    max_recursive_depth = _validate_max_recursive_depth(
        raw.get("max_recursive_depth"),
        field_name="max_recursive_depth",
    )

    raw_root_tags = raw.get("root_tags")
    if not isinstance(raw_root_tags, list) or not raw_root_tags:
        raise RunSpecError("run_spec_missing_root_tags")

    root_tags = [
        _validate_tag_spec(
            entry,
            known_functions=known_functions,
            inherited_depth_limit=max_recursive_depth,
            path=f"root_tags[{index}]",
        )
        for index, entry in enumerate(raw_root_tags)
    ]

    return RunSpec(
        version=1,
        run_id=run_id,
        request_id=request_id,
        tick_limit=tick_limit,
        max_recursive_depth=max_recursive_depth,
        root_tags=root_tags,
        source_path=str(spec_path),
        known_functions=sorted(known_functions),
    )


def instantiate_run_spec(spec: RunSpec, *, engine: ClockworkEngine | None = None) -> list[MetaTag]:
    target_engine = engine or ClockworkEngine(run_id=spec.run_id, request_id=spec.request_id)

    def build_tag(tag_spec: TagSpec, *, parent: MetaTag | None, recursive_depth: int) -> MetaTag:
        tag = MetaTag(
            tag_id=tag_spec.tag_id,
            tag_type=tag_spec.tag_type,
            data=dict(tag_spec.data),
            parent=parent,
            tick_rate=tag_spec.tick_rate,
            energy=tag_spec.energy,
            recursive_depth=recursive_depth,
            max_recursive_depth=tag_spec.max_recursive_depth or spec.max_recursive_depth,
            run_id=spec.run_id,
            request_id=spec.request_id,
        )
        for function_name in tag_spec.functions:
            tag.add_function(function_name, target_engine.function_registry[function_name])
        for child_spec in tag_spec.children:
            child = build_tag(child_spec, parent=tag, recursive_depth=recursive_depth + 1)
            tag.children.append(child)
        return tag

    return [build_tag(root_spec, parent=None, recursive_depth=0) for root_spec in spec.root_tags]


def execute_run_spec(
    spec: RunSpec,
    *,
    run_root: str,
    tick_limit: int | None = None,
    run_id: str | None = None,
    request_id: str | None = None,
) -> RunExecutionResult:
    resolved_tick_limit = spec.tick_limit if tick_limit is None else _validate_tick_limit(tick_limit)
    resolved_run_id = str(run_id or spec.run_id).strip() or spec.run_id
    resolved_request_id = str(request_id or spec.request_id).strip() or spec.request_id
    resolved_spec = replace(
        spec,
        run_id=resolved_run_id,
        request_id=resolved_request_id,
        tick_limit=resolved_tick_limit,
    )

    ledger_sink = LedgerEventSink(run_root=run_root, run_id=resolved_spec.run_id)
    engine = ClockworkEngine(
        event_sink=ledger_sink,
        run_id=resolved_spec.run_id,
        request_id=resolved_spec.request_id,
    )
    root_tags = instantiate_run_spec(resolved_spec, engine=engine)
    for root_tag in root_tags:
        engine.add_root_gear(root_tag)

    ledger_sink.emit(
        "metaflow.run.start",
        resolved_spec.run_id,
        resolved_spec.request_id,
        "info",
        {
            "source_path": resolved_spec.source_path,
            "tick_limit": resolved_spec.tick_limit,
            "root_tag_ids": [tag.tag_id for tag in root_tags],
        },
    )

    summaries: list[dict[str, Any]] = []
    for _ in range(resolved_spec.tick_limit):
        summaries.append(engine.tick())

    ledger_sink.emit(
        "metaflow.run.complete",
        resolved_spec.run_id,
        resolved_spec.request_id,
        "info",
        {
            "tick_limit": resolved_spec.tick_limit,
            "ticks_executed": len(summaries),
            "final_active_tags": summaries[-1]["active_tags"] if summaries else 0,
        },
    )

    return RunExecutionResult(
        run_id=resolved_spec.run_id,
        request_id=resolved_spec.request_id,
        tick_limit=resolved_spec.tick_limit,
        run_root=str(Path(run_root)),
        run_dir=str(ledger_sink.run_dir),
        events_path=str(ledger_sink.events_path),
        chain_path=str(ledger_sink.chain_path),
        failures_path=str(ledger_sink.failures_path),
        root_tag_ids=[tag.tag_id for tag in root_tags],
        tick_summaries=summaries,
    )
