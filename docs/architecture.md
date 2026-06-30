# Architecture v0

## Product boundary

`cv-app` is an installable Codex plugin that supplies progressive professional-identity workflows. It is not a public candidate database and does not contain real candidate material.

```text
Codex
  -> cv-app plugin
      -> grind-with-doc skill
          -> private candidate workspace or bounded conversation
```

The current slice is instruction-first. It contains no MCP server, lifecycle hook, database, remote transport, or rendering engine.

## Public and private authority

### Public `cv-app`

Owns:

- Codex plugin packaging;
- reusable skills;
- evidence, contribution, identity, closure, and promotion method;
- synthetic fixtures;
- conformance validation;
- future runtime contracts.

Must not own:

- real identity or contact data;
- employment, project, evidence, target, application, or outcome records;
- private source documents;
- candidate-specific defaults;
- generated private artifacts.

### Private candidate workspace

Owns:

- one candidate identity;
- raw statements and source material;
- canonical professional records;
- evidence and visibility boundaries;
- grind sessions and proposals;
- target analyses and applications;
- historical outcomes.

## First capability

The first capability resolves one bounded professional-identity uncertainty through:

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

The skill may iterate across investigation, modeling, and testing multiple times. It does not treat first-pass wording as closure.

## Extraction from the private research corpus

The private CV repository demonstrated several reusable patterns:

- mission-first retrieval;
- sources preserved before promotion;
- epistemic status separated from lifecycle status;
- visibility carried through derivation;
- contribution analysis based on ownership, mechanism, effect, proof, quantification, and boundary;
- target projection separated from durable identity;
- dependent review invalidated after material upstream change;
- historical applications preserved;
- outcomes routed into future evidence and positioning work.

The public implementation extracts these patterns, not their candidate-specific records, IDs, wording, projects, targets, or accepted career decisions.

## Design passes

### Pass 1: Codex packaging

Decision:

- plugin root is the repository root;
- `.codex-plugin/plugin.json` is the required entry point;
- bundled skills are referenced through `./skills/`;
- `.agents/plugins/marketplace.json` exposes the local repository plugin;
- no `.mcp.json` is advertised because no server exists;
- no hook is included because there is no trusted deterministic lifecycle need.

### Pass 2: domain extraction

Initial risk:

A direct copy of the private repository would embed one candidate's project gates, role models, target vocabulary, and authority topology.

Decision:

- extract general status, visibility, evidence, contribution, promotion, invalidation, and history rules;
- replace candidate-specific routes with one skill focused on a bounded uncertainty;
- keep private candidate workspaces as consumers rather than bundled examples;
- use a synthetic museum-installation fixture unrelated to known private data.

### Pass 3: product-loop test

Initial failure mode:

The skill could have chosen between `technical lead` and `technician` too quickly, producing a binary answer that erased real coordination or overstated authority.

Decision:

- require explicit competing models;
- test candidate recognition separately from evidence fit;
- allow a narrower, evidence-backed model such as integration ownership;
- require closure states that can retain unknowns;
- permit a successful session without final CV wording or canonical mutation.

## Deferred boundaries

### MCP

A bundled `.mcp.json` will be added only after a real local stdio server exists. The server should enforce candidate-root containment, revisions, proposal application, and deterministic storage operations. The skill should remain the reasoning procedure.

### Hooks

Hooks will be added only for a concrete trusted lifecycle need. Installation does not justify background commands.

### Candidate runtime

Candidate workspace schemas, CLI, persistence, and atomic promotion remain a later vertical slice.

### Remote operation

HTTP transport, authentication, `orb-gate`, ngrok, Orb placement, and VPS deployment remain outside this slice.
