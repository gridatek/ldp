# Local Data Platform - Windows Start Script
# Deploy the platform using Terraform

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Local Data Platform - Starting..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Change to terraform directory
Push-Location terraform

try {
    # Initialize Terraform if needed
    if (-not (Test-Path ".terraform")) {
        Write-Host "Initializing Terraform..." -ForegroundColor Yellow
        terraform init -backend=false
    }

    # Apply Terraform configuration
    Write-Host ""
    Write-Host "Deploying platform with Terraform..." -ForegroundColor Yellow
    Write-Host "This will take 10-15 minutes..." -ForegroundColor Gray
    Write-Host ""

    terraform apply -var-file="environments/local.tfvars" -auto-approve

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "======================================" -ForegroundColor Green
        Write-Host "Platform deployed successfully!" -ForegroundColor Green
        Write-Host "======================================" -ForegroundColor Green
        Write-Host ""

        Write-Host "Getting service URLs..." -ForegroundColor Yellow
        $minikubeIp = minikube ip

        Write-Host ""
        Write-Host "Access your services at:" -ForegroundColor Cyan
        Write-Host "  Airflow UI:    " -NoNewline; Write-Host "http://${minikubeIp}:30080" -ForegroundColor White -NoNewline; Write-Host " (admin/admin)" -ForegroundColor Gray
        Write-Host "  MinIO Console: " -NoNewline; Write-Host "http://${minikubeIp}:30901" -ForegroundColor White -NoNewline; Write-Host " (admin/minioadmin)" -ForegroundColor Gray
        Write-Host "  Spark Master:  " -NoNewline; Write-Host "http://${minikubeIp}:30707" -ForegroundColor White
        Write-Host "  Jupyter:       " -NoNewline; Write-Host "http://${minikubeIp}:30888" -ForegroundColor White
        Write-Host ""
        Write-Host "Run health check: " -NoNewline; Write-Host ".\scripts\windows\check-health.ps1" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "ERROR: Terraform apply failed" -ForegroundColor Red
        exit 1
    }
} finally {
    Pop-Location
}
