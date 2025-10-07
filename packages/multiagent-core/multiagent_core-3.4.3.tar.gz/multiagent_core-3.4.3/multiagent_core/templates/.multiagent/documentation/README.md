# Documentation Management System

A lightweight foundation for project documentation. The initializer script creates the `docs/` directory and a universal README template, while dedicated subagents generate and maintain the actual content.

## Components

1. **Bootstrap Script** (`scripts/create-structure.sh`)
   - Ensures `docs/` exists.
   - Copies `docs/README.md` from the universal template.
   - Seeds JSON memory files so agents can track status.

2. **Subagents**
   - **docs-init** runs the script (if needed), detects project type from specs, fills README placeholders, and creates any extra documentation files relevant to the project.
   - **docs-update** refreshes existing documentation without creating new files.
   - **docs-validate** checks the generated documentation for completeness and consistency.

3. **State Files** (under `memory/`)
   - `template-status.json` – tracks placeholder completion state.
   - `doc-registry.json` – registry of documentation files created by the agents.
   - `consistency-check.json` – results from validation passes.
   - `update-history.json` – append-only log of agent changes.

4. **Reference Material**
   - `PLACEHOLDER_REFERENCE.md` – canonical list of placeholders the agents understand.

## Workflow at a Glance

1. `multiagent init` copies this module into new projects and runs the bootstrap script.
2. `/docs init` executes `docs-init`, which fills the README and creates additional docs if the project type requires them.
3. `/docs update` applies non-destructive updates to documents already registered.
4. `/docs validate` reports missing placeholders or inconsistencies.

## Design Principles

- Keep templates minimal and easy to reason about.
- Push all contextual intelligence into subagents where specifications and code history are available.
- Never delete user-authored content—agents always preserve what exists.
- Use the JSON memory files as the single source of truth for documentation status.

## File Layout

```
.multiagent/documentation/
├── README.md
├── PLACEHOLDER_REFERENCE.md
├── init-hook.sh
├── scripts/
│   └── create-structure.sh
├── templates/
│   └── README.template.md
└── memory/
    ├── template-status.json
    ├── doc-registry.json
    ├── consistency-check.json
    └── update-history.json
```

## Next Steps for Agents

- Update agent prompts via `/update-agent-context` to reflect this architecture.
- Extend docs-init/docs-update/docs-validate to consume the memory files and placeholder reference.
- Add project-specific documentation templates within the subagents (not in the bootstrap script) if more coverage is needed.
