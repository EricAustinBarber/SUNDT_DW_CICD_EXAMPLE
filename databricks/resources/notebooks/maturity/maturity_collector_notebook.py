# Databricks notebook source
# maturity_collector_notebook.py
dbutils.widgets.text("env", "")
dbutils.widgets.text("run_id", "")
dbutils.widgets.text("commit_sha", "")
dbutils.widgets.text("repo", "")
dbutils.widgets.text("git_ref", "")
dbutils.widgets.text("workflow_run_id", "")
dbutils.widgets.text("bundle_name", "")

ENV = dbutils.widgets.get("env") or "unknown"
RUN_ID = dbutils.widgets.get("run_id") or "unknown"
COMMIT_SHA = dbutils.widgets.get("commit_sha") or None
REPO = dbutils.widgets.get("repo") or None
GIT_REF = dbutils.widgets.get("git_ref") or None
WORKFLOW_RUN_ID = dbutils.widgets.get("workflow_run_id") or None
BUNDLE_NAME = dbutils.widgets.get("bundle_name") or "unknown"

import json
from pyspark.sql import functions as F

spark.sql("CREATE SCHEMA IF NOT EXISTS governance_maturity")

spark.sql("""
CREATE TABLE IF NOT EXISTS governance_maturity.bundle_deployments (
  deployed_at        TIMESTAMP NOT NULL,
  env                STRING    NOT NULL,
  repo               STRING,
  bundle_name        STRING,
  git_sha            STRING,
  git_ref            STRING,
  workflow_run_id    STRING,
  run_id             STRING
)
USING DELTA
PARTITIONED BY (env)
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS governance_maturity.warehouse_telemetry_metrics (
  collected_at         TIMESTAMP NOT NULL,
  env                  STRING    NOT NULL,
  run_id               STRING,
  commit_sha           STRING,
  check_id             STRING    NOT NULL,
  dimension            STRING    NOT NULL,
  metric_name          STRING    NOT NULL,
  source_name          STRING,
  window_days          INT,
  metric_value_double  DOUBLE,
  metric_value_string  STRING,
  status_hint          STRING,
  notes                STRING,
  metric_sql           STRING,
  metric_json          STRING
)
USING DELTA
PARTITIONED BY (env)
""")

now_ts = spark.sql("SELECT current_timestamp() AS ts").collect()[0]["ts"]


def metric_row(
    *,
    check_id: str,
    dimension: str,
    metric_name: str,
    source_name: str,
    window_days: int,
    metric_sql: str,
    metric_value_double: float | None = None,
    metric_value_string: str | None = None,
    status_hint: str = "Observed",
    notes: str | None = None,
    metric_json: dict | None = None,
):
    return (
        now_ts,
        ENV,
        RUN_ID,
        COMMIT_SHA,
        check_id,
        dimension,
        metric_name,
        source_name,
        window_days,
        metric_value_double,
        metric_value_string,
        status_hint,
        notes,
        metric_sql,
        json.dumps(metric_json or {}, sort_keys=True),
    )


def safe_collect_one(sql_text: str):
    return spark.sql(sql_text).collect()[0]


metric_queries = [
    {
        "check_id": "WH-01",
        "dimension": "Adoption",
        "metric_name": "active_query_days_30d",
        "source_name": "system.query.history",
        "window_days": 30,
        "metric_sql": """
            SELECT CAST(COUNT(DISTINCT TO_DATE(start_time)) AS DOUBLE) AS metric_value
            FROM system.query.history
            WHERE start_time >= current_timestamp() - INTERVAL 30 DAYS
        """,
    },
    {
        "check_id": "WH-02",
        "dimension": "Adoption",
        "metric_name": "distinct_query_users_30d",
        "source_name": "system.query.history",
        "window_days": 30,
        "metric_sql": """
            SELECT CAST(COUNT(DISTINCT executed_as) AS DOUBLE) AS metric_value
            FROM system.query.history
            WHERE start_time >= current_timestamp() - INTERVAL 30 DAYS
              AND executed_as IS NOT NULL
        """,
    },
    {
        "check_id": "WH-03",
        "dimension": "Utilization",
        "metric_name": "successful_queries_30d",
        "source_name": "system.query.history",
        "window_days": 30,
        "metric_sql": """
            SELECT CAST(COUNT(*) AS DOUBLE) AS metric_value
            FROM system.query.history
            WHERE start_time >= current_timestamp() - INTERVAL 30 DAYS
              AND statement_status = 'FINISHED'
        """,
    },
    {
        "check_id": "WH-04",
        "dimension": "Reliability",
        "metric_name": "query_success_rate_pct_30d",
        "source_name": "system.query.history",
        "window_days": 30,
        "metric_sql": """
            SELECT CASE
                     WHEN COUNT(*) = 0 THEN NULL
                     ELSE 100.0 * SUM(CASE WHEN statement_status = 'FINISHED' THEN 1 ELSE 0 END) / COUNT(*)
                   END AS metric_value
            FROM system.query.history
            WHERE start_time >= current_timestamp() - INTERVAL 30 DAYS
        """,
    },
    {
        "check_id": "WH-05",
        "dimension": "Performance",
        "metric_name": "p95_runtime_seconds_30d",
        "source_name": "system.query.history",
        "window_days": 30,
        "metric_sql": """
            SELECT percentile_approx(total_duration_ms / 1000.0, 0.95) AS metric_value
            FROM system.query.history
            WHERE start_time >= current_timestamp() - INTERVAL 30 DAYS
              AND total_duration_ms IS NOT NULL
        """,
    },
    {
        "check_id": "WH-06",
        "dimension": "Performance",
        "metric_name": "p95_wait_for_compute_seconds_30d",
        "source_name": "system.query.history",
        "window_days": 30,
        "metric_sql": """
            SELECT percentile_approx(waiting_for_compute_duration_ms / 1000.0, 0.95) AS metric_value
            FROM system.query.history
            WHERE start_time >= current_timestamp() - INTERVAL 30 DAYS
              AND waiting_for_compute_duration_ms IS NOT NULL
        """,
    },
    {
        "check_id": "WH-07",
        "dimension": "Governance",
        "metric_name": "managed_table_coverage_pct",
        "source_name": "system.information_schema.tables",
        "window_days": 1,
        "metric_sql": """
            SELECT CASE
                     WHEN COUNT(*) = 0 THEN NULL
                     ELSE 100.0 * SUM(CASE WHEN UPPER(table_type) = 'MANAGED' THEN 1 ELSE 0 END) / COUNT(*)
                   END AS metric_value
            FROM system.information_schema.tables
            WHERE table_catalog NOT IN ('system', 'samples')
              AND table_schema NOT IN ('information_schema')
        """,
    },
    {
        "check_id": "WH-08",
        "dimension": "Governance",
        "metric_name": "table_comment_coverage_pct",
        "source_name": "system.information_schema.tables",
        "window_days": 1,
        "metric_sql": """
            SELECT CASE
                     WHEN COUNT(*) = 0 THEN NULL
                     ELSE 100.0 * SUM(CASE WHEN comment IS NOT NULL AND TRIM(comment) <> '' THEN 1 ELSE 0 END) / COUNT(*)
                   END AS metric_value
            FROM system.information_schema.tables
            WHERE table_catalog NOT IN ('system', 'samples')
              AND table_schema NOT IN ('information_schema')
        """,
    },
]


rows = []
for metric in metric_queries:
    try:
        result = safe_collect_one(metric["metric_sql"])
        metric_value = result["metric_value"] if "metric_value" in result else None
        notes = None
        status_hint = "Observed"
        if metric_value is None:
            status_hint = "Unknown"
            notes = "Metric query returned no measurable value"
        rows.append(
            metric_row(
                check_id=metric["check_id"],
                dimension=metric["dimension"],
                metric_name=metric["metric_name"],
                source_name=metric["source_name"],
                window_days=metric["window_days"],
                metric_sql=metric["metric_sql"],
                metric_value_double=float(metric_value) if metric_value is not None else None,
                status_hint=status_hint,
                notes=notes,
                metric_json={"source_name": metric["source_name"], "window_days": metric["window_days"]},
            )
        )
    except Exception as exc:
        rows.append(
            metric_row(
                check_id=metric["check_id"],
                dimension=metric["dimension"],
                metric_name=metric["metric_name"],
                source_name=metric["source_name"],
                window_days=metric["window_days"],
                metric_sql=metric["metric_sql"],
                status_hint="Unknown",
                notes=str(exc),
                metric_json={"source_name": metric["source_name"], "window_days": metric["window_days"]},
            )
        )

metrics_df = spark.createDataFrame(
    rows,
    schema="""
        collected_at timestamp, env string, run_id string, commit_sha string,
        check_id string, dimension string, metric_name string, source_name string,
        window_days int, metric_value_double double, metric_value_string string,
        status_hint string, notes string, metric_sql string, metric_json string
    """,
)
metrics_df.write.mode("append").format("delta").saveAsTable("governance_maturity.warehouse_telemetry_metrics")

deploy_df = spark.createDataFrame([(
    now_ts, ENV, REPO, BUNDLE_NAME, COMMIT_SHA, GIT_REF, WORKFLOW_RUN_ID, RUN_ID
)], schema="""
    deployed_at timestamp, env string, repo string, bundle_name string,
    git_sha string, git_ref string, workflow_run_id string, run_id string
""")
deploy_df.write.mode("append").format("delta").saveAsTable("governance_maturity.bundle_deployments")

print(f"[maturity] wrote {metrics_df.count()} warehouse telemetry metrics for env={ENV} run_id={RUN_ID}")
print(f"[maturity] recorded deployment metadata for env={ENV} bundle={BUNDLE_NAME}")
