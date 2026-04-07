import json

from fastapi import APIRouter, HTTPException

from backend.app.config import get_settings

router = APIRouter(prefix="/eval", tags=["evaluation"])


@router.get("/latest")
def get_latest_eval() -> dict:
    """Return the most recent RAGAS evaluation report from disk."""
    settings = get_settings()
    result_files = sorted(settings.eval_results_dir.glob("eval_*.json"), reverse=True)
    if not result_files:
        raise HTTPException(
            status_code=404,
            detail=(
                "No evaluation results found. "
                "Run: python -m backend.app.evaluation.ragas_eval"
            ),
        )
    latest = result_files[0]
    data = json.loads(latest.read_text(encoding="utf-8"))
    return {"filename": latest.name, "results": data}
