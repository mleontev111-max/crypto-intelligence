FROM python:3.12-slim

WORKDIR /app

COPY requirements-runtime.txt ./
RUN python -m pip install --no-cache-dir -r requirements-runtime.txt

COPY . .

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "scripts/collect_approved_sources.py"]
