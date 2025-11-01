"""Job executor - polls for jobs and executes them"""

import requests
import structlog
from typing import Optional, Dict

from config import Config

log = structlog.get_logger()


class JobExecutor:
    """Polls for and executes compute jobs"""

    def __init__(self, config: Config):
        self.config = config
        self.current_job: Optional[Dict] = None

    def poll_job(self) -> Optional[Dict]:
        """Poll backend for available jobs"""
        try:
            response = requests.get(
                f"{self.config.backend_url}/api/jobs/available",
                headers={"Authorization": f"Bearer {self.config.node_token}"},
                params={"wallet": self.config.wallet_pubkey},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                job = data.get("job")
                if job:
                    log.info("Job available", job_id=job.get("jobId"), type=job.get("jobType"))
                    return job

            return None

        except Exception as e:
            log.error("Job polling error", error=str(e))
            return None

    def execute_job(self, job: Dict) -> bool:
        """Execute a received job"""
        job_id = job.get("jobId")
        job_type = job.get("jobType")

        log.info("Executing job", job_id=job_id, type=job_type)

        try:
            # Job type routing
            if job_type == "llm_inference":
                result = self._execute_llm_inference(job)
            elif job_type == "llm_fine_tuning":
                result = self._execute_fine_tuning(job)
            elif job_type == "rag_indexing":
                result = self._execute_rag_indexing(job)
            elif job_type == "vision_pipeline":
                result = self._execute_vision(job)
            elif job_type == "render":
                result = self._execute_render(job)
            else:
                result = self._execute_generic(job)

            # Report result back to backend
            self._report_result(job_id, result)

            log.info("Job completed", job_id=job_id)
            return True

        except Exception as e:
            log.error("Job execution failed", job_id=job_id, error=str(e))
            self._report_failure(job_id, str(e))
            return False

    def _execute_llm_inference(self, job: Dict) -> Dict:
        """Execute LLM inference job"""
        # Placeholder - would load model and run inference
        return {
            "output": "This is a placeholder result for LLM inference",
            "tokens": 100,
            "time_ms": 1500
        }

    def _execute_fine_tuning(self, job: Dict) -> Dict:
        """Execute fine-tuning job"""
        return {
            "checkpoint_url": "https://example.com/checkpoint.pth",
            "loss": 0.25,
            "epochs": 3
        }

    def _execute_rag_indexing(self, job: Dict) -> Dict:
        """Execute RAG indexing job"""
        return {
            "index_url": "https://example.com/index.faiss",
            "documents_processed": 1000
        }

    def _execute_vision(self, job: Dict) -> Dict:
        """Execute vision pipeline job"""
        return {
            "detections": [],
            "confidence": 0.95
        }

    def _execute_render(self, job: Dict) -> Dict:
        """Execute render job"""
        return {
            "render_url": "https://example.com/render.png",
            "frames": 1
        }

    def _execute_generic(self, job: Dict) -> Dict:
        """Execute generic compute job"""
        return {
            "result": "Generic job completed",
            "exit_code": 0
        }

    def _report_result(self, job_id: str, result: Dict):
        """Report successful job result"""
        try:
            requests.post(
                f"{self.config.backend_url}/api/jobs/{job_id}/result",
                json={
                    "nodeId": "current_node_id",  # Would get from registration
                    "result": result,
                    "logs": [],
                    "metrics": {}
                },
                headers={"Authorization": f"Bearer {self.config.node_token}"},
                timeout=10
            )
        except Exception as e:
            log.error("Failed to report result", job_id=job_id, error=str(e))

    def _report_failure(self, job_id: str, error: str):
        """Report job failure"""
        try:
            requests.post(
                f"{self.config.backend_url}/api/jobs/{job_id}/failure",
                json={"error": error},
                headers={"Authorization": f"Bearer {self.config.node_token}"},
                timeout=10
            )
        except Exception as e:
            log.error("Failed to report failure", job_id=job_id, error=str(e))
