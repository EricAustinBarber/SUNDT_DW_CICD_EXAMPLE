# Databricks Scorecard Runbook

## Purpose

Run and refresh the Databricks environment scorecard, store results, and keep the baseline current.

This workflow is **non-blocking** and should not gate deployments until approval workflows are finalized.

## Inputs

- Scorecard definition: `docs/databricks-environment-scorecard.csv` (canonical)
- Scorecard bundle copy: `databricks/resources/scorecard/databricks-environment-scorecard.csv`
- Assessment evidence: `EnterpriseDataMaturity/assessments/databricks-transformation-review.md`
- Assessment evidence: `EnterpriseDataMaturity/assessments/assessment-tracker.csv`
- Assessment evidence: `EnterpriseDataMaturity/assessments/databricks-notebook-inventory.csv`
- Assessment evidence: `EnterpriseDataMaturity/assessments/databricks-function-inventory.csv`

## Output Tables (Delta)

- `governance_maturity.scorecard_definition`
- `governance_maturity.scorecard_check_status`
- `governance_maturity.scorecard_results`

## Execution Steps

1. Update assessment evidence in `EnterpriseDataMaturity/assessments/`.
2. Update scorecard definition if needed:
   - Edit `docs/databricks-environment-scorecard.csv`.
   - Copy changes to `databricks/resources/scorecard/databricks-environment-scorecard.csv`.
3. Maintain scorecard status via loader notebook:
   - Job: `maturity-scorecard-status-load-test`
   - Source CSV: `databricks/resources/scorecard/scorecard-check-status.csv`
4. Run the evaluation job in Databricks (test environment): `maturity-scorecard-eval-test`
5. Review outputs:
   - Check `governance_maturity.scorecard_results` for total score, blocked reasons, and run metadata.
6. Record the snapshot:
   - Update `docs/databricks-environment-scorecard.md` baseline table and date.

## Status Conventions

- `Pass` = 1.0
- `Partial` = 0.5
- `Fail` = 0.0
- Any `Fail` in the **Security** dimension blocks readiness.

## Manual Overrides

Update `databricks/resources/scorecard/scorecard-check-status.csv` and rerun the loader job.

## CI Integration

The `ci-test` workflow runs `maturity-scorecard-status-load-test` and `maturity-scorecard-eval-test` automatically after deploy.

## Evidence Stub Notebook

Use `scorecard_evidence_stub_notebook.py` to prototype evidence-derived statuses without enforcing gates. Set `write_mode=append` only when you are ready to persist results.

Job: `maturity-scorecard-evidence-stub-test`
