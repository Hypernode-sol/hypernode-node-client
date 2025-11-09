"""Telemetry reporter - sends GPU/system metrics"""

import psutil
import structlog
from typing import Dict

from config import Config
from gpu_detector import GPUDetector

log = structlog.get_logger()


class TelemetryReporter:
    """Reports system and GPU telemetry"""

    def __init__(self, config: Config):
        self.config = config
        self.gpu_detector = GPUDetector()

    def report(self):
        """Collect and report telemetry"""
        try:
            metrics = self._collect_metrics()

            # Check GPU health
            health = self.gpu_detector.monitor_health()
            metrics["gpu_health"] = health

            # Log warnings if unhealthy
            if not health["healthy"]:
                log.warning("GPU health issues detected", issues=health["issues"])

            log.debug("Telemetry collected", **metrics)

            # In production, send to backend
            # requests.post(f"{self.config.backend_url}/api/telemetry", json=metrics)

        except Exception as e:
            log.error("Telemetry collection error", error=str(e))

    def _collect_metrics(self) -> Dict:
        """Collect system metrics"""
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        }

        # Get detailed GPU stats using detector
        gpu_stats = self.gpu_detector.get_gpu_stats()
        if gpu_stats:
            metrics.update(gpu_stats)

        return metrics
