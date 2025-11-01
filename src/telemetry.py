"""Telemetry reporter - sends GPU/system metrics"""

import psutil
import structlog
from typing import Dict

from config import Config

log = structlog.get_logger()


class TelemetryReporter:
    """Reports system and GPU telemetry"""

    def __init__(self, config: Config):
        self.config = config

    def report(self):
        """Collect and report telemetry"""
        try:
            metrics = self._collect_metrics()
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

        # Try to get GPU metrics
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)

            gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            metrics["gpu_percent"] = gpu_util.gpu
            metrics["gpu_memory_percent"] = gpu_util.memory

            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            metrics["gpu_temp_c"] = temp

            power = pynvml.nvmlDeviceGetPowerUsage(handle) // 1000  # mW to W
            metrics["gpu_power_w"] = power

            pynvml.nvmlShutdown()
        except:
            pass

        return metrics
