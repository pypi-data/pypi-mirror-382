"""
Lazy evaluation system for deferred computations.

This module provides lazy evaluation capabilities to defer expensive computations
until they are actually needed, improving performance and memory usage.
"""

import pandas as pd
import numpy as np
from typing import Any, Callable, Dict, List, Optional, Union, Generator, Iterator
from dataclasses import dataclass, field
from functools import wraps, partial
import weakref
import gc
from abc import ABC, abstractmethod
import threading
from collections import defaultdict
import time

from .utils.logging import get_logger
from .exceptions import ComputationError, CausalAttributionError
from .caching import get_global_cache


@dataclass
class LazyComputation:
    """Represents a lazy computation that can be evaluated on demand."""
    func: Callable
    args: tuple
    kwargs: dict
    computed: bool = False
    result: Any = None
    error: Optional[Exception] = None
    dependencies: List['LazyComputation'] = field(default_factory=list)
    cache_key: Optional[str] = None
    
    def __post_init__(self):
        self.logger = get_logger("causallm.lazy_computation", level="DEBUG")
    
    def compute(self, force: bool = False) -> Any:
        """
        Compute the result if not already computed.
        
        Args:
            force: Force recomputation even if already computed
            
        Returns:
            Computation result
        """
        if self.computed and not force:
            return self.result
        
        try:
            # Check cache first
            cache = get_global_cache()
            if self.cache_key and not force:
                cached_result = cache.backend.get(self.cache_key)
                if cached_result is not None:
                    self.result = cached_result
                    self.computed = True
                    return self.result
            
            # Compute dependencies first
            computed_args = []
            for arg in self.args:
                if isinstance(arg, LazyComputation):
                    computed_args.append(arg.compute())
                else:
                    computed_args.append(arg)
            
            computed_kwargs = {}
            for key, value in self.kwargs.items():
                if isinstance(value, LazyComputation):
                    computed_kwargs[key] = value.compute()
                else:
                    computed_kwargs[key] = value
            
            # Execute computation
            self.logger.debug(f"Computing lazy computation: {self.func.__name__}")
            start_time = time.time()
            
            self.result = self.func(*computed_args, **computed_kwargs)
            self.computed = True
            self.error = None
            
            computation_time = time.time() - start_time
            self.logger.debug(f"Lazy computation completed in {computation_time:.3f}s")
            
            # Cache result if cache key provided
            if self.cache_key:
                cache.backend.set(self.cache_key, self.result)
            
            return self.result
            
        except Exception as e:
            self.error = e
            self.logger.error(f"Lazy computation failed: {e}")
            raise ComputationError(
                f"Lazy computation failed: {e}",
                operation=self.func.__name__,
                cause=e
            )
    
    def is_computed(self) -> bool:
        """Check if computation has been executed."""
        return self.computed
    
    def clear(self):
        """Clear computed result to save memory."""
        self.result = None
        self.computed = False
        self.error = None


class LazyDataFrame:
    """Lazy wrapper for DataFrame operations."""
    
    def __init__(self, data_source: Union[pd.DataFrame, Callable, str, LazyComputation]):
        """
        Initialize lazy DataFrame.
        
        Args:
            data_source: Source of data (DataFrame, function, file path, or LazyComputation)
        """
        self.logger = get_logger("causallm.lazy_dataframe", level="DEBUG")
        self._data_source = data_source
        self._operations = []
        self._computed_data = None
        self._metadata = {}
        
        # Track memory usage
        self._memory_usage = 0
        self._last_access = time.time()
    
    def _add_operation(self, op_name: str, func: Callable, *args, **kwargs) -> 'LazyDataFrame':
        """Add an operation to the lazy operation chain."""
        operation = {
            'name': op_name,
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'timestamp': time.time()
        }
        
        # Create new LazyDataFrame with updated operations
        new_lazy_df = LazyDataFrame(self._data_source)
        new_lazy_df._operations = self._operations + [operation]
        new_lazy_df._metadata = self._metadata.copy()
        
        return new_lazy_df
    
    def _get_base_data(self) -> pd.DataFrame:
        """Get the base DataFrame from the data source."""
        if isinstance(self._data_source, pd.DataFrame):
            return self._data_source
        elif isinstance(self._data_source, LazyComputation):
            return self._data_source.compute()
        elif callable(self._data_source):
            return self._data_source()
        elif isinstance(self._data_source, str):
            # Assume it's a file path
            return pd.read_csv(self._data_source)
        else:
            raise ValueError(f"Unsupported data source type: {type(self._data_source)}")
    
    def compute(self, force: bool = False) -> pd.DataFrame:
        """
        Execute all lazy operations and return the result.
        
        Args:
            force: Force recomputation even if already computed
            
        Returns:
            Computed DataFrame
        """
        if self._computed_data is not None and not force:
            self._last_access = time.time()
            return self._computed_data
        
        self.logger.debug(f"Computing lazy DataFrame with {len(self._operations)} operations")
        start_time = time.time()
        
        # Start with base data
        current_data = self._get_base_data()
        
        # Apply all operations sequentially
        for operation in self._operations:
            op_name = operation['name']
            func = operation['func']
            args = operation['args']
            kwargs = operation['kwargs']
            
            self.logger.debug(f"Applying operation: {op_name}")
            
            try:
                # Apply operation
                current_data = func(current_data, *args, **kwargs)
                
                # Update metadata
                self._metadata[f"{op_name}_applied"] = True
                
            except Exception as e:
                raise ComputationError(
                    f"Failed to apply operation {op_name}: {e}",
                    operation=op_name,
                    cause=e
                )
        
        computation_time = time.time() - start_time
        self.logger.debug(f"Lazy DataFrame computed in {computation_time:.3f}s")
        
        # Cache result
        self._computed_data = current_data
        self._last_access = time.time()
        self._memory_usage = current_data.memory_usage(deep=True).sum() / (1024**2)  # MB
        
        return current_data
    
    # DataFrame-like operations (lazy)
    def fillna(self, value=None, method=None, **kwargs) -> 'LazyDataFrame':
        """Lazy fillna operation."""
        return self._add_operation('fillna', pd.DataFrame.fillna, value=value, method=method, **kwargs)
    
    def dropna(self, **kwargs) -> 'LazyDataFrame':
        """Lazy dropna operation."""
        return self._add_operation('dropna', pd.DataFrame.dropna, **kwargs)
    
    def drop_duplicates(self, **kwargs) -> 'LazyDataFrame':
        """Lazy drop_duplicates operation."""
        return self._add_operation('drop_duplicates', pd.DataFrame.drop_duplicates, **kwargs)
    
    def select_dtypes(self, include=None, exclude=None) -> 'LazyDataFrame':
        """Lazy select_dtypes operation."""
        return self._add_operation('select_dtypes', pd.DataFrame.select_dtypes, include=include, exclude=exclude)
    
    def groupby(self, by, **kwargs) -> 'LazyGroupBy':
        """Create lazy GroupBy object."""
        return LazyGroupBy(self, by, **kwargs)
    
    def apply(self, func, **kwargs) -> 'LazyDataFrame':
        """Lazy apply operation."""
        return self._add_operation('apply', pd.DataFrame.apply, func, **kwargs)
    
    def query(self, expr, **kwargs) -> 'LazyDataFrame':
        """Lazy query operation."""
        return self._add_operation('query', pd.DataFrame.query, expr, **kwargs)
    
    def sample(self, n=None, frac=None, **kwargs) -> 'LazyDataFrame':
        """Lazy sample operation."""
        return self._add_operation('sample', pd.DataFrame.sample, n=n, frac=frac, **kwargs)
    
    # Properties (these trigger computation)
    @property
    def shape(self) -> tuple:
        """Get shape (triggers computation)."""
        return self.compute().shape
    
    @property
    def columns(self) -> pd.Index:
        """Get columns (triggers computation)."""
        return self.compute().columns
    
    @property
    def dtypes(self) -> pd.Series:
        """Get dtypes (triggers computation)."""
        return self.compute().dtypes
    
    def __len__(self) -> int:
        """Get length (triggers computation)."""
        return len(self.compute())
    
    def __getitem__(self, key) -> Union['LazyDataFrame', pd.Series]:
        """Get item (may trigger computation)."""
        if isinstance(key, (list, slice)):
            return self._add_operation('getitem', lambda df, k: df[k], key)
        else:
            # Single column access - return computed Series
            return self.compute()[key]
    
    def head(self, n: int = 5) -> pd.DataFrame:
        """Get head (optimized - doesn't compute all operations)."""
        # For head operation, we can optimize by applying operations to a small subset
        try:
            base_data = self._get_base_data()
            head_data = base_data.head(min(n * 10, 1000))  # Get more data for operations
            
            # Apply operations to small subset
            for operation in self._operations:
                head_data = operation['func'](head_data, *operation['args'], **operation['kwargs'])
            
            return head_data.head(n)
        except:
            # Fallback to full computation
            return self.compute().head(n)
    
    def clear_cache(self):
        """Clear cached computation results."""
        self._computed_data = None
        self._memory_usage = 0
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about lazy operations."""
        return {
            'operations_count': len(self._operations),
            'operations': [op['name'] for op in self._operations],
            'is_computed': self._computed_data is not None,
            'memory_usage_mb': self._memory_usage,
            'last_access': self._last_access
        }


class LazyGroupBy:
    """Lazy wrapper for GroupBy operations."""
    
    def __init__(self, lazy_df: LazyDataFrame, by, **kwargs):
        self.lazy_df = lazy_df
        self.by = by
        self.kwargs = kwargs
        self.logger = get_logger("causallm.lazy_groupby", level="DEBUG")
    
    def agg(self, func) -> LazyDataFrame:
        """Lazy aggregation."""
        def groupby_agg(df, by, func, **kwargs):
            return df.groupby(by, **kwargs).agg(func)
        
        return self.lazy_df._add_operation('groupby_agg', groupby_agg, self.by, func, **self.kwargs)
    
    def mean(self) -> LazyDataFrame:
        """Lazy mean aggregation."""
        return self.agg('mean')
    
    def sum(self) -> LazyDataFrame:
        """Lazy sum aggregation."""
        return self.agg('sum')
    
    def count(self) -> LazyDataFrame:
        """Lazy count aggregation."""
        return self.agg('count')


class LazyComputationGraph:
    """Manages a graph of lazy computations with dependency tracking."""
    
    def __init__(self):
        self.computations: Dict[str, LazyComputation] = {}
        self.dependencies: Dict[str, List[str]] = defaultdict(list)
        self.dependents: Dict[str, List[str]] = defaultdict(list)
        self.logger = get_logger("causallm.lazy_graph", level="INFO")
        self._lock = threading.Lock()
    
    def add_computation(self, 
                       name: str, 
                       func: Callable, 
                       args: tuple = (),
                       kwargs: dict = None,
                       dependencies: List[str] = None) -> LazyComputation:
        """
        Add a computation to the graph.
        
        Args:
            name: Unique name for the computation
            func: Function to execute
            args: Arguments for the function
            kwargs: Keyword arguments for the function
            dependencies: List of computation names this depends on
            
        Returns:
            LazyComputation object
        """
        with self._lock:
            if kwargs is None:
                kwargs = {}
            
            if dependencies is None:
                dependencies = []
            
            # Create LazyComputation
            computation = LazyComputation(
                func=func,
                args=args,
                kwargs=kwargs,
                cache_key=f"lazy_{name}"
            )
            
            # Add dependencies
            dep_computations = []
            for dep_name in dependencies:
                if dep_name not in self.computations:
                    raise ValueError(f"Dependency '{dep_name}' not found")
                
                dep_computations.append(self.computations[dep_name])
                self.dependencies[name].append(dep_name)
                self.dependents[dep_name].append(name)
            
            computation.dependencies = dep_computations
            self.computations[name] = computation
            
            self.logger.debug(f"Added computation '{name}' with {len(dependencies)} dependencies")
            return computation
    
    def compute(self, name: str, force: bool = False) -> Any:
        """
        Compute a specific computation and its dependencies.
        
        Args:
            name: Name of computation to execute
            force: Force recomputation
            
        Returns:
            Computation result
        """
        if name not in self.computations:
            raise ValueError(f"Computation '{name}' not found")
        
        return self.computations[name].compute(force=force)
    
    def compute_all(self, force: bool = False) -> Dict[str, Any]:
        """
        Compute all computations in topological order.
        
        Args:
            force: Force recomputation of all
            
        Returns:
            Dictionary of all computation results
        """
        # Topological sort
        execution_order = self._topological_sort()
        
        results = {}
        for name in execution_order:
            try:
                results[name] = self.compute(name, force=force)
            except Exception as e:
                self.logger.error(f"Failed to compute '{name}': {e}")
                results[name] = None
        
        return results
    
    def _topological_sort(self) -> List[str]:
        """Perform topological sort of computations."""
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(name: str):
            if name in temp_visited:
                raise ValueError(f"Circular dependency detected involving '{name}'")
            
            if name not in visited:
                temp_visited.add(name)
                
                for dep_name in self.dependencies[name]:
                    visit(dep_name)
                
                temp_visited.remove(name)
                visited.add(name)
                order.append(name)
        
        for name in self.computations:
            if name not in visited:
                visit(name)
        
        return order
    
    def invalidate(self, name: str, cascade: bool = True):
        """
        Invalidate a computation and optionally its dependents.
        
        Args:
            name: Name of computation to invalidate
            cascade: Whether to invalidate dependent computations
        """
        if name in self.computations:
            self.computations[name].clear()
            
            if cascade:
                # Invalidate all dependents
                to_invalidate = [name]
                invalidated = set()
                
                while to_invalidate:
                    current = to_invalidate.pop(0)
                    if current not in invalidated:
                        invalidated.add(current)
                        
                        if current in self.computations:
                            self.computations[current].clear()
                        
                        # Add dependents to queue
                        to_invalidate.extend(self.dependents[current])
                
                self.logger.info(f"Invalidated computation '{name}' and {len(invalidated)-1} dependents")
            else:
                self.logger.info(f"Invalidated computation '{name}'")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the computation graph."""
        computed_count = sum(1 for comp in self.computations.values() if comp.is_computed())
        
        return {
            'total_computations': len(self.computations),
            'computed_computations': computed_count,
            'pending_computations': len(self.computations) - computed_count,
            'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
            'computation_names': list(self.computations.keys())
        }


# Decorators for lazy evaluation

def lazy(cache_key: Optional[str] = None):
    """
    Decorator to make a function lazy.
    
    Args:
        cache_key: Optional cache key for the computation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return LazyComputation(
                func=func,
                args=args,
                kwargs=kwargs,
                cache_key=cache_key
            )
        return wrapper
    return decorator


def lazy_property(func: Callable) -> property:
    """
    Decorator to create a lazy property that computes once and caches the result.
    """
    attr_name = f'_lazy_{func.__name__}'
    
    @property
    @wraps(func)
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    
    return wrapper


# Global computation graph
_global_computation_graph = LazyComputationGraph()

def get_global_computation_graph() -> LazyComputationGraph:
    """Get global lazy computation graph."""
    return _global_computation_graph


# Utility functions for lazy evaluation

def lazy_correlation_matrix(data: Union[pd.DataFrame, LazyDataFrame]) -> LazyComputation:
    """Create lazy correlation matrix computation."""
    
    def compute_correlation(df):
        return df.corr()
    
    if isinstance(data, LazyDataFrame):
        return LazyComputation(
            func=lambda: compute_correlation(data.compute()),
            args=(),
            kwargs={},
            cache_key="correlation_matrix"
        )
    else:
        return LazyComputation(
            func=compute_correlation,
            args=(data,),
            kwargs={},
            cache_key="correlation_matrix"
        )


def lazy_pca(data: Union[pd.DataFrame, LazyDataFrame], 
             n_components: Optional[int] = None) -> LazyComputation:
    """Create lazy PCA computation."""
    from sklearn.decomposition import PCA
    
    def compute_pca(df, n_comp):
        numeric_data = df.select_dtypes(include=[np.number]).fillna(0)
        pca = PCA(n_components=n_comp)
        components = pca.fit_transform(numeric_data)
        
        return {
            'components': components,
            'explained_variance_ratio': pca.explained_variance_ratio_,
            'feature_names': numeric_data.columns.tolist()
        }
    
    if isinstance(data, LazyDataFrame):
        return LazyComputation(
            func=lambda: compute_pca(data.compute(), n_components),
            args=(),
            kwargs={},
            cache_key=f"pca_{n_components}"
        )
    else:
        return LazyComputation(
            func=compute_pca,
            args=(data, n_components),
            kwargs={},
            cache_key=f"pca_{n_components}"
        )