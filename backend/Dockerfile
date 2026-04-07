FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend

# Data directories are created at runtime by the app (ensure_directories).
# In Docker Compose, ./data is mounted as a volume at /app/data.
RUN mkdir -p /app/data/uploads /app/data/vector_stores /app/data/history /app/data/eval_results /app/data/test_sets

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
