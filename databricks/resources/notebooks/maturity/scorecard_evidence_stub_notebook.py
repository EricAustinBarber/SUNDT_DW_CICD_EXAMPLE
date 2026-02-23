# Databricks notebook source
# scorecard_evidence_stub_notebook.py
dbutils.widgets.text("env", "")
dbutils.widgets.text("status_source_path", "")  # optional CSV path with check_id,status,notes
dbutils.widgets.text("write_mode", "dry_run")   # dry_run|append
dbutils.widgets.text("updated_by", "evidence_stub")

ENV = dbutils.widgets.get("env") or "unknown"
STATUS_SOURCE_PATH = dbutils.widgets.get("status_source_path") or ""
WRITE_MODE = (dbutils.widgets.get("write_mode") or "dry_run").strip().lower()
UPDATED_BY = dbutils.widgets.get("updated_by") or "evidence_stub"

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

def normalize_path(path: str) -> str:
    if path.startswith("dbfs:/") or path.startswith("file:/"):
        return path
    if path.startswith("/Workspace/"):
        return f"file:{path}"
    return path

STATUS_SOURCE_PATH = normalize_path(STATUS_SOURCE_PATH) if STATUS_SOURCE_PATH else STATUS_SOURCE_PATH

if STATUS_SOURCE_PATH:
    status_df = (spark.read.option("header", "true")
                 .option("inferSchema", "false")
                 .csv(STATUS_SOURCE_PATH)
                 .select(
                     F.col("check_id"),
                     F.col("status"),
                     F.col("notes")
                 ))
    status_df = (status_df
                 .withColumn("status_lc", F.lower(F.trim(F.col("status"))))
                 .withColumn(
                     "status",
                     F.when(F.col("status_lc").isin("pass", "passed"), F.lit("Pass"))
                     .when(F.col("status_lc").isin("partial", "partially"), F.lit("Partial"))
                     .when(F.col("status_lc").isin("fail", "failed"), F.lit("Fail"))
                     .otherwise(F.lit("Unknown"))
                 )
                 .drop("status_lc"))
else:
    # Stub: create placeholder rows from the scorecard definition.
    try:
        definition_df = spark.table("governance_maturity.scorecard_definition")
    except Exception:
        raise Exception("scorecard_definition not found. Run scorecard evaluation once or provide status_source_path.")
    status_df = (definition_df
                 .select("check_id")
                 .withColumn("status", F.lit("Unknown"))
                 .withColumn("notes", F.lit("TODO: derive from evidence")))

status_df = (status_df
             .withColumn("env", F.lit(ENV))
             .withColumn("updated_at", F.lit(now_ts))
             .withColumn("updated_by", F.lit(UPDATED_BY)))

print("[scorecard] stubbed status rows:")
status_df.orderBy("check_id").show(50, False)

if WRITE_MODE == "append":
    status_df.write.mode("append").format("delta").saveAsTable("governance_maturity.scorecard_check_status")
    print(f"[scorecard] appended {status_df.count()} status rows for env={ENV}")
else:
    print("[scorecard] dry_run enabled; no rows written")
