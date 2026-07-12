# Cobane Workspace Structural Verification Utility
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Verifying Cobane Workspace Directory Mapping" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

$requiredPaths = @(
    "backend/app/api/v1",
    "backend/app/core",
    "backend/app/models",
    "backend/app/schemas",
    "backend/app/services",
    "frontend/src/components",
    "frontend/src/context",
    "frontend/src/hooks",
    "frontend/src/layouts",
    "frontend/src/pages",
    "frontend/src/services",
    "frontend/src/types",
    "database/seeders",
    "database/utilities",
    "docs/architecture",
    "docs/api",
    "docs/database",
    "docs/deployment",
    "docker/postgres",
    "uploads/temp",
    "reports/ai_reviews",
    "logs/app"
)

$allValid = $true

foreach ($path in $requiredPaths) {
    if (Test-Path $path) {
        Write-Host "[OK] Detected path: $path" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Missing path: $path" -ForegroundColor Red
        $allValid = $false
    }
}

if ($allValid) {
    Write-Host "Verification Success: Directory scaffolding checks out!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Verification Failure: Missing directories detected." -ForegroundColor Red
    exit 1
}
