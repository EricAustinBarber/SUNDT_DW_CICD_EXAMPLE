# Example Consuming Repo (Databricks CI/CD)

This repository demonstrates how to consume the reusable GitHub workflow from:
`sundt-edm-cicd-platform/.github/workflows/reusable-databricks.yml`.

## What this repo demonstrates
- Branch triggers for `dev`, `test`, and `prod`
- Calling a reusable workflow via `workflow_call`
- A minimal Databricks Asset Bundle (`databricks/databricks.yml`)
- Basic unit test structure for future expansion

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
- End-to-end promotion path (`dev` -> `test` -> `prod`) is documented in `docs/promotion-demo-runbook.md`.
