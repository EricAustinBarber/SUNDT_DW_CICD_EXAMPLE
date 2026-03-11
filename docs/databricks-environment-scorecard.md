# Databricks Warehouse Maturity Scorecard

## Purpose

Define the Databricks-only warehouse maturity scorecard used by this repo. The
scorecard now prioritizes objective telemetry from Databricks system tables and
warehouse metadata instead of external governance tools.

## Scope

This scorecard measures maturity and utilization of the Databricks warehouse
environment itself:

- Warehouse adoption and activity
- Warehouse query volume and reliability
- Warehouse performance
- Warehouse governance coverage for managed and documented assets

## Data Sources

- `system.query.history`
- `system.information_schema.tables`
- `governance_maturity.bundle_deployments`
- `governance_maturity.warehouse_telemetry_metrics`

If a source is unavailable in a workspace, the affected metric is recorded as
`Unknown` and called out in scorecard notes.

## Scoring Rules

- Each check is scored as:
  - `Pass` = 1.0
  - `Partial` = 0.5
  - `Fail` = 0.0
  - `Unknown` = 0.0
- Total score = sum of `(check score * weight)`. Maximum = 100.
- Any `Fail` in `Governance` or `Reliability` blocks readiness.
- Scores below `75` are warned even when they do not block readiness.

## Scorecard Checks

| Check ID | Dimension | Check | Source | Pass Criteria | Weight |
|---|---|---|---|---|---:|
| WH-01 | Adoption | Warehouse queried on at least ten distinct days in the last 30 days | `system.query.history` | Distinct query days in 30 days `>= 10` | 12 |
| WH-02 | Adoption | Warehouse used by multiple distinct query users in the last 30 days | `system.query.history` | Distinct users in 30 days `>= 5` | 10 |
| WH-03 | Utilization | Warehouse handled meaningful successful query volume in the last 30 days | `system.query.history` | Successful queries in 30 days `>= 100` | 10 |
| WH-04 | Reliability | Warehouse query success rate remains above the reliability threshold | `system.query.history` | Successful query rate in 30 days `>= 95%` | 14 |
| WH-05 | Performance | Warehouse p95 runtime remains within acceptable bounds | `system.query.history` | P95 total runtime `<= 60 seconds` | 14 |
| WH-06 | Performance | Warehouse p95 wait-for-compute time remains within acceptable bounds | `system.query.history` | P95 wait for compute `<= 10 seconds` | 12 |
| WH-07 | Governance | Managed table coverage demonstrates strong warehouse governance | `system.information_schema.tables` | Managed table coverage `>= 95%` | 14 |
| WH-08 | Governance | Table comment coverage demonstrates documented warehouse assets | `system.information_schema.tables` | Comment coverage `>= 80%` | 14 |

## Delivery Flow

1. `maturity_collect` records warehouse telemetry snapshots.
2. `maturity_scorecard_status_load` converts the latest metric values into
   `Pass` / `Partial` / `Fail` / `Unknown`.
3. `maturity_scorecard_eval` calculates weighted results and blocked reasons.
4. `maturity_ci_check` evaluates the latest scorecard result for deployment
   warnings or blocks.

## Near-Term Extensions

- Add cost and efficiency metrics from `system.billing.usage`.
- Add queue saturation and startup behavior metrics from
  `system.compute.warehouse_events`.
- Add table ownership and tagging coverage from Unity Catalog metadata.
- Add trends and burn-down views for each scorecard dimension.
