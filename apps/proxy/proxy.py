import time
import requests
import random
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagate import inject
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
    with tracer.start_as_current_span("proxy-to-frontend", kind=SpanKind.CLIENT):
        headers = {}
        inject(trace.get_current_span().context, headers)
        time.sleep(random.uniform(0.2, 0.8))
        response = requests.get(FRONTEND_URL, headers=headers)
        return f"Frontend says: {response.text}", response.status_code

if __name__ == "__main__":
    while True:
        call_frontend()
        time.sleep(random.uniform(3, 5))
