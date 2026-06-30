#!/usr/bin/env python3
"""Validate the local Codex plugin acceptance run without model judgment."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

EXPECTED = {
    "status": "passed",
    "skill_used": "grind-with-doc",
    "candidate_id": "candidate.morgan-vale",
    "focus_id": "focus.technical-lead-vs-integration-owner",
    "source_files_read": ["source.md"],
    "closure_state": "resolved-proposed",
    "selected_model_id": "installation-integration-owner-operational-handoff",
    "closure_file": "session-closure.md",
    "closure_written": True,
    "canonical_mutation_performed": False,
}

REQUIRED_REJECTED = {
    "whole-exhibition-technical-lead",
    "documentation-only-technician",
}
REQUIRED_UNKNOWNS = {
    "post-installation-ownership-duration",
    "measured-reliability-or-recovery-effect",
}
REQUIRED_PROHIBITED = {
    "formal-project-wide-leadership",
    "people-management",
    "budget-or-creative-authority",
    "quantified-reliability-impact",
}
REQUIRED_CLOSURE_MARKERS = (
    "candidate.morgan-vale",
    "focus.technical-lead-vs-integration-owner",
    "resolved-proposed",
    "whole-exhibition-technical-lead",
    "installation-integration-owner-operational-handoff",
    "documentation-only-technician",
    "formal-project-wide-leadership",
    "people-management",
    "budget-or-creative-authority",
    "quantified-reliability-impact",
    "no canonical mutation",
)


class AcceptanceError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AcceptanceError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AcceptanceError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AcceptanceError(f"{path}: expected a JSON object")
    return value


def require_set(report: dict[str, Any], field: str, required: set[str], errors: list[str]) -> None:
    value = report.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"report.{field}: expected an array of strings")
        return
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"report.{field}: missing required values {missing}")


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field, expected in EXPECTED.items():
        if report.get(field) != expected:
            errors.append(f"report.{field}: expected {expected!r}, got {report.get(field)!r}")

    require_set(report, "rejected_model_ids", REQUIRED_REJECTED, errors)
    require_set(report, "retained_unknown_ids", REQUIRED_UNKNOWNS, errors)
    require_set(report, "prohibited_inference_ids", REQUIRED_PROHIBITED, errors)

    summary = report.get("summary")
    if not isinstance(summary, str) or not 40 <= len(summary) <= 800:
        errors.append("report.summary: expected 40 to 800 characters")
    return errors


def validate_events(path: Path) -> list[str]:
    errors: list[str] = []
    seen_completed = False
    seen_agent_message = False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return [f"missing event stream: {path}"]

    if not lines:
        return ["event stream is empty"]

    for line_number, line in enumerate(lines, start=1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"events line {line_number}: invalid JSON: {exc}")
            continue
        if not isinstance(event, dict):
            errors.append(f"events line {line_number}: expected object")
            continue
        event_type = event.get("type")
        if event_type in {"error", "turn.failed"}:
            errors.append(f"event stream contains failure event {event_type!r}")
        if event_type == "turn.completed":
            seen_completed = True
        item = event.get("item")
        if (
            event_type == "item.completed"
            and isinstance(item, dict)
            and item.get("type") == "agent_message"
        ):
            seen_agent_message = True

    if not seen_completed:
        errors.append("event stream does not contain turn.completed")
    if not seen_agent_message:
        errors.append("event stream does not contain a completed agent message")
    return errors


def validate_workspace(candidate_root: Path, expected_source: Path) -> list[str]:
    errors: list[str] = []
    source = candidate_root / "source.md"
    closure = candidate_root / "session-closure.md"

    if not source.is_file():
        errors.append("candidate workspace is missing source.md")
    elif source.read_bytes() != expected_source.read_bytes():
        errors.append("source.md changed during the agent run")

    if not closure.is_file():
        errors.append("candidate workspace is missing session-closure.md")
    else:
        text = closure.read_text(encoding="utf-8", errors="replace")
        folded = text.casefold()
        for marker in REQUIRED_CLOSURE_MARKERS:
            if marker.casefold() not in folded:
                errors.append(f"session-closure.md is missing marker {marker!r}")

    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=candidate_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        errors.append(f"cannot inspect candidate Git status: {result.stderr.strip()}")
    else:
        changed = sorted(line for line in result.stdout.splitlines() if line.strip())
        if changed != ["?? session-closure.md"]:
            errors.append(
                "candidate workspace mutation set must be exactly ['?? session-closure.md']; "
                f"got {changed!r}"
            )
    return errors


def validate(candidate_root: Path, report_path: Path, events_path: Path, expected_source: Path) -> list[str]:
    errors: list[str] = []
    try:
        report = load_json(report_path)
    except AcceptanceError as exc:
        errors.append(str(exc))
    else:
        errors.extend(validate_report(report))
    errors.extend(validate_events(events_path))
    errors.extend(validate_workspace(candidate_root, expected_source))
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--events", required=True, type=Path)
    parser.add_argument("--expected-source", required=True, type=Path)
    args = parser.parse_args()

    errors = validate(
        args.candidate_root.resolve(),
        args.report.resolve(),
        args.events.resolve(),
        args.expected_source.resolve(),
    )
    payload = {
        "kind": "cv-app.agent-acceptance-validation",
        "version": 1,
        "valid": not errors,
        "errors": errors,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
