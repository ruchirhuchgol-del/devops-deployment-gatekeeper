"""
Web server for the DevSecOps Deployment Gatekeeper.
Provides health check (/health) and Prometheus metrics (/metrics) endpoints.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import logging
from typing import Dict, Any, Optional
from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    REGISTRY,
)
from .health import get_health_status
from .config.settings import settings
from .utils.logger import get_logger

logger = get_logger(__name__)

# Prometheus metrics
GATE_DECISIONS = Counter(
    "security_gate_decisions_total",
    "Total security gate decisions",
    ["result", "repository"],
)
SCAN_DURATION = Histogram(
    "security_gate_scan_duration_seconds",
    "Duration of security scans in seconds",
    buckets=[10, 30, 60, 120, 300],
)
GATE_UP = Gauge("security_gate_up", "Whether the security gate is operational")
GATE_UP.set(1)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health check and metrics endpoints."""

    def do_GET(self):
        if self.path == "/health":
            self._handle_health_check()
        elif self.path == "/metrics":
            self._handle_metrics()
        else:
            self._send_response(404, b'{"error": "Not found"}', "application/json")

    def _handle_health_check(self):
        try:
            health_status = get_health_status()
            status_code = 200 if health_status["status"] == "healthy" else 503
            body = json.dumps(health_status, indent=2).encode("utf-8")
            # Allow CORS only on health endpoint (for monitoring UIs)
            self.send_response(status_code)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self._send_response(
                500, json.dumps({"error": str(e)}).encode(), "application/json"
            )

    def _handle_metrics(self):
        try:
            # Prometheus text exposition format — no CORS header
            output = generate_latest(REGISTRY)
            self.send_response(200)
            self.send_header("Content-type", CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(output)
        except Exception as e:
            logger.error(f"Metrics error: {e}")
            self._send_response(500, str(e).encode(), "text/plain")

    def _send_response(self, status: int, body: bytes, content_type: str):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Safe: join args as strings, don't use format string from network input
        logger.debug("%s - %s", self.address_string(), " ".join(str(a) for a in args))


class HealthCheckServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8090):
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self._stop_event = threading.Event()

    def start(self) -> bool:
        try:
            self.server = HTTPServer((self.host, self.port), HealthCheckHandler)
            thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            thread.start()
            logger.info(f"Health check server started on {self.host}:{self.port}")
            return True
        except OSError as e:
            logger.error(f"Failed to start health check server (port conflict?): {e}")
            return False

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Health check server stopped")

    def is_running(self) -> bool:
        return self.server is not None


def start_health_server() -> Optional[HealthCheckServer]:
    if not settings.enable_metrics:
        logger.info("Metrics server disabled")
        return None
    server = HealthCheckServer(port=settings.metrics_port)
    return server if server.start() else None


if __name__ == "__main__":
    import time

    server = HealthCheckServer()
    if server.start():
        logger.info("Server running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)  # CPU-friendly keep-alive
        except KeyboardInterrupt:
            server.stop()
    else:
        logger.error("Failed to start server")
        exit(1)
