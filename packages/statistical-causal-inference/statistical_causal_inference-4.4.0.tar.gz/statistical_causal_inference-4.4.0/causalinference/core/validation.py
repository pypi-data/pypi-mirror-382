"""
Data validation utilities with proper error handling.

This module provides comprehensive validation functions for causal analysis
with detailed error reporting and recovery suggestions.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from .exceptions import (
    DataValidationError, VariableError, InsufficientDataError,
    AssumptionViolationError, ErrorHandler
)
from .utils.logging import get_logger


class DataValidator:
    """Comprehensive data validation for causal analysis."""
    
    def __init__(self):
        self.logger = get_logger("causallm.validation", level="INFO")
    
    def validate_causal_dataset(self, 
                               data: pd.DataFrame,
                               treatment: str,
                               outcome: str,
                               covariates: Optional[List[str]] = None,
                               min_samples: int = 30) -> Dict[str, Any]:
        """
        Comprehensive validation for causal analysis datasets.
        
        Args:
            data: Input dataset
            treatment: Treatment variable name
            outcome: Outcome variable name  
            covariates: List of covariate names
            min_samples: Minimum required sample size
            
        Returns:
            Validation results dictionary
            
        Raises:
            DataValidationError: If basic validation fails
            VariableError: If variables are invalid
            InsufficientDataError: If sample size is too small
            AssumptionViolationError: If causal assumptions are violated
        """
        self.logger.info(f"Validating causal dataset with {len(data)} samples")
        
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "issues": [],
            "recommendations": [],
            "data_characteristics": {}
        }
        
        try:
            # 1. Basic data validation
            self._validate_basic_structure(data)
            
            # 2. Variable validation
            all_vars = [treatment, outcome] + (covariates or [])
            self._validate_variables(data, all_vars)
            
            # 3. Sample size validation
            self._validate_sample_size(data, min_samples)
            
            # 4. Treatment variable validation
            treatment_info = self._validate_treatment_variable(data, treatment)
            validation_results["data_characteristics"]["treatment"] = treatment_info
            
            # 5. Outcome variable validation
            outcome_info = self._validate_outcome_variable(data, outcome)
            validation_results["data_characteristics"]["outcome"] = outcome_info
            
            # 6. Covariate validation
            if covariates:
                covariate_info = self._validate_covariates(data, covariates)
                validation_results["data_characteristics"]["covariates"] = covariate_info
            
            # 7. Missing data analysis
            missing_info = self._analyze_missing_data(data, all_vars)
            validation_results["data_characteristics"]["missing_data"] = missing_info
            
            # 8. Check for common causal inference issues
            causal_issues = self._check_causal_assumptions(data, treatment, outcome, covariates)
            validation_results["causal_assumptions"] = causal_issues
            
            self.logger.info("Dataset validation completed successfully")
            
        except (DataValidationError, VariableError, InsufficientDataError, AssumptionViolationError) as e:
            validation_results["is_valid"] = False
            validation_results["error"] = e.to_dict()
            self.logger.error(f"Dataset validation failed: {e.message}")
            raise
        
        return validation_results
    
    def _validate_basic_structure(self, data: pd.DataFrame):
        """Validate basic data structure."""
        if data is None:
            raise DataValidationError("Dataset cannot be None")
        
        if not isinstance(data, pd.DataFrame):
            raise DataValidationError(
                f"Expected pandas DataFrame, got {type(data).__name__}",
                context={"data_type": type(data).__name__}
            )
        
        if data.empty:
            raise DataValidationError("Dataset cannot be empty")
        
        if len(data.columns) == 0:
            raise DataValidationError("Dataset must have at least one column")
    
    def _validate_variables(self, data: pd.DataFrame, variables: List[str]):
        """Validate that all required variables exist."""
        missing_vars = [var for var in variables if var not in data.columns]
        
        if missing_vars:
            available_vars = list(data.columns)
            # Suggest similar variable names
            suggestions = []
            for missing_var in missing_vars:
                similar = [col for col in available_vars 
                          if missing_var.lower() in col.lower() or col.lower() in missing_var.lower()]
                if similar:
                    suggestions.extend(similar)
            
            raise VariableError(
                f"Missing required variables: {missing_vars}",
                missing_variables=missing_vars,
                context={
                    "available_variables": available_vars,
                    "suggested_variables": suggestions
                }
            )
    
    def _validate_sample_size(self, data: pd.DataFrame, min_samples: int):
        """Validate sample size."""
        actual_samples = len(data)
        
        if actual_samples < min_samples:
            raise InsufficientDataError(
                f"Insufficient sample size: {actual_samples} samples, minimum {min_samples} required",
                required_samples=min_samples,
                actual_samples=actual_samples,
                context={
                    "recommendation": f"Collect at least {min_samples - actual_samples} more samples"
                }
            )
    
    def _validate_treatment_variable(self, data: pd.DataFrame, treatment: str) -> Dict[str, Any]:
        """Validate treatment variable characteristics."""
        treatment_data = data[treatment]
        
        info = {
            "name": treatment,
            "dtype": str(treatment_data.dtype),
            "missing_count": treatment_data.isnull().sum(),
            "unique_values": treatment_data.nunique(),
            "is_binary": treatment_data.nunique() == 2
        }
        
        # Check for issues
        if info["missing_count"] > len(data) * 0.1:
            raise VariableError(
                f"Treatment variable '{treatment}' has too many missing values ({info['missing_count']}/{len(data)})",
                invalid_variables=[treatment],
                context={"missing_percentage": info["missing_count"] / len(data)}
            )
        
        if info["unique_values"] == 1:
            raise VariableError(
                f"Treatment variable '{treatment}' has no variation (all values are the same)",
                invalid_variables=[treatment]
            )
        
        # Add distribution info for different types
        if treatment_data.dtype in ['object', 'category']:
            info["value_counts"] = treatment_data.value_counts().to_dict()
        else:
            info["statistics"] = {
                "mean": float(treatment_data.mean()),
                "std": float(treatment_data.std()),
                "min": float(treatment_data.min()),
                "max": float(treatment_data.max())
            }
        
        return info
    
    def _validate_outcome_variable(self, data: pd.DataFrame, outcome: str) -> Dict[str, Any]:
        """Validate outcome variable characteristics."""
        outcome_data = data[outcome]
        
        info = {
            "name": outcome,
            "dtype": str(outcome_data.dtype),
            "missing_count": outcome_data.isnull().sum(),
            "unique_values": outcome_data.nunique()
        }
        
        # Check for issues
        if info["missing_count"] > len(data) * 0.1:
            raise VariableError(
                f"Outcome variable '{outcome}' has too many missing values ({info['missing_count']}/{len(data)})",
                invalid_variables=[outcome]
            )
        
        if info["unique_values"] == 1:
            raise VariableError(
                f"Outcome variable '{outcome}' has no variation (all values are the same)",
                invalid_variables=[outcome]
            )
        
        # Add statistics for numeric outcomes
        if pd.api.types.is_numeric_dtype(outcome_data):
            info["statistics"] = {
                "mean": float(outcome_data.mean()),
                "std": float(outcome_data.std()),
                "min": float(outcome_data.min()),
                "max": float(outcome_data.max()),
                "skewness": float(outcome_data.skew()) if len(outcome_data.dropna()) > 0 else None
            }
        
        return info
    
    def _validate_covariates(self, data: pd.DataFrame, covariates: List[str]) -> Dict[str, Any]:
        """Validate covariate variables."""
        covariate_info = {}
        
        for covar in covariates:
            covar_data = data[covar]
            
            info = {
                "name": covar,
                "dtype": str(covar_data.dtype),
                "missing_count": covar_data.isnull().sum(),
                "unique_values": covar_data.nunique()
            }
            
            # Check for high collinearity (simplified)
            if pd.api.types.is_numeric_dtype(covar_data):
                correlations = data[covariates].corr()[covar].abs().sort_values(ascending=False)
                high_corr = correlations[correlations > 0.9].drop(covar, errors='ignore')
                if len(high_corr) > 0:
                    info["high_correlation_with"] = high_corr.to_dict()
            
            covariate_info[covar] = info
        
        return covariate_info
    
    def _analyze_missing_data(self, data: pd.DataFrame, variables: List[str]) -> Dict[str, Any]:
        """Analyze missing data patterns."""
        missing_info = {
            "total_missing": data[variables].isnull().sum().sum(),
            "missing_by_variable": data[variables].isnull().sum().to_dict(),
            "complete_cases": len(data.dropna(subset=variables)),
            "missing_patterns": {}
        }
        
        # Check for systematic missing patterns
        missing_percentage = missing_info["total_missing"] / (len(data) * len(variables))
        if missing_percentage > 0.05:  # More than 5% missing
            missing_info["warning"] = f"High percentage of missing data: {missing_percentage:.1%}"
        
        return missing_info
    
    def _check_causal_assumptions(self, 
                                 data: pd.DataFrame,
                                 treatment: str, 
                                 outcome: str,
                                 covariates: Optional[List[str]]) -> Dict[str, Any]:
        """Check common causal inference assumptions."""
        assumptions = {
            "overlap": self._check_overlap(data, treatment, covariates),
            "balance": self._check_balance(data, treatment, covariates) if covariates else {},
            "linearity": self._check_linearity(data, treatment, outcome)
        }
        
        violated_assumptions = []
        for assumption, result in assumptions.items():
            if result.get("violated", False):
                violated_assumptions.append(assumption)
        
        if violated_assumptions:
            assumptions["violations"] = violated_assumptions
            assumptions["severity"] = "high" if len(violated_assumptions) > 1 else "medium"
        
        return assumptions
    
    def _check_overlap(self, data: pd.DataFrame, treatment: str, covariates: Optional[List[str]]) -> Dict[str, Any]:
        """Check for overlap/common support."""
        # Simplified overlap check
        if data[treatment].nunique() == 2:
            treatment_groups = data.groupby(treatment).size()
            min_group_size = treatment_groups.min()
            overlap_ratio = min_group_size / len(data)
            
            return {
                "sufficient_overlap": overlap_ratio >= 0.1,  # At least 10% in each group
                "overlap_ratio": float(overlap_ratio),
                "group_sizes": treatment_groups.to_dict(),
                "violated": overlap_ratio < 0.05  # Less than 5% is problematic
            }
        
        return {"message": "Overlap check only applicable for binary treatments"}
    
    def _check_balance(self, data: pd.DataFrame, treatment: str, covariates: List[str]) -> Dict[str, Any]:
        """Check covariate balance across treatment groups."""
        if data[treatment].nunique() != 2:
            return {"message": "Balance check only applicable for binary treatments"}
        
        balance_results = {}
        treatment_values = sorted(data[treatment].unique())
        
        for covar in covariates:
            if pd.api.types.is_numeric_dtype(data[covar]):
                group_means = data.groupby(treatment)[covar].mean()
                standardized_diff = abs(group_means.diff().iloc[-1]) / data[covar].std()
                
                balance_results[covar] = {
                    "standardized_difference": float(standardized_diff),
                    "imbalanced": standardized_diff > 0.25,  # Cohen's d > 0.25
                    "group_means": group_means.to_dict()
                }
        
        # Overall balance assessment
        imbalanced_vars = [var for var, result in balance_results.items() 
                          if result.get("imbalanced", False)]
        
        return {
            "variable_balance": balance_results,
            "imbalanced_variables": imbalanced_vars,
            "violated": len(imbalanced_vars) > len(covariates) * 0.3  # > 30% imbalanced
        }
    
    def _check_linearity(self, data: pd.DataFrame, treatment: str, outcome: str) -> Dict[str, Any]:
        """Check linearity assumption (simplified)."""
        if not (pd.api.types.is_numeric_dtype(data[treatment]) and 
                pd.api.types.is_numeric_dtype(data[outcome])):
            return {"message": "Linearity check only applicable for numeric variables"}
        
        try:
            correlation = data[[treatment, outcome]].corr().iloc[0, 1]
            
            # Simple linearity test using correlation
            return {
                "correlation": float(correlation),
                "appears_linear": abs(correlation) > 0.1,
                "violated": abs(correlation) < 0.05  # Very weak relationship might indicate non-linearity
            }
        except Exception:
            return {"message": "Could not assess linearity"}


# Global validator instance
validator = DataValidator()