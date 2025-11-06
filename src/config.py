"""Configuration management for Hypernode worker"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


@dataclass
class Config:
    """Worker configuration from environment variables"""

    node_token: str = field(default_factory=lambda: os.getenv("HN_NODE_TOKEN", ""))
    wallet_pubkey: str = field(default_factory=lambda: os.getenv("WALLET_PUBKEY", ""))
    backend_url: str = field(default_factory=lambda: os.getenv("BACKEND_URL", "https://api.hypernode.sol"))
    heartbeat_interval: int = field(default_factory=lambda: max(10, min(int(os.getenv("HEARTBEAT_INTERVAL", "60")), 600)))
    max_jobs_concurrent: int = field(default_factory=lambda: max(1, min(int(os.getenv("MAX_JOBS_CONCURRENT", "1")), 10)))
    gpu_index: int = field(default_factory=lambda: max(0, int(os.getenv("GPU_INDEX", "0"))))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    request_timeout: int = field(default_factory=lambda: max(5, min(int(os.getenv("REQUEST_TIMEOUT", "30")), 300)))
    job_poll_interval: int = field(default_factory=lambda: max(5, min(int(os.getenv("JOB_POLL_INTERVAL", "10")), 60)))

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate configuration values"""
        if not self.node_token:
            return False, "HN_NODE_TOKEN is required"

        if not self.wallet_pubkey or len(self.wallet_pubkey) < 32:
            return False, "WALLET_PUBKEY is required and must be valid Solana address"

        if not self.backend_url.startswith(("http://", "https://")):
            return False, "BACKEND_URL must start with http:// or https://"

        if self.heartbeat_interval < 10:
            return False, "HEARTBEAT_INTERVAL must be at least 10 seconds"

        return True, None
