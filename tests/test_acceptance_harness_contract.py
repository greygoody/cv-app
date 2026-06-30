from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "run_codex_local_acceptance.sh"
WORKCELL = ROOT / "scripts" / "run_local_acceptance_workcell.sh"
SUPERVISOR_PROMPT = ROOT / "tests" / "agent" / "prompts" / "local-supervisor-workcell.md"


class AcceptanceHarnessContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.harness = HARNESS.read_text(encoding="utf-8")
        cls.workcell = WORKCELL.read_text(encoding="utf-8")
        cls.supervisor_prompt = SUPERVISOR_PROMPT.read_text(encoding="utf-8")

    def test_does_not_pass_global_approval_flag_after_exec(self):
        self.assertNotIn("--ask-for-approval", self.harness)

    def test_uses_documented_noninteractive_approval_config(self):
        self.assertIn("--config 'approval_policy=\"never\"'", self.harness)

    def test_retains_workspace_write_sandbox(self):
        self.assertIn("--sandbox workspace-write", self.harness)

    def test_records_exec_help_for_cli_compatibility_evidence(self):
        self.assertIn('codex exec --help > "$OUT_ROOT/codex-exec-help.txt"', self.harness)

    def test_dependency_free_workcell_runs_proof_and_agent_harness(self):
        self.assertIn("python3 scripts/validate_plugin.py", self.workcell)
        self.assertIn("python3 -m unittest discover -s tests -p 'test_*.py'", self.workcell)
        self.assertIn("bash scripts/run_codex_local_acceptance.sh", self.workcell)
        self.assertNotIn("just ", self.workcell)

    def test_supervisor_does_not_block_on_missing_just(self):
        self.assertIn("`just` is optional", self.supervisor_prompt)
        self.assertIn("Do not stop merely because `just` is unavailable", self.supervisor_prompt)
        self.assertIn("bash scripts/run_local_acceptance_workcell.sh", self.supervisor_prompt)


if __name__ == "__main__":
    unittest.main()
