#!/usr/bin/env python3
"""
Hypernode Node Client - Main Worker
Detects GPU, registers with network, executes jobs, sends heartbeats
"""

import os
import time
import signal
import sys
import structlog
from typing import Optional
import threading

from config import Config
from gpu_detector import GPUDetector
from heartbeat import HeartbeatManager
from job_executor import JobExecutor
from telemetry import TelemetryReporter

# Setup logging
log = structlog.get_logger()


class HypernodeWorker:
    """Main worker class that orchestrates all node operations"""

    def __init__(self):
        self.config = Config()
        self.running = False
        self.gpu_detector = GPUDetector()
        self.heartbeat_manager: Optional[HeartbeatManager] = None
        self.job_executor: Optional[JobExecutor] = None
        self.telemetry_reporter: Optional[TelemetryReporter] = None

    def validate_config(self) -> bool:
        """Validate required configuration"""
        if not self.config.node_token:
            log.error("HN_NODE_TOKEN not set - get it from /app")
            return False

        if not self.config.wallet_pubkey:
            log.error("WALLET_PUBKEY not set - provide your Solana wallet")
            return False

        return True

    def register_node(self) -> bool:
        """Register node with the network"""
        log.info("Detecting GPU specifications...")

        gpu_info = self.gpu_detector.detect()

        log.info(
            "GPU detected",
            gpu_model=gpu_info.get("model", "Unknown"),
            vram_mb=gpu_info.get("vram_mb", 0),
            driver=gpu_info.get("driver_version", "Unknown")
        )

        # Send registration to backend
        try:
            import requests
            response = requests.post(
                f"{self.config.backend_url}/api/nodes/register",
                json={
                    "walletAddress": self.config.wallet_pubkey,
                    "gpuModel": gpu_info.get("model", "Unknown"),
                    "vram": gpu_info.get("vram_mb", 0) // 1024,  # Convert to GB
                    "driverVersion": gpu_info.get("driver_version", "Unknown"),
                    "cudaVersion": gpu_info.get("cuda_version", "Unknown"),
                    "hostOS": gpu_info.get("os", "Unknown"),
                    "cpuModel": gpu_info.get("cpu_model", "Unknown"),
                    "ramTotal": gpu_info.get("ram_total_mb", 0),
                    "location": {
                        "country": "Unknown",
                        "city": "Unknown",
                        "lat": 0,
                        "lon": 0
                    },
                    "capabilities": gpu_info.get("capabilities", ["inference"])
                },
                headers={"Authorization": f"Bearer {self.config.node_token}"},
                timeout=10
            )

            if response.status_code in [200, 201]:
                data = response.json()
                node_id = data.get("node", {}).get("nodeId")
                log.info("Node registered successfully", node_id=node_id)
                return True
            else:
                log.error("Registration failed", status=response.status_code, response=response.text)
                return False

        except Exception as e:
            log.error("Registration error", error=str(e))
            return False

    def start(self):
        """Start the worker"""
        log.info("🚀 Hypernode Worker starting...")
        log.info(
            "Configuration",
            backend_url=self.config.backend_url,
            wallet=self.config.wallet_pubkey[:8] + "...",
            heartbeat_interval=self.config.heartbeat_interval
        )

        if not self.validate_config():
            log.error("Invalid configuration - exiting")
            sys.exit(1)

        # Register node
        if not self.register_node():
            log.error("Failed to register node - retrying in 30s...")
            time.sleep(30)
            if not self.register_node():
                log.error("Registration failed twice - exiting")
                sys.exit(1)

        # Initialize components
        self.heartbeat_manager = HeartbeatManager(self.config)
        self.job_executor = JobExecutor(self.config)
        self.telemetry_reporter = TelemetryReporter(self.config)

        # Start background threads
        self.running = True

        heartbeat_thread = threading.Thread(target=self._run_heartbeat_loop, daemon=True)
        telemetry_thread = threading.Thread(target=self._run_telemetry_loop, daemon=True)
        job_thread = threading.Thread(target=self._run_job_loop, daemon=True)

        heartbeat_thread.start()
        telemetry_thread.start()
        job_thread.start()

        log.info("✅ Worker running - press Ctrl+C to stop")

        # Main loop (just keeps process alive)
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Shutdown signal received...")
            self.stop()

    def _run_heartbeat_loop(self):
        """Background loop for sending heartbeats"""
        while self.running:
            try:
                self.heartbeat_manager.send_heartbeat()
                time.sleep(self.config.heartbeat_interval)
            except Exception as e:
                log.error("Heartbeat error", error=str(e))
                time.sleep(5)

    def _run_telemetry_loop(self):
        """Background loop for reporting telemetry"""
        while self.running:
            try:
                self.telemetry_reporter.report()
                time.sleep(60)  # Report every minute
            except Exception as e:
                log.error("Telemetry error", error=str(e))
                time.sleep(10)

    def _run_job_loop(self):
        """Background loop for checking and executing jobs"""
        while self.running:
            try:
                # Poll for available jobs
                job = self.job_executor.poll_job()
                if job:
                    log.info("Job received", job_id=job.get("jobId"))
                    self.job_executor.execute_job(job)
                else:
                    time.sleep(10)  # Wait 10s before checking again
            except Exception as e:
                log.error("Job execution error", error=str(e))
                time.sleep(5)

    def stop(self):
        """Stop the worker gracefully"""
        log.info("Stopping worker...")
        self.running = False
        time.sleep(2)
        log.info("Worker stopped")
        sys.exit(0)


def main():
    """Entry point"""
    # Setup signal handlers
    def signal_handler(sig, frame):
        log.info("Signal received, shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start worker
    worker = HypernodeWorker()
    worker.start()


if __name__ == "__main__":
    main()
