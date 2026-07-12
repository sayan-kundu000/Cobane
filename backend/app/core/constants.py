# Cobane core system constants
# Chapter 03 - Backend Foundation

API_V1_PREFIX: str = "/api/v1"
DEFAULT_TIMEZONE: str = "UTC"
DEFAULT_ENCODING: str = "utf-8"

# Upload and code validation configurations
MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
SUPPORTED_FILE_TYPES: set[str] = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".cs", ".cpp", ".sql", ".r"
}

# Pagination guidelines
DEFAULT_PAGE: int = 1
DEFAULT_LIMIT: int = 20
MAX_LIMIT: int = 100
