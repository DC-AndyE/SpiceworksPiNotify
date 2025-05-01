# setup-venv.ps1

# Ensure script stops on error
$ErrorActionPreference = "Stop"

Write-Host "Creating virtual environment in .venv..." -ForegroundColor Cyan
python -m venv .venv

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
. .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt

# Confirm
Write-Host "`nInstalled packages:" -ForegroundColor Green
pip list
