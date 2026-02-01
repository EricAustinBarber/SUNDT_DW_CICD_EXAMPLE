# Example Consuming Repo (Databricks CI/CD)

This is an example repository that consumes the reusable GitHub workflow from:
`SUNDT_DW_CICD_PIPELINE/.github/workflows/reusable-databricks.yml`

## What this repo demonstrates
- Branch triggers for `dev`, `test`, and `prod`
- Calling a reusable workflow via `workflow_call`
- A minimal Databricks Asset Bundle (`databricks/databricks.yml`)
- Placeholder unit tests and structure for future expansion

## Required GitHub Environments (in THIS repo)
Create these environments in GitHub UI (Settings → Environments):
- `DataBricks-Dev`  : `DATABRICKS_HOST`, `DATABRICKS_TOKEN`
- `DataBricks-Test` : `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_VALIDATION_CLUSTER_ID`
- `DataBricks-Prod` : `DATABRICKS_HOST`, `DATABRICKS_TOKEN` (and enable required approvers)

## Notes
- The Databricks asset validation driver notebook path is referenced in the workflow and should exist in your Databricks workspace.
- This repo intentionally avoids storing any secrets.
