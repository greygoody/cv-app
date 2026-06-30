from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_agent_acceptance", ROOT / "scripts" / "validate_agent_acceptance.py"
)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class AgentAcceptanceValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.candidate = self.root / "candidate"
        self.candidate.mkdir()
        self.expected_source = self.root / "expected-source.md"
        source_text = "synthetic source\n"
        self.expected_source.write_text(source_text, encoding="utf-8")
        (self.candidate / "source.md").write_text(source_text, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.candidate, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=self.candidate, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.invalid"],
            cwd=self.candidate,
            check=True,
        )
        subprocess.run(["git", "add", "source.md"], cwd=self.candidate, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=self.candidate, check=True)

        self.report_path = self.root / "report.json"
        self.events_path = self.root / "events.jsonl"
        self.report = {
            **validator.EXPECTED,
            "rejected_model_ids": sorted(validator.REQUIRED_REJECTED),
            "retained_unknown_ids": sorted(validator.REQUIRED_UNKNOWNS),
            "prohibited_inference_ids": sorted(validator.REQUIRED_PROHIBITED),
            "summary": "The evidence supports integration ownership and operational handoff, not project-wide leadership or a documentation-only role.",
        }
        self.report_path.write_text(json.dumps(self.report), encoding="utf-8")
        self.events_path.write_text(
            "\n".join(
                [
                    json.dumps({"type": "thread.started", "thread_id": "test"}),
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {"type": "agent_message", "text": "done"},
                        }
                    ),
                    json.dumps({"type": "turn.completed", "usage": {}}),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        closure = "\n".join(validator.REQUIRED_CLOSURE_MARKERS)
        (self.candidate / "session-closure.md").write_text(closure, encoding="utf-8")

    def validate(self):
        return validator.validate(
            self.candidate,
            self.report_path,
            self.events_path,
            self.expected_source,
        )

    def test_valid_acceptance_artifacts_pass(self):
        self.assertEqual(self.validate(), [])

    def test_rejects_wrong_selected_model(self):
        self.report["selected_model_id"] = "whole-exhibition-technical-lead"
        self.report_path.write_text(json.dumps(self.report), encoding="utf-8")
        errors = self.validate()
        self.assertTrue(any("selected_model_id" in error for error in errors))

    def test_rejects_failure_event(self):
        self.events_path.write_text(
            json.dumps({"type": "turn.failed", "error": "test"}) + "\n",
            encoding="utf-8",
        )
        errors = self.validate()
        self.assertTrue(any("failure event" in error for error in errors))
        self.assertTrue(any("turn.completed" in error for error in errors))

    def test_rejects_source_mutation(self):
        (self.candidate / "source.md").write_text("changed\n", encoding="utf-8")
        errors = self.validate()
        self.assertTrue(any("source.md changed" in error for error in errors))

    def test_rejects_extra_workspace_file(self):
        (self.candidate / "extra.md").write_text("unexpected", encoding="utf-8")
        errors = self.validate()
        self.assertTrue(any("mutation set" in error for error in errors))

    def test_rejects_missing_closure_marker(self):
        (self.candidate / "session-closure.md").write_text(
            "candidate.morgan-vale\nresolved-proposed\n",
            encoding="utf-8",
        )
        errors = self.validate()
        self.assertTrue(any("missing marker" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
