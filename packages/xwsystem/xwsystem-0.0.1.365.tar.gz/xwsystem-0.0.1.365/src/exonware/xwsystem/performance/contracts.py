"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.365
Generation Date: September 04, 2025

Performance module contracts - interfaces and enums for performance management.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable
from contextlib import AbstractContextManager

# Import enums from types module
from .types import (
    PerformanceMetric,
    PerformanceLevel,
    OptimizationStrategy
)


class IPerformanceManager(ABC):
    """Interface for performance management."""
    
    @abstractmethod
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        pass
    
    @abstractmethod
    def get_metrics(self, metric_type: PerformanceMetric) -> Dict[str, Any]:
        """Get performance metrics."""
        pass
    
    @abstractmethod
    def set_threshold(self, metric_type: PerformanceMetric, threshold: float) -> None:
        """Set performance threshold."""
        pass
    
    @abstractmethod
    def is_threshold_exceeded(self, metric_type: PerformanceMetric) -> bool:
        """Check if threshold is exceeded."""
        pass


class IPerformanceProfiler(ABC):
    """Interface for performance profiling."""
    
    @abstractmethod
    def profile_function(self, func: Callable) -> Callable:
        """Profile function execution."""
        pass
    
    @abstractmethod
    def profile_context(self, name: str) -> AbstractContextManager:
        """Profile code context."""
        pass
    
    @abstractmethod
    def get_profile_results(self) -> Dict[str, Any]:
        """Get profiling results."""
        pass
    
    @abstractmethod
    def clear_results(self) -> None:
        """Clear profiling results."""
        pass


class IPerformanceOptimizer(ABC):
    """Interface for performance optimization."""
    
    @abstractmethod
    def optimize_memory(self) -> None:
        """Optimize memory usage."""
        pass
    
    @abstractmethod
    def optimize_cpu(self) -> None:
        """Optimize CPU usage."""
        pass
    
    @abstractmethod
    def optimize_io(self) -> None:
        """Optimize I/O operations."""
        pass
    
    @abstractmethod
    def set_optimization_strategy(self, strategy: OptimizationStrategy) -> None:
        """Set optimization strategy."""
        pass
    
    @abstractmethod
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations."""
        pass


class IPerformanceBenchmark(ABC):
    """Interface for performance benchmarking."""
    
    @abstractmethod
    def benchmark_function(self, func: Callable, iterations: int = 1000) -> Dict[str, float]:
        """Benchmark function performance."""
        pass
    
    @abstractmethod
    def benchmark_comparison(self, functions: List[Callable], iterations: int = 1000) -> Dict[str, Dict[str, float]]:
        """Compare function performance."""
        pass
    
    @abstractmethod
    def benchmark_system(self) -> Dict[str, float]:
        """Benchmark system performance."""
        pass
    
    @abstractmethod
    def save_benchmark_results(self, results: Dict[str, Any], filename: str) -> None:
        """Save benchmark results."""
        pass


class IPerformanceCache(ABC):
    """Interface for performance caching."""
    
    @abstractmethod
    def cache_result(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Cache computation result."""
        pass
    
    @abstractmethod
    def get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result."""
        pass
    
    @abstractmethod
    def invalidate_cache(self, key: str) -> None:
        """Invalidate cache entry."""
        pass
    
    @abstractmethod
    def clear_cache(self) -> None:
        """Clear all cache."""
        pass
    
    @abstractmethod
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class PerformanceConfig:
    """Performance configuration class."""
    
    def __init__(
        self,
        mode: Optional[str] = None,
        cpu_limit: Optional[float] = None,
        memory_limit: Optional[float] = None,
        io_limit: Optional[float] = None,
        optimization_strategy: Optional[OptimizationStrategy] = None,
        monitoring_enabled: bool = True,
        cache_enabled: bool = True,
        cache_size: int = 1000,
        **kwargs
    ):
        """Initialize performance configuration.
        
        Args:
            mode: Performance mode
            cpu_limit: CPU usage limit (0.0-1.0)
            memory_limit: Memory usage limit (0.0-1.0)
            io_limit: I/O usage limit (0.0-1.0)
            optimization_strategy: Optimization strategy
            monitoring_enabled: Enable performance monitoring
            cache_enabled: Enable caching
            cache_size: Cache size limit
            **kwargs: Additional configuration options
        """
        self.mode = mode
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.io_limit = io_limit
        self.optimization_strategy = optimization_strategy or OptimizationStrategy.BALANCED
        self.monitoring_enabled = monitoring_enabled
        self.cache_enabled = cache_enabled
        self.cache_size = cache_size
        self.extra_config = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'mode': self.mode,
            'cpu_limit': self.cpu_limit,
            'memory_limit': self.memory_limit,
            'io_limit': self.io_limit,
            'optimization_strategy': self.optimization_strategy.value if self.optimization_strategy else None,
            'monitoring_enabled': self.monitoring_enabled,
            'cache_enabled': self.cache_enabled,
            'cache_size': self.cache_size,
            **self.extra_config
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PerformanceConfig':
        """Create configuration from dictionary."""
        optimization_strategy = None
        if 'optimization_strategy' in config_dict and config_dict['optimization_strategy']:
            optimization_strategy = OptimizationStrategy(config_dict['optimization_strategy'])
        
        return cls(
            mode=config_dict.get('mode'),
            cpu_limit=config_dict.get('cpu_limit'),
            memory_limit=config_dict.get('memory_limit'),
            io_limit=config_dict.get('io_limit'),
            optimization_strategy=optimization_strategy,
            monitoring_enabled=config_dict.get('monitoring_enabled', True),
            cache_enabled=config_dict.get('cache_enabled', True),
            cache_size=config_dict.get('cache_size', 1000),
            **{k: v for k, v in config_dict.items() 
               if k not in ['mode', 'cpu_limit', 'memory_limit', 'io_limit', 
                           'optimization_strategy', 'monitoring_enabled', 
                           'cache_enabled', 'cache_size']}
        )