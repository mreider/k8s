from flask import Flask, jsonify, make_response, request
import time
import random
import os
import sys
import json
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.metrics.export import (AggregationTemporality,PeriodicExportingMetricReader,)
from opentelemetry.sdk.metrics import MeterProvider, Counter
from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider
from opentelemetry.propagate import extract
import mysql.connector
from opentelemetry.instrumentation.dbapi import trace_integration

db_user = 'orders'
db_password = 'orders'
db_host = 'order-db'
db_database = 'orders'
trace_integration(mysql.connector, "connect", "mysql")
logging.basicConfig(level=logging.INFO)
endpoint = "http://dynatrace-otel-collector-service:4317"

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

service_name = "backend"
resource = Resource(attributes={"service.name": service_name})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
trace.get_tracer_provider().add_span_processor(span_processor)

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
  BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint))
)
set_logger_provider(logger_provider)
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)

metric_exporter = OTLPMetricExporter(
  endpoint = endpoint,
  preferred_temporality = {
    Counter: AggregationTemporality.DELTA
  }
)

reader = PeriodicExportingMetricReader(metric_exporter)
provider = MeterProvider(metric_readers=[reader], resource=resource)
set_meter_provider(provider)
meter = get_meter_provider().get_meter("order-counter", "1.0.0")

orders_received_counter = meter.create_counter(
    "orders_received",
    description="Total number of orders received",
)

orders_fulfilled_counter = meter.create_counter(
    "orders_fulfilled",
    description="Total number of orders fulfilled",
)

def get_order_by_type(query):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)
        cursor = conn.cursor()
        cursor.execute(query)
        order_data = cursor.fetchall()
        return order_data
    except mysql.connector.Error as err:
        print("Database error:", err)
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/")
def receive_order():
    context = extract(request.headers)
    with tracer.start_as_current_span("receive-order",context=context):
        orders_received_counter.add(1)
        current_span = trace.get_current_span()
        current_span.set_attribute("order.received", "True")
        if random.random() < 0.05:
            get_order_by_type("SELECT id FROM orders WHERE typo = 'thingamabob'")
            current_span.set_attribute("db.statement", "SELECT id FROM orders WHERE typo = 'thingamabob'")
            current_span.set_attribute("order.fulfilled", "False")
            current_span.set_attribute("span.status", "ERROR")
            logging.error("500 Internal Server Error")
            time.sleep(random.uniform(0.9,2.5))
            return make_response(jsonify(error="Internal Server Error"), 500)
        else:
            get_order_by_type("SELECT id FROM orders WHERE type = 'thingamabob'")
            current_span.set_attribute("db.statement", "SELECT id FROM orders WHERE type = 'thingamabob'")
            current_span.set_attribute("order.fulfilled", "True")
            current_span.set_attribute("span.status", "OK")
            orders_fulfilled_counter.add(1)
            logging.info("200 OK Order fulfilled")
            time.sleep(random.uniform(0.2, 0.8))
            return "ok", 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=6000)
