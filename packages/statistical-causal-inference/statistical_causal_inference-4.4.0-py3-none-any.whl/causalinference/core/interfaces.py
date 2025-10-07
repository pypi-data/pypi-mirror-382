"""
Core interfaces for CausalAttribution components.

This module defines the base interfaces that all CausalAttribution components should implement
to ensure consistency and enable dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any, Union
import pandas as pd
from dataclasses import dataclass


@dataclass
class CausalEffect:
    """Standard result format for causal effect estimation."""
    treatment: str
    outcome: str
    effect_estimate: float
    std_error: float
    confidence_interval: Tuple[float, float]
    p_value: float
    method: str
    interpretation: str
    robustness_score: float = 0.0


class CausalDiscoveryInterface(ABC):
    """Interface for causal discovery methods."""
    
    @abstractmethod
    def discover_causal_structure(self, 
                                data: pd.DataFrame,
                                variables: Dict[str, str],
                                domain_context: str = "") -> Any:
        """Discover causal relationships in data."""
        pass


class CausalInferenceInterface(ABC):
    """Interface for causal effect estimation methods."""
    
    @abstractmethod
    async def estimate_effect(self, 
                            data: pd.DataFrame,
                            treatment: str,
                            outcome: str,
                            covariates: List[str] = None,
                            **kwargs) -> CausalEffect:
        """Estimate causal effect between treatment and outcome."""
        pass


class DoOperatorInterface(ABC):
    """Interface for do-operator implementations."""
    
    @abstractmethod
    async def estimate_effect(self, 
                            data: pd.DataFrame,
                            treatment: str,
                            outcome: str,
                            **kwargs) -> CausalEffect:
        """Estimate effect using do-calculus."""
        pass
    
    @abstractmethod
    def intervene(self, interventions: Dict[str, str]) -> str:
        """Perform interventions on variables."""
        pass


class CounterfactualEngineInterface(ABC):
    """Interface for counterfactual generation."""
    
    @abstractmethod
    async def generate_counterfactuals(self, 
                                     data: pd.DataFrame,
                                     intervention: Dict[str, Any],
                                     **kwargs) -> Dict[str, Any]:
        """Generate counterfactual scenarios."""
        pass


class LLMClientInterface(ABC):
    """Interface for LLM client implementations."""
    
    @abstractmethod
    async def chat(self, 
                   prompt: str,
                   temperature: float = 0.7,
                   max_tokens: Optional[int] = None,
                   **kwargs) -> str:
        """Send chat completion request to LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM client is available and configured."""
        pass


class DataValidatorInterface(ABC):
    """Interface for data validation."""
    
    @abstractmethod
    def validate_dataset(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate dataset for causal analysis."""
        pass
    
    @abstractmethod
    def validate_variables(self, 
                          data: pd.DataFrame,
                          treatment: str,
                          outcome: str,
                          covariates: List[str] = None) -> Dict[str, Any]:
        """Validate specific variables for analysis."""
        pass


# Factory interface for dependency injection
class ComponentFactory(ABC):
    """Factory interface for creating CausalAttribution components."""
    
    @abstractmethod
    def create_discovery_engine(self, **kwargs) -> CausalDiscoveryInterface:
        """Create causal discovery engine."""
        pass
    
    @abstractmethod
    def create_inference_engine(self, **kwargs) -> CausalInferenceInterface:
        """Create causal inference engine."""
        pass
    
    @abstractmethod
    def create_do_operator(self, **kwargs) -> DoOperatorInterface:
        """Create do-operator."""
        pass
    
    @abstractmethod
    def create_counterfactual_engine(self, **kwargs) -> CounterfactualEngineInterface:
        """Create counterfactual engine."""
        pass
    
    @abstractmethod
    def create_llm_client(self, provider: str, model: str, **kwargs) -> LLMClientInterface:
        """Create LLM client."""
        pass