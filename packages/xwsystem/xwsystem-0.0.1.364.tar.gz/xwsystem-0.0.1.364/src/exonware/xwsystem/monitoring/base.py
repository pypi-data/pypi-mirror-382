#exonware/xsystem/monitoring/base.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.364
Generation Date: September 04, 2025

Monitoring module base classes - abstract classes for monitoring functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable
from .contracts import MetricType, AlertLevel, MonitorState, HealthStatus


class APerformanceMonitorBase(ABC):
    """Abstract base class for performance monitoring."""
    
    def __init__(self, monitor_name: str):
        """
        Initialize performance monitor.
        
        Args:
            monitor_name: Name of the performance monitor
        """
        self.monitor_name = monitor_name
        self._metrics: Dict[str, Any] = {}
        self._thresholds: Dict[str, float] = {}
        self._alerts: List[Dict[str, Any]] = []
    
    @abstractmethod
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        pass
    
    @abstractmethod
    def is_monitoring(self) -> bool:
        """Check if monitoring is active."""
        pass
    
    @abstractmethod
    def record_metric(self, metric_name: str, value: float, metric_type: MetricType = MetricType.GAUGE) -> None:
        """Record performance metric."""
        pass
    
    @abstractmethod
    def get_metric(self, metric_name: str) -> Optional[float]:
        """Get metric value."""
        pass
    
    @abstractmethod
    def get_all_metrics(self) -> Dict[str, float]:
        """Get all metrics."""
        pass
    
    @abstractmethod
    def set_threshold(self, metric_name: str, threshold: float) -> None:
        """Set metric threshold."""
        pass
    
    @abstractmethod
    def check_thresholds(self) -> List[Dict[str, Any]]:
        """Check if any metrics exceed thresholds."""
        pass
    
    @abstractmethod
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        pass


class AMemoryMonitorBase(ABC):
    """Abstract base class for memory monitoring."""
    
    def __init__(self):
        """Initialize memory monitor."""
        self._memory_snapshots: List[Dict[str, Any]] = []
        self._leak_detection_enabled = False
    
    @abstractmethod
    def start_monitoring(self) -> None:
        """Start memory monitoring."""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop memory monitoring."""
        pass
    
    @abstractmethod
    def take_snapshot(self) -> Dict[str, Any]:
        """Take memory snapshot."""
        pass
    
    @abstractmethod
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage."""
        pass
    
    @abstractmethod
    def detect_memory_leaks(self) -> List[Dict[str, Any]]:
        """Detect potential memory leaks."""
        pass
    
    @abstractmethod
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        pass
    
    @abstractmethod
    def cleanup_memory(self) -> int:
        """Cleanup memory and return bytes freed."""
        pass
    
    @abstractmethod
    def get_garbage_collection_stats(self) -> Dict[str, Any]:
        """Get garbage collection statistics."""
        pass
    
    @abstractmethod
    def force_garbage_collection(self) -> None:
        """Force garbage collection."""
        pass


class AMetricsBase(ABC):
    """Abstract base class for metrics collection."""
    
    def __init__(self, metrics_name: str):
        """
        Initialize metrics collector.
        
        Args:
            metrics_name: Name of the metrics collector
        """
        self.metrics_name = metrics_name
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
        self._timers: Dict[str, List[float]] = {}
    
    @abstractmethod
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment counter metric."""
        pass
    
    @abstractmethod
    def set_gauge(self, name: str, value: float) -> None:
        """Set gauge metric."""
        pass
    
    @abstractmethod
    def record_histogram(self, name: str, value: float) -> None:
        """Record histogram metric."""
        pass
    
    @abstractmethod
    def record_timer(self, name: str, duration: float) -> None:
        """Record timer metric."""
        pass
    
    @abstractmethod
    def get_counter(self, name: str) -> int:
        """Get counter value."""
        pass
    
    @abstractmethod
    def get_gauge(self, name: str) -> float:
        """Get gauge value."""
        pass
    
    @abstractmethod
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics."""
        pass
    
    @abstractmethod
    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """Get timer statistics."""
        pass
    
    @abstractmethod
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics."""
        pass
    
    @abstractmethod
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        pass


class AErrorRecoveryBase(ABC):
    """Abstract base class for error recovery."""
    
    def __init__(self):
        """Initialize error recovery."""
        self._recovery_strategies: Dict[str, Callable] = {}
        self._circuit_breakers: Dict[str, Dict[str, Any]] = {}
    
    @abstractmethod
    def register_recovery_strategy(self, error_type: str, strategy: Callable) -> None:
        """Register error recovery strategy."""
        pass
    
    @abstractmethod
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Handle error with recovery strategy."""
        pass
    
    @abstractmethod
    def create_circuit_breaker(self, name: str, failure_threshold: int = 5, 
                              recovery_timeout: int = 60) -> None:
        """Create circuit breaker."""
        pass
    
    @abstractmethod
    def is_circuit_open(self, name: str) -> bool:
        """Check if circuit breaker is open."""
        pass
    
    @abstractmethod
    def record_success(self, name: str) -> None:
        """Record successful operation."""
        pass
    
    @abstractmethod
    def record_failure(self, name: str) -> None:
        """Record failed operation."""
        pass
    
    @abstractmethod
    def get_circuit_state(self, name: str) -> Dict[str, Any]:
        """Get circuit breaker state."""
        pass


class ASystemMonitorBase(ABC):
    """Abstract base class for system monitoring."""
    
    def __init__(self):
        """Initialize system monitor."""
        self._monitoring_enabled = False
        self._system_metrics: Dict[str, Any] = {}
    
    @abstractmethod
    def start_system_monitoring(self) -> None:
        """Start system monitoring."""
        pass
    
    @abstractmethod
    def stop_system_monitoring(self) -> None:
        """Stop system monitoring."""
        pass
    
    @abstractmethod
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        pass
    
    @abstractmethod
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics."""
        pass
    
    @abstractmethod
    def get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage statistics."""
        pass
    
    @abstractmethod
    def get_network_usage(self) -> Dict[str, float]:
        """Get network usage statistics."""
        pass
    
    @abstractmethod
    def get_system_load(self) -> float:
        """Get system load average."""
        pass
    
    @abstractmethod
    def get_process_count(self) -> int:
        """Get number of running processes."""
        pass
    
    @abstractmethod
    def get_system_uptime(self) -> float:
        """Get system uptime in seconds."""
        pass
    
    @abstractmethod
    def get_system_health(self) -> HealthStatus:
        """Get overall system health status."""
        pass
    
    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        pass
