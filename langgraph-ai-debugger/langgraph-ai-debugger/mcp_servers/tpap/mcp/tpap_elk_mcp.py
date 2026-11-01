#!/usr/bin/env python3
"""Elasticsearch/Kibana MCP server for TPAP — routes all ES calls via Kibana console proxy."""

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

KIBANA_URL = "https://tpapprod-logging-elk.paytm.com"
# TPAP Kibana often works without auth for these APIs if accessed from internal network
HEADERS = {"kbn-xsrf": "true", "Content-Type": "application/json"}
DEFAULT_SIZE = 50
MAX_SIZE = 500

# Team-owned indices — only query these
INDICES = {
    "transactional_switch": "prod-tpap-transactional-switch-*,prod-tpap-transactional-switch_exchange*",
    "consumers_set1":       "prod-tpap-consumers-set1-switch-*",
    "gwts_mindgate_hdfc":   "prod-tpap_gwts_mindgate-hdfc-*",
    "gwts_mindgate_sbi":    "prod-tpap_gwts_mindgate-sbi-*",
    "gwts_ocil_yes":        "prod-tpap-gwts-ocil-switch-yes-*",
    "gwts_juspay_axis":     "prod-tpap_gwts_juspay-axis-*",
}

mcp = FastMCP("tpap_elk")


def _rison_kql_string(kql: str) -> str:
    """Escape a KQL string for use inside rison single quotes."""
    return kql.replace("\\", "\\\\").replace("'", "\\'")


def _rison_time_value(t: str) -> str:
    """Rison value for Kibana time: now-* unquoted; absolute times single-quoted."""
    t = t.strip()
    if t.startswith("now"):
        return t
    return f"'{_rison_kql_string(t)}'"


def kibana_discover_url(
    kql: str,
    from_time: str = "now-3d",
    to_time: str = "now",
    sort_desc: bool = False,
    data_view_id: str | None = None,
    index_pattern: str | None = None,
) -> str:
    """Build a Kibana Discover URL."""
    index_token = data_view_id if data_view_id else (index_pattern or INDICES["transactional_switch"])
    
    # rison: quoted if it contains commas or special chars
    if data_view_id and "," not in data_view_id and "*" not in data_view_id and " " not in data_view_id:
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
        "(columns:!('@timestamp',log.message,log.level,log.loggerName),"
        "filters:!(),"
        f"index:{index_rison},"
        "interval:auto,"
        f"query:(language:kuery,query:'{kq}'),"
        f"sort:!(!('@timestamp',{sort_order})))"
    )
    return f"{KIBANA_URL}/app/discover#/?_g={_g}&_a={_a}"


@mcp.tool()
def discover_link(
    kql: str,
    from_time: str = "now-3d",
    to_time: str = "now",
    sort_desc: bool = False,
    data_view_id: str | None = None,
    index_pattern: str | None = None,
) -> str:
    """
    Generate a Kibana Discover URL for TPAP logs.

    Args:
        kql: KQL query e.g. txn id or message substring.
        from_time / to_time: ES date math (now-3d) or ISO-8601 instant.
        sort_desc: true = newest first.
        data_view_id: Optional saved data view id.
        index_pattern: Optional raw index pattern (defaults to transactional_switch if no data_view_id).
    """
    url = kibana_discover_url(
        kql=kql,
        from_time=from_time,
        to_time=to_time,
        sort_desc=sort_desc,
        data_view_id=data_view_id,
        index_pattern=index_pattern,
    )
    return json.dumps({
        "kibana_base": KIBANA_URL,
        "discover_url": url,
    }, indent=2)


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
    Search tpap production logs via Lucene query string + time range.

    Team-owned indices (use the pattern directly as `index`):
      transactional_switch → prod-tpap-transactional-switch-*,prod-tpap-transactional-switch_exchange*
      consumers_set1       → prod-tpap-consumers-set1-switch-*
      gwts_mindgate_hdfc   → prod-tpap_gwts_mindgate-hdfc-*
      gwts_mindgate_sbi    → prod-tpap_gwts_mindgate-sbi-*
      gwts_ocil_yes        → prod-tpap-gwts-ocil-switch-yes-*
      gwts_juspay_axis     → prod-tpap_gwts_juspay-axis-*

    Key field: contextMap.seq-no = txnId

    Args:
        index: Index pattern (use team-owned patterns above).
        query_string: Lucene query e.g. 'contextMap.seq-no:"txn123"' or 'log.level:ERROR'.
        size: Max hits (default 50, cap 500).
        from_time: ES date math start — max "now-3d" (logs older than 3 days don't exist).
        to_time: End of range. Default "now".
        time_field: Timestamp field. Default "@timestamp".
        sort_desc: Newest-first if true.
        source_fields: Specific fields to return. None = all.
    """
    size = min(size, MAX_SIZE)
    _log(f"[tpap_elk] search index={index} q={query_string} range={from_time}~{to_time}")
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
    Execute raw Elasticsearch Query DSL — for aggregations or complex queries.

    Team-owned indices same as search_logs. Max log age: now-3d.
    contextMap.seq-no = txnId.

    Args:
        index: Index pattern.
        dsl: JSON string of ES query body.
        size: Injected as "size" unless already in dsl.
    """
    size = min(size, MAX_SIZE)
    _log(f"[tpap_elk] search_dsl index={index}")
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
def list_indices(pattern: str = "*") -> str:
    """
    List actual ES indices matching a pattern.

    Args:
        pattern: Glob e.g. "prod-tpap-transactional-switch-*". Default "*" lists all.
    """
    _log(f"[tpap_elk] list_indices pattern={pattern}")
    try:
        es_path = f"_cat/indices/{pattern}?format=json&h=index,health,docs.count,store.size&s=index"
        data = _proxy(es_path, method="GET")
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_index_mapping(index: str) -> str:
    """
    Get all field names and types for an index — inspect before querying unknown fields.

    Args:
        index: Index name or pattern e.g. "prod-tpap-consumers-set1-switch-*".
    """
    _log(f"[tpap_elk] get_index_mapping index={index}")

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
def list_data_views(per_page: int = 1000) -> str:
    """
    List Kibana index patterns (data views) for TPAP.
    Useful for finding the correct ID to use in Kibana Discover URLs.
    """
    _log(f"[tpap_elk] list_data_views per_page={per_page}")
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
