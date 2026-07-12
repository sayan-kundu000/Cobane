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

class BanditAdapter(BaseAnalyzer):
    """Adapter programmatically executing Bandit programmatically to scan for security vulnerabilities."""

    def validate(self, file_path: str) -> bool:
        """Validates that the file exists and has a .py extension."""
        if not os.path.exists(file_path):
            return False
        return file_path.endswith(".py")

    def _compile_args(self, file_path: str) -> List[str]:
        """Assembles CLI arguments array using sys.executable path."""
        return [sys.executable, "-m", "bandit", "-f", "json", "-q", file_path]

    def _parse_raw_stdout(self, stdout: str) -> Dict[str, Any]:
        """Safely parses stdout JSON payload."""
        if not stdout.strip():
            return {"results": []}
        try:
            return json.loads(stdout)
        except json.JSONDecodeError as e:
            analysis_logger.warning("Bandit stdout was not valid JSON: %s. Raw: %s", str(e), stdout)
            return {"results": []}

    def run_sync(self, file_path: str) -> Dict[str, Any]:
        """Runs Bandit synchronously via subprocess."""
        if not self.validate(file_path):
            raise ValidationException(f"File {file_path} is invalid for Bandit analysis.")

        args = self._compile_args(file_path)
        analysis_logger.info("Executing Bandit sync command: %s", " ".join(args))

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            parsed = self._parse_raw_stdout(result.stdout)
            return parsed
        except subprocess.TimeoutExpired as e:
            analysis_logger.error("Bandit execution timed out for file %s.", file_path)
            return {"results": [], "error": "Timeout expired."}
        except Exception as e:
            analysis_logger.error("Failed running Bandit checker tool: %s", str(e))
            return {"results": [], "error": str(e)}

    async def run_async(self, file_path: str) -> Dict[str, Any]:
        """Runs Bandit asynchronously via asyncio subprocess."""
        if not self.validate(file_path):
            raise ValidationException(f"File {file_path} is invalid for Bandit analysis.")

        args = self._compile_args(file_path)
        analysis_logger.info("Executing Bandit async command: %s", " ".join(args))

        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout_seconds
                )
                stdout = stdout_bytes.decode("utf-8", errors="ignore")
                parsed = self._parse_raw_stdout(stdout)
                return parsed
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
                analysis_logger.error("Bandit async execution timed out for file %s.", file_path)
                return {"results": [], "error": "Timeout expired."}
        except Exception as e:
            analysis_logger.error("Failed executing Bandit async checker: %s", str(e))
            return {"results": [], "error": str(e)}

    def normalize(self, raw_output: Dict[str, Any], file_path: str) -> List[NormalizedFinding]:
        """Normalizes Bandit JSON logs into standard NormalizedFinding objects."""
        findings = []
        raw_list = raw_output.get("results", [])
        for item in raw_list:
            raw_severity = item.get("issue_severity", "LOW")
            severity = SeverityMapper.map_bandit(raw_severity)
            line = item.get("line_number", 1)
            test_id = item.get("test_id", "unknown")
            test_name = item.get("test_name", "")
            rule = f"{test_id} ({test_name})" if test_name else test_id
            description = item.get("issue_text", "Bandit check warning.")
            
            more_info = item.get("more_info", "")
            rec = f"Review security constraints to address Bandit issue. Avoid unsafe programming constructs."
            if more_info:
                rec += f" Refer to documentation at: {more_info}"

            findings.append(
                NormalizedFinding(
                    analyzer="bandit",
                    category="security",
                    severity=severity,
                    rule=rule,
                    description=description,
                    recommendation=rec,
                    file_path=os.path.basename(file_path),
                    function_name=None,
                    line_number=line,
                    confidence=item.get("issue_confidence", "medium").lower()
                )
            )
        return findings
