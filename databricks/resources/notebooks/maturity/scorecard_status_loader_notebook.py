# Databricks notebook source
# scorecard_status_loader_notebook.py
dbutils.widgets.text("env", "")
dbutils.widgets.text("updated_by", "notebook")

ENV = dbutils.widgets.get("env") or "unknown"
UPDATED_BY = dbutils.widgets.get("updated_by") or "notebook"

from pyspark.sql import functions as F

spark.sql("CREATE SCHEMA IF NOT EXISTS governance_maturity")

spark.sql("""
CREATE TABLE IF NOT EXISTS governance_maturity.scorecard_check_status (
  check_id    STRING NOT NULL,
  status      STRING NOT NULL,
  notes       STRING,
  env         STRING,
  updated_at  TIMESTAMP NOT NULL,
  updated_by  STRING
)
USING DELTA
""")

now_ts = spark.sql("SELECT current_timestamp() AS ts").collect()[0]["ts"]

baseline_statuses = [
    ("DBX-01", "Pass", "Baseline status from assessment"),
    ("DBX-02", "Partial", "Delta indicators present; table-level validation pending"),
    ("DBX-03", "Partial", "Merge usage present; coverage by dataset not yet measured"),
    ("DBX-04", "Partial", "Rule inventory per domain not yet captured"),
    ("DBX-05", "Partial", "Optimize/Vacuum present; compliance mapping incomplete"),
    ("DBX-06", "Partial", "Partition usage present; completeness by table unknown"),
    ("DBX-07", "Fail", "No file-size threshold policy evidence captured"),
    ("DBX-08", "Partial", "Patterns exist in utilities; job-level coverage pending"),
    ("DBX-09", "Partial", "Secure retrieval present; potential literals need triage"),
    ("DBX-10", "Partial", "Needs per-job mapping to logging/metrics standard"),
]

df = (spark.createDataFrame(baseline_statuses, ["check_id", "status", "notes"])
      .withColumn("env", F.lit(ENV))
      .withColumn("updated_at", F.lit(now_ts))
      .withColumn("updated_by", F.lit(UPDATED_BY)))

df.write.mode("append").format("delta").saveAsTable("governance_maturity.scorecard_check_status")

print(f"[scorecard] loaded {df.count()} baseline status rows for env={ENV}")
