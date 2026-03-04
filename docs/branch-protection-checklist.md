# Branch Protection Checklist (Sundt EDM Databricks Maturity)

Use this checklist to enforce safe promotion from `dev` -> `test` -> `prod`.

## Global repository settings

- Protect branches: `dev`, `test`, `prod`, `main`.
- Require pull requests before merge.
- Require at least 1 approval (`prod` requires 2).
- Dismiss stale reviews on push.
- Require branches to be up to date before merging.
- Block force pushes and branch deletion.
- Restrict direct pushes to `prod`.
- Enable secret scanning and push protection.

## Required status checks

Branch `dev`:
- `PR-Checks / unit-tests`
- `PR-Checks / bundle-validate-dev`

Branch `test`:
- `PR-Checks / unit-tests`
- `PR-Checks / bundle-validate-test`

Branch `prod`:
- `PR-Checks / unit-tests`
- `PR-Checks / bundle-validate-test` (PRs targeting `prod` validate with test target)
- Enforce deployment approvals in `DataBricks-Prod` environment for `deploy-prod`.

## Deploy workflow monitoring (recommended)

These are not PR gates, but should be monitored after branch merges:

- `Deploy / deploy-dev`
- `Deploy / deploy-test`
- `Deploy / deploy-prod`

## Environment approvals

- `DataBricks-Dev`: no manual approval.
- `DataBricks-Test`: optional approvals for high-risk changes.
- `DataBricks-Prod`: required approvers from platform + data owners.

## Release / hotfix controls

- Merge `release/*` into `prod` via PR only.
- Allow emergency `hotfix/*` with same required checks.
- Back-merge hotfixes to `dev` after prod deployment.
