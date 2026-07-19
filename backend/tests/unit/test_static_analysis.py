import pytest
import os
from app.services.static_analysis_engine.config import static_config
from app.services.static_analysis_engine.registry import analyzer_registry
from app.services.static_analysis_engine.models import StaticAnalysisReport
from app.services.static_analysis_engine.severity import SeverityMapper
from app.services.static_analysis_engine.pylint_adapter import PylintAdapter
from app.services.static_analysis_engine.bandit_adapter import BanditAdapter
from app.services.static_analysis_engine.radon_adapter import RadonAdapter
from app.services.static_analysis_engine.orchestrator import StaticAnalysisOrchestrator
from app.services.static_analysis import StaticAnalysisService
from app.core.exceptions import ValidationException


@pytest.fixture
def temp_stub_file():
    """Generates a temporary python stub script inside the workspace for static analysis testing."""
    path = os.path.abspath("tests/unit/stub_test_file.py")
    code = (
        "'''Module docstring placeholder.'''\n\n"
        "def check_value(val):\n"
        "    '''Checks non-none constraint.'''\n"
        "    assert val is not None\n"
        "    print('Completed value evaluation: ' + str(val))\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.mark.anyio
async def test_source_code_validation():
    orchestrator = StaticAnalysisOrchestrator()

    # 1. Non-existent file
    with pytest.raises(ValidationException, match="does not exist"):
        orchestrator.validate_source(os.path.abspath("non_existent_file.py"))

    # 2. Unsupported extension
    invalid_ext_path = os.path.abspath("tests/unit/invalid.rust")
    with open(invalid_ext_path, "w") as f:
        f.write("hello")
    try:
        with pytest.raises(ValidationException, match="Unsupported file extension"):
            orchestrator.validate_source(invalid_ext_path)
    finally:
        if os.path.exists(invalid_ext_path):
            os.remove(invalid_ext_path)

    # 3. Empty file
    empty_path = os.path.abspath("tests/unit/empty.py")
    with open(empty_path, "w") as f:
        pass
    try:
        with pytest.raises(ValidationException, match="File is empty"):
            orchestrator.validate_source(empty_path)
    finally:
        if os.path.exists(empty_path):
            os.remove(empty_path)


@pytest.mark.anyio
async def test_analyzer_registry():
    assert "pylint" in analyzer_registry.list_registered()
    assert "bandit" in analyzer_registry.list_registered()
    assert "radon" in analyzer_registry.list_registered()

    pylint_cls = analyzer_registry.get("pylint")
    assert pylint_cls == PylintAdapter

    with pytest.raises(KeyError):
        analyzer_registry.get("invalid_analyzer")


@pytest.mark.anyio
async def test_severity_mapping():
    assert SeverityMapper.map_pylint("fatal") == "critical"
    assert SeverityMapper.map_pylint("error") == "high"
    assert SeverityMapper.map_pylint("warning") == "medium"
    assert SeverityMapper.map_pylint("refactor") == "low"
    assert SeverityMapper.map_pylint("convention") == "info"

    assert SeverityMapper.map_bandit("HIGH") == "high"
    assert SeverityMapper.map_bandit("MEDIUM") == "medium"
    assert SeverityMapper.map_bandit("LOW") == "low"
    assert SeverityMapper.map_bandit("UNDEFINED") == "info"


@pytest.mark.anyio
async def test_individual_adapters_execution(temp_stub_file):
    # 1. Pylint Adapter
    pylint = PylintAdapter()
    assert pylint.validate(temp_stub_file) is True
    pylint_raw = pylint.run_sync(temp_stub_file)
    assert pylint_raw["success"] is True
    findings_pylint = pylint.normalize(pylint_raw, temp_stub_file)
    assert len(findings_pylint) >= 0
    score = PylintAdapter.calculate_score(pylint_raw.get("results", []))
    assert 0.0 <= score <= 10.0

    # 2. Bandit Adapter
    bandit = BanditAdapter()
    assert bandit.validate(temp_stub_file) is True
    bandit_raw = bandit.run_sync(temp_stub_file)
    assert "results" in bandit_raw
    findings_bandit = bandit.normalize(bandit_raw, temp_stub_file)
    # The assert statement in stub code should trigger a bandit warning (B101)
    assert len(findings_bandit) >= 1
    assert any(f.rule.startswith("B101") for f in findings_bandit)

    # 3. Radon Adapter
    radon = RadonAdapter()
    assert radon.validate(temp_stub_file) is True
    radon_raw = radon.run_sync(temp_stub_file)
    assert "cc" in radon_raw
    assert "mi" in radon_raw
    assert "raw" in radon_raw
    metrics = radon.normalize_metrics(radon_raw, temp_stub_file)
    assert metrics.loc > 0
    assert metrics.cyclomatic_complexity >= 1
    assert 0.0 <= metrics.maintainability_index <= 100.0


@pytest.mark.anyio
async def test_orchestrator_sync_and_async(temp_stub_file):
    orchestrator = StaticAnalysisOrchestrator()

    # Test sync orchestrator run
    report_sync = orchestrator.run_analysis_sync(temp_stub_file)
    assert isinstance(report_sync, StaticAnalysisReport)
    assert report_sync.metrics.loc > 0
    assert report_sync.pylint_score is not None

    # Test async orchestrator run
    report_async = await orchestrator.run_analysis_async(temp_stub_file)
    assert isinstance(report_async, StaticAnalysisReport)
    assert report_async.metrics.loc == report_sync.metrics.loc
    assert len(report_async.findings) == len(report_sync.findings)


@pytest.mark.anyio
async def test_legacy_service_wrapper(temp_stub_file):
    service = StaticAnalysisService()
    results = service.run_all(temp_stub_file)

    assert "pylint" in results
    assert "bandit" in results
    assert "radon" in results

    assert "score" in results["pylint"]
    assert "warnings" in results["pylint"]
    assert "issues" in results["bandit"]
    assert "cc" in results["radon"]
    assert results["radon"]["cc"]["loc"] > 0


@pytest.mark.anyio
async def test_non_python_file_analysis():
    path = os.path.abspath("tests/unit/stub_test_file.cpp")
    code = (
        "#include <iostream>\n"
        "int main() {\n"
        "    std::cout << \"Hello, World!\" << std::endl;\n"
        "    return 0;\n"
        "}\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        orchestrator = StaticAnalysisOrchestrator()

        # Test sync
        report_sync = orchestrator.run_analysis_sync(path)
        assert isinstance(report_sync, StaticAnalysisReport)
        assert len(report_sync.findings) == 0
        assert report_sync.metrics.loc == 0
        assert report_sync.metrics.maintainability_index == 100.0
        assert report_sync.pylint_score == 10.0
        assert report_sync.bandit_issues_count == 0

        # Test async
        report_async = await orchestrator.run_analysis_async(path)
        assert report_async.pylint_score == 10.0
        assert report_async.metrics.loc == 0

        # Test legacy wrapper
        service = StaticAnalysisService()
        results = service.run_all(path)
        assert results["pylint"]["score"] == 10.0
        assert len(results["pylint"]["warnings"]) == 0
        assert results["bandit"]["score"] == "PASS"
        assert results["radon"]["score"] == "A"
        assert results["radon"]["cc"]["loc"] == 0
    finally:
        if os.path.exists(path):
            os.remove(path)
