from typing import List, Dict, Any, Optional

class ContextBuilder:
    """Formats code static checker findings and complexity metrics into structured prompt contexts."""

    @staticmethod
    def format_static_analysis(findings: List[Any]) -> str:
        """Formats the ORM review findings or dict structures into a structured list block."""
        if not findings:
            return "No previous static analysis issues or vulnerabilities were detected."
            
        lines = ["Detected static analysis check warnings:"]
        for f in findings:
            if hasattr(f, "provider"):
                provider = f.provider
                category = f.category
                severity = f.severity
                line = f.line_number
                msg = f.message
            elif isinstance(f, dict):
                provider = f.get("provider", "unknown")
                category = f.get("category", "style")
                severity = f.get("severity", "warning")
                line = f.get("line_number", 0)
                msg = f.get("message", "")
            else:
                continue

            lines.append(f"- [{provider.upper()}] Line {line}: [{severity.upper()}] ({category}) {msg}")
            
        return "\n".join(lines)

    @staticmethod
    def format_metrics(metrics: Any) -> str:
        """Formats complexity metrics details into descriptive prompt contexts."""
        if not metrics:
            return "No code complexity statistics are available."
            
        if hasattr(metrics, "cyclomatic_complexity"):
            cc = metrics.cyclomatic_complexity
            mi = metrics.maintainability_index
            loc = metrics.loc
            funcs = metrics.functions_count
            classes = metrics.classes_count
        elif isinstance(metrics, dict):
            cc = metrics.get("cyclomatic_complexity", 0)
            mi = metrics.get("maintainability_index", 100.0)
            loc = metrics.get("loc", 0)
            funcs = metrics.get("functions_count", 0)
            classes = metrics.get("classes_count", 0)
        else:
            return "No code complexity statistics are available."

        return (
            f"Code Metrics Summary:\n"
            f"- Cyclomatic Complexity: {cc}\n"
            f"- Maintainability Index: {mi:.2f}\n"
            f"- Lines of Code (LOC): {loc}\n"
            f"- Functions Count: {funcs}\n"
            f"- Classes Count: {classes}"
        )

    @classmethod
    def build_full_context(cls, findings: List[Any], metrics: Any) -> str:
        """Aggregates all diagnostics reports into a single consolidated string block."""
        analysis_str = cls.format_static_analysis(findings)
        metrics_str = cls.format_metrics(metrics)
        return f"{analysis_str}\n\n{metrics_str}"
