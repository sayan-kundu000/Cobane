import abc
from typing import Dict, Any, List
from app.services.static_analysis_engine.models import NormalizedFinding


class BaseAnalyzer(abc.ABC):
    """Abstract base class establishing the contract that all static analysis adapters must satisfy."""

    def __init__(self, timeout_seconds: float = 15.0):
        self.timeout_seconds = timeout_seconds

    @abc.abstractmethod
    def validate(self, file_path: str) -> bool:
        """Validates if the target source file is supported and exists."""
        pass

    @abc.abstractmethod
    def run_sync(self, file_path: str) -> Dict[str, Any]:
        """Runs the static analysis tool synchronously. Returns raw dictionary output."""
        pass

    @abc.abstractmethod
    async def run_async(self, file_path: str) -> Dict[str, Any]:
        """Runs the static analysis tool asynchronously. Returns raw dictionary output."""
        pass

    @abc.abstractmethod
    def normalize(self, raw_output: Dict[str, Any], file_path: str) -> List[NormalizedFinding]:
        """Converts raw tool output dictionaries to a list of standard NormalizedFinding objects."""
        pass
