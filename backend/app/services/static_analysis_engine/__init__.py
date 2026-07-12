from app.services.static_analysis_engine.config import static_config
from app.services.static_analysis_engine.models import StaticAnalysisReport, NormalizedFinding, NormalizedMetrics
from app.services.static_analysis_engine.interface import BaseAnalyzer
from app.services.static_analysis_engine.registry import analyzer_registry
from app.services.static_analysis_engine.pylint_adapter import PylintAdapter
from app.services.static_analysis_engine.bandit_adapter import BanditAdapter
from app.services.static_analysis_engine.radon_adapter import RadonAdapter
from app.services.static_analysis_engine.orchestrator import StaticAnalysisOrchestrator

# Automatically register analyzers in registry on package import
analyzer_registry.register("pylint", PylintAdapter)
analyzer_registry.register("bandit", BanditAdapter)
analyzer_registry.register("radon", RadonAdapter)

__all__ = [
    "static_config",
    "StaticAnalysisReport",
    "NormalizedFinding",
    "NormalizedMetrics",
    "BaseAnalyzer",
    "analyzer_registry",
    "PylintAdapter",
    "BanditAdapter",
    "RadonAdapter",
    "StaticAnalysisOrchestrator"
]
