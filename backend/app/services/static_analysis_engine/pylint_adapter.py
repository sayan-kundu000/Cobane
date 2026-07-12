import asyncio
import json
import os
import sys
import subprocess
from typing import Dict, Any, List
from app.services.static_analysis_engine.interface import BaseAnalyzer
from app.services.static_analysis_engine.models import NormalizedFinding
from app.services.static_analysis_engine.severity import SeverityMapper
from app.core.exceptions import ValidationException
from app.core.logging import analysis_logger


class PylintAdapter(BaseAnalyzer):
    """Adapter programmatically executing Pylint programmatically and normalizing output logs."""

    def validate(self, file_path: str) -> bool:
        """Validates that the file exists and has a .py extension."""
        if not os.path.exists(file_path):
            return False
        return file_path.endswith(".py")

    def _compile_args(self, file_path: str) -> List[str]:
        """Assembles CLI arguments array using active python interpreter execution path."""
        return [sys.executable, "-m", "pylint", "--output-format=json", file_path]

    def _parse_raw_stdout(self, stdout: str) -> List[Dict[str, Any]]:
        """Safely parses stdout JSON payload."""
        if not stdout.strip():
            return []
        try:
            return json.loads(stdout)
        except json.JSONDecodeError as e:
            analysis_logger.warning("Pylint stdout was not valid JSON: %s. Raw: %s", str(e), stdout)
            return []

    def run_sync(self, file_path: str) -> Dict[str, Any]:
        """Runs pylint synchronously via subprocess."""
        if not self.validate(file_path):
            raise ValidationException(f"File {file_path} is invalid for Pylint analysis.")

        args = self._compile_args(file_path)
        analysis_logger.info("Executing Pylint sync command: %s", " ".join(args))

        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=self.timeout_seconds)
            parsed = self._parse_raw_stdout(result.stdout)
            return {"results": parsed, "success": True}
        except subprocess.TimeoutExpired as e:
            analysis_logger.error("Pylint execution timed out for file %s.", file_path)
            return {"results": [], "success": False, "error": "Timeout expired."}
        except Exception as e:
            analysis_logger.error("Failed running Pylint checker tool: %s", str(e))
            return {"results": [], "success": False, "error": str(e)}

    async def run_async(self, file_path: str) -> Dict[str, Any]:
        """Runs pylint asynchronously via asyncio subprocess."""
        if not self.validate(file_path):
            raise ValidationException(f"File {file_path} is invalid for Pylint analysis.")

        args = self._compile_args(file_path)
        analysis_logger.info("Executing Pylint async command: %s", " ".join(args))

        try:
            process = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=self.timeout_seconds)
                stdout = stdout_bytes.decode("utf-8", errors="ignore")
                parsed = self._parse_raw_stdout(stdout)
                return {"results": parsed, "success": True}
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
                analysis_logger.error("Pylint async execution timed out for file %s.", file_path)
                return {"results": [], "success": False, "error": "Timeout expired."}
        except Exception as e:
            analysis_logger.error("Failed executing Pylint async checker: %s", str(e))
            return {"results": [], "success": False, "error": str(e)}

    def normalize(self, raw_output: Dict[str, Any], file_path: str) -> List[NormalizedFinding]:
        """Normalizes Pylint JSON logs into standard NormalizedFinding objects."""
        findings = []
        raw_list = raw_output.get("results", [])
        for item in raw_list:
            category = item.get("type", "style")
            severity = SeverityMapper.map_pylint(category)
            line = item.get("line", 1)
            msg_id = item.get("message-id", "unknown")
            symbol = item.get("symbol", "")
            rule = f"{msg_id} ({symbol})" if symbol else msg_id
            description = item.get("message", "Pylint check warning.")
            recommendation = f"Refactor suggestion to resolve Pylint warning rule: {symbol}."

            findings.append(
                NormalizedFinding(
                    analyzer="pylint",
                    category="style" if category in {"convention", "refactor"} else "bug",
                    severity=severity,
                    rule=rule,
                    description=description,
                    recommendation=recommendation,
                    file_path=os.path.basename(file_path),
                    function_name=item.get("obj") or None,
                    line_number=line,
                    confidence="high",
                )
            )
        return findings

    @staticmethod
    def calculate_score(raw_list: List[Dict[str, Any]]) -> float:
        """Calculates a custom code quality score out of 10 based on issue volume."""
        if not raw_list:
            return 10.0
        errors = sum(1 for item in raw_list if item.get("type") in {"error", "fatal"})
        warnings = sum(1 for item in raw_list if item.get("type") == "warning")
        refactors = sum(1 for item in raw_list if item.get("type") == "refactor")
        conventions = sum(1 for item in raw_list if item.get("type") == "convention")

        score = 10.0 - (errors * 2.0 + warnings * 0.5 + refactors * 0.2 + conventions * 0.1)
        return round(max(0.0, score), 2)
