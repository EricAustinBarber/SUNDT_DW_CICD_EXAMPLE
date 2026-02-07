# Databricks notebook source
import json, time
from dataclasses import dataclass
from typing import List, Dict, Any

dbutils.widgets.text("env", "")
dbutils.widgets.text("commit_sha", "")
dbutils.widgets.text("manifest_json", "")  # optional: embed manifest directly
dbutils.widgets.text("manifest_path", "")  # optional: dbfs:/... or /Workspace/... if you implement reading

env = dbutils.widgets.get("env") or "dev"
commit_sha = dbutils.widgets.get("commit_sha") or "unknown"
manifest_json = dbutils.widgets.get("manifest_json") or ""

print(f"[validation] env={env} commit_sha={commit_sha}")
print(f"[validation] utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")

# ---- Manifest loading (quick win) ----
# Easiest: pass JSON from CI as a parameter (manifest_json). For now, fall back to a small default list.
if manifest_json.strip():
    manifest = json.loads(manifest_json)
else:
    manifest = {
        "objects": [
            # Replace these with real objects when ready
            # {"name": "main.dataflow.some_table", "type": "table", "checks": ["describe", "query_limit_1"]},
        ]
    }

objects = manifest.get("objects", [])
print(f"[validation] objects_to_check={len(objects)}")

results: List[Dict[str, Any]] = []
failed = False

def run_sql(stmt: str):
    return spark.sql(stmt)

for obj in objects:
    name = obj["name"]
    checks = obj.get("checks", ["describe"])
    obj_ok = True
    messages = []

    print(f"\n[validation] object={name} checks={checks}")

    try:
        if "describe" in checks:
            run_sql(f"DESCRIBE TABLE {name}").limit(1).collect()
            messages.append("describe:OK")

        if "query_limit_1" in checks:
            run_sql(f"SELECT * FROM {name} LIMIT 1").collect()
            messages.append("limit_1:OK")

    except Exception as e:
        obj_ok = False
        failed = True
        messages.append(f"ERROR: {type(e).__name__}: {e}")

    results.append({"object": name, "ok": obj_ok, "messages": messages})

# ---- Report ----
report = {
    "env": env,
    "commit_sha": commit_sha,
    "ok": (not failed),
    "checked": len(results),
    "results": results,
}

print("\n[validation] report:")
print(json.dumps(report, indent=2))

if failed:
    raise Exception("[validation] FAILED: one or more validation checks failed")

print("[validation] SUCCESS")