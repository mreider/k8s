FROM python:3.8-slim

WORKDIR /app

COPY proxy.py /app

RUN pip install requests opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

CMD ["python", "proxy.py"]