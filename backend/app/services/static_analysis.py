# Static code analysis executor (Pylint, Bandit, Radon wrappers).

from app.core.logging import analysis_logger

class StaticAnalysisService:
    """Service orchestrating static analysis verification engines."""
    
    def run_all(self, file_path: str) -> dict:
        """Runs synchronous static checkers pipeline, formatting outputs to map onto legacy schemas."""
        analysis_logger.info("Running static analysis tools for file: %s", file_path)

        # Import orchestrator programmatically to avoid circular import paths
        from app.services.static_analysis_engine.orchestrator import StaticAnalysisOrchestrator
        orchestrator = StaticAnalysisOrchestrator()

        # Run synchronous code checks
        report = orchestrator.run_analysis_sync(file_path)

        # Build pylint warnings dictionary list
        pylint_warnings = []
        for finding in report.findings:
            if finding.analyzer == "pylint":
                pylint_warnings.append({
                    "line": finding.line_number,
                    "message": finding.description,
                    "symbol": finding.rule,
                    "type": finding.severity
                })

        # Build bandit issues list
        bandit_issues = []
        for finding in report.findings:
            if finding.analyzer == "bandit":
                bandit_issues.append({
                    "line": finding.line_number,
                    "issue_text": finding.description,
                    "severity": finding.severity,
                    "test_id": finding.rule
                })

        # Format radon metrics data
        radon_cc = {
            "cyclomatic_complexity": report.metrics.cyclomatic_complexity,
            "maintainability_index": report.metrics.maintainability_index,
            "loc": report.metrics.loc,
            "functions_count": report.metrics.functions_count,
            "classes_count": report.metrics.classes_count
        }

        # Return backward-compatible results wrapper
        return {
            "pylint": {
                "score": report.pylint_score,
                "conventions": [],
                "warnings": pylint_warnings
            },
            "bandit": {
                "score": "FAIL" if report.bandit_issues_count > 0 else "PASS",
                "issues": bandit_issues
            },
            "radon": {
                "score": "A" if report.metrics.maintainability_index >= 80.0 else "B",
                "cc": radon_cc
            }
        }
