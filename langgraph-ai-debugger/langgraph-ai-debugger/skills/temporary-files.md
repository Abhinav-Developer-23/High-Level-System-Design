
# Temporary Files

- Put every temporary, generated, intermediate, downloaded, or investigation-only file under the workspace `tmp/` directory.
- This includes ad hoc Markdown reports, SQL/CSV/JSON evidence, patches, log downloads, reconciliation outputs, scratch scripts, and command output captures.
- Store archival-log downloads specifically under `tmp/logs/archival/`.
- Do not create new temporary artifacts under `out/`, the repository root, or source directories.
- `tmp/` is intentionally gitignored. Do not force-add anything from it.
- A durable source/config file explicitly requested by the user is not temporary and belongs in its normal project path.
