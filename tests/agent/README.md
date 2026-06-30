# Local Codex plugin acceptance

This directory contains the model-backed acceptance test for the installed `cv-app` plugin.

The ordinary deterministic proof does not call a model. The local acceptance harness is opt-in because it requires:

- network access to clone the selected repository ref;
- Bash, Git, and Python 3;
- a current Codex CLI;
- saved authentication from `codex login`;
- model usage;
- temporary changes to local Codex plugin configuration.

`just` is optional convenience tooling. It is not required for acceptance.

## What it proves

The harness exercises this path:

```text
fresh clone
  -> deterministic repository proof
  -> temporary local marketplace
  -> actual cv-app plugin installation
  -> fresh synthetic candidate Git repository
  -> separate codex exec consumer run
  -> JSON Schema constrained report
  -> deterministic event, content, and mutation validation
  -> plugin and marketplace cleanup
```

It does not copy `SKILL.md` into `.agents/skills`. The spawned consumer uses the installed plugin.

## Run the full workcell

From the repository checkout:

```bash
CV_APP_ACCEPTANCE_REF=feat/codex-plugin-grind-v0 \
bash scripts/run_local_acceptance_workcell.sh
```

This dependency-free entrypoint runs:

```bash
python3 scripts/validate_plugin.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash scripts/run_codex_local_acceptance.sh
```

When `just` happens to be installed, this is equivalent:

```bash
just agent-acceptance
```

Optional environment variables:

```text
CV_APP_ACCEPTANCE_REPO   Git repository URL
CV_APP_ACCEPTANCE_REF    branch, tag, or commit-ish to test
CV_APP_ACCEPTANCE_OUT    persistent artifact directory
CV_APP_CODEX_MODEL       optional model override
```

The default output location is:

```text
.local/agent-acceptance/<UTC timestamp>/
```

## Ask a local Codex supervisor to run it

Give a fresh local Codex agent the complete prompt in:

```text
tests/agent/prompts/local-supervisor-workcell.md
```

That supervisor clones the repository, invokes the dependency-free workcell entrypoint, and inspects its receipts.

The nested consumer prompt is:

```text
tests/agent/prompts/technical-lead-vs-integration-owner.md
```

The consumer's final response must satisfy:

```text
tests/agent/output.schema.json
```

## Security

Do not run this harness with `OPENAI_API_KEY` or `CODEX_API_KEY` exported. Repository-controlled setup executes before the model invocation. Use saved Codex authentication instead.

The consumer runs with:

```text
--ephemeral
--sandbox workspace-write
approval_policy="never"
web_search="disabled"
mcp_servers={}
apps={}
history.persistence="none"
```

`approval_policy="never"` is supplied through the documented `--config` path. The harness does not place the global `--ask-for-approval` flag after the `exec` subcommand, because Codex CLI 0.142.4 rejects that placement.

The explicit configuration removes cached and live web search, inherited MCP servers, and inherited app tool surfaces from the nested consumer run. Its working directory contains only a committed synthetic `source.md`. The validator requires the sole mutation to be an untracked `session-closure.md`.

The harness records `codex exec --help` in `codex-exec-help.txt` so CLI compatibility can be inspected from the acceptance artifacts.

## Cleanup

The runner creates a unique marketplace name for every invocation. It removes only the plugin and marketplace created under that unique name. Cleanup runs through a shell trap even when the consumer or validator fails.

Cleanup failure makes the entire acceptance run fail. The generated output directory retains installation, execution, validation, and cleanup receipts for inspection.

## Honest limitations

- This is one behavioral scenario, not proof that every ambiguous career question is handled correctly.
- Structured output constrains the final report but does not reveal private model reasoning.
- Plugin discovery and installation remain experimental Codex CLI features.
- The test proves instruction behavior, not candidate storage, atomic promotion, MCP tools, remote operation, or CV rendering.
- A real authenticated local Codex host is still required for the model-backed run. Deterministic repository tests remain suitable for CI.
