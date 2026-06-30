# cv-app

`cv-app` is an open-source Codex plugin for progressive, evidence-bound professional identity alignment and CV work.

The plugin helps a person finish one bounded uncertainty at a time. It does not assume that the user already knows the correct professional label, role category, contribution wording, or target framing.

## Current capability

The first bundled skill is `grind-with-doc`.

Use it when a candidate is unsure:

- what they actually owned in a project or role;
- whether a title or professional label fits;
- which interpretation is supported, limited, or still unknown;
- why a CV section feels inaccurate or generic;
- whether target-facing wording preserves the underlying evidence.

The skill works progressively:

```text
focus
  -> externalize
  -> distinguish
  -> investigate
  -> model alternatives
  -> test
  -> compose when ready
  -> challenge
  -> confirm
  -> propose promotion
  -> close
```

A successful session may close with a proposal, a rejected interpretation, or a bounded evidence request. It does not need to rewrite the whole CV.

## Install in Codex

For local development, add the repository root as a marketplace:

```sh
codex plugin marketplace add /absolute/path/to/cv-app
```

For repository distribution after the desired branch is available:

```sh
codex plugin marketplace add greygoody/cv-app --ref main
```

Install from the configured marketplace non-interactively:

```sh
codex plugin add cv-app --marketplace cv-app-development
```

Or restart Codex, open `/plugins`, select the `CV App Development` marketplace, and install `CV App`.

Invoke the skill explicitly with `$grind-with-doc`, or describe a matching professional-identity uncertainty and let Codex select it implicitly.

## Repository structure

```text
.codex-plugin/plugin.json             plugin manifest
.agents/plugins/marketplace.json      local repository marketplace
skills/grind-with-doc/                progressive alignment skill
examples/synthetic-candidate/         public synthetic proof fixture
scripts/validate_plugin.py            package and privacy validation
scripts/run_codex_local_acceptance.sh installed-plugin agent harness
tests/agent/                           model-backed prompt, schema, and docs
tests/                                 fail-closed deterministic tests
docs/architecture.md                  product and extraction boundary
```

## Deterministic proof

```sh
just proof
```

The proof validates plugin paths, skill metadata, marketplace wiring, synthetic-fixture declarations, absence of advertised missing components, optional local private-marker scanning, and the acceptance-result validator.

## Local Codex acceptance

On a trusted machine with a current authenticated Codex CLI:

```sh
just agent-acceptance
```

This opt-in harness:

1. clones the selected repository ref;
2. runs deterministic proof on the clone;
3. creates a unique temporary Codex marketplace;
4. installs the actual cloned plugin;
5. creates a fresh synthetic candidate Git repository;
6. spawns a separate `codex exec` consumer using `$grind-with-doc`;
7. validates the JSONL event stream, schema-constrained final report, closure content, unchanged source, and exact mutation set;
8. removes only the temporary plugin and marketplace it introduced.

The exact outer-agent prompt is in:

```text
tests/agent/prompts/local-supervisor-workcell.md
```

Detailed prerequisites and limitations are documented in `tests/agent/README.md`.

## Privacy boundary

This public repository contains method, plugin packaging, synthetic fixtures, and validation only. Real candidate identity, contact information, experience, evidence, targets, applications, and artifacts belong in separate private candidate workspaces.

Create an ignored `.cv-app-private-denylist` locally to scan for private names, emails, repository identifiers, or other markers that must never enter this public repository.

## Deferred

The current slice contains no MCP server, hook, candidate database, web UI, remote transport, or deployment integration. Those components will be added only after a real deterministic boundary exists for them.
