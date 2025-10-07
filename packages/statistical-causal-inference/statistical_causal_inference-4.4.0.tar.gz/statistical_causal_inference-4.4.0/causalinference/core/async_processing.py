"""
Async processing capabilities for independent computations.

This module provides asynchronous processing capabilities to improve performance
by parallelizing independent computations in causal inference workflows.
"""

import asyncio
import aiofiles
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional, Union, Awaitable, Tuple
import time
import pandas as pd
import numpy as np
from dataclasses import dataclass
from functools import partial, wraps
import multiprocessing as mp
import threading
from collections import defaultdict
import queue
import weakref

from .utils.logging import get_logger
from .exceptions import ComputationError, CausalAttributionError
from .caching import get_global_cache


@dataclass
class AsyncTaskResult:
    """Result of an async task execution."""
    task_id: str
    result: Any
    execution_time: float
    memory_used: float
    error: Optional[Exception] = None
    worker_id: Optional[str] = None


@dataclass
class AsyncBatchResult:
    """Result of a batch of async tasks."""
    batch_id: str
    results: List[AsyncTaskResult]
    total_time: float
    success_count: int
    failure_count: int


class AsyncTaskManager:
    """Manages asynchronous task execution with resource monitoring."""
    
    def __init__(self, 
                 max_workers: Optional[int] = None,
                 use_processes: bool = False,
                 enable_monitoring: bool = True):
        """
        Initialize async task manager.
        
        Args:
            max_workers: Maximum number of worker threads/processes
            use_processes: Whether to use processes instead of threads
            enable_monitoring: Whether to enable resource monitoring
        """
        self.max_workers = max_workers or min(mp.cpu_count(), 8)
        self.use_processes = use_processes
        self.enable_monitoring = enable_monitoring
        self.logger = get_logger("causallm.async_manager", level="INFO")
        
        # Task tracking
        self._active_tasks = {}
        self._completed_tasks = {}
        self._task_counter = 0
        self._lock = threading.Lock()
        
        # Resource monitoring
        if enable_monitoring:
            self._resource_monitor = ResourceMonitor()
        else:
            self._resource_monitor = None
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        with self._lock:
            self._task_counter += 1
            return f"task_{self._task_counter}"
    
    async def execute_task(self,
                          func: Callable,
                          *args,
                          task_id: Optional[str] = None,
                          timeout: Optional[float] = None,
                          **kwargs) -> AsyncTaskResult:
        """
        Execute a single async task.
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            task_id: Optional task ID
            timeout: Optional timeout in seconds
            **kwargs: Keyword arguments for the function
            
        Returns:
            AsyncTaskResult with execution details
        """
        if task_id is None:
            task_id = self._generate_task_id()
        
        start_time = time.time()
        start_memory = self._resource_monitor.get_memory_usage() if self._resource_monitor else 0
        
        try:
            # Record task start
            self._active_tasks[task_id] = {
                'start_time': start_time,
                'function': func.__name__,
                'status': 'running'
            }
            
            # Execute task
            loop = asyncio.get_event_loop()
            
            if self.use_processes:
                with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                    future = loop.run_in_executor(executor, func, *args)
            else:
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    future = loop.run_in_executor(executor, func, *args)
            
            if timeout:
                result = await asyncio.wait_for(future, timeout=timeout)
            else:
                result = await future
            
            execution_time = time.time() - start_time
            end_memory = self._resource_monitor.get_memory_usage() if self._resource_monitor else 0
            memory_used = max(0, end_memory - start_memory)
            
            # Record completion
            task_result = AsyncTaskResult(
                task_id=task_id,
                result=result,
                execution_time=execution_time,
                memory_used=memory_used
            )
            
            self._completed_tasks[task_id] = task_result
            self._active_tasks.pop(task_id, None)
            
            self.logger.debug(f"Task {task_id} completed in {execution_time:.2f}s")
            return task_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            task_result = AsyncTaskResult(
                task_id=task_id,
                result=None,
                execution_time=execution_time,
                memory_used=0,
                error=e
            )
            
            self._completed_tasks[task_id] = task_result
            self._active_tasks.pop(task_id, None)
            
            self.logger.error(f"Task {task_id} failed after {execution_time:.2f}s: {e}")
            return task_result
    
    async def execute_batch(self,
                           tasks: List[Tuple[Callable, tuple, dict]],
                           batch_id: Optional[str] = None,
                           max_concurrent: Optional[int] = None) -> AsyncBatchResult:
        """
        Execute a batch of tasks concurrently.
        
        Args:
            tasks: List of (function, args, kwargs) tuples
            batch_id: Optional batch identifier
            max_concurrent: Maximum concurrent tasks (defaults to max_workers)
            
        Returns:
            AsyncBatchResult with batch execution details
        """
        if batch_id is None:
            batch_id = f"batch_{int(time.time())}"
        
        if max_concurrent is None:
            max_concurrent = self.max_workers
        
        self.logger.info(f"Executing batch {batch_id} with {len(tasks)} tasks")
        batch_start = time.time()
        
        # Create semaphore to limit concurrent tasks
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(func, args, kwargs):
            async with semaphore:
                return await self.execute_task(func, *args, **kwargs)
        
        # Create coroutines for all tasks
        coroutines = [
            execute_with_semaphore(func, args, kwargs)
            for func, args, kwargs in tasks
        ]
        
        # Execute all tasks
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Process results
        task_results = []
        success_count = 0
        failure_count = 0
        
        for result in results:
            if isinstance(result, AsyncTaskResult):
                task_results.append(result)
                if result.error is None:
                    success_count += 1
                else:
                    failure_count += 1
            else:
                # Handle exceptions from gather
                failure_count += 1
                task_results.append(AsyncTaskResult(
                    task_id=f"failed_{len(task_results)}",
                    result=None,
                    execution_time=0,
                    memory_used=0,
                    error=result if isinstance(result, Exception) else Exception(str(result))
                ))
        
        batch_time = time.time() - batch_start
        
        batch_result = AsyncBatchResult(
            batch_id=batch_id,
            results=task_results,
            total_time=batch_time,
            success_count=success_count,
            failure_count=failure_count
        )
        
        self.logger.info(f"Batch {batch_id} completed: {success_count} success, {failure_count} failures, {batch_time:.2f}s total")
        return batch_result
    
    def get_active_tasks(self) -> Dict[str, Dict]:
        """Get information about currently active tasks."""
        return dict(self._active_tasks)
    
    def get_completed_tasks(self) -> Dict[str, AsyncTaskResult]:
        """Get information about completed tasks."""
        return dict(self._completed_tasks)
    
    def cleanup_completed_tasks(self, older_than_hours: int = 24):
        """Clean up old completed tasks."""
        current_time = time.time()
        cutoff_time = current_time - (older_than_hours * 3600)
        
        to_remove = [
            task_id for task_id, result in self._completed_tasks.items()
            if (current_time - result.execution_time) > cutoff_time
        ]
        
        for task_id in to_remove:
            self._completed_tasks.pop(task_id, None)
        
        self.logger.info(f"Cleaned up {len(to_remove)} old completed tasks")


class ResourceMonitor:
    """Monitor system resources during async processing."""
    
    def __init__(self):
        import psutil
        self.process = psutil.Process()
        self.logger = get_logger("causallm.resource_monitor", level="INFO")
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return self.process.cpu_percent()
    
    def get_system_stats(self) -> Dict[str, float]:
        """Get comprehensive system statistics."""
        import psutil
        
        return {
            'memory_usage_mb': self.get_memory_usage(),
            'cpu_usage_percent': self.get_cpu_usage(),
            'available_memory_gb': psutil.virtual_memory().available / (1024**3),
            'cpu_count': psutil.cpu_count()
        }


class AsyncCausalAnalysis:
    """Async wrapper for causal analysis operations."""
    
    def __init__(self, task_manager: Optional[AsyncTaskManager] = None):
        self.task_manager = task_manager or AsyncTaskManager()
        self.logger = get_logger("causallm.async_causal", level="INFO")
    
    async def parallel_correlation_analysis(self,
                                          data: pd.DataFrame,
                                          chunk_size: int = 5000) -> pd.DataFrame:
        """
        Compute correlation matrix in parallel chunks.
        
        Args:
            data: Input DataFrame
            chunk_size: Size of chunks for parallel processing
            
        Returns:
            Complete correlation matrix
        """
        numeric_data = data.select_dtypes(include=[np.number])
        columns = numeric_data.columns.tolist()
        n_vars = len(columns)
        
        self.logger.info(f"Computing correlation matrix for {n_vars} variables in parallel")
        
        # Create tasks for variable pairs
        tasks = []
        for i in range(0, n_vars, chunk_size):
            for j in range(i, n_vars, chunk_size):
                end_i = min(i + chunk_size, n_vars)
                end_j = min(j + chunk_size, n_vars)
                
                chunk_cols_i = columns[i:end_i]
                chunk_cols_j = columns[j:end_j]
                
                tasks.append((
                    self._compute_correlation_chunk,
                    (numeric_data[chunk_cols_i + chunk_cols_j].values, chunk_cols_i, chunk_cols_j),
                    {}
                ))
        
        # Execute tasks
        batch_result = await self.task_manager.execute_batch(tasks)
        
        # Combine results
        correlation_matrix = pd.DataFrame(
            np.eye(n_vars), index=columns, columns=columns
        )
        
        for result in batch_result.results:
            if result.error is None:
                chunk_corr, chunk_cols_i, chunk_cols_j = result.result
                
                # Update correlation matrix
                for k, col_i in enumerate(chunk_cols_i):
                    for l, col_j in enumerate(chunk_cols_j):
                        correlation_matrix.loc[col_i, col_j] = chunk_corr[k, len(chunk_cols_i) + l]
                        correlation_matrix.loc[col_j, col_i] = chunk_corr[k, len(chunk_cols_i) + l]
        
        return correlation_matrix
    
    @staticmethod
    def _compute_correlation_chunk(chunk_data: np.ndarray, 
                                  cols_i: List[str], 
                                  cols_j: List[str]) -> Tuple[np.ndarray, List[str], List[str]]:
        """Compute correlation for a chunk of variables."""
        corr_matrix = np.corrcoef(chunk_data.T)
        return corr_matrix, cols_i, cols_j
    
    async def parallel_causal_discovery(self,
                                       data: pd.DataFrame,
                                       variables: List[str],
                                       max_conditioning_size: int = 3) -> List[Dict[str, Any]]:
        """
        Perform causal discovery with parallel independence testing.
        
        Args:
            data: Input DataFrame
            variables: Variables to analyze
            max_conditioning_size: Maximum size of conditioning sets
            
        Returns:
            List of independence test results
        """
        from itertools import combinations
        
        self.logger.info(f"Parallel causal discovery for {len(variables)} variables")
        
        # Generate all variable pairs
        variable_pairs = list(combinations(variables, 2))
        
        # Generate conditioning sets
        other_vars = [v for v in variables]
        conditioning_sets = []
        
        for pair in variable_pairs:
            remaining_vars = [v for v in other_vars if v not in pair]
            
            # Generate conditioning sets of different sizes
            pair_conditioning_sets = [[]]  # Empty conditioning set
            
            for size in range(1, min(max_conditioning_size + 1, len(remaining_vars) + 1)):
                for cond_set in combinations(remaining_vars, size):
                    pair_conditioning_sets.append(list(cond_set))
            
            conditioning_sets.append(pair_conditioning_sets)
        
        # Create tasks for independence tests
        tasks = []
        for pair, cond_sets in zip(variable_pairs, conditioning_sets):
            for cond_set in cond_sets:
                tasks.append((
                    self._independence_test,
                    (data.values, data.columns.tolist(), pair, cond_set),
                    {}
                ))
        
        # Execute tests in parallel
        batch_result = await self.task_manager.execute_batch(
            tasks, max_concurrent=self.task_manager.max_workers
        )
        
        # Collect results
        independence_results = []
        for result in batch_result.results:
            if result.error is None:
                independence_results.append(result.result)
            else:
                self.logger.error(f"Independence test failed: {result.error}")
        
        self.logger.info(f"Completed {len(independence_results)} independence tests")
        return independence_results
    
    @staticmethod
    def _independence_test(data: np.ndarray,
                          columns: List[str],
                          variable_pair: Tuple[str, str],
                          conditioning_set: List[str]) -> Dict[str, Any]:
        """Perform independence test between two variables."""
        from scipy.stats import pearsonr
        
        try:
            var1_idx = columns.index(variable_pair[0])
            var2_idx = columns.index(variable_pair[1])
            
            x = data[:, var1_idx]
            y = data[:, var2_idx]
            
            if not conditioning_set:
                # Simple correlation test
                corr, p_value = pearsonr(x, y)
                test_stat = abs(corr)
            else:
                # Partial correlation (simplified)
                cond_indices = [columns.index(var) for var in conditioning_set]
                Z = data[:, cond_indices]
                
                # Regression residuals approach
                from sklearn.linear_model import LinearRegression
                
                reg_x = LinearRegression().fit(Z, x)
                reg_y = LinearRegression().fit(Z, y)
                
                residuals_x = x - reg_x.predict(Z)
                residuals_y = y - reg_y.predict(Z)
                
                corr, p_value = pearsonr(residuals_x, residuals_y)
                test_stat = abs(corr)
            
            return {
                'var1': variable_pair[0],
                'var2': variable_pair[1],
                'conditioning_set': conditioning_set,
                'test_statistic': float(test_stat),
                'p_value': float(p_value),
                'independent': p_value > 0.05
            }
            
        except Exception as e:
            return {
                'var1': variable_pair[0],
                'var2': variable_pair[1],
                'conditioning_set': conditioning_set,
                'test_statistic': 0.0,
                'p_value': 1.0,
                'independent': True,
                'error': str(e)
            }
    
    async def parallel_bootstrap_analysis(self,
                                        data: pd.DataFrame,
                                        analysis_func: Callable,
                                        n_bootstrap: int = 1000,
                                        sample_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform bootstrap analysis in parallel.
        
        Args:
            data: Input DataFrame
            analysis_func: Function to apply to each bootstrap sample
            n_bootstrap: Number of bootstrap samples
            sample_size: Size of each bootstrap sample
            
        Returns:
            Bootstrap analysis results
        """
        if sample_size is None:
            sample_size = len(data)
        
        self.logger.info(f"Parallel bootstrap analysis with {n_bootstrap} samples")
        
        # Create bootstrap tasks
        tasks = []
        for i in range(n_bootstrap):
            tasks.append((
                self._bootstrap_sample_analysis,
                (data.values, data.columns.tolist(), analysis_func, sample_size, i),
                {}
            ))
        
        # Execute bootstrap samples in parallel
        batch_result = await self.task_manager.execute_batch(tasks)
        
        # Collect results
        bootstrap_results = []
        for result in batch_result.results:
            if result.error is None:
                bootstrap_results.append(result.result)
        
        # Compute bootstrap statistics
        if bootstrap_results:
            bootstrap_array = np.array(bootstrap_results)
            
            return {
                'mean': float(np.mean(bootstrap_array)),
                'std': float(np.std(bootstrap_array)),
                'ci_lower': float(np.percentile(bootstrap_array, 2.5)),
                'ci_upper': float(np.percentile(bootstrap_array, 97.5)),
                'samples': bootstrap_results,
                'n_successful': len(bootstrap_results),
                'n_failed': n_bootstrap - len(bootstrap_results)
            }
        else:
            return {
                'mean': 0.0,
                'std': 0.0,
                'ci_lower': 0.0,
                'ci_upper': 0.0,
                'samples': [],
                'n_successful': 0,
                'n_failed': n_bootstrap
            }
    
    @staticmethod
    def _bootstrap_sample_analysis(data: np.ndarray,
                                  columns: List[str],
                                  analysis_func: Callable,
                                  sample_size: int,
                                  seed: int) -> float:
        """Analyze a single bootstrap sample."""
        np.random.seed(seed)
        
        # Generate bootstrap sample
        indices = np.random.choice(len(data), size=sample_size, replace=True)
        bootstrap_sample = pd.DataFrame(data[indices], columns=columns)
        
        # Apply analysis function
        return analysis_func(bootstrap_sample)


# Decorators for async processing

def async_cached(cache_ttl: int = 3600):
    """Decorator for async caching of function results."""
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import time
            import hashlib
            
            # Generate cache key
            key_str = f"{func.__name__}_{hash((args, tuple(sorted(kwargs.items()))))}"
            key = hashlib.md5(key_str.encode()).hexdigest()
            
            # Check cache
            current_time = time.time()
            if key in cache and (current_time - cache_times[key]) < cache_ttl:
                return cache[key]
            
            # Compute result
            result = await func(*args, **kwargs)
            
            # Update cache
            cache[key] = result
            cache_times[key] = current_time
            
            return result
        
        return wrapper
    return decorator


def make_async(func: Callable, use_processes: bool = False) -> Callable:
    """Convert a synchronous function to async."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        
        if use_processes:
            with ProcessPoolExecutor() as executor:
                return await loop.run_in_executor(executor, func, *args)
        else:
            with ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(executor, func, *args)
    
    return async_wrapper


# Global instances
_global_task_manager = None

def get_global_task_manager() -> AsyncTaskManager:
    """Get global async task manager."""
    global _global_task_manager
    if _global_task_manager is None:
        _global_task_manager = AsyncTaskManager()
    return _global_task_manager

def set_global_task_manager(manager: AsyncTaskManager):
    """Set global async task manager."""
    global _global_task_manager
    _global_task_manager = manager