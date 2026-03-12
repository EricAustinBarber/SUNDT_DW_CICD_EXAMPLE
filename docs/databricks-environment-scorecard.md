# Databricks Warehouse Maturity Scorecard

Related living design document:

- `docs/warehouse-maturity-model.md`

## Purpose

Define the Databricks-only warehouse maturity scorecard used by this repo. The
scorecard now prioritizes objective telemetry from Databricks system tables and
warehouse metadata instead of external governance tools.

## Scope

This scorecard measures maturity and utilization of the Databricks warehouse
environment itself:

- Platform feature utilization
- Pipeline engineering patterns
- Performance and file-layout efficiency
- Operational reliability
- Cost control and efficiency signals

## Data Sources

- `system.query.history`
- `system.information_schema.tables`
- `DESCRIBE DETAIL`
- `DESCRIBE HISTORY`
- `system.lakeflow.job_run_timeline`
- `governance_maturity.bundle_deployments`
- `governance_maturity.warehouse_metric_catalog`
- `governance_maturity.warehouse_telemetry_metrics`

If a source is unavailable in a workspace, the affected metric is recorded as
`Unknown` and called out in scorecard notes.

## Scoring Rules

- Each check is scored as:
  - `Pass` = 1.0
  - `Partial` = 0.5
  - `Fail` = 0.0
  - `Unknown` = excluded from the available score weight
- Total score = normalized weighted score over observed metrics only. Maximum = 100.
- Any `Fail` in `Operational Reliability` blocks readiness.
- Scores below `75` are warned even when they do not block readiness.
- Missing telemetry is warned and reported as observed weight coverage.

## Scorecard Checks

| Check ID | Dimension | Check | Source | Pass Criteria | Weight |
|---|---|---|---|---|---:|
| WH-01 | Platform Feature Utilization | Curated warehouse tables are primarily stored in Delta format | `system.information_schema.tables` + `DESCRIBE DETAIL` | Delta curated table coverage `>= 90%` | 5 |
| WH-02 | Platform Feature Utilization | Observed warehouse write workloads favor `MERGE` over rebuild-only logic | `system.query.history` | `MERGE` load ratio `>= 60%` | 6 |
| WH-03 | Platform Feature Utilization | Large tables use a layout strategy such as partitioning | `DESCRIBE DETAIL` | Large table layout strategy coverage `>= 80%` | 5 |
| WH-04 | Performance and Efficiency | Only a small number of large tables show small-file issues | `DESCRIBE DETAIL` | Small-file problem tables `<= 3` | 5 |
| WH-05 | Performance and Efficiency | Only a limited number of tables show oversized file patterns | `DESCRIBE DETAIL` | Oversized-file problem tables `<= 1` | 3 |
| WH-06 | Platform Feature Utilization | Large Delta tables show recent `OPTIMIZE` usage | `DESCRIBE HISTORY` | Large table `OPTIMIZE` coverage `>= 70%` | 5 |
| WH-07 | Performance and Efficiency | Large join workloads remain limited | `system.query.history` | Large join query count `<= 25` | 5 |
| WH-08 | Platform Feature Utilization | Broadcast join hints are used where appropriate | `system.query.history` | Broadcast join hint count `>= 10` | 3 |
| WH-09 | Platform Feature Utilization | Observed write workloads are primarily incremental | `system.query.history` | Incremental load coverage `>= 70%` | 6 |
| WH-10 | Platform Feature Utilization | Observed ingestion workloads use auto-trigger or streaming patterns | `system.query.history` | Auto-trigger or streaming load coverage `>= 40%` | 5 |
| WH-11 | Performance and Efficiency | Critical pipeline p95 runtime remains within the target window | `system.lakeflow.job_run_timeline` | P95 pipeline runtime `<= 900 seconds` | 5 |
| WH-12 | Operational Reliability | Observed pipeline success rate remains above the reliability threshold | `system.lakeflow.job_run_timeline` | Pipeline success rate `>= 95%` | 5 |
| CC-01 | Cost Control | Full reload workload ratio remains below the cost threshold | `system.query.history` | Full reload workload ratio `<= 20%` | 2 |
| CC-02 | Cost Control | Full reload workload count remains below the cost threshold | `system.query.history` | Full reload workload count `<= 25` | 2 |
| CC-03 | Cost Control | SELECT * query count remains below the cost threshold | `system.query.history` | SELECT * query count `<= 50` | 2 |
| CC-04 | Cost Control | Long-running query count remains below the cost threshold | `system.query.history` | Long-running query count `<= 50` | 2 |
| CC-05 | Cost Control | Large table layout strategy coverage remains above the cost threshold | `DESCRIBE DETAIL` | Large table layout strategy coverage `>= 80%` | 2 |
| CC-06 | Cost Control | Small-file problem table count remains below the cost threshold | `DESCRIBE DETAIL` | Small-file problem tables `<= 3` | 2 |
| CC-07 | Cost Control | Oversized file problem table count remains below the cost threshold | `DESCRIBE DETAIL` | Oversized file problem tables `<= 1` | 2 |
| CC-08 | Cost Control | Large join query count remains below the cost threshold | `system.query.history` | Large join query count `<= 25` | 2 |
| CC-09 | Cost Control | Pipeline p95 runtime remains within the cost target | `system.lakeflow.job_run_timeline` | P95 pipeline runtime `<= 900 seconds` | 2 |
| CC-10 | Cost Control | Large table count remains below the cost threshold | `DESCRIBE DETAIL` | Large table count `<= 200` | 2 |
| CC-11 | Cost Control | Non-Delta table count remains below the cost threshold | `DESCRIBE DETAIL` | Non-Delta table count `<= 10` | 2 |
| CC-12 | Cost Control | Large tables without partitioning remain below the cost threshold | `DESCRIBE DETAIL` | Large tables without partitioning `<= 20` | 2 |
| CC-13 | Cost Control | Large Delta tables missing OPTIMIZE remain below the cost threshold | `DESCRIBE HISTORY` | Large tables missing OPTIMIZE `<= 20` | 2 |
| CC-14 | Cost Control | P95 query runtime remains within the cost threshold | `system.query.history` | P95 query runtime `<= 60 seconds` | 2 |
| CC-15 | Cost Control | High scan byte query count remains below the cost threshold | `system.query.history` | High scan byte query count `<= 50` | 2 |
| CC-16 | Cost Control | High scan-to-output ratio query count remains below the cost threshold | `system.query.history` | High scan-to-output ratio query count `<= 30` | 2 |
| CC-17 | Cost Control | Spill-to-disk query count remains below the cost threshold | `system.query.history` | Spill-to-disk query count `<= 10` | 2 |
| CC-18 | Cost Control | High shuffle byte query count remains below the cost threshold | `system.query.history` | High shuffle byte query count `<= 10` | 2 |
| CC-19 | Cost Control | SELECT * query ratio remains below the cost threshold | `system.query.history` | SELECT * query ratio `<= 5%` | 2 |
| CC-20 | Cost Control | Broadcast join ratio remains above the cost threshold | `system.query.history` | Broadcast join ratio `>= 10%` | 2 |
| CC-21 | Cost Control | Write workload count baseline is available | `system.query.history` | Write workload count observed in last 30 days | 2 |

## Notes

- This document is the current exact scorecard definition.
- Use `docs/warehouse-maturity-model.md` for roadmap, assumptions, and planned
  future metrics.

## Delivery Flow

1. `maturity_collect` records warehouse telemetry snapshots.
2. `maturity_scorecard_status_load` converts the latest metric values into
   `Pass` / `Partial` / `Fail` / `Unknown`.
3. `maturity_scorecard_eval` calculates weighted results and blocked reasons.
4. `maturity_ci_check` evaluates the latest scorecard result for deployment
   warnings or blocks.

## Near-Term Extensions

- Replace query-text heuristics with more explicit pipeline metadata where available.
- Add cost and efficiency metrics from `system.billing.usage`.
- Add queue saturation and startup behavior metrics from `system.compute.warehouse_events`.
- Add table ownership, tags, and stewardship coverage from Unity Catalog metadata.
- Add trend and burn-down views by rollup area and metric family.
