"""GPU detection and specification gathering"""

import platform
import psutil
import structlog
from typing import Dict, List

log = structlog.get_logger()


class GPUDetector:
    """Detects GPU specifications and capabilities"""

    def detect(self) -> Dict:
        """Detect GPU and system specifications"""
        gpu_info = {
            "model": "Unknown",
            "vram_mb": 0,
            "driver_version": "Unknown",
            "cuda_version": "Unknown",
            "os": platform.system() + " " + platform.release(),
            "cpu_model": self._get_cpu_model(),
            "ram_total_mb": self._get_total_ram(),
            "capabilities": []
        }

        # Try NVIDIA first
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()

            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)

                gpu_info["model"] = pynvml.nvmlDeviceGetName(handle).decode("utf-8")

                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_info["vram_mb"] = mem_info.total // (1024 * 1024)

                gpu_info["driver_version"] = pynvml.nvmlSystemGetDriverVersion().decode("utf-8")
                gpu_info["cuda_version"] = pynvml.nvmlSystemGetCudaDriverVersion_v2()

                # Determine capabilities based on VRAM
                vram_gb = gpu_info["vram_mb"] // 1024
                gpu_info["capabilities"] = self._determine_capabilities(vram_gb)

                pynvml.nvmlShutdown()
                log.info("NVIDIA GPU detected", model=gpu_info["model"])

        except Exception as e:
            log.warning("NVIDIA GPU not found or pynvml error", error=str(e))

            # Try AMD (ROCm)
            try:
                # ROCm detection would go here
                pass
            except:
                pass

            # Fallback to CPU-only
            if gpu_info["model"] == "Unknown":
                gpu_info["model"] = "CPU-only (No GPU detected)"
                gpu_info["capabilities"] = ["cpu_compute"]

        return gpu_info

    def _get_cpu_model(self) -> str:
        """Get CPU model name"""
        try:
            if platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
            return platform.processor()
        except:
            return "Unknown"

    def _get_total_ram(self) -> int:
        """Get total system RAM in MB"""
        try:
            return psutil.virtual_memory().total // (1024 * 1024)
        except:
            return 0

    def _determine_capabilities(self, vram_gb: int) -> List[str]:
        """Determine node capabilities based on VRAM"""
        capabilities = []

        if vram_gb >= 24:
            # High-end GPU (RTX 4090, A6000, etc.)
            capabilities = ["inference", "training", "fine_tuning", "render", "vision"]
        elif vram_gb >= 12:
            # Mid-high GPU (RTX 3080, 4070, etc.)
            capabilities = ["inference", "fine_tuning", "render"]
        elif vram_gb >= 8:
            # Mid-range GPU
            capabilities = ["inference", "render"]
        elif vram_gb >= 4:
            # Entry-level GPU
            capabilities = ["inference"]
        else:
            # Very low VRAM or CPU-only
            capabilities = ["cpu_compute"]

        return capabilities

    def estimate_max_batch_size(self, vram_mb: int) -> int:
        """Estimate maximum batch size based on VRAM"""
        vram_gb = vram_mb / 1024

        if vram_gb >= 24:
            return 32
        elif vram_gb >= 16:
            return 16
        elif vram_gb >= 12:
            return 8
        elif vram_gb >= 8:
            return 4
        elif vram_gb >= 6:
            return 2
        else:
            return 1

    def get_gpu_stats(self) -> Dict:
        """Get current GPU utilization and health stats"""
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)

            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

            try:
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000  # Convert mW to W
            except:
                power = 0

            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            mem_utilization = (mem_info.used / mem_info.total) * 100

            pynvml.nvmlShutdown()

            return {
                "gpu_utilization": utilization.gpu,
                "memory_utilization": mem_utilization,
                "temperature": temperature,
                "power_draw": power,
                "vram_used_mb": mem_info.used // (1024 * 1024),
                "vram_total_mb": mem_info.total // (1024 * 1024)
            }

        except Exception as e:
            log.warning("Failed to get GPU stats", error=str(e))
            return {}

    def monitor_health(self) -> Dict:
        """Monitor GPU health and detect issues"""
        stats = self.get_gpu_stats()

        if not stats:
            return {"healthy": True, "issues": [], "stats": {}}

        issues = []

        # Temperature check
        if stats.get("temperature", 0) > 85:
            issues.append("High temperature (>85°C)")

        # GPU utilization check
        if stats.get("gpu_utilization", 0) > 95:
            issues.append("GPU overloaded (>95% utilization)")

        # VRAM check
        if stats.get("memory_utilization", 0) > 95:
            issues.append("VRAM overloaded (>95% utilization)")

        healthy = len(issues) == 0

        if not healthy:
            log.warning("GPU health issues detected", issues=issues, stats=stats)

        return {
            "healthy": healthy,
            "issues": issues,
            "stats": stats
        }
