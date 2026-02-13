import time
import logging
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Optional dependencies for enterprise observability
HAS_PROMETHEUS = False
try:
    import prometheus_client
    HAS_PROMETHEUS = True
except ImportError:
    pass

HAS_OPENTELEMETRY = False
try:
    import opentelemetry
    HAS_OPENTELEMETRY = True
except ImportError:
    pass

logger = logging.getLogger("goatclaw.core.metrics")

class MetricsManager:
    """
    USP: Centralized metrics and tracing manager for enterprise observability.
    """
    def __init__(self):
        self._enabled = False
        self._initialized = False
        self._counters = {}
        self._gauges = {}
        self._histograms = {}
        self.tracer = None

    def _ensure_initialized(self):
        if self._initialized:
            return
            
        self._enabled = HAS_PROMETHEUS
        if HAS_PROMETHEUS:
            try:
                self._init_prometheus_metrics()
            except Exception as e:
                logger.warning(f"Failed to init Prometheus metrics: {e}")
                self._enabled = False
                
        if HAS_OPENTELEMETRY:
            try:
                self._init_tracing()
            except Exception as e:
                logger.warning(f"Failed to init tracing: {e}")

        self._initialized = True

    def _init_prometheus_metrics(self):
        """Initialize core platform metrics."""
        from prometheus_client import Counter, Gauge, Histogram
        self._counters["tasks_total"] = Counter("goatclaw_tasks_total", "Total tasks processed", ["agent_type", "status"])
        self._gauges["active_workers"] = Gauge("goatclaw_active_workers", "Number of currently active workers")
        self._gauges["queue_size"] = Gauge("goatclaw_queue_size", "Current task queue depth")
        self._histograms["task_latency"] = Histogram("goatclaw_task_latency_seconds", "Task processing latency", ["agent_type"])
        self._counters["api_calls_total"] = Counter("goatclaw_api_calls_total", "Total external API calls", ["provider"])
        self._counters["credits_deducted"] = Counter("goatclaw_credits_deducted_total", "Total USP credits deducted")

    def _init_tracing(self):
        """Initialize OpenTelemetry tracing."""
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        
        trace.set_tracer_provider(TracerProvider())
        self.tracer = trace.get_tracer("goatclaw")
        # For production, we'd add OTLP exporter here
        # For now, console output if debug enabled
        if os.getenv("GOATCLAW_DEBUG_TRACING", "").lower() == "true":
            span_processor = BatchSpanProcessor(ConsoleSpanExporter())
            trace.get_tracer_provider().add_span_processor(span_processor)

    def increment_task_count(self, agent_type: str, status: str):
        self._ensure_initialized()
        if self._enabled:
            self._counters["tasks_total"].labels(agent_type=agent_type, status=status).inc()

    def update_queue_size(self, size: int):
        self._ensure_initialized()
        if self._enabled:
            self._gauges["queue_size"].set(size)

    def record_task_latency(self, agent_type: str, duration: float):
        self._ensure_initialized()
        if self._enabled:
            self._histograms["task_latency"].labels(agent_type=agent_type).observe(duration)

    def record_api_call(self, provider: str):
        self._ensure_initialized()
        if self._enabled:
            self._counters["api_calls_total"].labels(provider=provider).inc()

    def record_credits(self, amount: float):
        self._ensure_initialized()
        if self._enabled:
            self._counters["credits_deducted"].inc(amount)

    def start_span(self, name: str):
        """Start an OpenTelemetry span."""
        self._ensure_initialized()
        if HAS_OPENTELEMETRY and self.tracer:
            return self.tracer.start_as_current_span(name)
        return None

# Global Instance
metrics_manager = MetricsManager()
