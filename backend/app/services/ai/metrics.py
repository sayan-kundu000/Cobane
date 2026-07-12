class AIMetricsTracker:
    """Simple in-memory diagnostics tracker collecting request volumes and latency metrics."""

    def __init__(self):
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        self.total_retries: int = 0
        self.total_tokens_estimated: int = 0
        self.total_response_time: float = 0.0

    def record_request(self, tokens_count: int) -> None:
        """Increments request volume counter and registers token counts."""
        self.total_requests += 1
        self.total_tokens_estimated += tokens_count

    def record_success(self, duration_seconds: float) -> None:
        """Increments success counter and tracks completion processing times."""
        self.successful_requests += 1
        self.total_response_time += duration_seconds

    def record_failure(self) -> None:
        """Increments failed request diagnostics counters."""
        self.failed_requests += 1

    def record_retry(self) -> None:
        """Tracks retry attempts triggered by remote service errors."""
        self.total_retries += 1

    @property
    def average_response_time(self) -> float:
        """Computes average response latencies in seconds."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests

    @property
    def success_rate(self) -> float:
        """Computes success rate ratio of requests volume."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    def get_summary(self) -> dict:
        """Returns aggregated dashboard-compatible summary payload configurations."""
        return {
            "total_requests_sent": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "total_retries": self.total_retries,
            "total_tokens_estimated": self.total_tokens_estimated,
            "average_response_time_seconds": round(self.average_response_time, 3),
            "success_rate": round(self.success_rate, 3),
        }


ai_metrics = AIMetricsTracker()
