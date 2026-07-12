class PromptManager:
    """Manager for system instructions and compiled user prompts templates."""

    @staticmethod
    def get_system_prompt() -> str:
        """Returns the base system instruction rules enforcing JSON output conformity."""
        return (
            "You are Cobane, an expert AI Code Review Assistant designed to perform deep, premium code reviews.\n"
            "Analyze the provided code content alongside its static check findings. Your job is to detect issues and "
            "provide constructive, actionable recommendations.\n\n"
            "CRITICAL: You MUST respond ONLY with a raw, valid JSON object matching the JSON schema below.\n"
            "Do not wrap your output in ```json ... ``` markdown blocks, and do not add any conversational text before or after the JSON.\n\n"
            "JSON Response Schema:\n"
            "{\n"
            '  "summary": "Overall summary of the review, highlights, and high-level feedback",\n'
            '  "findings": [\n'
            "    {\n"
            '      "category": "bug" | "smell" | "performance" | "security" | "refactor" | "naming" | "best_practice" | "docs" | "maintainability" | "readability",\n'
            '      "severity": "info" | "warning" | "error" | "critical",\n'
            '      "summary": "Short 1-line recommendation header",\n'
            '      "explanation": "Why this code is problematic or needs improvement",\n'
            '      "recommendation": "Code suggestion showing how to rewrite or fix it",\n'
            '      "confidence": 0.0 to 1.0 (float),\n'
            '      "file_reference": "Name of the file reviewed",\n'
            '      "function_reference": "Optional function name or null",\n'
            '      "line_reference": 1-indexed line number or null\n'
            "    }\n"
            "  ]\n"
            "}\n"
        )

    @staticmethod
    def get_user_prompt(filename: str, language: str, code_content: str, static_context: str) -> str:
        """Compiles code content and static diagnostics context into a formatted user prompt."""
        return (
            f"Review Request Details:\n"
            f"File: {filename}\n"
            f"Language: {language}\n\n"
            f"--- CODE CONTENT TO REVIEW ---\n"
            f"{code_content}\n"
            f"------------------------------\n\n"
            f"--- STATIC ANALYSIS DIAGNOSTICS ---\n"
            f"{static_context}\n"
            f"-----------------------------------\n\n"
            f"Please conduct the code review now and return findings in the requested JSON structure."
        )
