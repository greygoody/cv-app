#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${CV_APP_ACCEPTANCE_REPO:-https://github.com/greygoody/cv-app.git}"
REF="${CV_APP_ACCEPTANCE_REF:-feat/codex-plugin-grind-v0}"
MODEL="${CV_APP_CODEX_MODEL:-}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${CV_APP_ACCEPTANCE_OUT:-$PWD/.local/agent-acceptance/$STAMP}"
MARKETPLACE_NAME="cv-app-acceptance-${STAMP,,}-$$"
TMP_ROOT="$(mktemp -d -t cv-app-acceptance.XXXXXX)"
CLONE_ROOT="$TMP_ROOT/cv-app"
MARKET_ROOT="$TMP_ROOT/marketplace"
CANDIDATE_ROOT="$OUT_ROOT/candidate"
PLUGIN_ADDED=0
MARKETPLACE_ADDED=0

cleanup() {
  local exit_code=$?
  if [[ "$PLUGIN_ADDED" == "1" ]]; then
    codex plugin remove "cv-app@$MARKETPLACE_NAME" --json \
      > "$OUT_ROOT/plugin-remove.json" 2> "$OUT_ROOT/plugin-remove.stderr" || true
  fi
  if [[ "$MARKETPLACE_ADDED" == "1" ]]; then
    codex plugin marketplace remove "$MARKETPLACE_NAME" --json \
      > "$OUT_ROOT/marketplace-remove.json" 2> "$OUT_ROOT/marketplace-remove.stderr" || true
  fi
  rm -rf "$TMP_ROOT"
  exit "$exit_code"
}
trap cleanup EXIT INT TERM

fail() {
  printf 'cv-app acceptance error: %s\n' "$*" >&2
  exit 1
}

for command in git python3 codex; do
  command -v "$command" >/dev/null 2>&1 || fail "required command not found: $command"
done

if [[ -n "${OPENAI_API_KEY:-}" || -n "${CODEX_API_KEY:-}" ]]; then
  fail "do not export OPENAI_API_KEY or CODEX_API_KEY while running repository-controlled setup; use saved 'codex login' authentication"
fi

mkdir -p "$OUT_ROOT"
printf '%s\n' "$REPO_URL" > "$OUT_ROOT/repository.txt"
printf '%s\n' "$REF" > "$OUT_ROOT/requested-ref.txt"
codex --version > "$OUT_ROOT/codex-version.txt"
python3 --version > "$OUT_ROOT/python-version.txt" 2>&1
git --version > "$OUT_ROOT/git-version.txt"

printf 'Cloning %s at %s...\n' "$REPO_URL" "$REF"
git clone --no-checkout "$REPO_URL" "$CLONE_ROOT" \
  > "$OUT_ROOT/clone.stdout" 2> "$OUT_ROOT/clone.stderr"
git -C "$CLONE_ROOT" checkout --detach "$REF" \
  > "$OUT_ROOT/checkout.stdout" 2> "$OUT_ROOT/checkout.stderr"
git -C "$CLONE_ROOT" rev-parse HEAD > "$OUT_ROOT/tested-commit.txt"

printf 'Running static proof on cloned source...\n'
(
  cd "$CLONE_ROOT"
  python3 scripts/validate_plugin.py
  python3 -m unittest discover -s tests -p 'test_*.py'
) > "$OUT_ROOT/static-proof.stdout" 2> "$OUT_ROOT/static-proof.stderr"

printf 'Preparing isolated marketplace %s...\n' "$MARKETPLACE_NAME"
cp -a "$CLONE_ROOT" "$MARKET_ROOT"
python3 - "$MARKET_ROOT/.agents/plugins/marketplace.json" "$MARKETPLACE_NAME" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
name = sys.argv[2]
data = json.loads(path.read_text(encoding="utf-8"))
data["name"] = name
data.setdefault("interface", {})["displayName"] = f"CV App Acceptance {name}"
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY

codex plugin marketplace add "$MARKET_ROOT" --json \
  > "$OUT_ROOT/marketplace-add.json" 2> "$OUT_ROOT/marketplace-add.stderr"
MARKETPLACE_ADDED=1

codex plugin add "cv-app@$MARKETPLACE_NAME" --json \
  > "$OUT_ROOT/plugin-add.json" 2> "$OUT_ROOT/plugin-add.stderr"
PLUGIN_ADDED=1

codex plugin list --json > "$OUT_ROOT/plugin-list.json"
python3 - "$OUT_ROOT/plugin-list.json" "$MARKETPLACE_NAME" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
marketplace = sys.argv[2]
data = json.loads(path.read_text(encoding="utf-8"))
installed = data.get("installed", [])
match = [
    item for item in installed
    if item.get("name") == "cv-app"
    and item.get("marketplaceName") == marketplace
    and item.get("installed") is True
    and item.get("enabled") is True
]
if len(match) != 1:
    raise SystemExit(f"expected one enabled cv-app installation from {marketplace!r}; got {match!r}")
PY

printf 'Creating fresh synthetic candidate repository...\n'
mkdir -p "$CANDIDATE_ROOT"
cp "$CLONE_ROOT/examples/synthetic-candidate/source.md" "$CANDIDATE_ROOT/source.md"
git -C "$CANDIDATE_ROOT" init -q
git -C "$CANDIDATE_ROOT" config user.name "cv-app acceptance"
git -C "$CANDIDATE_ROOT" config user.email "acceptance@example.invalid"
git -C "$CANDIDATE_ROOT" add source.md
git -C "$CANDIDATE_ROOT" commit -q -m "test: seed synthetic candidate source"

CODEX_ARGS=(
  exec
  --ephemeral
  --sandbox workspace-write
  --ask-for-approval never
  --search=false
  --json
  --output-schema "$CLONE_ROOT/tests/agent/output.schema.json"
  --output-last-message "$OUT_ROOT/report.json"
  --cd "$CANDIDATE_ROOT"
)
if [[ -n "$MODEL" ]]; then
  CODEX_ARGS+=(--model "$MODEL")
fi
CODEX_ARGS+=(-)

printf 'Spawning fresh Codex consumer agent...\n'
codex "${CODEX_ARGS[@]}" \
  < "$CLONE_ROOT/tests/agent/prompts/technical-lead-vs-integration-owner.md" \
  > "$OUT_ROOT/events.jsonl" \
  2> "$OUT_ROOT/codex.stderr"

printf 'Validating structured report, event stream, and workspace effects...\n'
python3 "$CLONE_ROOT/scripts/validate_agent_acceptance.py" \
  --candidate-root "$CANDIDATE_ROOT" \
  --report "$OUT_ROOT/report.json" \
  --events "$OUT_ROOT/events.jsonl" \
  --expected-source "$CLONE_ROOT/examples/synthetic-candidate/source.md" \
  | tee "$OUT_ROOT/validation.json"

git -C "$CANDIDATE_ROOT" status --porcelain --untracked-files=all \
  > "$OUT_ROOT/candidate-status.txt"
cp "$CANDIDATE_ROOT/session-closure.md" "$OUT_ROOT/session-closure.md"

printf '\nAcceptance passed. Artifacts: %s\n' "$OUT_ROOT"
