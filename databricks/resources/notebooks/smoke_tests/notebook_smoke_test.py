# Databricks notebook source
import time

# Parameters from Jobs submit (your workflow passes base_parameters env + commit_sha)
dbutils.widgets.text("env", "")
dbutils.widgets.text("commit_sha", "")

env = dbutils.widgets.get("env") or "dev"
commit_sha = dbutils.widgets.get("commit_sha") or "unknown"

print(f"[smoke] env={env} commit_sha={commit_sha}")
print(f"[smoke] utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")

# 1) Spark sanity (forces an action)
assert spark.range(1).count() == 1
print("[smoke] spark_action=OK")

# 2) Metastore sanity (pick one depending on your setup)
try:
    # Unity Catalog
    _ = spark.sql("SHOW CATALOGS").limit(5).collect()
    print("[smoke] show_catalogs=OK")
except Exception as e:
    # Hive metastore fallback
    _ = spark.sql("SHOW DATABASES").limit(5).collect()
    print("[smoke] show_databases=OK")

# 3) Optional: object existence checks (edit or leave empty)
# Keep these lightweight (DESCRIBE + LIMIT 1 only)
expected_objects = [
    # "catalog.schema.table",
    # "schema.table"  # if not using UC
]

for obj in expected_objects:
    print(f"[smoke] checking {obj}")
    spark.sql(f"DESCRIBE TABLE {obj}").limit(1).collect()
    spark.sql(f"SELECT * FROM {obj} LIMIT 1").collect()

print("[smoke] SUCCESS")
