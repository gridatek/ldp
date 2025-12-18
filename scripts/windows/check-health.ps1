# Local Data Platform - Windows Health Check Script

$ErrorActionPreference = "SilentlyContinue"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Local Data Platform - Health Check" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check Minikube status
Write-Host "Checking Minikube..." -ForegroundColor Yellow
minikube status
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Minikube is running" -ForegroundColor Green
} else {
    Write-Host "✗ Minikube is not running" -ForegroundColor Red
}
Write-Host ""

# Check namespace
Write-Host "Checking namespace..." -ForegroundColor Yellow
$namespace = kubectl get namespace ldp -o jsonpath='{.metadata.name}' 2>$null
if ($namespace -eq "ldp") {
    Write-Host "✓ Namespace 'ldp' exists" -ForegroundColor Green
} else {
    Write-Host "✗ Namespace 'ldp' not found" -ForegroundColor Red
}
Write-Host ""

# Check pods
Write-Host "Checking pods..." -ForegroundColor Yellow
Write-Host ""
kubectl get pods -n ldp

Write-Host ""
$runningPods = (kubectl get pods -n ldp -o json | ConvertFrom-Json).items | Where-Object { $_.status.phase -eq "Running" }
$totalPods = (kubectl get pods -n ldp -o json | ConvertFrom-Json).items.Count

Write-Host "Running pods: $($runningPods.Count)/$totalPods" -ForegroundColor $(if ($runningPods.Count -eq $totalPods) { "Green" } else { "Yellow" })
Write-Host ""

# Check services
Write-Host "Checking services..." -ForegroundColor Yellow
Write-Host ""
kubectl get services -n ldp

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "For detailed logs, run:" -ForegroundColor Yellow
Write-Host "  kubectl logs -n ldp <pod-name>" -ForegroundColor White
Write-Host ""
