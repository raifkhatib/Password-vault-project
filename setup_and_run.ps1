$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "Password Vault setup started." -ForegroundColor Cyan

$projectPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $projectPython)) {
    Write-Host "Creating the virtual environment..."
    python -m venv .venv

    if ($LASTEXITCODE -ne 0) {
        throw "Virtual environment creation failed."
    }
}

Write-Host "Installing the required Python packages..."
& $projectPython -m pip install --upgrade pip

if ($LASTEXITCODE -ne 0) {
    throw "Pip upgrade failed."
}

& $projectPython -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed."
}

if (-not $env:SECRET_KEY) {
    $env:SECRET_KEY = & $projectPython -c "import secrets; print(secrets.token_hex(32))"

    if ($LASTEXITCODE -ne 0) {
        throw "Secret key generation failed."
    }
}

Write-Host "Initializing the SQLite database..."
& $projectPython -c "from app import app; from models import db; app.app_context().push(); db.create_all(); print('Database initialized successfully.')"

if ($LASTEXITCODE -ne 0) {
    throw "Database initialization failed."
}

Write-Host "Running automated tests..."
& $projectPython -m pytest -q

if ($LASTEXITCODE -ne 0) {
    throw "Automated tests failed. The application will not start."
}

Write-Host "All checks passed." -ForegroundColor Green
Write-Host "Open http://127.0.0.1:5000 in your browser." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server."

& $projectPython app.py