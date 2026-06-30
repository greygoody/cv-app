# Agent contract

## Mission

Develop `cv-app` as a public, candidate-agnostic Codex plugin for progressive professional-identity and CV work.

## Entry

1. Read issue #1 or the active workcell.
2. Read `docs/architecture.md`.
3. Inspect `.codex-plugin/plugin.json` and the affected skill.
4. Use only synthetic fixtures from this repository.
5. Run `just proof` before claiming completion.

## Privacy boundary

Never commit real candidate data, including:

- names, addresses, phone numbers, email addresses, or profile URLs;
- employment, education, project, portfolio, evidence, target, application, or outcome records;
- private repository names or private document excerpts;
- data copied from `greygoody/cv` or another candidate workspace.

Extract reusable rules and patterns only. When a private corpus inspires a rule, rewrite it generically and test it against synthetic material.

## Product boundary

- Skills own reusable reasoning procedures.
- Future deterministic tools own validation, containment, revision checks, and mutation.
- Candidate workspaces own personal truth.
- The plugin does not silently turn temporary conversation into canonical records.
- One active candidate and one active focus are required before candidate retrieval.
- Source, observation, interpretation, proposal, confirmation, promotion, and projection remain distinct.

## Change discipline

- Keep each skill focused on one job.
- Prefer instructions over scripts until deterministic behavior is required.
- Do not advertise MCP servers, apps, hooks, or assets that do not exist.
- Keep plugin paths relative, `./`-prefixed, and contained by the plugin root.
- Use semantic versioning in the plugin manifest.
- Material skill changes require a synthetic scenario review.
- Do not create real-person examples with altered names.

## Deferred work

Do not add a web UI, hosted database, remote MCP deployment, Orb deployment, or full CV generator unless an accepted workcell grants that scope.
