## What and why
<!-- One or two sentences: what changes, and what problem it solves. -->

## Checklist
- [ ] `make lint types test` pass locally (and `make eval` if agent behaviour changed)
- [ ] Still **read-only**: no new write tool, no new write path in an MCP server or adapter
- [ ] No secrets, `.env` values or real production data in the diff, tests, fixtures or docs
- [ ] New behaviour has a test; new code carries the usual `WHAT / WHERE / KEY IDEAS` docstring and `# LEARN:` / `# WHY:` notes
- [ ] Docs updated if a setting, event or endpoint changed (`docs/spec/API.md`, `.env.example`, `README.md`)
