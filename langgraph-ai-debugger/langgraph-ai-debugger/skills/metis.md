
# Metis eBPF network dashboards (TPAP) — verified 2026-10-12

Metis is an eBPF agent on TPAP EKS nodes (owner `daniyaal.khan@finmate.tech`), exported through Telegraf on `:9273`. It shows what a pod saw on the wire. Use it for "is it the network, DNS, or the DB round trip?" — app metrics, ELK and PMM cannot answer that. Long form: workspace `CLAUDE.md` → *Metis eBPF network dashboards*.

Folder **UPI-TPAP**, https://monitor.mypaytm.com (orgId=12):

| Dashboard | UID | Use for |
|---|---|---|
| Metis · MySQL (detailed) | `metis-mysql` | Client-side per-statement latency, rows, MySQL error code + message |
| Metis · DNS (detailed) | `metis-dns` | rcode; NXDOMAIN / SERVFAIL / NODATA by domain and querier; ndots noise |
| Metis · TCP connection stats (detailed) | `metis-tcp-connection-stats` | RTT, cwnd, ssthresh, windows, zero-window, throughput per (pod, destination) |
| Metis · TCP retransmits & resets (detailed) | `metis-tcp-retransmits-resets` | Retransmits by destination / pod / state; resets sent (reason) and received |
| Metis · Public (non-private) IPs (detailed) | `metis-public-ips` | Egress to public IPs, pod → domain, unresolved IPs |
| Daniyaal's Scratch Space - Metis | `bf613ad5-4c26-4641-a946-b1ca2da8ff44` | Owner's scratch board — prefer the `metis-*` boards |

## The datasource decides the estate — the `metis-*` boards default to NON-PROD

| Datasource | uid | Estate |
|---|---|---|
| `Prometheus-TPAP` | `e6d5cdaa-2ddd-4314-9d92-3039eafa003e` | **prod** EKS (`ip-10-198-*`). No `environment` / `application`; the node group is in `job` |
| `Global-Thanos` | `e6bcafdd-ba97-4a55-a971-a52285730975` | **non-prod** (`ip-10-161-*`, stage2 / stage3 / uth-flink). `environment="tpap"`, `application=<node group>` |
| `Prometheus-staging` | `c9cc740c-fcea-40bf-8e1b-205a87366781` | same non-prod estate as `Global-Thanos` |

For prod, query `Prometheus-TPAP` through `tpap_grafana`. In the browser, append `&var-datasource=Prometheus-TPAP`; the empty *Environment* / *Node group* dropdowns are then expected. The scratch board already defaults to `Prometheus-TPAP`.

## Coverage is partial — check it before trusting silence

2026-10-12: 13 of the 90 TPAP prod-cluster nodes. 12 are `tpap-preprod-nodegroup` (namespace `tpappreprod`); 1 is `tpap-trans-nodegroup` (prod `tpap-pms` pods). The live `tpapprod` switch, BFF and consumers are mostly not covered. Prod data starts ~7 Oct 2026. The rollout moves, so re-check:

```promql
count by (job, host) (metis_bpf_tcp_probe_srtt_us_count)
```

If the pod is not on a Metis node, an empty panel means "not instrumented", never "no errors".

## Metrics — each has `_count _mean _min _max _stdev _s2`

- `metis_mysql_query_latency_latency_ms`, `metis_mysql_affected_rows_rows` — `db_ip port domain db user src_ip query`
- `metis_mysql_query_error_count` — the same + `error_code error_message`
- `metis_dns_query_count` — `querier_ip domain rcode resolved_ips` (`&`-joined; empty + `NOERROR` = NODATA)
- `metis_bpf_tcp_probe_{srtt_us,snd_cwnd,ssthresh,snd_wnd,rcv_wnd,data_len}` — `src_ip dest_ip dest_port domain`
- `metis_bpf_tcp_retransmit_skb_count` — + `state err`; `metis_bpf_tcp_receive_reset_count` — `dest_port`
- `metis_bpf_tcp_send_reset_count` — **`dst_port`** (not `dest_port`) + `reason state`

## Math — Telegraf basicstats in 10s windows, not counters

- Events/s = `sum(<m>_count) / 10`. Never `rate()` / `increase()`.
- Mean = `sum(<m>_mean * <m>_count) / sum(<m>_count)`. Never average `_mean` directly.
- `sum_over_time(<m>_count[range])` is **not** a total, and neither are the boards' "(selected range)" tables. With 15s scrapes of 10s windows a busy series reads ≈0.67x; a quiet series re-exposes its last window for ~60s and reads up to 4x. Use it to rank only.
- `ssthresh_min = 2147483647` means no loss. `snd_cwnd_min` of 1–2 means an RTO. `snd_wnd_min == 0` means the peer advertised a zero window.
- `state`: 1 ESTABLISHED, 2 SYN_SENT, 3 SYN_RECV, 4 FIN_WAIT1, 5 FIN_WAIT2, 6 TIME_WAIT, 7 CLOSE, 8 CLOSE_WAIT, 9 LAST_ACK, 10 LISTEN, 11 CLOSING, 12 NEW_SYN_RECV.
- IPs are pod IPs → `kube_pod_info{pod_ip="<ip>"}` on `Prometheus-TPAP`. `127.0.0.6` is the Istio sidecar, not a pod.
- MySQL latency is client-side (network + ProxySQL + MySQL), and `db_ip` / `domain` is usually a ProxySQL NLB. If Metis is slow while PMM is healthy, suspect the path, not MySQL.

## Where to look

| Symptom | Board |
|---|---|
| DB calls slow from the app side, or MySQL errors | MySQL — then PMM for the server side |
| `UnknownHostException`, NXDOMAIN storms, slow first call | DNS |
| Timeouts or connection resets to a downstream | TCP retransmits & resets + TCP connection stats |
| Latency spike: network or app? | TCP connection stats — RTT floor vs jitter, zero-window flows |
| Unexpected internet egress | Public IPs |
