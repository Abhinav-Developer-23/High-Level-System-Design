#!/usr/bin/env python3
"""Jarvis Bitbucket MCP — STRICTLY READ-ONLY.

Account: jarvis.agent@finmate.tech. Default workspace: finmatetech
(tpap_bop and the other finmatetech repos). The paytmteam `bitbucket_mcp`
server cannot see that workspace.

Tools are all reads: identity, projects, repos, branches, commits, file
contents, pull requests (metadata, diff, commits), pipelines.

=== WHY THIS SERVER CANNOT WRITE ===

There is no create/update/merge/approve/comment tool. The only outbound call
is httpx.get() inside _request(). Paths are decoded (single and double
percent-encoding), then matched against an exact structure allowlist — never
a prefix match, because every mutating Bitbucket route is a string-prefix of
a read route (/pullrequests/{id}/approve sits under /pullrequests/{id}).
Redirects are off. No tool accepts a method, header map, or body.

Credentials: Agent-debugger/.env only
  JARVIS_BITBUCKET_URL, JARVIS_BITBUCKET_USERNAME,
  JARVIS_BITBUCKET_API_TOKEN, JARVIS_BITBUCKET_WORKSPACE
Never copy the token into .mcp.json or .cursor/mcp.json.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
logging.disable(logging.INFO)

_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

BASE = os.getenv("JARVIS_BITBUCKET_URL", "https://api.bitbucket.org/2.0").rstrip("/")
if BASE.endswith("/2.0"):
    ORIGIN = BASE[: -len("/2.0")]
else:
    ORIGIN = BASE
    BASE = ORIGIN + "/2.0"
USER = os.getenv("JARVIS_BITBUCKET_USERNAME", "")
TOKEN = os.getenv("JARVIS_BITBUCKET_API_TOKEN", "")
DEFAULT_WORKSPACE = os.getenv("JARVIS_BITBUCKET_WORKSPACE", "finmatetech")
TIMEOUT = 30.0
MAX_BODY = 200_000

_SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_PR = re.compile(r"^[0-9]{1,12}$")
_REV = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UUID = re.compile(r"^\{?[0-9a-fA-F-]{32,40}\}?$")
_QUERY_KEYS = frozenset({"pagelen", "page", "q", "sort", "fields", "state"})
_DENY_SEGMENTS = frozenset({
    "approve", "unapprove", "merge", "decline", "request-changes",
    "commit", "build", "downloads", "hooks",
})


class BitbucketPathError(ValueError):
    pass


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


if not (USER and TOKEN):
    _log(
        "[jarvis_bitbucket] WARNING: JARVIS_BITBUCKET_USERNAME / "
        f"JARVIS_BITBUCKET_API_TOKEN missing in {_ENV_PATH}"
    )


def _slug(value: str, what: str) -> str:
    v = (value or "").strip()
    if not _SLUG.match(v):
        raise BitbucketPathError(f"invalid {what} {value!r}")
    return v


def _decode(path: str) -> str:
    cur = path
    for _ in range(2):
        nxt = unquote(cur)
        if nxt == cur:
            break
        cur = nxt
    return cur


def _assert_read_only(path: str) -> str:
    """Allowlist the request path. Raises BitbucketPathError otherwise."""
    if any(c in path for c in "\r\n?#\\") or "://" in path:
        raise BitbucketPathError(f"refusing path {path!r}")
    decoded = _decode(path)
    if any(c in decoded for c in "\r\n?#\\") or "://" in decoded:
        raise BitbucketPathError(f"refusing decoded path {decoded!r}")
    parts = [p for p in decoded.split("/") if p != ""]
    if any(p in (".", "..") or p.lower() in _DENY_SEGMENTS for p in parts):
        raise BitbucketPathError(f"refusing path {decoded!r}: not a read route")
    if not parts or parts[0] != "2.0":
        raise BitbucketPathError(f"refusing path {decoded!r}")
    rest = parts[1:]
    ok = False
    if rest == ["user"]:
        ok = True
    elif len(rest) == 2 and rest[0] == "workspaces" and _SLUG.match(rest[1]):
        ok = True
    elif len(rest) == 3 and rest[0] == "workspaces" and rest[2] == "projects" and _SLUG.match(rest[1]):
        ok = True
    elif (
        len(rest) == 4
        and rest[0] == "workspaces"
        and rest[2] == "projects"
        and _SLUG.match(rest[1])
        and _SLUG.match(rest[3])
    ):
        ok = True
    elif len(rest) >= 2 and rest[0] == "repositories" and _SLUG.match(rest[1]):
        if len(rest) == 2:
            ok = True
        elif _SLUG.match(rest[2]):
            tail = rest[3:]
            if not tail:
                ok = True
            elif tail == ["refs", "branches"] or tail == ["commits"] or tail == ["pullrequests"] or tail == ["pipelines"]:
                ok = True
            elif len(tail) == 2 and tail[0] == "commits" and _REV.match(tail[1]):
                ok = True
            elif len(tail) == 2 and tail[0] == "pullrequests" and _PR.match(tail[1]):
                ok = True
            elif (
                len(tail) == 3
                and tail[0] == "pullrequests"
                and _PR.match(tail[1])
                and tail[2] in {"diff", "commits", "comments", "activity", "statuses"}
            ):
                ok = True
            elif len(tail) == 2 and tail[0] == "pipelines" and _UUID.match(tail[1]):
                ok = True
            elif len(tail) == 3 and tail[0] == "pipelines" and _UUID.match(tail[1]) and tail[2] == "steps":
                ok = True
            elif (
                len(tail) == 4
                and tail[0] == "pipelines"
                and _UUID.match(tail[1])
                and tail[2] == "steps"
                and _UUID.match(tail[3])
            ):
                ok = True
            elif (
                len(tail) == 5
                and tail[0] == "pipelines"
                and _UUID.match(tail[1])
                and tail[2] == "steps"
                and _UUID.match(tail[3])
                and tail[4] == "log"
            ):
                ok = True
            elif tail and tail[0] == "src" and all(_REV.match(p) for p in tail[1:]):
                ok = True
    if not ok:
        raise BitbucketPathError(
            f"refusing {decoded!r}: jarvis_bitbucket is read-only and this path "
            f"is not on the GET allowlist"
        )
    return "/" + "/".join(parts)


def _params(raw: dict | None) -> dict | None:
    if not raw:
        return None
    out = {}
    for key, value in raw.items():
        if key not in _QUERY_KEYS:
            raise BitbucketPathError(f"query param {key!r} is not allowed")
        if value is None:
            continue
        text = str(value)
        if len(text) > 500 or any(c in text for c in "\r\n"):
            raise BitbucketPathError(f"query param {key!r} is not allowed")
        out[key] = text
    return out or None


def _request(path: str, params: dict | None = None) -> httpx.Response:
    """The only outbound call. GET, always."""
    safe = _assert_read_only(path)
    return httpx.get(
        f"{ORIGIN}{safe}",
        auth=(USER, TOKEN),
        params=_params(params),
        timeout=TIMEOUT,
        follow_redirects=False,
    )


def _ws(workspace: str | None) -> str:
    return _slug(workspace or DEFAULT_WORKSPACE, "workspace")


def _dump(resp: httpx.Response, what: str) -> str:
    if resp.status_code >= 400:
        hint = {
            401: "auth failed — check JARVIS_BITBUCKET_USERNAME / JARVIS_BITBUCKET_API_TOKEN in .env",
            403: "token is authenticated but cannot read this resource",
            404: "no such workspace, project, or repository for this account",
        }.get(resp.status_code)
        body = (resp.text or "")[:500]
        return json.dumps(
            {"error": f"HTTP {resp.status_code} for {what}", "hint": hint, "body": body},
            indent=2,
        )
    text = resp.text or ""
    truncated = len(text) > MAX_BODY
    if truncated:
        text = text[:MAX_BODY]
    ctype = resp.headers.get("content-type", "")
    if "json" in ctype:
        try:
            data = json.loads(text if not truncated else resp.text[:MAX_BODY])
        except json.JSONDecodeError:
            data = text
        if truncated:
            return json.dumps({"truncated": True, "data": data}, indent=2)
        return json.dumps(data, indent=2)
    return json.dumps({"truncated": truncated, "text": text}, indent=2)


def _page(pagelen: int, page: int) -> dict:
    return {"pagelen": str(max(1, min(int(pagelen), 50))), "page": str(max(1, int(page)))}


mcp = FastMCP(
    "jarvis_bitbucket",
    instructions=(
        "Read-only Bitbucket for the jarvis.agent@finmate.tech account. "
        "Default workspace is finmatetech (tpap_bop and the other finmatetech repos). "
        "The paytmteam bitbucket_mcp server does not see this workspace. "
        "Every tool is a GET. This server cannot create repos, open or merge pull "
        "requests, comment, approve, or change permissions. "
        "Pass workspace only when it is not finmatetech."
    ),
)


@mcp.tool()
def check_connection() -> str:
    """Verify the Jarvis Bitbucket token and report the account plus default workspace."""
    resp = _request("/2.0/user")
    if resp.status_code >= 400:
        return _dump(resp, "GET /2.0/user")
    data = resp.json()
    return json.dumps(
        {
            "ok": True,
            "read_only": True,
            "username": data.get("username") or data.get("nickname"),
            "display_name": data.get("display_name"),
            "account_id": data.get("account_id"),
            "default_workspace": DEFAULT_WORKSPACE,
            "note": "GET only. No create, merge, approve, comment, or permission change exists.",
        },
        indent=2,
    )


@mcp.tool()
def list_projects(workspace: str | None = None, pagelen: int = 50, page: int = 1) -> str:
    """List Bitbucket projects in a workspace. Default workspace is finmatetech."""
    ws = _ws(workspace)
    return _dump(_request(f"/2.0/workspaces/{ws}/projects", _page(pagelen, page)), f"projects {ws}")


@mcp.tool()
def get_project(project_key: str, workspace: str | None = None) -> str:
    """One Bitbucket project: key, name, description."""
    ws = _ws(workspace)
    key = _slug(project_key, "project_key")
    return _dump(_request(f"/2.0/workspaces/{ws}/projects/{key}"), f"project {ws}/{key}")


@mcp.tool()
def list_repositories(
    name_contains: str | None = None,
    project_key: str | None = None,
    workspace: str | None = None,
    pagelen: int = 20,
    page: int = 1,
) -> str:
    """List repositories. Filter by name substring and/or project key (for example UPI)."""
    ws = _ws(workspace)
    params = _page(pagelen, page)
    clauses = []
    if name_contains:
        needle = name_contains.replace('"', "").strip()
        if needle:
            clauses.append(f'name ~ "{needle}"')
    if project_key:
        key = _slug(project_key, "project_key")
        clauses.append(f'project.key = "{key}"')
    if clauses:
        params["q"] = " AND ".join(clauses)
    return _dump(_request(f"/2.0/repositories/{ws}", params), f"repos {ws}")


@mcp.tool()
def get_repository(repo_slug: str, workspace: str | None = None) -> str:
    """One repository, including its Bitbucket project key and name."""
    ws = _ws(workspace)
    repo = _slug(repo_slug, "repo_slug")
    resp = _request(f"/2.0/repositories/{ws}/{repo}")
    if resp.status_code >= 400:
        return _dump(resp, f"repo {ws}/{repo}")
    data = resp.json()
    project = data.get("project") or {}
    main = (data.get("mainbranch") or {}).get("name")
    return json.dumps(
        {
            "workspace": ws,
            "slug": data.get("slug"),
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "project_key": project.get("key"),
            "project_name": project.get("name"),
            "mainbranch": main,
            "is_private": data.get("is_private"),
            "description": data.get("description"),
            "html_url": (data.get("links") or {}).get("html", {}).get("href"),
            "updated_on": data.get("updated_on"),
        },
        indent=2,
    )


@mcp.tool()
def list_branches(repo_slug: str, workspace: str | None = None, pagelen: int = 20, page: int = 1) -> str:
    """Branch names on a repository."""
    ws = _ws(workspace)
    repo = _slug(repo_slug, "repo_slug")
    return _dump(
        _request(f"/2.0/repositories/{ws}/{repo}/refs/branches", _page(pagelen, page)),
        f"branches {ws}/{repo}",
    )


@mcp.tool()
def list_commits(
    repo_slug: str,
    revision: str | None = None,
    workspace: str | None = None,
    pagelen: int = 20,
    page: int = 1,
) -> str:
    """Recent commits. Optional revision is a branch name or commit SHA without slashes."""
    ws = _ws(workspace)
    repo = _slug(repo_slug, "repo_slug")
    path = f"/2.0/repositories/{ws}/{repo}/commits"
    if revision:
        path += "/" + _slug(revision, "revision")
    return _dump(_request(path, _page(pagelen, page)), f"commits {ws}/{repo}")


@mcp.tool()
def get_file(repo_slug: str, revision: str, path: str = "", workspace: str | None = None) -> str:
    """File or directory listing at revision. path is relative, for example bop/package.json."""
    ws = _ws(workspace)
    repo = _slug(repo_slug, "repo_slug")
    rev = _slug(revision, "revision")
    parts = [p for p in (path or "").split("/") if p not in ("", ".")]
    if any(p == ".." or not _REV.match(p) for p in parts):
        raise BitbucketPathError(f"invalid file path {path!r}")
    suffix = "/" + "/".join(quote(p, safe="") for p in parts) if parts else ""
    # quote() is fine; allowlist runs on the decoded path
    return _dump(_request(f"/2.0/repositories/{ws}/{repo}/src/{rev}{suffix}"), f"src {ws}/{repo}")


@mcp.tool()
def list_pull_requests(
    repo_slug: str,
    state: str = "OPEN",
    workspace: str | None = None,
    pagelen: int = 20,
    page: int = 1,
) -> str:
    """Pull requests. state is OPEN, MERGED, DECLINED, or SUPERSEDED."""
    ws = _ws(workspace)
    repo = _slug(repo_slug, "repo_slug")
    allowed = {"OPEN", "MERGED", "DECLINED", "SUPERSEDED"}
    st = (state or "OPEN").strip().upper()
    if st not in allowed:
        raise BitbucketPathError(f"invalid state {state!r}")
    params = _page(pagelen, page)
    params["state"] = st
    return _dump(_request(f"/2.0/repositories/{ws}/{repo}/pullrequests", params), f"prs {ws}/{repo}")


@mcp.tool()
def get_pull_request(repo_slug: str, pr_id: int, workspace: str | None = None) -> str:
    """One pull request: title, state, author, source and destination branches."""
    ws = _ws(workspace)
    repo = _slug(repo_slug, "repo_slug")
    if pr_id < 1:
        raise BitbucketPathError("pr_id must be positive")
    return _dump(
        _request(f"/2.0/repositories/{ws}/{repo}/pullrequests/{int(pr_id)}"),
        f"pr {ws}/{repo}#{pr_id}",
    )


@mcp.tool()
def get_pull_request_diff(repo_slug: str, pr_id: int, workspace: str | None = None) -> str:
    """Unified diff of a pull request. Truncated at 200KB."""
    ws = _ws(workspace)
    repo = _slug(repo_slug, "repo_slug")
    if pr_id < 1:
        raise BitbucketPathError("pr_id must be positive")
    return _dump(
        _request(f"/2.0/repositories/{ws}/{repo}/pullrequests/{int(pr_id)}/diff"),
        f"diff {ws}/{repo}#{pr_id}",
    )


@mcp.tool()
def list_pipelines(repo_slug: str, workspace: str | None = None, pagelen: int = 10, page: int = 1) -> str:
    """Recent Bitbucket pipelines for a repository."""
    ws = _ws(workspace)
    repo = _slug(repo_slug, "repo_slug")
    return _dump(
        _request(f"/2.0/repositories/{ws}/{repo}/pipelines", _page(pagelen, page)),
        f"pipelines {ws}/{repo}",
    )


if __name__ == "__main__":
    mcp.run()
