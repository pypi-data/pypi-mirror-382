# Standard Documentation Placeholders

The documentation subagents understand the following universal placeholders. Keep templates simple and let the agents decide how much content to generate.

| Placeholder | Description |
|-------------|-------------|
| `{{PROJECT_NAME}}` | Human-friendly project name derived from specs or repository metadata |
| `{{DESCRIPTION}}` | Short summary of what the project delivers |
| `{{GETTING_STARTED}}` | Quick intro or checklist for new contributors |
| `{{INSTALLATION}}` | Steps required to install or bootstrap the project |
| `{{USAGE}}` | How to execute or interact with the project once installed |
| `{{SUPPORT}}` | Where to file issues, escalation channels, or support notes |
| `{{LICENSE}}` | License statement or reference to the LICENSE file |

## Agent Expectations
- **docs-init** fills all placeholders intelligently based on the project type and spec contents. It may also create additional documentation files when relevant.
- **docs-update** edits only documents that already exist, preserving existing content and placeholders the agent does not need to touch.
- **docs-validate** checks completed documents for missing placeholders and ensures the generated content matches the project type.

Remember: keep templates minimal. If you introduce a new placeholder, add it to this reference file and update the agent prompts so they know how to populate it.
