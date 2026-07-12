import os


def sanitize_path(base_dir: str, user_path: str) -> str:
    """Sanitizes user paths to prevent directory traversal exploits.

    Raises ValueError if path attempts to escape the root base directory.
    """
    resolved_base = os.path.abspath(base_dir)
    resolved_target = os.path.abspath(os.path.join(base_dir, user_path))

    if not resolved_target.startswith(resolved_base):
        raise ValueError("Directory traversal attempt detected.")

    return resolved_target


def ensure_directory_exists(directory_path: str) -> None:
    """Creates directory if not exists."""
    os.makedirs(directory_path, exist_ok=True)
