
# TPAP monorepo — these six services only

Monorepo debugging checkout: `/Users/abhinavanand/personal_projects/Agent-debugger/repos/upi-tpap-transactional-monorepo`

Only these services are on the monorepo. Their old standalone repos are retired.

| Directory | Was |
|---|---|
| `tpap-reporting/` | new in the monorepo |
| `tpap-transactional-jobs/` | `tpap-transactional-jobs` |
| `tpap-archiver/` | new in the monorepo |
| `tpap-stream-recon/` | `tpap-stream-recon` |
| `tpap-consumers/` | `tpap-consumers_java_17` |
| `tpap-compliance/` | `tpap-compliance` |

**For code debugging of these six, read only this checkout.** Not the retired standalone repos, and not the development checkout `/Users/abhinavanand/Finmate_Projects/upi-tpap-transactional-monorepo`. The `~/Finmate_Projects` repos are where development happens, so they are often on a feature branch and can show code that is not in production. The `repos/` checkout stays on `main`.

- **Read-only.** Never edit, switch branch, commit or push in `repos/`. Do not pull it: a cron job pulls every `repos/` checkout every 5 minutes. If it is not on `main` or has local changes, the user is working there — leave it alone and read `main` from a worktree (see *Reading code — never touch the user's checkout*).
- **Search it by explicit path.** `repos/` is gitignored, so searches from the workspace root skip it. Example: `rg 'ClassName' /Users/abhinavanand/personal_projects/Agent-debugger/repos/upi-tpap-transactional-monorepo/tpap-consumers`.
- **Build and deploy through the monorepo pipelines only.** The individual repo pipelines have been replaced by their monorepo pipelines. Use each service's existing pipeline — do not add a monorepo-wide build.
- **Edits** to these six go in `/Users/abhinavanand/Finmate_Projects/upi-tpap-transactional-monorepo` only — never in `repos/`.

Every other TPAP service stays on its own repo. The monorepo checkout also holds `tpap-transactional-switch/`, `tpap-transactional-bff/`, `tpap-hss/`, `tpap_gwts/` and `tpap-txn-bff-aggregator/`. Those copies are stale, so never read them:

| Repo | Service |
|---|---|
| `/Users/abhinavanand/Finmate_Projects/tpap-transactional-switch` | core switch |
| `/Users/abhinavanand/Finmate_Projects/tpap-transactional-bff` | transactional BFF |
| `/Users/abhinavanand/Finmate_Projects/tpap-hss` | HSS |
| `/Users/abhinavanand/Finmate_Projects/tpap_gwts_hdfc` | GWTS Mindgate HDFC |
| `/Users/abhinavanand/Finmate_Projects/tpap_gwts_axis` | GWTS Juspay Axis |
| `/Users/abhinavanand/Finmate_Projects/tpap_gwts_ocil` | GWTS OCIL Yes Bank |
| `/Users/abhinavanand/Finmate_Projects/tpap_gwts_sbi` | GWTS Mindgate SBI |
| `/Users/abhinavanand/Finmate_Projects/paytm-alerts` | Prometheus alert rules |

TSP has cut over too, even though the TSP monorepo README still says "not yet cut over" (that README is stale): debug TSP services from `/Users/abhinavanand/personal_projects/Agent-debugger/repos/upi-tsp-transactional-monorepo` (same read-only rules), except the switch, which stays on `/Users/abhinavanand/Finmate_Projects/tsp-transactional-switch` until the monorepo copy is resynced. Full map in `CLAUDE.md`.

## Reading code — never touch the user's checkout

**The user develops in these repos by hand, alongside agents. Never disturb their work.** In any source repo — `repos/*` or `~/Finmate_Projects/*` — never run `checkout`/`switch`, `stash`, `reset`, `restore`, `clean`, `pull`, `merge`, `rebase` or `commit`, and never edit a file. A checkout on a feature branch or with uncommitted changes is the user's work in progress, not something to fix.

**Read code at `main` from a temporary worktree**, under the workspace `tmp/`:

```bash
R=/Users/abhinavanand/Finmate_Projects/tpap-transactional-switch   # the repo to read
W=/Users/abhinavanand/personal_projects/Agent-debugger/tmp/worktrees/$(basename "$R")-$(date +%s)
git -C "$R" fetch -q origin                    # updates origin/* refs only; leaves the user's files alone
git -C "$R" worktree add -q --detach "$W" origin/main
# ... debug inside "$W" ...
git -C "$R" worktree remove --force "$W" && git -C "$R" worktree prune
```

- **When to use it:** always for the `~/Finmate_Projects` repos (dev checkouts, often on a feature branch). A `repos/` checkout that is on `main` and clean can be read directly — the cron job keeps it current — and only needs a worktree when the user is working in it (skip the `fetch` there; the cron pull already updates `origin/main`).
- **`--detach`** checks out the commit rather than the branch, so it never collides with the user's `main` and never moves it.
- **GWTS has no useful `main`** — `tpap_gwts` `main` dates from 2024. Use the gateway branch: `origin/hdfc_master`, `origin/axis_master`, `origin/sbi_master`, `origin/ocil_switch_master`. The `~/Finmate_Projects/tpap_gwts_*` folders can be on the wrong gateway (`tpap_gwts_sbi` was on `hdfc_master` on 2026-10-05), so never trust their checked-out branch.
- **Always remove the worktree when the debugging is done**, including when the investigation fails or is abandoned. Never leave one behind, and only ever remove worktrees you created under `tmp/worktrees/`.
- The worktree is read-only working space: no edits, no commits.
