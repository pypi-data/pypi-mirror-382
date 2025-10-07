"""
Factory implementation for creating CausalAttribution components with dependency injection.

This module provides concrete implementations of the ComponentFactory interface
for creating properly configured CausalAttribution components.
"""

from typing import Dict, Any, Optional
from .interfaces import (
    ComponentFactory,
    CausalDiscoveryInterface,
    CausalInferenceInterface, 
    DoOperatorInterface,
    CounterfactualEngineInterface,
    LLMClientInterface
)
from .utils.logging import get_logger
from .exceptions import CausalAttributionError, ConfigurationError, DependencyError


class CausalAttributionFactory(ComponentFactory):
    """Default factory for creating CausalAttribution components."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize factory with configuration.
        
        Args:
            config: Configuration dictionary for component settings
        """
        self.config = config or {}
        self.logger = get_logger("causallm.factory", level="INFO")
        self._component_cache = {}
        
    def create_discovery_engine(self, **kwargs) -> CausalDiscoveryInterface:
        """Create causal discovery engine."""
        try:
            from .enhanced_causal_discovery import EnhancedCausalDiscovery
            
            # Get configuration
            llm_client = kwargs.get('llm_client')
            significance_level = kwargs.get('significance_level', 0.05)
            
            # Create and cache component
            cache_key = f"discovery_{significance_level}_{id(llm_client)}"
            if cache_key not in self._component_cache:
                self._component_cache[cache_key] = EnhancedCausalDiscovery(
                    llm_client=llm_client,
                    significance_level=significance_level
                )
                self.logger.info(f"Created new discovery engine with significance_level={significance_level}")
            
            return self._component_cache[cache_key]
            
        except ImportError as e:
            error = DependencyError(
                "Failed to create discovery engine due to missing dependencies",
                missing_dependencies=["enhanced_causal_discovery"],
                cause=e
            )
            self.logger.error(error.message)
            raise error
    
    def create_inference_engine(self, **kwargs) -> CausalInferenceInterface:
        """Create causal inference engine."""
        try:
            from .statistical_inference import StatisticalCausalInference
            
            significance_level = kwargs.get('significance_level', 0.05)
            
            cache_key = f"inference_{significance_level}"
            if cache_key not in self._component_cache:
                self._component_cache[cache_key] = StatisticalCausalInference(
                    significance_level=significance_level
                )
                self.logger.info(f"Created new inference engine with significance_level={significance_level}")
            
            return self._component_cache[cache_key]
            
        except ImportError as e:
            error = DependencyError(
                "Failed to create inference engine due to missing dependencies",
                missing_dependencies=["statistical_inference"],
                cause=e
            )
            self.logger.error(error.message)
            raise error
    
    def create_do_operator(self, **kwargs) -> DoOperatorInterface:
        """Create do-operator."""
        try:
            from .do_operator import DoOperatorSimulator
            
            base_context = kwargs.get('base_context', "")
            variables = kwargs.get('variables', {})
            
            # Don't cache do-operators as they may have different contexts
            do_operator = DoOperatorSimulator(
                base_context=base_context,
                variables=variables
            )
            
            self.logger.info(f"Created new do-operator with {len(variables)} variables")
            return do_operator
            
        except ImportError as e:
            error = DependencyError(
                "Failed to create do-operator due to missing dependencies",
                missing_dependencies=["do_operator"],
                cause=e
            )
            self.logger.error(error.message)
            raise error
    
    def create_counterfactual_engine(self, **kwargs) -> CounterfactualEngineInterface:
        """Create counterfactual engine."""
        try:
            from .counterfactual_engine import CounterfactualEngine
            
            llm_client = kwargs.get('llm_client')
            
            cache_key = f"counterfactual_{id(llm_client)}"
            if cache_key not in self._component_cache:
                self._component_cache[cache_key] = CounterfactualEngine(llm_client)
                self.logger.info("Created new counterfactual engine")
            
            return self._component_cache[cache_key]
            
        except ImportError as e:
            error = DependencyError(
                "Failed to create counterfactual engine due to missing dependencies",
                missing_dependencies=["counterfactual_engine"],
                cause=e
            )
            self.logger.error(error.message)
            raise error
    
    def create_llm_client(self, provider: str, model: str, **kwargs) -> LLMClientInterface:
        """Create LLM client."""
        try:
            from .llm_client import get_llm_client
            
            cache_key = f"llm_{provider}_{model}"
            if cache_key not in self._component_cache:
                client = get_llm_client(provider, model, **kwargs)
                
                # Wrap in interface adapter if needed
                if not isinstance(client, LLMClientInterface):
                    client = LLMClientAdapter(client)
                    
                self._component_cache[cache_key] = client
                self.logger.info(f"Created new LLM client: {provider}/{model}")
            
            return self._component_cache[cache_key]
            
        except Exception as e:
            error = ConfigurationError(
                f"Failed to create LLM client {provider}/{model}",
                context={"provider": provider, "model": model},
                cause=e
            )
            self.logger.error(error.message)
            raise error
    
    def clear_cache(self):
        """Clear component cache."""
        self._component_cache.clear()
        self.logger.info("Component cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached components."""
        return {
            "cached_components": len(self._component_cache),
            "cache_keys": list(self._component_cache.keys())
        }


class LLMClientAdapter(LLMClientInterface):
    """Adapter to wrap existing LLM clients with the interface."""
    
    def __init__(self, client):
        self.client = client
        self.logger = get_logger("causallm.llm_adapter", level="INFO")
    
    async def chat(self, 
                   prompt: str,
                   temperature: float = 0.7,
                   max_tokens: Optional[int] = None,
                   **kwargs) -> str:
        """Send chat completion request to LLM."""
        try:
            # Try different method names that might exist
            if hasattr(self.client, 'chat'):
                return await self.client.chat(prompt, temperature=temperature, max_tokens=max_tokens, **kwargs)
            elif hasattr(self.client, 'complete'):
                return await self.client.complete(prompt, temperature=temperature, max_tokens=max_tokens, **kwargs)
            elif hasattr(self.client, 'generate'):
                return await self.client.generate(prompt, temperature=temperature, max_tokens=max_tokens, **kwargs)
            else:
                # Fallback for clients with different interfaces
                return await self.client(prompt, **kwargs)
                
        except Exception as e:
            self.logger.error(f"LLM client call failed: {e}")
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if LLM client is available and configured."""
        try:
            return self.client is not None and (
                hasattr(self.client, 'chat') or
                hasattr(self.client, 'complete') or
                hasattr(self.client, 'generate') or
                callable(self.client)
            )
        except Exception:
            return False


# Global factory instance
_default_factory = None

def get_default_factory() -> CausalAttributionFactory:
    """Get the default factory instance."""
    global _default_factory
    if _default_factory is None:
        _default_factory = CausalAttributionFactory()
    return _default_factory

def set_default_factory(factory: ComponentFactory):
    """Set a custom default factory."""
    global _default_factory
    _default_factory = factory