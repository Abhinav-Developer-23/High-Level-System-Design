#!/usr/bin/env python3
"""Elasticsearch/Kibana MCP server for TSP — routes all ES calls via Kibana console proxy."""

import os
import sys
import json
import logging
import urllib.parse
import httpx
from mcp.server.fastmcp import FastMCP

# Cursor treats MCP stderr INFO as errors and may hide the server from the agent.
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
logging.disable(logging.INFO)

MAGENTA = "\033[95m"
RESET = "\033[0m"

def _log(msg: str) -> None:
    print(f"{MAGENTA}{msg}{RESET}", file=sys.stderr, flush=True)

KIBANA_URL = "https://kibana.paytmybl.com"
HEADERS = {"kbn-xsrf": "true", "Content-Type": "application/json"}
DEFAULT_SIZE = 50
MAX_SIZE = 500

# Shard C3: transactional switch + ingress exchange + consumers (same shard as switchv2_C3 DB).
SWITCHC3_ES_INDEX_PATTERN = (
    "prod-paytmybl-tsp-switchc3-*,"
    "prod-paytmybl-tsp-switchc3_exchange-*,"
    "prod-paytmybl-tsp-consumersc3-set1-*"
)
# Optional: set in .env to your Kibana **saved data view id** (Stack Management → Data views).
# Then Discover links bind to switch C3 without picking a data view manually.
# You can assign a **custom data view id** when creating the data view (e.g. tsp-switchc3).
ENV_SWITCHC3_DATA_VIEW_ID = "KIBANA_TSP_SWITCHC3_DATA_VIEW_ID"

mcp = FastMCP("tsp_elk")


def _rison_kql_string(kql: str) -> str:
    """Escape a KQL string for use inside rison single quotes."""
    return kql.replace("\\", "\\\\").replace("'", "\\'")


def _rison_time_value(t: str) -> str:
    """Rison value for Kibana time: now-* unquoted; absolute times single-quoted."""
    t = t.strip()
    if t.startswith("now"):
        return t
    return f"'{_rison_kql_string(t)}'"


def kibana_discover_switchc3_url(
    kql: str,
    from_time: str = "now-3d",
    to_time: str = "now",
    sort_desc: bool = False,
    data_view_id: str | None = None,
) -> str:
    """
    Build a Kibana Discover URL scoped to TSP switch shard C3 logs.

    Uses SWITCHC3_ES_INDEX_PATTERN in the `index` slot when no data view id is provided.
    Kibana 8 often resolves `index` to a **saved data view** by id; raw wildcards work only
    if your cluster’s data view title/id matches. Prefer setting KIBANA_TSP_SWITCHC3_DATA_VIEW_ID
    in .env to a saved data view that covers the three index patterns above.
    """
    dv = (data_view_id or os.environ.get(ENV_SWITCHC3_DATA_VIEW_ID, "") or "").strip()
    index_token = dv if dv else SWITCHC3_ES_INDEX_PATTERN
    # rison: quoted if it contains commas or special chars; bare id ok for simple custom ids
    if dv and "," not in dv and "*" not in dv and " " not in dv:
        index_rison = index_token
    else:
        index_rison = f"'{_rison_kql_string(index_token)}'"
    kq = _rison_kql_string(kql)
    sort_order = "desc" if sort_desc else "asc"
    tf = _rison_time_value(from_time)
    tt = _rison_time_value(to_time)
    _g = (
        f"(filters:!(),refreshInterval:(pause:!t,value:0),"
        f"time:(from:{tf},to:{tt}))"
    )
    _a = (
        "(columns:!('@timestamp',log.message,log.level,log.loggerName,fields.type,host.name),"
        "filters:!(),"
        f"index:{index_rison},"
        "interval:auto,"
        f"query:(language:kuery,query:'{kq}'),"
        f"sort:!(!('@timestamp',{sort_order})))"
    )
    return f"{KIBANA_URL}/app/discover#/?_g={_g}&_a={_a}"


@mcp.tool()
def discover_switchc3_link(
    kql: str,
    from_time: str = "now-3d",
    to_time: str = "now",
    sort_desc: bool = False,
    data_view_id: str | None = None,
) -> str:
    """
    Kibana Discover URL for TSP **switch shard C3** only (switch + exchange + consumers).

    Embeds the C3 index pattern in the link so you do not pick a data view by hand.
    If your Kibana ignores wildcard `index` in the URL, create a data view covering:
    prod-paytmybl-tsp-switchc3-*, prod-paytmybl-tsp-switchc3_exchange-*,
    prod-paytmybl-tsp-consumersc3-set1-* — optionally set custom id `tsp-switchc3` — then set
    env KIBANA_TSP_SWITCHC3_DATA_VIEW_ID or pass data_view_id here.

    Args:
        kql: KQL query e.g. txn id or message substring.
        from_time / to_time: ES date math (now-3d) or ISO-8601 instant.
        sort_desc: true = newest first.
        data_view_id: Override saved data view id for this link only.
    """
    url = kibana_discover_switchc3_url(
        kql=kql,
        from_time=from_time,
        to_time=to_time,
        sort_desc=sort_desc,
        data_view_id=data_view_id,
    )
    return json.dumps(
        {
            "kibana_base": KIBANA_URL,
            "switchc3_index_pattern": SWITCHC3_ES_INDEX_PATTERN,
            "data_view_env": ENV_SWITCHC3_DATA_VIEW_ID,
            "discover_url": url,
        },
        indent=2,
    )


def _proxy(es_path: str, method: str = "GET", body: dict | None = None, timeout: int = 20) -> dict:
    encoded = urllib.parse.quote(es_path, safe="/:*,-_.")
    url = f"{KIBANA_URL}/api/console/proxy?path={encoded}&method={method.upper()}"
    r = httpx.post(url, headers=HEADERS, json=body, timeout=timeout, verify=False)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def search_logs(
    index: str,
    query_string: str = "*",
    size: int = DEFAULT_SIZE,
    from_time: str = "now-1h",
    to_time: str = "now",
    time_field: str = "@timestamp",
    sort_desc: bool = True,
    source_fields: list[str] | None = None,
) -> str:
    """
    Search TSP production logs via Lucene query string + time range.

    Use list_indices to discover available index patterns before querying.
    Max log age: now-3d (logs older than 3 days don't exist in prod).
    Production log levels: INFO, WARN, ERROR only — DEBUG/TRACE don't exist.

    Args:
        index: Index pattern e.g. "prod-tsp-transactional-switch-*".
        query_string: Lucene query e.g. '"txn123"' or 'log.level:ERROR'.
        size: Max hits (default 50, cap 500).
        from_time: ES date math start — max "now-3d".
        to_time: End of range. Default "now".
        time_field: Timestamp field. Default "@timestamp".
        sort_desc: Newest-first if true.
        source_fields: Specific fields to return. None = all.
    """
    size = min(size, MAX_SIZE)
    _log(f"[tsp_elk] search index={index} q={query_string} range={from_time}~{to_time}")
    body: dict = {
        "size": size,
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": query_string, "lenient": True, "analyze_wildcard": True}},
                    {"range": {time_field: {"gte": from_time, "lte": to_time}}},
                ]
            }
        },
        "sort": [{time_field: {"order": "desc" if sort_desc else "asc"}}],
    }
    if source_fields:
        body["_source"] = source_fields
    try:
        resp = _proxy(f"{index}/_search", method="POST", body=body)
        hits = resp.get("hits", {})
        total = hits.get("total", {})
        total_val = total.get("value", total) if isinstance(total, dict) else total
        docs = [
            {"_index": h.get("_index"), "_id": h.get("_id"), **h.get("_source", {})}
            for h in hits.get("hits", [])
        ]
        return json.dumps({"total": total_val, "returned": len(docs), "hits": docs}, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_logs_dsl(index: str, dsl: str, size: int = DEFAULT_SIZE) -> str:
    """
    Execute raw Elasticsearch Query DSL — for aggregations or complex queries on TSP.

    Max log age: now-3d. Production log levels: INFO, WARN, ERROR only.

    Args:
        index: Index pattern.
        dsl: JSON string of ES query body.
        size: Injected as "size" unless already in dsl.
    """
    size = min(size, MAX_SIZE)
    _log(f"[tsp_elk] search_dsl index={index}")
    try:
        body = json.loads(dsl)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON in dsl: {e}"})
    body.setdefault("size", size)
    try:
        resp = _proxy(f"{index}/_search", method="POST", body=body)
        hits = resp.get("hits", {})
        total = hits.get("total", {})
        total_val = total.get("value", total) if isinstance(total, dict) else total
        docs = [
            {"_index": h.get("_index"), "_id": h.get("_id"), **h.get("_source", {})}
            for h in hits.get("hits", [])
        ]
        result: dict = {"total": total_val, "returned": len(docs), "hits": docs}
        if "aggregations" in resp:
            result["aggregations"] = resp["aggregations"]
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def list_indices(pattern: str = "prod-tsp*") -> str:
    """
    List actual ES indices matching a pattern. Use this to discover TSP index patterns.

    Args:
        pattern: Glob e.g. "prod-tsp*". Default lists all TSP prod indices.
    """
    _log(f"[tsp_elk] list_indices pattern={pattern}")
    try:
        es_path = f"_cat/indices/{pattern}?format=json&h=index,health,docs.count,store.size&s=index"
        data = _proxy(es_path, method="GET")
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_index_mapping(index: str) -> str:
    """
    Get all field names and types for a TSP index — inspect before querying unknown fields.

    Args:
        index: Index name or pattern e.g. "prod-tsp-transactional-switch-*".
    """
    _log(f"[tsp_elk] get_index_mapping index={index}")

    def _flatten(properties: dict, prefix: str = "") -> list[dict]:
        fields = []
        for name, meta in properties.items():
            full = f"{prefix}{name}"
            fields.append({"field": full, "type": meta.get("type", "object")})
            if "properties" in meta:
                fields.extend(_flatten(meta["properties"], prefix=f"{full}."))
            for sub_name, sub_meta in meta.get("fields", {}).items():
                fields.append({"field": f"{full}.{sub_name}", "type": sub_meta.get("type", "?")})
        return fields

    try:
        data = _proxy(f"{index}/_mapping", method="GET")
        all_fields = []
        for idx_name, idx_meta in data.items():
            props = idx_meta.get("mappings", {}).get("properties", {})
            all_fields.append({"index": idx_name, "fields": _flatten(props)})
        if len(all_fields) == 1:
            return json.dumps(all_fields[0]["fields"], indent=2)
        return json.dumps(all_fields, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def list_data_views(per_page: int = 500) -> str:
    """
    List Kibana index patterns (data views) for TSP.
    Useful for finding the correct ID to use in Kibana Discover URLs.
    """
    _log(f"[tsp_elk] list_data_views per_page={per_page}")
    url = f"{KIBANA_URL}/api/saved_objects/_find?type=index-pattern&per_page={per_page}"
    try:
        r = httpx.get(url, headers=HEADERS, timeout=20, verify=False)
        r.raise_for_status()
        data = r.json()
        views = []
        for obj in data.get("saved_objects", []):
            attr = obj.get("attributes", {})
            views.append({
                "id": obj.get("id"),
                "title": attr.get("title"),
                "timeFieldName": attr.get("timeFieldName")
            })
        return json.dumps(views, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
