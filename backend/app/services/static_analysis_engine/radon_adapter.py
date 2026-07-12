import asyncio
import json
import os
import sys
import subprocess
from typing import Dict, Any, List
from app.services.static_analysis_engine.interface import BaseAnalyzer
from app.services.static_analysis_engine.models import NormalizedFinding, NormalizedMetrics
from app.core.exceptions import ValidationException
from app.core.logging import analysis_logger


class RadonAdapter(BaseAnalyzer):
    """Adapter programmatically executing Radon programmatically to collect code complexities and LOC metrics."""

    def validate(self, file_path: str) -> bool:
        """Validates that the file exists and has a .py extension."""
        if not os.path.exists(file_path):
            return False
        return file_path.endswith(".py")

    def _compile_args(self, tool_subcommand: str, file_path: str) -> List[str]:
        """Assembles CLI arguments array for specific radon subcommands."""
        return [sys.executable, "-m", "radon", tool_subcommand, "-j", file_path]

    def _parse_raw_stdout(self, stdout: str) -> Dict[str, Any]:
        """Safely parses stdout JSON payload."""
        if not stdout.strip():
            return {}
        try:
            return json.loads(stdout)
        except json.JSONDecodeError as e:
            analysis_logger.warning("Radon stdout was not valid JSON: %s. Raw: %s", str(e), stdout)
            return {}

    def _find_matching_key(self, data_dict: Dict[str, Any], file_path: str) -> str:
        """Finds matching dictionary key by normalizing slash differences on Windows/Linux."""
        if not data_dict:
            return file_path
        normalized_target = os.path.normpath(file_path).replace("\\", "/").lower().strip()
        for k in data_dict.keys():
            normalized_k = os.path.normpath(k).replace("\\", "/").lower().strip()
            if normalized_target in normalized_k or normalized_k in normalized_target:
                return k
        return file_path

    def _run_subcommand_sync(self, subcommand: str, file_path: str) -> Dict[str, Any]:
        """Invokes a radon subcommand synchronously."""
        args = self._compile_args(subcommand, file_path)
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=self.timeout_seconds)
            return self._parse_raw_stdout(result.stdout)
        except Exception as e:
            analysis_logger.error("Failed running Radon sync subcommand '%s': %s", subcommand, str(e))
            return {}

    async def _run_subcommand_async(self, subcommand: str, file_path: str) -> Dict[str, Any]:
        """Invokes a radon subcommand asynchronously."""
        args = self._compile_args(subcommand, file_path)
        try:
            process = await asyncio.create_subprocess_exec(
                *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout_bytes, _ = await asyncio.wait_for(process.communicate(), timeout=self.timeout_seconds)
            return self._parse_raw_stdout(stdout_bytes.decode("utf-8", errors="ignore"))
        except Exception as e:
            analysis_logger.error("Failed executing Radon async subcommand '%s': %s", subcommand, str(e))
            return {}

    def run_sync(self, file_path: str) -> Dict[str, Any]:
        """Runs Radon's CC, MI, and Raw metrics synchronously."""
        if not self.validate(file_path):
            raise ValidationException(f"File {file_path} is invalid for Radon analysis.")

        cc = self._run_subcommand_sync("cc", file_path)
        mi = self._run_subcommand_sync("mi", file_path)
        raw = self._run_subcommand_sync("raw", file_path)
        return {"cc": cc, "mi": mi, "raw": raw}

    async def run_async(self, file_path: str) -> Dict[str, Any]:
        """Runs Radon's CC, MI, and Raw metrics asynchronously in parallel."""
        if not self.validate(file_path):
            raise ValidationException(f"File {file_path} is invalid for Radon analysis.")

        cc_task, mi_task, raw_task = await asyncio.gather(
            self._run_subcommand_async("cc", file_path),
            self._run_subcommand_async("mi", file_path),
            self._run_subcommand_async("raw", file_path),
        )
        return {"cc": cc_task, "mi": mi_task, "raw": raw_task}

    def normalize(self, raw_output: Dict[str, Any], file_path: str) -> List[NormalizedFinding]:
        """Generates findings for highly complex code blocks (Complexity > 10)."""
        findings = []
        cc_data = raw_output.get("cc", {})
        key = self._find_matching_key(cc_data, file_path)
        items = cc_data.get(key, [])
        if not isinstance(items, list):
            items = []

        for item in items:
            complexity = item.get("complexity", 0)
            if complexity > 10:
                name = item.get("name", "")
                item_type = item.get("type", "function")
                line = item.get("lineno", 1)

                findings.append(
                    NormalizedFinding(
                        analyzer="radon",
                        category="complexity",
                        severity="high" if complexity > 20 else "medium",
                        rule="high-complexity",
                        description=f"High cyclomatic complexity ({complexity}) detected in {item_type} '{name}'.",
                        recommendation=f"Refactor the logic of '{name}' to decrease complexity by decomposing operations into smaller sub-methods.",
                        file_path=os.path.basename(file_path),
                        function_name=name if item_type == "function" else None,
                        line_number=line,
                        confidence="high",
                    )
                )
        return findings

    def normalize_metrics(self, raw_output: Dict[str, Any], file_path: str) -> NormalizedMetrics:
        """Parses combined Radon reports into standard NormalizedMetrics models."""
        cc_data = raw_output.get("cc", {})
        mi_data = raw_output.get("mi", {})
        raw_data = raw_output.get("raw", {})

        cc_key = self._find_matching_key(cc_data, file_path)
        cc_items = cc_data.get(cc_key, [])
        if not isinstance(cc_items, list):
            cc_items = []

        max_cc = 0
        funcs = 0
        classes = 0
        for item in cc_items:
            comp = item.get("complexity", 0)
            if comp > max_cc:
                max_cc = comp
            item_type = item.get("type", "function")
            if item_type in {"function", "method"}:
                funcs += 1
            elif item_type == "class":
                classes += 1

        mi_key = self._find_matching_key(mi_data, file_path)
        mi = mi_data.get(mi_key, {}).get("mi", 100.0)

        raw_key = self._find_matching_key(raw_data, file_path)
        loc = raw_data.get(raw_key, {}).get("loc", 0)

        return NormalizedMetrics(
            cyclomatic_complexity=max_cc or 1,
            maintainability_index=float(mi),
            loc=int(loc),
            functions_count=funcs,
            classes_count=classes,
        )
