from __future__ import annotations

import json
import unittest
from pathlib import Path


class PromptAssetsPublicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.prompts_root = self.repo_root / "prompts"

    def _load_contract(self) -> dict[str, object]:
        contract_path = self.prompts_root / "contracts" / "local_runtime_agent.v1.json"
        return json.loads(contract_path.read_text(encoding="utf-8"))

    @staticmethod
    def _normalize_text(text: str) -> str:
        return " ".join(text.replace("`", "").split())

    def test_required_prompt_framework_files_exist(self) -> None:
        required = [
            self.prompts_root / "README.md",
            self.prompts_root / "PROMPT_HYGIENE.md",
            self.prompts_root / "PROMPT_TEMPLATE_V1.md",
            self.prompts_root / "SELF_CONTAINED_EXECUTION_DOCTRINE.md",
            self.prompts_root / "contracts" / "local_runtime_agent.v1.json",
            self.prompts_root / "examples" / "local_runtime_agent.prompt.md",
        ]
        for path in required:
            self.assertTrue(path.is_file(), f"missing prompt asset: {path}")
            self.assertGreater(path.stat().st_size, 0, f"empty prompt asset: {path}")

    def test_local_runtime_agent_contract_is_well_formed(self) -> None:
        payload = self._load_contract()

        for key in (
            "version",
            "id",
            "name",
            "purpose",
            "lane_type",
            "inputs",
            "allowed_resources",
            "execution_boundaries",
            "allowed_completion_states",
            "output_contract",
            "prompt_template",
        ):
            self.assertIn(key, payload, f"missing contract key: {key}")

        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["id"], "local_runtime_agent")
        self.assertIn("accepted_formats", payload["inputs"])
        self.assertIn("missing_input_behavior", payload["inputs"])
        self.assertIn("read_files", payload["allowed_resources"])
        self.assertIn("write_files", payload["allowed_resources"])
        self.assertEqual(
            payload["allowed_completion_states"],
            ["completed", "already complete", "blocked by missing local input"],
        )

        prompt_path = self.repo_root / payload["prompt_template"]
        self.assertTrue(prompt_path.is_file(), f"missing contract-linked prompt: {prompt_path}")

    def test_prompt_template_exposes_required_hygiene_slots(self) -> None:
        template_path = self.prompts_root / "PROMPT_TEMPLATE_V1.md"
        text = template_path.read_text(encoding="utf-8")
        payload = self._load_contract()

        required_fragments = [
            "accepted formats:",
            "missing-input behavior:",
            "read files:",
            "write files:",
            "depth limit:",
            "stop condition:",
            "expected result",
        ]
        for fragment in required_fragments:
            self.assertIn(fragment, text, f"missing template fragment: {fragment}")

        for state in payload["allowed_completion_states"]:
            self.assertIn(state, text, f"missing template completion state: {state}")

        for field in payload["output_contract"]["required_report_fields"]:
            self.assertIn(field, text, f"missing template output field: {field}")

    def test_example_prompt_contains_required_sections(self) -> None:
        prompt_path = self.prompts_root / "examples" / "local_runtime_agent.prompt.md"
        text = prompt_path.read_text(encoding="utf-8")

        required_sections = [
            "Role:",
            "Mission:",
            "Lane type:",
            "Read first:",
            "Current state:",
            "Input contract:",
            "Allowed resources:",
            "Execution doctrine:",
            "Steps:",
            "Output contract:",
            "Validation:",
            "Explicit non-goals:",
        ]
        for section in required_sections:
            self.assertIn(section, text, f"missing prompt section: {section}")

    def test_example_prompt_matches_contract_and_hygiene_requirements(self) -> None:
        prompt_path = self.prompts_root / "examples" / "local_runtime_agent.prompt.md"

        payload = self._load_contract()
        text = prompt_path.read_text(encoding="utf-8")
        normalized = self._normalize_text(text)

        self.assertIn("accepted formats:", text)
        self.assertIn("missing-input behavior:", text)
        self.assertIn("read files:", text)
        self.assertIn("write files:", text)
        self.assertIn("depth limit:", text)
        self.assertIn("stop condition:", text)
        self.assertIn("already complete", text)
        self.assertIn("blocked by missing local input", text)
        self.assertIn("Apply MetaFlow prompt hygiene and the Self-Contained Execution Doctrine", text)
        self.assertIn("expected result:", text)

        for name in payload["inputs"]["required"]:
            self.assertIn(f"`{name}`", text, f"missing required input in example: {name}")

        for name in payload["inputs"]["optional"]:
            self.assertIn(f"`{name}`", text, f"missing optional input in example: {name}")

        for name, value in payload["inputs"]["accepted_formats"].items():
            self.assertIn(f"`{name}`", text, f"missing accepted format key in example: {name}")
            self.assertIn(value, normalized, f"missing accepted format value in example: {value}")

        self.assertIn(payload["inputs"]["missing_input_behavior"], normalized)

        for rejected in payload["inputs"]["rejected"]:
            self.assertIn(f"- {rejected}", text, f"missing rejected literal in example: {rejected}")

        for path_class in payload["allowed_resources"]["read_files"]:
            self.assertIn(f"- {path_class}", text, f"missing read_files literal in example: {path_class}")

        for path_class in payload["allowed_resources"]["write_files"]:
            self.assertIn(f"- {path_class}", text, f"missing write_files literal in example: {path_class}")

        self.assertIn(payload["allowed_resources"]["network"], normalized)
        self.assertIn(payload["allowed_resources"]["external_authority"], normalized)
        self.assertIn(payload["allowed_resources"]["state_scope"], normalized)

        for boundary in payload["execution_boundaries"]:
            self.assertIn(f"- {boundary}", text, f"missing execution boundary in example: {boundary}")

        for artifact in payload["output_contract"]["artifacts"]:
            self.assertIn(artifact, text, f"missing output artifact in example: {artifact}")

        for field in payload["output_contract"]["required_report_fields"]:
            rendered_field = f"`{field}`"
            self.assertIn(rendered_field, text, f"missing contract report field in example: {field}")
