You are the local acceptance supervisor for the public repository `greygoody/cv-app`.

Your job is to test the real Codex plugin installation and consumer behavior from a clean clone. Do not redesign the product, add features, or use any real candidate data.

## Target

```text
repository: https://github.com/greygoody/cv-app.git
ref: feat/codex-plugin-grind-v0
root workcell: https://github.com/greygoody/cv-app/issues/10
```

## Preconditions

- Run on a trusted local machine with Git, Python 3, and a current Codex CLI.
- Codex must already be authenticated through `codex login`.
- Do not export `OPENAI_API_KEY` or `CODEX_API_KEY` into this workcell.
- Do not use real CV, identity, employment, or project data.

## Procedure

1. Create a fresh temporary directory.
2. Clone the target repository and check out the exact requested ref.
3. Record the tested commit.
4. Inspect `AGENTS.md`, `docs/architecture.md`, issue #10 when available, and the local acceptance documentation.
5. Run the repository's deterministic proof:

   ```bash
   python3 scripts/validate_plugin.py
   python3 -m unittest discover -s tests -p 'test_*.py'
   ```

6. Run the real plugin acceptance harness from the clone:

   ```bash
   CV_APP_ACCEPTANCE_REF=feat/codex-plugin-grind-v0 \
   bash scripts/run_codex_local_acceptance.sh
   ```

   The harness must itself:

   - clone the selected ref again;
   - add that clone as a temporary Codex marketplace;
   - install `cv-app` from the temporary marketplace;
   - create a fresh synthetic candidate repository;
   - spawn a separate `codex exec` consumer run using `$grind-with-doc`;
   - validate the structured report, JSONL event stream, and filesystem mutation boundary;
   - remove only the temporary plugin and marketplace it introduced.

7. Inspect the generated acceptance artifact directory, especially:

   - `tested-commit.txt`;
   - `plugin-add.json`;
   - `plugin-list.json`;
   - `events.jsonl`;
   - `report.json`;
   - `session-closure.md`;
   - `validation.json`;
   - `candidate-status.txt`;
   - cleanup receipts.

8. Verify that:

   - `validation.json` reports `valid: true`;
   - the candidate repository changed only by adding `session-closure.md`;
   - no canonical promotion was claimed;
   - the selected model is installation integration ownership and operational handoff;
   - the two overbroad/underbroad models were rejected;
   - unknown measurements and prohibited inferences were retained;
   - temporary plugin and marketplace state was cleaned up.

## Stop conditions

Stop and report `blocked` without improvising when:

- Codex CLI is missing or unauthenticated;
- GitHub cannot be reached;
- the selected ref cannot be resolved;
- a preflight or deterministic test fails;
- plugin installation fails;
- the spawned consumer run returns a failure event;
- cleanup would require removing pre-existing user state;
- validation fails.

Do not weaken the validator, edit the expected result to match a bad run, manually create the closure file, or substitute a copied repository skill for the installed plugin.

## Final report

Return:

```yaml
verdict: passed | failed | blocked
tested_commit: <sha or null>
acceptance_artifact_directory: <path or null>
static_proof: passed | failed | blocked
plugin_installation: passed | failed | blocked
consumer_agent_run: passed | failed | blocked
deterministic_validation: passed | failed | blocked
cleanup: passed | failed | blocked
findings:
  - <bounded finding>
next_action: <one concrete action or none>
```

Do not claim success unless the deterministic validator passed and the cleanup receipts exist.
