from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

from metaflow_clockwork import ClockworkEngine, MetaTagType
from metaflow_clockwork.cli import main
from metaflow_clockwork.run_spec import RunSpecError, instantiate_run_spec, load_run_spec


class RunSpecPhase6Tests(unittest.TestCase):
    def test_load_run_spec_applies_defaults_and_known_functions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "demo_spec.json"
            path.write_text(
                json.dumps(
                    {
                        "root_tags": [
                            {
                                "tag_type": "gear",
                                "data": {"frequency": 528},
                                "functions": ["spawn_harmonics"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            spec = load_run_spec(path)

        self.assertEqual(spec.version, 1)
        self.assertEqual(spec.run_id, "metaflow_spec_demo_spec")
        self.assertEqual(spec.request_id, "metaflow_spec_demo_spec-request")
        self.assertEqual(spec.tick_limit, 1)
        self.assertEqual(spec.max_recursive_depth, 10)
        self.assertEqual(spec.root_tags[0].tag_type, MetaTagType.GEAR)
        self.assertEqual(spec.root_tags[0].functions, ["spawn_harmonics"])

    def test_load_run_spec_rejects_unknown_tag_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad_tag.json"
            path.write_text(
                json.dumps({"root_tags": [{"tag_type": "unknown"}]}),
                encoding="utf-8",
            )

            with self.assertRaises(RunSpecError) as ctx:
                load_run_spec(path)

        self.assertIn("run_spec_unknown_tag_type", str(ctx.exception))

    def test_load_run_spec_rejects_unknown_function_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad_fn.json"
            path.write_text(
                json.dumps(
                    {
                        "root_tags": [
                            {
                                "tag_type": "gear",
                                "functions": ["nope"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(RunSpecError) as ctx:
                load_run_spec(path)

        self.assertIn("run_spec_unknown_function", str(ctx.exception))

    def test_instantiate_run_spec_binds_registered_functions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "instantiated.json"
            path.write_text(
                json.dumps(
                    {
                        "run_id": "run-bound",
                        "request_id": "req-bound",
                        "max_recursive_depth": 7,
                        "root_tags": [
                            {
                                "tag_type": "gear",
                                "functions": ["spawn_harmonics"],
                                "children": [
                                    {
                                        "tag_type": "spring",
                                        "functions": ["data_transform"],
                                    }
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            engine = ClockworkEngine()
            spec = load_run_spec(path, engine=engine)
            tags = instantiate_run_spec(spec, engine=engine)

        self.assertEqual(len(tags), 1)
        root = tags[0]
        self.assertEqual(sorted(root.functions.keys()), ["spawn_harmonics"])
        self.assertEqual(root.max_recursive_depth, 7)
        self.assertEqual(root.children[0].recursive_depth, 1)
        self.assertEqual(sorted(root.children[0].functions.keys()), ["data_transform"])

    def test_spec_validate_cli_outputs_normalized_contract(self) -> None:
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cli_spec.json"
            path.write_text(
                json.dumps(
                    {
                        "tick_limit": 3,
                        "root_tags": [
                            {
                                "tag_type": "gear",
                                "functions": ["spawn_harmonics"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            rc = main(["spec-validate", str(path)], stdout=output)

        self.assertEqual(rc, 0)
        payload = json.loads(output.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["entry_point"], "spec-validate")
        self.assertEqual(payload["spec"]["tick_limit"], 3)
        self.assertIn("spawn_harmonics", payload["known_functions"])


if __name__ == "__main__":
    unittest.main()
