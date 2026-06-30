#!/usr/bin/env python3
"""Validate the cv-app Codex plugin package using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PLUGIN_MANIFEST = Path(".codex-plugin/plugin.json")
MARKETPLACE_MANIFEST = Path(".agents/plugins/marketplace.json")
SYNTHETIC_FIXTURE = Path("examples/synthetic-candidate/fixture.json")
LOCAL_DENYLIST = Path(".cv-app-private-denylist")

KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
)
TEXT_SUFFIXES = {".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}


class ValidationError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path}: root must be a JSON object")
    return value


def contained_path(root: Path, relative: str, field: str) -> Path:
    if not relative.startswith("./"):
        raise ValidationError(f"{field}: path must start with './'")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValidationError(f"{field}: path escapes plugin root") from exc
    return candidate


def parse_skill_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValidationError(f"{path}: missing YAML front matter")

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValidationError(f"{path}: invalid front-matter line {line!r}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    else:
        raise ValidationError(f"{path}: unterminated YAML front matter")

    for required in ("name", "description"):
        if not metadata.get(required):
            raise ValidationError(f"{path}: missing required front-matter field {required!r}")
    if not KEBAB_CASE.fullmatch(metadata["name"]):
        raise ValidationError(f"{path}: skill name must be kebab-case")
    return metadata


def validate_plugin(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_json(root / PLUGIN_MANIFEST)
        for field in ("name", "version", "description"):
            if not isinstance(manifest.get(field), str) or not manifest[field].strip():
                errors.append(f"plugin manifest: missing non-empty {field!r}")

        name = manifest.get("name")
        if isinstance(name, str) and not KEBAB_CASE.fullmatch(name):
            errors.append("plugin manifest: name must be stable kebab-case")

        version = manifest.get("version")
        if isinstance(version, str) and not SEMVER.fullmatch(version):
            errors.append("plugin manifest: version must be semantic versioning")

        component_fields = {
            "skills": "directory",
            "mcpServers": "file",
            "apps": "file",
            "hooks": "path",
        }
        resolved_components: dict[str, Path] = {}
        for field, kind in component_fields.items():
            value = manifest.get(field)
            if value is None:
                continue
            if not isinstance(value, str):
                errors.append(f"plugin manifest: {field} must be a relative path string")
                continue
            try:
                path = contained_path(root, value, f"plugin.{field}")
            except ValidationError as exc:
                errors.append(str(exc))
                continue
            resolved_components[field] = path
            if kind == "directory" and not path.is_dir():
                errors.append(f"plugin manifest: {field} directory does not exist: {value}")
            elif kind in {"file", "path"} and not path.exists():
                errors.append(f"plugin manifest: {field} path does not exist: {value}")

        skills_path = resolved_components.get("skills")
        skill_names: set[str] = set()
        if skills_path and skills_path.is_dir():
            skill_dirs = sorted(path for path in skills_path.iterdir() if path.is_dir())
            if not skill_dirs:
                errors.append("plugin manifest: bundled skills directory is empty")
            for skill_dir in skill_dirs:
                skill_file = skill_dir / "SKILL.md"
                if not skill_file.is_file():
                    errors.append(f"skill directory missing SKILL.md: {skill_dir.relative_to(root)}")
                    continue
                try:
                    metadata = parse_skill_front_matter(skill_file)
                    if metadata["name"] in skill_names:
                        errors.append(f"duplicate bundled skill name: {metadata['name']}")
                    skill_names.add(metadata["name"])
                except ValidationError as exc:
                    errors.append(str(exc))

        marketplace = load_json(root / MARKETPLACE_MANIFEST)
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            errors.append("marketplace: plugins must be a non-empty array")
        else:
            matches = [entry for entry in plugins if isinstance(entry, dict) and entry.get("name") == name]
            if len(matches) != 1:
                errors.append("marketplace: expected exactly one entry matching plugin name")
            else:
                source = matches[0].get("source")
                if not isinstance(source, dict):
                    errors.append("marketplace: plugin source must be an object")
                else:
                    source_path = source.get("path")
                    if not isinstance(source_path, str):
                        errors.append("marketplace: source.path must be a string")
                    else:
                        try:
                            resolved = contained_path(root, source_path, "marketplace.source.path")
                            if resolved != root.resolve():
                                errors.append("marketplace: cv-app source must resolve to plugin root")
                        except ValidationError as exc:
                            errors.append(str(exc))
                policy = matches[0].get("policy")
                if not isinstance(policy, dict):
                    errors.append("marketplace: policy object is required")
                else:
                    for key in ("installation", "authentication"):
                        if not isinstance(policy.get(key), str) or not policy[key]:
                            errors.append(f"marketplace: policy.{key} is required")
                if not isinstance(matches[0].get("category"), str):
                    errors.append("marketplace: category is required")

        fixture = load_json(root / SYNTHETIC_FIXTURE)
        required_fixture_values = {
            "synthetic": True,
            "contains_real_personal_data": False,
            "safe_for_public_distribution": True,
        }
        for field, expected in required_fixture_values.items():
            if fixture.get(field) is not expected:
                errors.append(f"synthetic fixture: {field} must be {expected!r}")
        for field in ("source", "expected_closure"):
            value = fixture.get(field)
            if not isinstance(value, str):
                errors.append(f"synthetic fixture: {field} must be a path string")
                continue
            try:
                path = contained_path((root / SYNTHETIC_FIXTURE).parent, f"./{value}", f"fixture.{field}")
                if not path.is_file():
                    errors.append(f"synthetic fixture: missing {field} file {value}")
            except ValidationError as exc:
                errors.append(str(exc))

        errors.extend(scan_public_tree(root))
    except ValidationError as exc:
        errors.append(str(exc))
    return sorted(set(errors))


def scan_public_tree(root: Path) -> list[str]:
    errors: list[str] = []
    local_literals: list[str] = []
    local_path = root / LOCAL_DENYLIST
    if local_path.exists():
        local_literals = [
            line.strip()
            for line in local_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if ".git" in path.parts or path == local_path:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = path.relative_to(root)
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"privacy scan: apparent secret material in {relative}")
        for literal in local_literals:
            if literal.casefold() in text.casefold():
                errors.append(f"privacy scan: local private marker found in {relative}")

    fixture_dir = root / SYNTHETIC_FIXTURE.parent
    for path in fixture_dir.rglob("*") if fixture_dir.exists() else []:
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.IGNORECASE):
            errors.append(f"privacy scan: email-like value in synthetic fixture {path.relative_to(root)}")
        if re.search(r"(?<!\d)(?:\+?\d[\d ()-]{8,}\d)(?!\d)", text):
            errors.append(f"privacy scan: phone-like value in synthetic fixture {path.relative_to(root)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate_plugin(root)
    payload = {
        "kind": "cv-app.plugin-validation",
        "version": 1,
        "root": root.as_posix(),
        "valid": not errors,
        "errors": errors,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
