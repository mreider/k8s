import time
import requests
import random
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind

service_name = "proxy"
resource = Resource(attributes={"service.name": service_name})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://dynatrace-otel-collector-service:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

FRONTEND_URL = "http://frontend-service:8000/"

def call_frontend():
    with tracer.start_as_current_span("proxy-to-frontend", kind=SpanKind.SERVER):
        response = requests.get(FRONTEND_URL)
        print(f"Frontend says: {response.text}")

if __name__ == "__main__":
    while True:
        call_frontend()
        time.sleep(random.uniform(3, 5))
