"""Heartbeat manager - sends periodic keep-alive signals"""

import requests
import structlog
from typing import Optional

from config import Config

log = structlog.get_logger()


class HeartbeatManager:
    """Manages heartbeat sending to keep node alive"""

    def __init__(self, config: Config):
        self.config = config
        self.node_id: Optional[str] = None

    def send_heartbeat(self) -> bool:
        """Send heartbeat to backend"""
        try:
            response = requests.post(
                f"{self.config.backend_url}/api/nodes/heartbeat",
                json={
                    "walletAddress": self.config.wallet_pubkey,
                    "status": "online"
                },
                headers={"Authorization": f"Bearer {self.config.node_token}"},
                timeout=10
            )

            if response.status_code == 200:
                log.debug("Heartbeat sent successfully")
                return True
            else:
                log.warning("Heartbeat failed", status=response.status_code)
                return False

        except Exception as e:
            log.error("Heartbeat error", error=str(e))
            return False
