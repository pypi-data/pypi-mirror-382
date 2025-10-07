"""
Data processing utilities with performance optimizations.

This module provides efficient data processing capabilities for large datasets,
including chunking, streaming, and memory-efficient operations.
"""

import pandas as pd
import numpy as np
from typing import Iterator, List, Dict, Any, Optional, Union, Callable, Tuple
import gc
import psutil
import os
from dataclasses import dataclass
from pathlib import Path
import dask.dataframe as dd
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from functools import partial

from .utils.logging import get_logger
from .exceptions import DataValidationError, InsufficientDataError, ComputationError


@dataclass
class ChunkProcessingResult:
    """Result of processing a data chunk."""
    chunk_id: int
    result: Any
    memory_used: float
    processing_time: float
    row_count: int


@dataclass
class DataProcessingConfig:
    """Configuration for data processing operations."""
    chunk_size: int = 10000
    max_memory_usage: float = 0.8  # 80% of available memory
    use_dask: bool = True
    n_workers: int = None
    cache_intermediate: bool = True
    lazy_evaluation: bool = True


class MemoryMonitor:
    """Monitor and manage memory usage during data processing."""
    
    def __init__(self):
        self.logger = get_logger("causallm.memory_monitor", level="INFO")
        self.process = psutil.Process()
        self.initial_memory = self.get_memory_usage()
    
    def get_memory_usage(self) -> float:
        """Get current memory usage as percentage of total system memory."""
        return self.process.memory_percent()
    
    def get_available_memory_gb(self) -> float:
        """Get available memory in GB."""
        return psutil.virtual_memory().available / (1024**3)
    
    def check_memory_threshold(self, threshold: float = 0.8) -> bool:
        """Check if memory usage is below threshold."""
        current_usage = self.get_memory_usage() / 100  # Convert to ratio
        return current_usage < threshold
    
    def suggest_chunk_size(self, data_size_mb: float, target_memory_mb: float = 500) -> int:
        """Suggest optimal chunk size based on data size and available memory."""
        available_memory_mb = self.get_available_memory_gb() * 1024
        
        # Conservative estimate: use 1/4 of available memory per chunk
        max_chunk_memory = min(available_memory_mb / 4, target_memory_mb)
        
        # Estimate rows per MB (rough approximation)
        if data_size_mb > 0:
            estimated_rows = int((max_chunk_memory / data_size_mb) * 1000)  # Assume ~1000 rows per MB
            return max(1000, min(50000, estimated_rows))  # Clamp between 1K and 50K
        
        return 10000  # Default fallback


class DataChunker:
    """Efficient data chunking for large datasets."""
    
    def __init__(self, config: Optional[DataProcessingConfig] = None):
        self.config = config or DataProcessingConfig()
        self.logger = get_logger("causallm.data_chunker", level="INFO")
        self.memory_monitor = MemoryMonitor()
    
    def chunk_dataframe(self, 
                       data: pd.DataFrame, 
                       chunk_size: Optional[int] = None) -> Iterator[Tuple[int, pd.DataFrame]]:
        """
        Chunk a DataFrame for memory-efficient processing.
        
        Args:
            data: Input DataFrame
            chunk_size: Size of each chunk (rows)
            
        Yields:
            Tuple of (chunk_id, chunk_dataframe)
        """
        if chunk_size is None:
            # Auto-determine chunk size based on data size and available memory
            data_size_mb = data.memory_usage(deep=True).sum() / (1024**2)
            chunk_size = self.memory_monitor.suggest_chunk_size(data_size_mb)
        
        total_rows = len(data)
        num_chunks = (total_rows + chunk_size - 1) // chunk_size
        
        self.logger.info(f"Chunking DataFrame: {total_rows} rows into {num_chunks} chunks of ~{chunk_size} rows each")
        
        for i, start_idx in enumerate(range(0, total_rows, chunk_size)):
            end_idx = min(start_idx + chunk_size, total_rows)
            chunk = data.iloc[start_idx:end_idx].copy()
            
            # Log memory usage periodically
            if i % 10 == 0:
                memory_usage = self.memory_monitor.get_memory_usage()
                self.logger.debug(f"Processing chunk {i+1}/{num_chunks}, memory usage: {memory_usage:.1f}%")
            
            yield i, chunk
            
            # Force garbage collection periodically
            if i % 50 == 0:
                gc.collect()
    
    def process_chunks_parallel(self,
                              data: pd.DataFrame,
                              processing_func: Callable[[pd.DataFrame], Any],
                              chunk_size: Optional[int] = None,
                              max_workers: Optional[int] = None) -> List[ChunkProcessingResult]:
        """
        Process DataFrame chunks in parallel.
        
        Args:
            data: Input DataFrame
            processing_func: Function to apply to each chunk
            chunk_size: Size of each chunk
            max_workers: Maximum number of worker threads
            
        Returns:
            List of chunk processing results
        """
        import time
        
        if max_workers is None:
            max_workers = min(os.cpu_count() or 1, 4)  # Cap at 4 to avoid memory issues
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all chunks for processing
            future_to_chunk = {}
            
            for chunk_id, chunk in self.chunk_dataframe(data, chunk_size):
                future = executor.submit(self._process_chunk_with_monitoring, 
                                       chunk, processing_func, chunk_id)
                future_to_chunk[future] = chunk_id
            
            # Collect results as they complete
            for future in as_completed(future_to_chunk):
                chunk_id = future_to_chunk[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.logger.debug(f"Completed chunk {chunk_id}")
                except Exception as e:
                    self.logger.error(f"Error processing chunk {chunk_id}: {e}")
                    raise ComputationError(
                        f"Failed to process data chunk {chunk_id}",
                        operation="parallel_chunk_processing",
                        cause=e
                    )
        
        # Sort results by chunk_id to maintain order
        results.sort(key=lambda x: x.chunk_id)
        return results
    
    def _process_chunk_with_monitoring(self, 
                                     chunk: pd.DataFrame, 
                                     processing_func: Callable,
                                     chunk_id: int) -> ChunkProcessingResult:
        """Process a single chunk with memory and time monitoring."""
        import time
        
        start_time = time.time()
        start_memory = self.memory_monitor.get_memory_usage()
        
        try:
            result = processing_func(chunk)
            
            end_time = time.time()
            end_memory = self.memory_monitor.get_memory_usage()
            
            return ChunkProcessingResult(
                chunk_id=chunk_id,
                result=result,
                memory_used=end_memory - start_memory,
                processing_time=end_time - start_time,
                row_count=len(chunk)
            )
        
        except Exception as e:
            raise ComputationError(
                f"Error processing chunk {chunk_id}",
                operation="chunk_processing",
                context={"chunk_size": len(chunk), "chunk_id": chunk_id},
                cause=e
            )


class StreamingDataProcessor:
    """Process data in a streaming fashion for very large datasets."""
    
    def __init__(self, config: Optional[DataProcessingConfig] = None):
        self.config = config or DataProcessingConfig()
        self.logger = get_logger("causallm.streaming_processor", level="INFO")
        self.memory_monitor = MemoryMonitor()
    
    def stream_from_file(self, 
                        file_path: Union[str, Path],
                        chunk_size: Optional[int] = None,
                        **read_kwargs) -> Iterator[pd.DataFrame]:
        """
        Stream data from a file in chunks.
        
        Args:
            file_path: Path to the data file
            chunk_size: Number of rows per chunk
            **read_kwargs: Additional arguments for pd.read_csv
            
        Yields:
            DataFrame chunks
        """
        file_path = Path(file_path)
        
        if chunk_size is None:
            chunk_size = self.config.chunk_size
        
        self.logger.info(f"Streaming data from {file_path} in chunks of {chunk_size} rows")
        
        try:
            # Use pandas chunking capability
            chunk_iter = pd.read_csv(file_path, chunksize=chunk_size, **read_kwargs)
            
            for i, chunk in enumerate(chunk_iter):
                # Monitor memory usage
                if i % 10 == 0:
                    memory_usage = self.memory_monitor.get_memory_usage()
                    self.logger.debug(f"Processed {i} chunks, memory usage: {memory_usage:.1f}%")
                    
                    # Check memory threshold
                    if not self.memory_monitor.check_memory_threshold():
                        self.logger.warning("High memory usage detected, forcing garbage collection")
                        gc.collect()
                
                yield chunk
        
        except Exception as e:
            raise DataValidationError(
                f"Failed to stream data from {file_path}",
                context={"file_path": str(file_path), "chunk_size": chunk_size},
                cause=e
            )
    
    def process_streaming(self,
                         data_source: Union[str, Path, Iterator[pd.DataFrame]],
                         processing_func: Callable[[pd.DataFrame], Any],
                         aggregation_func: Optional[Callable[[List[Any]], Any]] = None) -> Any:
        """
        Process streaming data with a given function.
        
        Args:
            data_source: File path or iterator of DataFrames
            processing_func: Function to apply to each chunk
            aggregation_func: Function to aggregate results from all chunks
            
        Returns:
            Aggregated result
        """
        results = []
        total_chunks = 0
        total_rows = 0
        
        try:
            # Handle different data sources
            if isinstance(data_source, (str, Path)):
                chunk_iterator = self.stream_from_file(data_source)
            else:
                chunk_iterator = data_source
            
            # Process each chunk
            for chunk in chunk_iterator:
                result = processing_func(chunk)
                results.append(result)
                
                total_chunks += 1
                total_rows += len(chunk)
                
                # Log progress periodically
                if total_chunks % 100 == 0:
                    self.logger.info(f"Processed {total_chunks} chunks, {total_rows:,} total rows")
            
            self.logger.info(f"Streaming processing complete: {total_chunks} chunks, {total_rows:,} total rows")
            
            # Aggregate results if aggregation function provided
            if aggregation_func:
                return aggregation_func(results)
            else:
                return results
        
        except Exception as e:
            raise ComputationError(
                "Failed during streaming data processing",
                operation="streaming_processing",
                context={"total_chunks": total_chunks, "total_rows": total_rows},
                cause=e
            )


class DaskDataProcessor:
    """Use Dask for distributed data processing on large datasets."""
    
    def __init__(self, config: Optional[DataProcessingConfig] = None):
        self.config = config or DataProcessingConfig()
        self.logger = get_logger("causallm.dask_processor", level="INFO")
        self._client = None
    
    def setup_dask_cluster(self, n_workers: Optional[int] = None):
        """Setup Dask cluster for distributed processing."""
        try:
            from dask.distributed import Client, LocalCluster
            
            if n_workers is None:
                n_workers = min(os.cpu_count() or 1, 4)
            
            # Create local cluster
            cluster = LocalCluster(
                n_workers=n_workers,
                threads_per_worker=2,
                memory_limit='2GB',  # Limit memory per worker
                silence_logs=False
            )
            
            self._client = Client(cluster)
            self.logger.info(f"Dask cluster started with {n_workers} workers")
            
        except ImportError:
            self.logger.warning("Dask not available, falling back to pandas processing")
            self.config.use_dask = False
        except Exception as e:
            self.logger.error(f"Failed to setup Dask cluster: {e}")
            self.config.use_dask = False
    
    def load_large_dataset(self, file_path: Union[str, Path], **kwargs) -> dd.DataFrame:
        """Load large dataset using Dask."""
        try:
            # Use Dask to read the file
            ddf = dd.read_csv(file_path, **kwargs)
            self.logger.info(f"Loaded dataset with Dask: {len(ddf.columns)} columns")
            return ddf
            
        except Exception as e:
            raise DataValidationError(
                f"Failed to load dataset with Dask from {file_path}",
                cause=e
            )
    
    def process_with_dask(self, 
                         ddf: dd.DataFrame,
                         processing_func: Callable,
                         compute: bool = True) -> Union[dd.DataFrame, Any]:
        """
        Process Dask DataFrame with given function.
        
        Args:
            ddf: Dask DataFrame
            processing_func: Function to apply
            compute: Whether to compute result immediately
            
        Returns:
            Processed result
        """
        try:
            result = processing_func(ddf)
            
            if compute and hasattr(result, 'compute'):
                self.logger.info("Computing Dask result...")
                return result.compute()
            
            return result
            
        except Exception as e:
            raise ComputationError(
                "Failed during Dask processing",
                operation="dask_processing",
                cause=e
            )
    
    def cleanup_dask(self):
        """Cleanup Dask cluster."""
        if self._client:
            self._client.close()
            self.logger.info("Dask cluster closed")


# Utility functions for common operations

def efficient_correlation_matrix(data: pd.DataFrame, 
                                chunk_size: int = 10000,
                                method: str = 'pearson') -> pd.DataFrame:
    """
    Compute correlation matrix efficiently for large datasets.
    
    Args:
        data: Input DataFrame
        chunk_size: Size of chunks for processing
        method: Correlation method ('pearson', 'spearman', 'kendall')
        
    Returns:
        Correlation matrix
    """
    logger = get_logger("causallm.correlation", level="INFO")
    
    if len(data) <= chunk_size:
        # Small dataset, compute directly
        return data.corr(method=method)
    
    # For large datasets, use chunked approach
    logger.info(f"Computing correlation matrix for large dataset ({len(data):,} rows)")
    
    try:
        # Use numpy for efficiency
        numeric_data = data.select_dtypes(include=[np.number])
        
        if len(numeric_data.columns) == 0:
            raise DataValidationError("No numeric columns found for correlation computation")
        
        # Compute correlation using numpy (more memory efficient)
        corr_matrix = np.corrcoef(numeric_data.values.T)
        
        # Convert back to pandas DataFrame
        result = pd.DataFrame(
            corr_matrix,
            index=numeric_data.columns,
            columns=numeric_data.columns
        )
        
        logger.info("Correlation matrix computed successfully")
        return result
        
    except Exception as e:
        raise ComputationError(
            "Failed to compute correlation matrix",
            operation="correlation_computation",
            cause=e
        )


def memory_efficient_groupby(data: pd.DataFrame,
                           groupby_cols: List[str],
                           agg_func: Union[str, Dict[str, str]],
                           chunk_size: int = 50000) -> pd.DataFrame:
    """
    Perform memory-efficient groupby operations on large datasets.
    
    Args:
        data: Input DataFrame
        groupby_cols: Columns to group by
        agg_func: Aggregation function(s)
        chunk_size: Size of chunks for processing
        
    Returns:
        Grouped and aggregated DataFrame
    """
    logger = get_logger("causallm.groupby", level="INFO")
    
    if len(data) <= chunk_size:
        # Small dataset, compute directly
        return data.groupby(groupby_cols).agg(agg_func)
    
    logger.info(f"Performing memory-efficient groupby on {len(data):,} rows")
    
    try:
        chunker = DataChunker()
        partial_results = []
        
        # Process chunks and collect partial results
        for chunk_id, chunk in chunker.chunk_dataframe(data, chunk_size):
            partial_result = chunk.groupby(groupby_cols).agg(agg_func)
            partial_results.append(partial_result)
        
        # Combine partial results
        if len(partial_results) == 1:
            return partial_results[0]
        
        # Concatenate and re-aggregate
        combined = pd.concat(partial_results)
        final_result = combined.groupby(level=groupby_cols).agg(agg_func)
        
        logger.info("Memory-efficient groupby completed successfully")
        return final_result
        
    except Exception as e:
        raise ComputationError(
            "Failed during memory-efficient groupby",
            operation="groupby_operation",
            cause=e
        )