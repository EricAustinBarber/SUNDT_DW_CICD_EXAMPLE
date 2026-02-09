# Databricks notebook source
# maturity_ci_check_notebook.py
dbutils.widgets.text("env", "")
dbutils.widgets.text("enforcement_mode", "")      # optional: off|warn|block
dbutils.widgets.text("maturity_override", "none") # none|warn_only|skip

ENV = dbutils.widgets.get("env") or "unknown"
enforcement_mode_param = (dbutils.widgets.get("enforcement_mode") or "").strip().lower()
override = (dbutils.widgets.get("maturity_override") or "none").strip().lower()

from pyspark.sql import functions as F

spark.sql("CREATE SCHEMA IF NOT EXISTS governance_maturity")
spark.sql("""
CREATE TABLE IF NOT EXISTS governance_maturity.maturity_config (
  env              STRING  NOT NULL,
  config_key       STRING  NOT NULL,
  value_type       STRING  NOT NULL,
  value_string     STRING,
  value_double     DOUBLE,
  value_long       BIGINT,
  value_int        INT,
  value_boolean    BOOLEAN,
  value_json       STRING,
  description      STRING,
  updated_at       TIMESTAMP NOT NULL DEFAULT current_timestamp(),
  updated_by       STRING
)
USING DELTA
""")

# seed a default
spark.sql("""
MERGE INTO governance_maturity.maturity_config t
USING (
  SELECT '*' AS env, 'enforcement_mode' AS config_key, 'string' AS value_type, 'warn' AS value_string,
         'Default enforcement mode (*): warn' AS description
) s
ON t.env=s.env AND t.config_key=s.config_key
WHEN NOT MATCHED THEN
  INSERT (env, config_key, value_type, value_string, description)
  VALUES (s.env, s.config_key, s.value_type, s.value_string, s.description)
""")

def get_config_string(env: str, key: str, default: str):
    df = (spark.table("governance_maturity.maturity_config")
          .filter((F.col("config_key")==key) & (F.col("env").isin("*", env)))
          .withColumn("env_rank", F.when(F.col("env")==env, F.lit(2)).otherwise(F.lit(1)))
          .orderBy(F.col("env_rank").desc(), F.col("updated_at").desc())
          .limit(1))
    rows = df.collect()
    return (rows[0]["value_string"] if rows else None) or default

cfg_mode = get_config_string(ENV, "enforcement_mode", "warn").strip().lower()
mode = enforcement_mode_param or cfg_mode

if override == "skip":
    print(f"[maturity] override=skip -> skipping check for env={ENV}")
    dbutils.notebook.exit("SKIPPED")

if override == "warn_only":
    mode = "warn"

if mode not in ("off", "warn", "block"):
    mode = "warn"

latest = (spark.table("governance_maturity.prod_readiness")
          .filter(F.col("env")==ENV)
          .orderBy(F.col("collected_at").desc())
          .limit(1))

rows = latest.collect()
if not rows:
    raise Exception(f"[maturity] No readiness row found for env={ENV}. Did maturity_collect run?")
row = rows[0]

blocked = row["blocked_reasons"] or []
warned  = row["warned_reasons"] or []

print(f"[maturity] enforcement_mode={mode} override={override} env={ENV}")
print(f"[maturity] collected_at={row['collected_at']} run_id={row['run_id']} commit_sha={row['commit_sha']}")

print("\nBLOCKS (fail build if mode=block):")
print("  - none" if not blocked else "\n".join([f"  - {b}" for b in blocked]))

print("\nWARNS:")
print("  - none" if not warned else "\n".join([f"  - {w}" for w in warned]))

if mode == "block" and blocked:
    raise Exception(f"[maturity] BLOCK gates failed: {len(blocked)} (env={ENV})")

print("[maturity] PASS (no blocking enforcement)")
