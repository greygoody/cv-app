from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_plugin", ROOT / "scripts" / "validate_plugin.py"
)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PluginValidationTests(unittest.TestCase):
    def test_repository_slice_is_valid(self):
        self.assertEqual(validator.validate_plugin(ROOT), [])

    def make_copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        destination = Path(temporary.name) / "repo"
        shutil.copytree(
            ROOT,
            destination,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        return temporary, destination

    def test_rejects_non_contained_component_path(self):
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        path = root / ".codex-plugin" / "plugin.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["skills"] = "../private-skills"
        path.write_text(json.dumps(manifest), encoding="utf-8")

        errors = validator.validate_plugin(root)
        self.assertTrue(any("must start with './'" in error for error in errors))

    def test_rejects_advertised_missing_mcp_config(self):
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        path = root / ".codex-plugin" / "plugin.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["mcpServers"] = "./.mcp.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")

        errors = validator.validate_plugin(root)
        self.assertTrue(any("mcpServers path does not exist" in error for error in errors))

    def test_rejects_missing_skill_description(self):
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        path = root / "skills" / "grind-with-doc" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("description:", "summary:", 1)
        path.write_text(text, encoding="utf-8")

        errors = validator.validate_plugin(root)
        self.assertTrue(any("missing required front-matter field 'description'" in error for error in errors))

    def test_rejects_marketplace_source_not_at_plugin_root(self):
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        path = root / ".agents" / "plugins" / "marketplace.json"
        marketplace = json.loads(path.read_text(encoding="utf-8"))
        marketplace["plugins"][0]["source"]["path"] = "./skills"
        path.write_text(json.dumps(marketplace), encoding="utf-8")

        errors = validator.validate_plugin(root)
        self.assertTrue(any("source must resolve to plugin root" in error for error in errors))

    def test_rejects_non_synthetic_fixture(self):
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        path = root / "examples" / "synthetic-candidate" / "fixture.json"
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["contains_real_personal_data"] = True
        path.write_text(json.dumps(fixture), encoding="utf-8")

        errors = validator.validate_plugin(root)
        self.assertTrue(any("contains_real_personal_data must be False" in error for error in errors))

    def test_local_private_denylist_is_enforced(self):
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        marker = "private-candidate-marker-for-test"
        (root / ".cv-app-private-denylist").write_text(marker + "\n", encoding="utf-8")
        (root / "docs" / "leak.md").write_text(marker, encoding="utf-8")

        errors = validator.validate_plugin(root)
        self.assertTrue(any("local private marker found" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
