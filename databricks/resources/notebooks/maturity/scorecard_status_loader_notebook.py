# Databricks notebook source
# scorecard_status_loader_notebook.py
dbutils.widgets.text("env", "")
dbutils.widgets.text("status_path", "")  # workspace path to CSV
dbutils.widgets.text("updated_by", "notebook")

ENV = dbutils.widgets.get("env") or "unknown"
STATUS_PATH = dbutils.widgets.get("status_path") or ""
UPDATED_BY = dbutils.widgets.get("updated_by") or "notebook"

from pyspark.sql import functions as F

if not STATUS_PATH:
    raise Exception("status_path is required (CSV with columns: check_id,status,notes)")

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

df = (spark.read.option("header", "true")
      .option("inferSchema", "false")
      .csv(STATUS_PATH)
      .select(
          F.col("check_id"),
          F.col("status"),
          F.col("notes")
      )
      .withColumn("env", F.lit(ENV))
      .withColumn("updated_at", F.lit(now_ts))
      .withColumn("updated_by", F.lit(UPDATED_BY)))

df.write.mode("append").format("delta").saveAsTable("governance_maturity.scorecard_check_status")

print(f"[scorecard] loaded {df.count()} status rows for env={ENV} from {STATUS_PATH}")
