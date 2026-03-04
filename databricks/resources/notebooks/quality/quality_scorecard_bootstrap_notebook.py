# Databricks notebook source
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema_raw", "")
dbutils.widgets.text("schema_staging", "")
dbutils.widgets.text("schema_mart", "")

CATALOG = (dbutils.widgets.get("catalog") or "").strip()
SCHEMA_RAW = (dbutils.widgets.get("schema_raw") or "").strip()
SCHEMA_STAGING = (dbutils.widgets.get("schema_staging") or "").strip()
SCHEMA_MART = (dbutils.widgets.get("schema_mart") or "").strip()

if not CATALOG or not SCHEMA_RAW or not SCHEMA_STAGING or not SCHEMA_MART:
    raise ValueError(
        "Missing required catalog/schema parameters. "
        "Expected catalog, schema_raw, schema_staging, schema_mart."
    )
if CATALOG.lower() == "main":
    raise ValueError(
        "Refusing to deploy quality scorecard objects to catalog 'main'. "
        "Set target variable quality_catalog to dev/test/prod catalog."
    )

from pyspark.sql.types import StringType, StructField, StructType, TimestampType


def _json_payload_schema() -> StructType:
    return StructType(
        [
            StructField("ingested_at", TimestampType(), True),
            StructField("payload", StringType(), True),
        ]
    )


def _create_json_table(full_name: str) -> None:
    df = spark.createDataFrame([], schema=_json_payload_schema())
    df.write.format("delta").mode("ignore").saveAsTable(full_name)


spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA_RAW}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA_STAGING}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA_MART}")

_create_json_table(f"{CATALOG}.{SCHEMA_RAW}.bigeye_monitors_json")
_create_json_table(f"{CATALOG}.{SCHEMA_RAW}.bigeye_alerts_json")
_create_json_table(f"{CATALOG}.{SCHEMA_RAW}.alation_assets_json")
_create_json_table(f"{CATALOG}.{SCHEMA_STAGING}.sliver_scorecard_metric_definitions_json")
_create_json_table(f"{CATALOG}.{SCHEMA_STAGING}.sliver_critical_datasets_json")

print(
    f"[quality-bootstrap] complete catalog={CATALOG} raw={SCHEMA_RAW} "
    f"staging={SCHEMA_STAGING} mart={SCHEMA_MART}"
)
