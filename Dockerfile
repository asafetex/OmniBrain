FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY omnibrain-triad/ .

RUN pip install --no-cache-dir "pytest>=8.0.0" "ruff>=0.8.0"

ENV PYTHONPATH=/app
ENV TRIAD_TIMEOUT_SECONDS=120
ENV TRIAD_ENCODING=utf-8

ENTRYPOINT ["python", "-m", "pytest", "tests/", "-q"]
