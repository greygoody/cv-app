Use the installed `$grind-with-doc` skill explicitly.

You are running a behavioral acceptance test for the `cv-app` Codex plugin inside a fresh synthetic candidate Git repository.

## Boundaries

- Candidate: `candidate.morgan-vale`.
- Focus ID: `focus.technical-lead-vs-integration-owner`.
- Mode: `align`.
- Active question: Does the available evidence support describing this candidate as the technical lead for the whole exhibition, or is a narrower integration-ownership model more accurate?
- The only source you may read is `source.md` in the current repository.
- Do not inspect parent directories, home-directory files, global Codex configuration, network sources, Git history, or any other candidate data.
- Do not modify `source.md`.
- Do not create or modify canonical candidate records.
- Do not claim a promotion was applied.
- The only file you may create is `session-closure.md`.

## Required reasoning behavior

Follow the progressive loop rather than immediately producing a polished CV bullet:

1. Bind the candidate, source, focus, mode, and closure condition.
2. Preserve the candidate statement separately from observed facts.
3. Compare these three models explicitly:
   - `whole-exhibition-technical-lead`;
   - `installation-integration-owner-operational-handoff`;
   - `documentation-only-technician`.
4. Test each model against evidence fit, candidate recognition, market legibility, and claim safety.
5. Reject the whole-exhibition technical-lead model if the evidence does not support project-wide authority.
6. Reject the documentation-only technician model if it erases supported integration and coordination responsibility.
7. Select the installation integration-owner and operational-handoff model only if it is the strongest supported interpretation.
8. Retain unmeasured duration, reliability, recovery-time, uptime, and cost effects as unknown rather than inventing numbers.
9. Record prohibited inferences for formal project-wide leadership, people management, budget or creative authority, and quantified reliability impact.
10. Close as `resolved-proposed`, not promoted.

## Required file

Create `session-closure.md` using the structure provided by the installed skill. It must include:

- candidate and focus identity;
- source boundary;
- candidate statement;
- observed facts;
- all three models and their decisions;
- selected proposed framing;
- retained unknowns;
- prohibited inferences;
- explicit statement that no canonical mutation occurred;
- closure state `resolved-proposed`.

## Final response

Return only the JSON object required by the supplied output schema.

Use these exact identifiers:

- selected model: `installation-integration-owner-operational-handoff`;
- rejected models: `whole-exhibition-technical-lead`, `documentation-only-technician`;
- retained unknowns: `post-installation-ownership-duration`, `measured-reliability-or-recovery-effect`;
- prohibited inferences: `formal-project-wide-leadership`, `people-management`, `budget-or-creative-authority`, `quantified-reliability-impact`.

Set `skill_used` to `grind-with-doc`, `closure_file` to `session-closure.md`, `closure_written` to true, and `canonical_mutation_performed` to false.
