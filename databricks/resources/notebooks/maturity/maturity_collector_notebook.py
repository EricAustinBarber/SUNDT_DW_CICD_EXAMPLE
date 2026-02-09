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

from pyspark.sql import functions as F

spark.sql("CREATE SCHEMA IF NOT EXISTS governance_maturity")

spark.sql("""
CREATE TABLE IF NOT EXISTS governance_maturity.bundle_deployments (
  deployed_at        TIMESTAMP NOT NULL,
  env                STRING    NOT NULL,
  repo               STRING,
  bundle_name         STRING,
  git_sha            STRING,
  git_ref            STRING,
  workflow_run_id     STRING,
  run_id              STRING
)
USING DELTA
PARTITIONED BY (env)
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS governance_maturity.prod_readiness (
  collected_at        TIMESTAMP NOT NULL,
  env                 STRING    NOT NULL,
  run_id              STRING    NOT NULL,
  commit_sha          STRING,
  readiness_passed    BOOLEAN   NOT NULL,
  blocked_reasons     ARRAY<STRING>,
  warned_reasons      ARRAY<STRING>,
  gate_summary_json   STRING
)
USING DELTA
PARTITIONED BY (env)
""")

now_ts = spark.sql("SELECT current_timestamp() AS ts").collect()[0]["ts"]

# Placeholder snapshot (your real implementation will compute these arrays)
readiness_df = spark.createDataFrame([(
    now_ts, ENV, RUN_ID, COMMIT_SHA, True, [], [], "{}"
)], schema="""
    collected_at timestamp, env string, run_id string, commit_sha string,
    readiness_passed boolean, blocked_reasons array<string>, warned_reasons array<string>, gate_summary_json string
""")
readiness_df.write.mode("append").format("delta").saveAsTable("governance_maturity.prod_readiness")

deploy_df = spark.createDataFrame([(
    now_ts, ENV, REPO, BUNDLE_NAME, COMMIT_SHA, GIT_REF, WORKFLOW_RUN_ID, RUN_ID
)], schema="""
    deployed_at timestamp, env string, repo string, bundle_name string,
    git_sha string, git_ref string, workflow_run_id string, run_id string
""")
deploy_df.write.mode("append").format("delta").saveAsTable("governance_maturity.bundle_deployments")

print(f"[maturity] wrote readiness + deployment tracking for env={ENV} run_id={RUN_ID} bundle={BUNDLE_NAME}")
