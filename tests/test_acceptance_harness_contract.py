from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "run_codex_local_acceptance.sh"


class AcceptanceHarnessContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = HARNESS.read_text(encoding="utf-8")

    def test_does_not_pass_global_approval_flag_after_exec(self):
        self.assertNotIn("--ask-for-approval", self.text)

    def test_uses_documented_noninteractive_approval_config(self):
        self.assertIn("--config 'approval_policy=\"never\"'", self.text)

    def test_retains_workspace_write_sandbox(self):
        self.assertIn("--sandbox workspace-write", self.text)

    def test_records_exec_help_for_cli_compatibility_evidence(self):
        self.assertIn('codex exec --help > "$OUT_ROOT/codex-exec-help.txt"', self.text)


if __name__ == "__main__":
    unittest.main()
