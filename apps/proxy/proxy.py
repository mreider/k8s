import time
import requests
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="dynatrace-collector:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

FRONTEND_URL = "http://frontend-service:8000/"

def call_frontend():
    with tracer.start_as_current_span("proxy-to-frontend"):
        response = requests.get(FRONTEND_URL)
        print(f"Frontend says: {response.text}")

if __name__ == "__main__":
    while True:
        call_frontend()
        time.sleep(3)
