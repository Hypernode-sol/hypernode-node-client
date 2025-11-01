"""Configuration management for Hypernode worker"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Worker configuration from environment variables"""

    node_token: str = os.getenv("HN_NODE_TOKEN", "")
    wallet_pubkey: str = os.getenv("WALLET_PUBKEY", "")
    backend_url: str = os.getenv("BACKEND_URL", "https://api.hypernode.sol")
    heartbeat_interval: int = int(os.getenv("HEARTBEAT_INTERVAL", "60"))
    max_jobs_concurrent: int = int(os.getenv("MAX_JOBS_CONCURRENT", "1"))
    gpu_index: int = int(os.getenv("GPU_INDEX", "0"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
