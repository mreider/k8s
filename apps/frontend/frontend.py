from flask import Flask, request
import requests
import time
import random
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.propagate import inject, extract
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.trace import SpanKind

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

service_name = "frontend"
resource = Resource(attributes={"service.name": service_name})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://dynatrace-otel-collector-service:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

BACKEND_URL = "http://backend-service:6000/"

@app.route("/")
def order():
    context = extract(request.headers)
    with tracer.start_as_current_span("frontend-to-backend", context=context, kind=SpanKind.CLIENT):
        headers = {}
        inject(trace.get_current_span().context, headers)
        time.sleep(random.uniform(0.2, 0.8))
        response = requests.get(BACKEND_URL, headers=headers)
        return f"Backend says: {response.text}", response.status_code

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
