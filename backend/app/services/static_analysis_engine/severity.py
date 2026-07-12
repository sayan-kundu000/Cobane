class SeverityMapper:
    """Standardizes static analysis output severity values from checker-specific ratings into a common rating scale."""

    @staticmethod
    def map_pylint(pylint_type: str) -> str:
        """Maps Pylint message categories to: info, low, medium, high, critical."""
        val = pylint_type.lower().strip()
        if val == "fatal":
            return "critical"
        elif val == "error":
            return "high"
        elif val == "warning":
            return "medium"
        elif val == "refactor":
            return "low"
        elif val in {"convention", "info"}:
            return "info"
        return "info"

    @staticmethod
    def map_bandit(bandit_severity: str) -> str:
        """Maps Bandit risk ratings to: info, low, medium, high, critical."""
        val = bandit_severity.upper().strip()
        if val == "HIGH":
            return "high"
        elif val == "MEDIUM":
            return "medium"
        elif val == "LOW":
            return "low"
        elif val in {"UNDEFINED", "INFO"}:
            return "info"
        return "low"
