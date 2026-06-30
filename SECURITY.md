# Security and privacy

## Supported state

`cv-app` is pre-release. The current plugin contains an instruction-only skill and static validation. It does not yet run an MCP server, accept network traffic, store credentials, or provide a canonical candidate-data runtime.

## Public-data boundary

Do not report public synthetic fixtures as a privacy incident. Do report any committed material that appears to identify or describe a real candidate, employer relationship, private project, target application, source document, or contact channel.

Real candidate data belongs in a separate private workspace. The public repository must contain only:

- reusable method and contracts;
- plugin packaging;
- deterministic validation;
- wholly synthetic fixtures;
- public documentation.

## Reporting

Open a private security advisory in the GitHub repository for vulnerabilities or suspected personal-data exposure. Do not paste exposed personal material into a public issue.

## Future runtime expectations

Any future candidate runtime must fail closed on:

- candidate-root traversal and symlink escape;
- sibling-candidate access;
- stale revision mutation;
- visibility broadening;
- unconfirmed promotion;
- credential or secret logging;
- arbitrary filesystem or shell access through MCP tools.
