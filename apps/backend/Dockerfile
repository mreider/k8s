FROM python:3.9-slim

WORKDIR /app

COPY backend.py /app

RUN pip install flask opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-flask requests

CMD ["python", "backend.py"]
