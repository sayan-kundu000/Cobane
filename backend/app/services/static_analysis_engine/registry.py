from typing import Dict, Type, List
from app.services.static_analysis_engine.interface import BaseAnalyzer

class AnalyzerRegistry:
    """Manages static analyzer tool registrations dynamically."""

    def __init__(self):
        self._analyzers: Dict[str, Type[BaseAnalyzer]] = {}

    def register(self, name: str, analyzer_cls: Type[BaseAnalyzer]) -> None:
        """Registers an analyzer class under a string name key."""
        self._analyzers[name.lower().strip()] = analyzer_cls

    def get(self, name: str) -> Type[BaseAnalyzer]:
        """Retrieves the registered analyzer class corresponding to the key name."""
        key = name.lower().strip()
        if key not in self._analyzers:
            raise KeyError(f"Analyzer '{name}' is not registered in the system registry.")
        return self._analyzers[key]

    def list_registered(self) -> List[str]:
        """Lists all registered static analyzer key names."""
        return list(self._analyzers.keys())

analyzer_registry = AnalyzerRegistry()
