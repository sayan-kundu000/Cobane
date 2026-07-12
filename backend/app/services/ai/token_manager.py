from typing import List
from app.core.logging import ai_logger


def estimate_tokens(text: str, model_name: str = "gpt-4o") -> int:
    """Estimates token size using tiktoken if available, with a safe character-based fallback."""
    if not text:
        return 0
    try:
        import tiktoken  # pylint: disable=import-outside-toplevel

        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except ImportError:
        # Fallback heuristic: 1 token ~ 4 characters on average
        return max(1, len(text) // 4)


def chunk_code(code_content: str, max_tokens_per_chunk: int = 3000, model_name: str = "gpt-4o") -> List[str]:
    """Splits a large codebase content string into separate logical chunks below token thresholds."""
    estimated_total = estimate_tokens(code_content, model_name)
    if estimated_total <= max_tokens_per_chunk:
        return [code_content]

    ai_logger.info(
        "Code size (%d estimated tokens) exceeds chunk limit of %d. Splitting content...",
        estimated_total,
        max_tokens_per_chunk,
    )

    lines = code_content.splitlines()
    chunks = []
    current_lines = []
    current_tokens = 0

    for line in lines:
        line_str = line + "\n"
        line_tokens = estimate_tokens(line_str, model_name)

        # If a single line is somehow larger than the chunk size limit, we force split it
        if line_tokens > max_tokens_per_chunk:
            if current_lines:
                chunks.append("\n".join(current_lines))
                current_lines = []
                current_tokens = 0
            chunks.append(line)
            continue

        if current_tokens + line_tokens > max_tokens_per_chunk:
            if current_lines:
                chunks.append("\n".join(current_lines))
            current_lines = [line]
            current_tokens = line_tokens
        else:
            current_lines.append(line)
            current_tokens += line_tokens

    if current_lines:
        chunks.append("\n".join(current_lines))

    ai_logger.info("Successfully split code content into %d chunks.", len(chunks))
    return chunks
