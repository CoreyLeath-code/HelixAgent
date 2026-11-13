# api/monitoring.py

"""
Monitoring for HelixAgent
-------------------------
Provides Prometheus metrics and OpenTelemetry tracing integration.
"""

import os
import time

from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

# -----------------------------
# Prometheus Metrics
# -----------------------------
REQUEST_COUNT = Counter(
    "helixagent_request_count",
    "Total number of requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "helixagent_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
)


def _endpoint_label(request: Request) -> str:
    """Use the matched route template to avoid unbounded metric cardinality."""

    route = request.scope.get("route")
    return getattr(route, "path", "unmatched")


def setup_monitoring(app: FastAPI):
    """Attach monitoring endpoints and tracing to FastAPI"""

    # Prometheus /metrics endpoint
    @app.get("/metrics")
    async def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # Middleware for metrics
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            endpoint = _endpoint_label(request)
            REQUEST_COUNT.labels(
                method=request.method, endpoint=endpoint, status_code=500
            ).inc()
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.perf_counter() - start)
            raise

        endpoint = _endpoint_label(request)
        REQUEST_COUNT.labels(
            method=request.method, endpoint=endpoint, status_code=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.perf_counter() - start)
        return response

    # -----------------------------
    # OpenTelemetry Tracing
    # -----------------------------
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        provider = TracerProvider()
        trace.set_tracer_provider(provider)
    if os.getenv("HELIXAGENT_OTEL_CONSOLE", "false").lower() == "true":
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Auto-instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    return app
