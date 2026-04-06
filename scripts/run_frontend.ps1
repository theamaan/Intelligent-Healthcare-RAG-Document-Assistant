if (-Not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Error "Virtual environment not found. Run: python -m venv .venv"
    exit 1
}

. .\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
