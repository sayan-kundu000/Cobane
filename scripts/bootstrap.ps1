# Cobane Environment Bootstrapper script
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Initializing Cobane Development Environment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Initialize Upload Directories
$dirs = @(
    "uploads/temp",
    "uploads/processed",
    "uploads/archived",
    "uploads/quarantine",
    "reports/static_analysis",
    "reports/ai_reviews",
    "reports/exports",
    "reports/history",
    "logs/app",
    "logs/security",
    "logs/ai",
    "logs/analysis",
    "logs/deployment",
    "docker/postgres"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

# 2. Write empty gitkeeps to keep directories in Git history
foreach ($dir in $dirs) {
    $gitkeep = Join-Path $dir ".gitkeep"
    if (-not (Test-Path $gitkeep)) {
        New-Item -ItemType File -Force -Path $gitkeep | Out-Null
    }
}

# 3. Setup Postgres Docker Init DB placeholder
$initDb = "docker/postgres/init.sql"
if (-not (Test-Path $initDb)) {
    "CREATE DATABASE cobane;" | Out-File -FilePath $initDb -Encoding utf8
    Write-Host "Created placeholder init.sql" -ForegroundColor Green
}

# 4. Copy Environment Template
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created default .env from template" -ForegroundColor Yellow
}

Write-Host "Scaffolding completed successfully." -ForegroundColor Cyan
