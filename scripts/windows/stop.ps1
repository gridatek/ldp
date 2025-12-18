# Local Data Platform - Windows Stop Script
# Stop the platform (destroy Terraform resources)

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Local Data Platform - Stopping..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Push-Location terraform

try {
    Write-Host "Destroying platform resources..." -ForegroundColor Yellow
    terraform destroy -var-file="environments/local.tfvars" -auto-approve

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Platform stopped successfully!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Terraform destroy failed" -ForegroundColor Red
        exit 1
    }
} finally {
    Pop-Location
}
