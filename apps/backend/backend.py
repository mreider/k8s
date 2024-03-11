from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor


app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://dynatrace-otel-collector-service:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

@app.route("/")
def receive_order():
    with tracer.start_as_current_span("backend-span"):
        return "ok", 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=6000)
