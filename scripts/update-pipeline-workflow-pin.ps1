param(
  [Parameter(Mandatory = $true)]
  [string]$PipelineSha
)

$workflowPath = ".github/workflows/ci.yml"
if (!(Test-Path $workflowPath)) {
  throw "Workflow file not found: $workflowPath"
}

$content = Get-Content -Raw $workflowPath
$updated = $content -replace "EricAustinBarber/SUNDT_DW_CICD_PIPELINE/\.github/workflows/reusable-databricks\.yml@[a-f0-9]{40}", "EricAustinBarber/SUNDT_DW_CICD_PIPELINE/.github/workflows/reusable-databricks.yml@$PipelineSha"

if ($updated -eq $content) {
  throw "No reusable workflow references were updated. Verify workflow format."
}

Set-Content -Path $workflowPath -Value $updated
Write-Output "Updated reusable workflow pin in $workflowPath to $PipelineSha"
