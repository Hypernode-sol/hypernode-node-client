"""Base class for job execution"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import structlog

log = structlog.get_logger()


class BaseJob(ABC):
    """Base class for all job types"""

    def __init__(self, job_data: Dict[str, Any]):
        self.job_id = job_data.get('jobId')
        self.job_type = job_data.get('type')
        self.input_data = job_data.get('input', {})
        self.config = job_data.get('config', {})

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the job and return results"""
        pass

    def validate(self) -> bool:
        """Validate job inputs before execution"""
        if not self.job_id:
            log.error("Job ID missing")
            return False
        return True

    def cleanup(self):
        """Clean up resources after job execution"""
        pass
