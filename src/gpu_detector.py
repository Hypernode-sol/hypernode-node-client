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
