"""
Pipeline Metrics Collection and Reporting Module.

This module provides utilities for collecting, aggregating, and reporting
metrics from data pipelines. It supports various output formats including
JSON, Prometheus exposition format, and direct database storage.

Usage:
    from lib.metrics import PipelineMetrics, MetricType

    metrics = PipelineMetrics("my_pipeline", "daily_etl")
    metrics.record_counter("rows_processed", 1000)
    metrics.record_gauge("processing_time_seconds", 45.5)
    metrics.record_histogram("batch_size", [100, 200, 150, 300])

    report = metrics.get_report()
"""
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
import threading


class MetricType(Enum):
    """Types of metrics that can be collected."""

    COUNTER = "counter"  # Monotonically increasing value
    GAUGE = "gauge"  # Value that can go up or down
    HISTOGRAM = "histogram"  # Distribution of values
    SUMMARY = "summary"  # Similar to histogram with quantiles
    TIMER = "timer"  # Duration measurements


@dataclass
class Metric:
    """A single metric measurement."""

    name: str
    value: Union[int, float, List[float]]
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        result = {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.labels:
            result["labels"] = self.labels
        if self.description:
            result["description"] = self.description
        return result

    def to_prometheus(self) -> str:
        """Convert metric to Prometheus exposition format."""
        labels_str = ""
        if self.labels:
            label_pairs = [f'{k}="{v}"' for k, v in self.labels.items()]
            labels_str = "{" + ",".join(label_pairs) + "}"

        lines = []
        if self.description:
            lines.append(f"# HELP {self.name} {self.description}")
        lines.append(f"# TYPE {self.name} {self.metric_type.value}")

        if self.metric_type == MetricType.HISTOGRAM:
            # For histograms, output bucket counts
            if isinstance(self.value, list):
                sorted_values = sorted(self.value)
                buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, float("inf")]
                for bucket in buckets:
                    count = sum(1 for v in sorted_values if v <= bucket)
                    bucket_label = f'+Inf' if bucket == float("inf") else str(bucket)
                    lines.append(f'{self.name}_bucket{{le="{bucket_label}"{labels_str[1:-1] if labels_str else ""}}} {count}')
                lines.append(f"{self.name}_sum{labels_str} {sum(self.value)}")
                lines.append(f"{self.name}_count{labels_str} {len(self.value)}")
        else:
            lines.append(f"{self.name}{labels_str} {self.value}")

        return "\n".join(lines)


@dataclass
class StageMetrics:
    """Metrics for a pipeline stage."""

    name: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    input_rows: int = 0
    output_rows: int = 0
    status: str = "pending"
    error_message: Optional[str] = None
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate stage duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert stage metrics to dictionary."""
        return {
            "name": self.name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "input_rows": self.input_rows,
            "output_rows": self.output_rows,
            "status": self.status,
            "error_message": self.error_message,
            "custom_metrics": self.custom_metrics,
        }


class PipelineMetrics:
    """
    Main class for collecting and managing pipeline metrics.

    This class is thread-safe and can be used across multiple workers.
    """

    def __init__(
        self,
        pipeline_name: str,
        run_id: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize pipeline metrics collector.

        Args:
            pipeline_name: Name of the pipeline
            run_id: Unique identifier for this run (auto-generated if not provided)
            labels: Common labels to apply to all metrics
        """
        self.pipeline_name = pipeline_name
        self.run_id = run_id or f"{pipeline_name}_{int(time.time())}"
        self.common_labels = labels or {}
        self.common_labels["pipeline"] = pipeline_name
        self.common_labels["run_id"] = self.run_id

        self._metrics: List[Metric] = []
        self._stages: Dict[str, StageMetrics] = {}
        self._lock = threading.Lock()

        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.status = "running"

    def record_counter(
        self,
        name: str,
        value: int = 1,
        labels: Optional[Dict[str, str]] = None,
        description: str = "",
    ) -> None:
        """Record a counter metric (monotonically increasing)."""
        all_labels = {**self.common_labels, **(labels or {})}
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            labels=all_labels,
            description=description,
        )
        with self._lock:
            self._metrics.append(metric)

    def record_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        description: str = "",
    ) -> None:
        """Record a gauge metric (can go up or down)."""
        all_labels = {**self.common_labels, **(labels or {})}
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=all_labels,
            description=description,
        )
        with self._lock:
            self._metrics.append(metric)

    def record_histogram(
        self,
        name: str,
        values: List[float],
        labels: Optional[Dict[str, str]] = None,
        description: str = "",
    ) -> None:
        """Record a histogram metric (distribution of values)."""
        all_labels = {**self.common_labels, **(labels or {})}
        metric = Metric(
            name=name,
            value=values,
            metric_type=MetricType.HISTOGRAM,
            labels=all_labels,
            description=description,
        )
        with self._lock:
            self._metrics.append(metric)

    def record_timer(
        self,
        name: str,
        duration_seconds: float,
        labels: Optional[Dict[str, str]] = None,
        description: str = "",
    ) -> None:
        """Record a timer metric (duration measurement)."""
        all_labels = {**self.common_labels, **(labels or {})}
        metric = Metric(
            name=name,
            value=duration_seconds,
            metric_type=MetricType.TIMER,
            labels=all_labels,
            description=description,
        )
        with self._lock:
            self._metrics.append(metric)

    def start_stage(self, stage_name: str, input_rows: int = 0) -> None:
        """Start tracking a pipeline stage."""
        with self._lock:
            self._stages[stage_name] = StageMetrics(
                name=stage_name,
                start_time=datetime.now(),
                input_rows=input_rows,
                status="running",
            )

    def end_stage(
        self,
        stage_name: str,
        output_rows: int = 0,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        """End tracking a pipeline stage."""
        with self._lock:
            if stage_name in self._stages:
                stage = self._stages[stage_name]
                stage.end_time = datetime.now()
                stage.output_rows = output_rows
                stage.status = status
                stage.error_message = error_message

                # Record stage metrics
                if stage.duration_seconds:
                    self.record_timer(
                        f"pipeline_stage_duration_seconds",
                        stage.duration_seconds,
                        labels={"stage": stage_name},
                        description="Duration of pipeline stage in seconds",
                    )

                self.record_gauge(
                    f"pipeline_stage_input_rows",
                    stage.input_rows,
                    labels={"stage": stage_name},
                    description="Number of input rows for pipeline stage",
                )

                self.record_gauge(
                    f"pipeline_stage_output_rows",
                    stage.output_rows,
                    labels={"stage": stage_name},
                    description="Number of output rows for pipeline stage",
                )

    def add_stage_metric(
        self, stage_name: str, metric_name: str, value: Any
    ) -> None:
        """Add a custom metric to a stage."""
        with self._lock:
            if stage_name in self._stages:
                self._stages[stage_name].custom_metrics[metric_name] = value

    def finish(self, status: str = "success") -> None:
        """Mark the pipeline as finished."""
        self.end_time = datetime.now()
        self.status = status

        # Record overall pipeline metrics
        duration = (self.end_time - self.start_time).total_seconds()
        self.record_timer(
            "pipeline_duration_seconds",
            duration,
            description="Total pipeline execution time",
        )

        self.record_counter(
            f"pipeline_runs_total",
            1,
            labels={"status": status},
            description="Total number of pipeline runs",
        )

    def get_report(self) -> Dict[str, Any]:
        """Generate a complete metrics report."""
        return {
            "pipeline_name": self.pipeline_name,
            "run_id": self.run_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (
                (self.end_time - self.start_time).total_seconds()
                if self.end_time
                else None
            ),
            "status": self.status,
            "stages": {name: stage.to_dict() for name, stage in self._stages.items()},
            "metrics": [m.to_dict() for m in self._metrics],
            "labels": self.common_labels,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert metrics to JSON string."""
        return json.dumps(self.get_report(), indent=indent, default=str)

    def to_prometheus(self) -> str:
        """Convert all metrics to Prometheus exposition format."""
        lines = []
        for metric in self._metrics:
            lines.append(metric.to_prometheus())
            lines.append("")
        return "\n".join(lines)

    def save_to_file(self, path: str, format: str = "json") -> None:
        """
        Save metrics to a file.

        Args:
            path: File path to save metrics
            format: Output format ('json' or 'prometheus')
        """
        content = self.to_json() if format == "json" else self.to_prometheus()
        with open(path, "w") as f:
            f.write(content)


class TimerContext:
    """Context manager for timing operations."""

    def __init__(
        self,
        metrics: PipelineMetrics,
        name: str,
        labels: Optional[Dict[str, str]] = None,
    ):
        self.metrics = metrics
        self.name = name
        self.labels = labels
        self.start_time: Optional[float] = None

    def __enter__(self) -> "TimerContext":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics.record_timer(self.name, duration, self.labels)


def timed(metrics: PipelineMetrics, name: str, labels: Optional[Dict[str, str]] = None):
    """
    Decorator to time function execution.

    Usage:
        @timed(metrics, "my_function_duration")
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start
                metrics.record_timer(name, duration, labels)
        return wrapper
    return decorator


class MetricsRegistry:
    """
    Global registry for pipeline metrics.

    Useful for aggregating metrics across multiple pipeline components.
    """

    _instance: Optional["MetricsRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "MetricsRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._pipelines: Dict[str, PipelineMetrics] = {}
        return cls._instance

    def register(self, metrics: PipelineMetrics) -> None:
        """Register a pipeline metrics collector."""
        with self._lock:
            self._pipelines[metrics.run_id] = metrics

    def get(self, run_id: str) -> Optional[PipelineMetrics]:
        """Get metrics for a specific run."""
        return self._pipelines.get(run_id)

    def get_all(self) -> List[PipelineMetrics]:
        """Get all registered metrics collectors."""
        return list(self._pipelines.values())

    def clear(self) -> None:
        """Clear all registered metrics."""
        with self._lock:
            self._pipelines.clear()

    def get_aggregate_report(self) -> Dict[str, Any]:
        """Get aggregate report for all pipelines."""
        return {
            "total_pipelines": len(self._pipelines),
            "pipelines": [p.get_report() for p in self._pipelines.values()],
        }


# Convenience function to create and register metrics
def create_pipeline_metrics(
    pipeline_name: str,
    run_id: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
    register: bool = True,
) -> PipelineMetrics:
    """
    Create a new pipeline metrics collector.

    Args:
        pipeline_name: Name of the pipeline
        run_id: Optional run identifier
        labels: Optional common labels
        register: Whether to register with global registry

    Returns:
        PipelineMetrics instance
    """
    metrics = PipelineMetrics(pipeline_name, run_id, labels)
    if register:
        MetricsRegistry().register(metrics)
    return metrics
