# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CONTEXTOS_QDRANT_URL=http://qdrant:6333 \
    CONTEXTOS_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

COPY pyproject.toml ./

# Keep heavyweight ML/runtime dependencies cached when application code changes.
RUN --mount=type=cache,target=/root/.cache/pip \
    mkdir -p app && touch app/__init__.py && \
    pip install --upgrade pip && \
    pip install \
      --index-url https://download.pytorch.org/whl/cpu \
      --extra-index-url https://pypi.org/simple \
      "torch==2.13.0+cpu" && \
    pip install . && \
    rm -rf app

COPY app ./app
RUN pip install --no-deps .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
