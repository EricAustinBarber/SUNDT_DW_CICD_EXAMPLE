# Sundt EDM Databricks Maturity

This repository is the production Databricks Asset Bundle (DAB) for assessing
and tracking Databricks environment maturity. It deploys maturity jobs and
notebooks, runs CI/CD validation, and stores scorecard outputs in Delta tables.

## What this repo provides

- Bundle-managed Databricks jobs and notebooks under `databricks/`
- CI/CD workflows that validate, deploy, and run post-deploy maturity checks
- Embedded scorecard definition used by the evaluation notebook
- Runbooks for workflow validation and promotion

## Required GitHub Environments (in this repo)

Create these environments in GitHub UI (`Settings -> Environments`):

- `DataBricks-Dev`: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_SQL_WAREHOUSE_ID`
- `DataBricks-Test`: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_SQL_WAREHOUSE_ID`
- `DataBricks-Prod`: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_SQL_WAREHOUSE_ID` (with required approvers)

## Notes

- The Databricks asset validation notebook path used in the workflow must exist in your workspace.
- This repo intentionally avoids storing secret values.
- The reusable workflow is pinned to an immutable commit SHA; update it whenever `sundt-edm-cicd-platform` is intentionally upgraded.
- Helper script for pin updates: `scripts/update-pipeline-workflow-pin.ps1 -PipelineSha <new_sha>`.
- Branch governance setup is documented in `docs/branch-protection-checklist.md`.
- Dev/test workflow execution is documented in `docs/workflow-validation-runbook.md`.
- End-to-end promotion path (`dev` -> `test` -> `prod`) is documented in `docs/promotion-runbook.md`.
- Asset build and decommission workflow is documented in `docs/databricks-asset-bundles-lifecycle.md`.
