# PowerShell script to reset Django database and migrations
Write-Host "Resetting Django database and migrations..." -ForegroundColor Yellow
Write-Host ""

# Delete SQLite database
if (Test-Path "db.sqlite3") {
    Remove-Item "db.sqlite3"
    Write-Host "✓ Deleted db.sqlite3" -ForegroundColor Green
} else {
    Write-Host "! db.sqlite3 not found" -ForegroundColor Gray
}

# Delete migration files (keep __init__.py)
$migrationFiles = @(
    "api\migrations\0001_initial.py",
    "api\migrations\0002_customuser_otpverification.py"
)

foreach ($file in $migrationFiles) {
    if (Test-Path $file) {
        Remove-Item $file
        Write-Host "✓ Deleted $file" -ForegroundColor Green
    }
}

# Delete migration cache
if (Test-Path "api\migrations\__pycache__") {
    Remove-Item -Recurse -Force "api\migrations\__pycache__"
    Write-Host "✓ Deleted migration cache" -ForegroundColor Green
}

Write-Host "✓ Cleaned up old migrations" -ForegroundColor Green
Write-Host ""

# Create fresh migrations
Write-Host "Creating new migrations..." -ForegroundColor Cyan
$makeMigrationsResult = & python manage.py makemigrations api
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create migrations" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Applying migrations..." -ForegroundColor Cyan
$migrateResult = & python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to apply migrations" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "✅ Database reset complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host "2. Run server: python manage.py runserver" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"
