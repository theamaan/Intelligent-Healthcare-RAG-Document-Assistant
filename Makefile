setup:
	python -m venv .venv
	.venv\\Scripts\\pip install -r requirements.txt

backend:
	.venv\\Scripts\\uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	.venv\\Scripts\\streamlit run frontend/app.py

test:
	.venv\\Scripts\\pytest

eval:
	.venv\\Scripts\\python -m backend.app.evaluation.ragas_eval
