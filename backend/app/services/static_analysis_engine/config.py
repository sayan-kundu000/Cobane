import os


class StaticAnalysisConfig:
    """Manages system validation checks limits, active tools registry list, and shell command execution timeouts."""

    def __init__(self):
        self.max_file_size_kb: int = int(os.getenv("STATIC_MAX_FILE_SIZE_KB", "5000"))
        self.timeout_seconds: float = float(os.getenv("STATIC_TIMEOUT_SECONDS", "15.0"))
        self.supported_extensions = {".py"}
        self.supported_languages = {"python"}
        self.enabled_analyzers = ["pylint", "bandit", "radon"]


static_config = StaticAnalysisConfig()
