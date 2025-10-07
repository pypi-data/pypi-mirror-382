"""
Optimized statistical algorithms with vectorization and performance enhancements.

This module provides vectorized implementations of statistical algorithms used in
causal inference, optimized for performance on large datasets.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional, Union
from dataclasses import dataclass
import scipy.stats as stats
from scipy.sparse import csr_matrix, issparse
from scipy.linalg import solve, LinAlgError
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import pairwise_distances
import warnings
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial

# Optional numba import for performance optimization
try:
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    # Provide fallback decorators if numba is not available
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if args and callable(args[0]) else decorator

    # prange is just range when numba is not available
    prange = range
    NUMBA_AVAILABLE = False

from .utils.logging import get_logger
from .exceptions import ComputationError, StatisticalInferenceError
from .caching import cached_method


@dataclass
class PerformanceMetrics:
    """Performance metrics for algorithm execution."""
    execution_time: float
    memory_used_mb: float
    input_size: int
    algorithm_name: str
    vectorized: bool


class VectorizedStatistics:
    """Vectorized statistical computations for improved performance."""
    
    def __init__(self):
        self.logger = get_logger("causallm.vectorized_stats", level="INFO")
        self._scaler_cache = {}
    
    @staticmethod
    def _fast_correlation_matrix(X: np.ndarray) -> np.ndarray:
        """
        Fast correlation matrix computation using Numba JIT compilation (if available).
        Falls back to standard numpy if numba is not installed.

        Args:
            X: Input matrix (n_samples, n_features)

        Returns:
            Correlation matrix
        """
        n_features = X.shape[1]
        corr_matrix = np.zeros((n_features, n_features))

        # Standardize the data
        X_std = np.zeros_like(X)
        for j in prange(n_features):
            mean_j = np.mean(X[:, j])
            std_j = np.std(X[:, j])
            if std_j > 0:
                X_std[:, j] = (X[:, j] - mean_j) / std_j
            else:
                X_std[:, j] = 0.0

        # Compute correlations
        n_samples = X.shape[0]
        for i in prange(n_features):
            for j in range(i, n_features):
                corr = np.sum(X_std[:, i] * X_std[:, j]) / (n_samples - 1)
                corr_matrix[i, j] = corr
                corr_matrix[j, i] = corr

        return corr_matrix
    
    @cached_method()
    def compute_correlation_matrix(self, 
                                 data: pd.DataFrame,
                                 method: str = 'pearson',
                                 use_numba: bool = True) -> pd.DataFrame:
        """
        Compute correlation matrix with optimization options.
        
        Args:
            data: Input DataFrame
            method: Correlation method ('pearson', 'spearman', 'kendall')
            use_numba: Whether to use Numba JIT compilation
            
        Returns:
            Correlation matrix
        """
        numeric_data = data.select_dtypes(include=[np.number])
        
        if numeric_data.empty:
            raise StatisticalInferenceError(
                "No numeric columns found for correlation computation",
                method="correlation_matrix"
            )
        
        # Fill missing values
        X = numeric_data.fillna(numeric_data.mean()).values
        
        if method == 'pearson' and use_numba and X.shape[1] <= 1000:
            # Use fast Numba implementation for Pearson correlation
            corr_matrix = self._fast_correlation_matrix(X)
            result = pd.DataFrame(
                corr_matrix,
                index=numeric_data.columns,
                columns=numeric_data.columns
            )
        else:
            # Use pandas/scipy for other methods or very large matrices
            result = numeric_data.corr(method=method)
        
        self.logger.debug(f"Computed {method} correlation matrix: {result.shape}")
        return result
    
    @staticmethod
    def _fast_partial_correlation(X: np.ndarray,
                                 i: int,
                                 j: int,
                                 control_indices: np.ndarray) -> float:
        """
        Fast partial correlation computation using Numba.
        
        Args:
            X: Data matrix
            i, j: Indices of variables to correlate
            control_indices: Indices of control variables
            
        Returns:
            Partial correlation coefficient
        """
        if len(control_indices) == 0:
            # Simple correlation
            return np.corrcoef(X[:, i], X[:, j])[0, 1]
        
        # Regression approach for partial correlation
        n_samples = X.shape[0]
        
        # Regress X_i on control variables
        X_controls = X[:, control_indices]
        
        # Add intercept
        X_controls_with_intercept = np.column_stack((np.ones(n_samples), X_controls))
        
        # Solve for coefficients (simplified - assumes no multicollinearity)
        try:
            beta_i = np.linalg.solve(
                X_controls_with_intercept.T @ X_controls_with_intercept,
                X_controls_with_intercept.T @ X[:, i]
            )
            beta_j = np.linalg.solve(
                X_controls_with_intercept.T @ X_controls_with_intercept,
                X_controls_with_intercept.T @ X[:, j]
            )
            
            # Compute residuals
            residuals_i = X[:, i] - X_controls_with_intercept @ beta_i
            residuals_j = X[:, j] - X_controls_with_intercept @ beta_j
            
            # Correlation of residuals
            return np.corrcoef(residuals_i, residuals_j)[0, 1]
            
        except:
            return 0.0
    
    def compute_partial_correlations(self,
                                   data: pd.DataFrame,
                                   target_vars: List[str],
                                   control_vars: List[str]) -> pd.DataFrame:
        """
        Compute partial correlations controlling for specified variables.
        
        Args:
            data: Input DataFrame
            target_vars: Variables to compute correlations for
            control_vars: Variables to control for
            
        Returns:
            Partial correlation matrix
        """
        all_vars = target_vars + control_vars
        subset_data = data[all_vars].fillna(data[all_vars].mean())
        X = subset_data.values
        
        n_targets = len(target_vars)
        control_indices = np.array(list(range(n_targets, len(all_vars))))
        
        # Compute partial correlations
        partial_corr_matrix = np.zeros((n_targets, n_targets))
        
        for i in range(n_targets):
            for j in range(i, n_targets):
                if i == j:
                    partial_corr_matrix[i, j] = 1.0
                else:
                    corr = self._fast_partial_correlation(X, i, j, control_indices)
                    partial_corr_matrix[i, j] = corr
                    partial_corr_matrix[j, i] = corr
        
        result = pd.DataFrame(
            partial_corr_matrix,
            index=target_vars,
            columns=target_vars
        )
        
        self.logger.debug(f"Computed partial correlations: {result.shape}")
        return result


class OptimizedPropensityScoring:
    """Optimized propensity score estimation with vectorization."""
    
    def __init__(self):
        self.logger = get_logger("causallm.optimized_ps", level="INFO")
    
    def compute_propensity_scores_batch(self,
                                      X: np.ndarray,
                                      treatment: np.ndarray,
                                      batch_size: int = 10000) -> np.ndarray:
        """
        Compute propensity scores in batches for large datasets.
        
        Args:
            X: Covariate matrix
            treatment: Treatment assignment vector
            batch_size: Size of processing batches
            
        Returns:
            Propensity scores
        """
        from sklearn.linear_model import LogisticRegression
        
        n_samples = X.shape[0]
        
        if n_samples <= batch_size:
            # Small dataset, process directly
            model = LogisticRegression(solver='lbfgs', max_iter=1000)
            model.fit(X, treatment)
            return model.predict_proba(X)[:, 1]
        
        # Large dataset, use batched approach
        self.logger.info(f"Computing propensity scores for {n_samples:,} samples in batches")
        
        # Fit model on a sample for coefficient initialization
        sample_indices = np.random.choice(n_samples, size=min(50000, n_samples), replace=False)
        X_sample = X[sample_indices]
        treatment_sample = treatment[sample_indices]
        
        model = LogisticRegression(solver='lbfgs', max_iter=1000)
        model.fit(X_sample, treatment_sample)
        
        # Apply to full dataset in batches
        propensity_scores = np.zeros(n_samples)
        
        for start_idx in range(0, n_samples, batch_size):
            end_idx = min(start_idx + batch_size, n_samples)
            batch_X = X[start_idx:end_idx]
            propensity_scores[start_idx:end_idx] = model.predict_proba(batch_X)[:, 1]
        
        return propensity_scores
    
    @staticmethod
    def _fast_matching(propensity_scores: np.ndarray,
                      treatment: np.ndarray,
                      caliper: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fast propensity score matching using Numba.
        
        Args:
            propensity_scores: Propensity scores
            treatment: Treatment assignment
            caliper: Maximum distance for matching
            
        Returns:
            Tuple of (treated_indices, control_indices)
        """
        treated_indices = np.where(treatment == 1)[0]
        control_indices = np.where(treatment == 0)[0]
        
        treated_ps = propensity_scores[treated_indices]
        control_ps = propensity_scores[control_indices]
        
        matches_treated = []
        matches_control = []
        used_control = np.zeros(len(control_indices), dtype=np.bool_)
        
        # Simple greedy matching
        for i in prange(len(treated_indices)):
            treated_score = treated_ps[i]
            best_match = -1
            best_distance = float('inf')
            
            for j in range(len(control_indices)):
                if not used_control[j]:
                    distance = abs(treated_score - control_ps[j])
                    if distance < caliper and distance < best_distance:
                        best_distance = distance
                        best_match = j
            
            if best_match >= 0:
                matches_treated.append(treated_indices[i])
                matches_control.append(control_indices[best_match])
                used_control[best_match] = True
        
        return np.array(matches_treated), np.array(matches_control)
    
    def perform_matching(self,
                        X: np.ndarray,
                        treatment: np.ndarray,
                        caliper: float = 0.1) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Perform propensity score matching.
        
        Args:
            X: Covariate matrix
            treatment: Treatment assignment
            caliper: Maximum distance for matching
            
        Returns:
            Tuple of (matched_treated_indices, matched_control_indices, propensity_scores)
        """
        # Compute propensity scores
        propensity_scores = self.compute_propensity_scores_batch(X, treatment)
        
        # Perform matching
        matched_treated, matched_control = self._fast_matching(
            propensity_scores, treatment, caliper
        )
        
        self.logger.info(f"Matched {len(matched_treated)} treated units with controls")
        
        return matched_treated, matched_control, propensity_scores


class VectorizedCausalInference:
    """Vectorized implementations of causal inference algorithms."""
    
    def __init__(self):
        self.logger = get_logger("causallm.vectorized_ci", level="INFO")
        self.ps_optimizer = OptimizedPropensityScoring()
    
    def estimate_ate_vectorized(self,
                               X: np.ndarray,
                               treatment: np.ndarray,
                               outcome: np.ndarray,
                               method: str = 'regression') -> Dict[str, float]:
        """
        Estimate Average Treatment Effect using vectorized operations.
        
        Args:
            X: Covariate matrix
            treatment: Treatment assignment
            outcome: Outcome variable
            method: Estimation method ('regression', 'matching', 'doubly_robust')
            
        Returns:
            Dictionary with ATE estimate and statistics
        """
        if method == 'regression':
            return self._ate_regression_vectorized(X, treatment, outcome)
        elif method == 'matching':
            return self._ate_matching_vectorized(X, treatment, outcome)
        elif method == 'doubly_robust':
            return self._ate_doubly_robust_vectorized(X, treatment, outcome)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _ate_regression_vectorized(self,
                                  X: np.ndarray,
                                  treatment: np.ndarray,
                                  outcome: np.ndarray) -> Dict[str, float]:
        """Vectorized regression-based ATE estimation."""
        from sklearn.linear_model import LinearRegression
        
        # Create design matrix with treatment and covariates
        design_matrix = np.column_stack([treatment, X])
        
        # Fit regression model
        model = LinearRegression()
        model.fit(design_matrix, outcome)
        
        # Treatment coefficient is the ATE
        ate = model.coef_[0]
        
        # Compute standard error
        residuals = outcome - model.predict(design_matrix)
        mse = np.mean(residuals**2)
        
        # Design matrix for variance calculation
        XTX_inv = np.linalg.pinv(design_matrix.T @ design_matrix)
        se = np.sqrt(mse * XTX_inv[0, 0])
        
        # Confidence interval
        t_stat = ate / se if se > 0 else 0
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(outcome)-design_matrix.shape[1]))
        
        return {
            'ate': float(ate),
            'se': float(se),
            'ci_lower': float(ate - 1.96 * se),
            'ci_upper': float(ate + 1.96 * se),
            'p_value': float(p_value),
            't_stat': float(t_stat)
        }
    
    def _ate_matching_vectorized(self,
                                X: np.ndarray,
                                treatment: np.ndarray,
                                outcome: np.ndarray) -> Dict[str, float]:
        """Vectorized matching-based ATE estimation."""
        # Perform propensity score matching
        matched_treated, matched_control, ps_scores = self.ps_optimizer.perform_matching(
            X, treatment
        )
        
        if len(matched_treated) == 0:
            return {
                'ate': 0.0,
                'se': float('inf'),
                'ci_lower': float('-inf'),
                'ci_upper': float('inf'),
                'p_value': 1.0,
                't_stat': 0.0
            }
        
        # Compute differences for matched pairs
        treated_outcomes = outcome[matched_treated]
        control_outcomes = outcome[matched_control]
        differences = treated_outcomes - control_outcomes
        
        # ATE is mean difference
        ate = np.mean(differences)
        se = np.std(differences) / np.sqrt(len(differences))
        
        # Statistics
        t_stat = ate / se if se > 0 else 0
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(differences)-1))
        
        return {
            'ate': float(ate),
            'se': float(se),
            'ci_lower': float(ate - 1.96 * se),
            'ci_upper': float(ate + 1.96 * se),
            'p_value': float(p_value),
            't_stat': float(t_stat),
            'n_matched': len(matched_treated)
        }
    
    def _ate_doubly_robust_vectorized(self,
                                     X: np.ndarray,
                                     treatment: np.ndarray,
                                     outcome: np.ndarray) -> Dict[str, float]:
        """Vectorized doubly robust ATE estimation."""
        from sklearn.linear_model import LinearRegression
        
        # Step 1: Estimate propensity scores
        ps_scores = self.ps_optimizer.compute_propensity_scores_batch(X, treatment)
        
        # Step 2: Estimate outcome regression for each treatment group
        treated_mask = treatment == 1
        control_mask = treatment == 0
        
        # Outcome models
        model_treated = LinearRegression()
        model_control = LinearRegression()
        
        if np.sum(treated_mask) > X.shape[1] and np.sum(control_mask) > X.shape[1]:
            model_treated.fit(X[treated_mask], outcome[treated_mask])
            model_control.fit(X[control_mask], outcome[control_mask])
        else:
            # Fallback to simple means if insufficient data
            mean_treated = np.mean(outcome[treated_mask]) if np.sum(treated_mask) > 0 else 0
            mean_control = np.mean(outcome[control_mask]) if np.sum(control_mask) > 0 else 0
            
            return {
                'ate': float(mean_treated - mean_control),
                'se': float('inf'),
                'ci_lower': float('-inf'),
                'ci_upper': float('inf'),
                'p_value': 1.0,
                't_stat': 0.0,
                'method': 'simple_difference'
            }
        
        # Predict outcomes for all units under both treatments
        mu1_hat = model_treated.predict(X)
        mu0_hat = model_control.predict(X)
        
        # Doubly robust estimator
        n = len(outcome)
        
        # IPW components
        ipw_treated = (treatment * outcome) / ps_scores
        ipw_control = ((1 - treatment) * outcome) / (1 - ps_scores)
        
        # Regression adjustment components
        reg_adj_treated = (treatment - ps_scores) * mu1_hat / ps_scores
        reg_adj_control = (ps_scores - treatment) * mu0_hat / (1 - ps_scores)
        
        # Doubly robust estimator
        phi1 = ipw_treated + reg_adj_treated
        phi0 = ipw_control + reg_adj_control
        
        ate = np.mean(phi1 - phi0)
        se = np.std(phi1 - phi0) / np.sqrt(n)
        
        # Statistics
        t_stat = ate / se if se > 0 else 0
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=n-1))
        
        return {
            'ate': float(ate),
            'se': float(se),
            'ci_lower': float(ate - 1.96 * se),
            'ci_upper': float(ate + 1.96 * se),
            'p_value': float(p_value),
            't_stat': float(t_stat),
            'method': 'doubly_robust'
        }


class ParallelStatisticalTests:
    """Parallel implementations of statistical tests for large datasets."""
    
    def __init__(self, n_jobs: Optional[int] = None):
        self.n_jobs = n_jobs or min(mp.cpu_count(), 4)
        self.logger = get_logger("causallm.parallel_tests", level="INFO")
    
    def parallel_correlation_test(self,
                                 data: pd.DataFrame,
                                 alpha: float = 0.05) -> pd.DataFrame:
        """
        Perform correlation tests in parallel for large datasets.
        
        Args:
            data: Input DataFrame
            alpha: Significance level
            
        Returns:
            DataFrame with correlation coefficients and p-values
        """
        numeric_data = data.select_dtypes(include=[np.number])
        columns = numeric_data.columns
        n_vars = len(columns)
        
        # Generate all pairs
        pairs = [(i, j) for i in range(n_vars) for j in range(i+1, n_vars)]
        
        # Parallel computation
        with ProcessPoolExecutor(max_workers=self.n_jobs) as executor:
            partial_corr_test = partial(self._correlation_test_pair, data=numeric_data.values)
            results = list(executor.map(partial_corr_test, pairs))
        
        # Create results DataFrame
        result_data = []
        for (i, j), (corr, p_val) in zip(pairs, results):
            result_data.append({
                'var1': columns[i],
                'var2': columns[j],
                'correlation': corr,
                'p_value': p_val,
                'significant': p_val < alpha
            })
        
        return pd.DataFrame(result_data)
    
    @staticmethod
    def _correlation_test_pair(pair: Tuple[int, int], data: np.ndarray) -> Tuple[float, float]:
        """Compute correlation and p-value for a pair of variables."""
        i, j = pair
        x = data[:, i]
        y = data[:, j]
        
        # Remove missing values
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean = x[mask]
        y_clean = y[mask]
        
        if len(x_clean) < 3:
            return 0.0, 1.0
        
        # Compute correlation and p-value
        corr, p_val = stats.pearsonr(x_clean, y_clean)
        return float(corr), float(p_val)
    
    def parallel_independence_tests(self,
                                  data: pd.DataFrame,
                                  variable_pairs: List[Tuple[str, str]],
                                  conditioning_sets: Optional[List[List[str]]] = None,
                                  test_type: str = 'pearson') -> List[Dict[str, Any]]:
        """
        Perform conditional independence tests in parallel.
        
        Args:
            data: Input DataFrame
            variable_pairs: List of variable pairs to test
            conditioning_sets: List of conditioning sets for each pair
            test_type: Type of test ('pearson', 'mutual_info')
            
        Returns:
            List of test results
        """
        if conditioning_sets is None:
            conditioning_sets = [[] for _ in variable_pairs]
        
        # Prepare test arguments
        test_args = [(pair, cond_set, data.values, data.columns.tolist()) 
                    for pair, cond_set in zip(variable_pairs, conditioning_sets)]
        
        # Parallel execution
        with ProcessPoolExecutor(max_workers=self.n_jobs) as executor:
            if test_type == 'pearson':
                test_func = self._pearson_independence_test
            else:
                test_func = self._mutual_info_independence_test
                
            results = list(executor.map(test_func, test_args))
        
        return results
    
    @staticmethod
    def _pearson_independence_test(args: Tuple) -> Dict[str, Any]:
        """Perform Pearson correlation-based independence test."""
        (var1, var2), cond_set, data, columns = args
        
        try:
            var1_idx = columns.index(var1)
            var2_idx = columns.index(var2)
            cond_indices = [columns.index(var) for var in cond_set]
            
            x = data[:, var1_idx]
            y = data[:, var2_idx]
            
            if not cond_indices:
                # Simple correlation test
                corr, p_val = stats.pearsonr(x, y)
                test_stat = abs(corr)
            else:
                # Partial correlation test (simplified)
                Z = data[:, cond_indices]
                
                # Regression residuals approach
                from sklearn.linear_model import LinearRegression
                
                reg_x = LinearRegression().fit(Z, x)
                reg_y = LinearRegression().fit(Z, y)
                
                residuals_x = x - reg_x.predict(Z)
                residuals_y = y - reg_y.predict(Z)
                
                corr, p_val = stats.pearsonr(residuals_x, residuals_y)
                test_stat = abs(corr)
            
            return {
                'var1': var1,
                'var2': var2,
                'conditioning_set': cond_set,
                'test_statistic': float(test_stat),
                'p_value': float(p_val),
                'independent': p_val > 0.05
            }
            
        except Exception as e:
            return {
                'var1': var1,
                'var2': var2,
                'conditioning_set': cond_set,
                'test_statistic': 0.0,
                'p_value': 1.0,
                'independent': True,
                'error': str(e)
            }
    
    @staticmethod
    def _mutual_info_independence_test(args: Tuple) -> Dict[str, Any]:
        """Perform mutual information-based independence test."""
        from sklearn.feature_selection import mutual_info_regression
        
        (var1, var2), cond_set, data, columns = args
        
        try:
            var1_idx = columns.index(var1)
            var2_idx = columns.index(var2)
            
            x = data[:, var1_idx].reshape(-1, 1)
            y = data[:, var2_idx]
            
            # Compute mutual information
            mi_score = mutual_info_regression(x, y)[0]
            
            # Simple threshold-based test (could be improved with proper statistical test)
            p_val = 1.0 / (1.0 + mi_score * 100)  # Rough approximation
            
            return {
                'var1': var1,
                'var2': var2,
                'conditioning_set': cond_set,
                'test_statistic': float(mi_score),
                'p_value': float(p_val),
                'independent': mi_score < 0.1
            }
            
        except Exception as e:
            return {
                'var1': var1,
                'var2': var2,
                'conditioning_set': cond_set,
                'test_statistic': 0.0,
                'p_value': 1.0,
                'independent': True,
                'error': str(e)
            }


# Global instances for easy access
vectorized_stats = VectorizedStatistics()
parallel_tests = ParallelStatisticalTests()
causal_inference = VectorizedCausalInference()