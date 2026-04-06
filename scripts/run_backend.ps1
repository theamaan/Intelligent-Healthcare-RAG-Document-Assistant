param(
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8000
)

if (-Not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Error "Virtual environment not found. Run: python -m venv .venv"
    exit 1
}

. .\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --host $HostAddress --port $Port
