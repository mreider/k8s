from flask import Flask
import requests
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import time

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://dynatrace-otel-collector-service:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

BACKEND_URL = "http://backend-service:6000/"

@app.route("/")
def order():
    with tracer.start_as_current_span("frontend-span"):
        response = requests.get(BACKEND_URL)
        return f"Backend says: {response.text}", response.status_code

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)  # Run the Flask app