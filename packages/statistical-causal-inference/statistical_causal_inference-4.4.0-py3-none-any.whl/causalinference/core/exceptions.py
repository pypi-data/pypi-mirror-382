"""
Custom exceptions for CausalAttribution.

This module defines a hierarchy of custom exceptions for better error handling
and debugging throughout the CausalAttribution library.
"""

from typing import Optional, Dict, Any, List
import traceback


class CausalAttributionError(Exception):
    """Base exception for all CausalAttribution errors."""
    
    def __init__(self, 
                 message: str, 
                 error_code: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None,
                 cause: Optional[Exception] = None):
        """
        Initialize CausalAttribution error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            context: Additional context information
            cause: The underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.cause = cause
        
        # Capture stack trace
        self.stack_trace = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
            "stack_trace": self.stack_trace
        }


class DataValidationError(CausalAttributionError):
    """Raised when input data validation fails."""
    
    def __init__(self, message: str, 
                 data_issues: Optional[List[str]] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.data_issues = data_issues or []


class VariableError(CausalAttributionError):
    """Raised when there are issues with specified variables."""
    
    def __init__(self, message: str,
                 missing_variables: Optional[List[str]] = None,
                 invalid_variables: Optional[List[str]] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.missing_variables = missing_variables or []
        self.invalid_variables = invalid_variables or []


class CausalDiscoveryError(CausalAttributionError):
    """Raised when causal discovery fails."""
    
    def __init__(self, message: str,
                 method: Optional[str] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.method = method


class StatisticalInferenceError(CausalAttributionError):
    """Raised when statistical inference fails."""
    
    def __init__(self, message: str,
                 method: Optional[str] = None,
                 convergence_issues: bool = False,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.method = method
        self.convergence_issues = convergence_issues


class LLMClientError(CausalAttributionError):
    """Raised when LLM client operations fail."""
    
    def __init__(self, message: str,
                 provider: Optional[str] = None,
                 model: Optional[str] = None,
                 api_error: Optional[str] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.provider = provider
        self.model = model
        self.api_error = api_error


class ConfigurationError(CausalAttributionError):
    """Raised when there are configuration issues."""
    
    def __init__(self, message: str,
                 missing_config: Optional[List[str]] = None,
                 invalid_config: Optional[Dict[str, str]] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.missing_config = missing_config or []
        self.invalid_config = invalid_config or {}


class InsufficientDataError(CausalAttributionError):
    """Raised when there is insufficient data for analysis."""
    
    def __init__(self, message: str,
                 required_samples: Optional[int] = None,
                 actual_samples: Optional[int] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.required_samples = required_samples
        self.actual_samples = actual_samples


class AssumptionViolationError(CausalAttributionError):
    """Raised when causal inference assumptions are violated."""
    
    def __init__(self, message: str,
                 violated_assumptions: Optional[List[str]] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.violated_assumptions = violated_assumptions or []


class ComputationError(CausalAttributionError):
    """Raised when computational operations fail."""
    
    def __init__(self, message: str,
                 operation: Optional[str] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.operation = operation


class DependencyError(CausalAttributionError):
    """Raised when required dependencies are missing or incompatible."""
    
    def __init__(self, message: str,
                 missing_dependencies: Optional[List[str]] = None,
                 version_conflicts: Optional[Dict[str, str]] = None,
                 **kwargs):
        super().__init__(message, **kwargs)
        self.missing_dependencies = missing_dependencies or []
        self.version_conflicts = version_conflicts or {}


# Error handling utilities

class ErrorHandler:
    """Utility class for consistent error handling across CausalAttribution."""
    
    @staticmethod
    def wrap_exception(func, exception_class=CausalAttributionError, **error_kwargs):
        """
        Decorator to wrap functions and convert generic exceptions to CausalAttribution exceptions.
        
        Args:
            func: Function to wrap
            exception_class: CausalAttribution exception class to use
            **error_kwargs: Additional arguments for the exception
            
        Returns:
            Wrapped function
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except CausalAttributionError:
                # Re-raise CausalAttribution exceptions as-is
                raise
            except Exception as e:
                # Convert generic exceptions to CausalAttribution exceptions
                error_message = f"Error in {func.__name__}: {str(e)}"
                raise exception_class(
                    message=error_message,
                    cause=e,
                    context={"function": func.__name__},
                    **error_kwargs
                )
        
        return wrapper
    
    @staticmethod
    def validate_data(data, required_columns=None, min_rows=1):
        """
        Validate input data and raise appropriate exceptions.
        
        Args:
            data: Input data to validate
            required_columns: List of required column names
            min_rows: Minimum number of rows required
            
        Raises:
            DataValidationError: If validation fails
        """
        issues = []
        
        if data is None:
            raise DataValidationError("Input data cannot be None")
        
        if hasattr(data, 'empty') and data.empty:
            raise DataValidationError("Input data cannot be empty")
        
        if hasattr(data, '__len__') and len(data) < min_rows:
            raise InsufficientDataError(
                f"Insufficient data: {len(data)} rows, minimum {min_rows} required",
                required_samples=min_rows,
                actual_samples=len(data)
            )
        
        if required_columns and hasattr(data, 'columns'):
            missing_cols = [col for col in required_columns if col not in data.columns]
            if missing_cols:
                raise VariableError(
                    f"Missing required columns: {missing_cols}",
                    missing_variables=missing_cols
                )
        
        # Check for common data issues
        if hasattr(data, 'isnull'):
            null_percentage = data.isnull().sum().sum() / (len(data) * len(data.columns))
            if null_percentage > 0.5:
                issues.append(f"High percentage of missing values: {null_percentage:.1%}")
        
        if issues:
            raise DataValidationError(
                "Data quality issues detected",
                data_issues=issues
            )
    
    @staticmethod
    def require_dependencies(dependencies: List[str]):
        """
        Check if required dependencies are available.
        
        Args:
            dependencies: List of module names to check
            
        Raises:
            DependencyError: If dependencies are missing
        """
        missing = []
        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        
        if missing:
            raise DependencyError(
                f"Missing required dependencies: {missing}",
                missing_dependencies=missing
            )


def handle_errors(exception_class=CausalAttributionError, **error_kwargs):
    """
    Decorator for automatic error handling in CausalAttribution methods.
    
    Usage:
        @handle_errors(DataValidationError, context={"operation": "validation"})
        def validate_input(self, data):
            # Method implementation
    """
    def decorator(func):
        return ErrorHandler.wrap_exception(func, exception_class, **error_kwargs)
    return decorator