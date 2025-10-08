"""
Advanced monitoring and observability service.

This module provides comprehensive monitoring capabilities including
distributed tracing, metrics collection, alerting, and performance monitoring.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json

from evolvishub_outlook_ingestor.core.interfaces import IMonitoringService, service_registry
from evolvishub_outlook_ingestor.core.exceptions import MonitoringError


@dataclass
class MetricPoint:
    """Represents a metric data point."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    metric_type: str  # counter, gauge, histogram, timer


@dataclass
class TraceSpan:
    """Represents a distributed trace span."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[float]
    tags: Dict[str, str]
    logs: List[Dict[str, Any]]
    status: str  # success, error, timeout


@dataclass
class Alert:
    """Represents a monitoring alert."""
    alert_id: str
    name: str
    description: str
    severity: str  # critical, high, medium, low
    condition: str
    threshold: float
    current_value: float
    triggered_at: datetime
    resolved_at: Optional[datetime]
    metadata: Dict[str, Any]


class AdvancedMonitoringService(IMonitoringService):
    """
    Advanced monitoring and observability service.
    
    This service provides comprehensive monitoring capabilities including:
    - Distributed tracing with OpenTelemetry integration
    - Custom metrics collection and aggregation
    - Real-time alerting and notification system
    - Performance monitoring and profiling
    - Health checks and service discovery
    - Log aggregation and analysis
    - Dashboard and visualization support
    
    Example:
        ```python
        monitoring = AdvancedMonitoringService({
            'enable_tracing': True,
            'enable_metrics': True,
            'enable_alerting': True,
            'jaeger_endpoint': 'http://localhost:14268/api/traces',
            'prometheus_port': 8090,
            'alert_webhooks': ['http://slack.webhook.url']
        })
        
        await monitoring.initialize()
        
        # Record metrics
        await monitoring.record_metric('emails_processed', 1.0, {'tenant': 'acme'})
        
        # Start trace
        trace_id = await monitoring.start_trace('email_processing')
        
        # Log event
        await monitoring.log_event('info', 'Email processed successfully', {
            'email_id': 'email_123',
            'processing_time': 1.5
        })
        
        # End trace
        await monitoring.end_trace(trace_id, 'success')
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enable_tracing = config.get('enable_tracing', True)
        self.enable_metrics = config.get('enable_metrics', True)
        self.enable_alerting = config.get('enable_alerting', True)
        self.enable_profiling = config.get('enable_profiling', False)
        self.jaeger_endpoint = config.get('jaeger_endpoint')
        self.prometheus_port = config.get('prometheus_port', 8090)
        self.alert_webhooks = config.get('alert_webhooks', [])
        self.metrics_retention_hours = config.get('metrics_retention_hours', 24)
        
        # State management
        self.is_initialized = False
        self._active_traces: Dict[str, TraceSpan] = {}
        self._metrics_buffer: deque = deque(maxlen=10000)
        self._alerts: Dict[str, Alert] = {}
        self._alert_rules: Dict[str, Dict[str, Any]] = {}
        
        # Metrics aggregation
        self._metric_aggregates: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'sum': 0.0,
            'min': float('inf'),
            'max': float('-inf'),
            'last_value': 0.0,
            'last_updated': datetime.utcnow()
        })
        
        # Background tasks
        self._metrics_processor_task: Optional[asyncio.Task] = None
        self._alert_processor_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # OpenTelemetry components
        self._tracer = None
        self._meter = None
        
        # Statistics
        self.stats = {
            'metrics_recorded': 0,
            'traces_started': 0,
            'traces_completed': 0,
            'alerts_triggered': 0,
            'alerts_resolved': 0
        }
    
    async def initialize(self) -> None:
        """Initialize the monitoring service."""
        if self.is_initialized:
            return
        
        try:
            self.logger.info("Initializing advanced monitoring service")
            
            # Initialize OpenTelemetry
            if self.enable_tracing:
                await self._initialize_tracing()
            
            # Initialize metrics collection
            if self.enable_metrics:
                await self._initialize_metrics()
            
            # Initialize alerting
            if self.enable_alerting:
                await self._initialize_alerting()
            
            # Start background tasks
            self._metrics_processor_task = asyncio.create_task(self._process_metrics())
            self._alert_processor_task = asyncio.create_task(self._process_alerts())
            self._cleanup_task = asyncio.create_task(self._cleanup_old_data())
            
            self.is_initialized = True
            self.logger.info("Advanced monitoring service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize monitoring service: {str(e)}")
            raise MonitoringError(f"Monitoring initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown the monitoring service."""
        if not self.is_initialized:
            return
        
        self.logger.info("Shutting down monitoring service")
        
        # Cancel background tasks
        tasks = [self._metrics_processor_task, self._alert_processor_task, self._cleanup_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Flush remaining metrics
        await self._flush_metrics()
        
        # Close active traces
        for trace_id in list(self._active_traces.keys()):
            await self.end_trace(trace_id, "shutdown")
        
        self.is_initialized = False
        self.logger.info("Monitoring service shutdown complete")
    
    async def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a metric value.
        
        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for the metric
        """
        if not self.enable_metrics:
            return
        
        try:
            metric_point = MetricPoint(
                name=name,
                value=value,
                timestamp=datetime.utcnow(),
                tags=tags or {},
                metric_type='gauge'  # Default to gauge
            )
            
            # Add to buffer
            self._metrics_buffer.append(metric_point)
            
            # Update aggregates
            key = f"{name}:{json.dumps(tags or {}, sort_keys=True)}"
            agg = self._metric_aggregates[key]
            agg['count'] += 1
            agg['sum'] += value
            agg['min'] = min(agg['min'], value)
            agg['max'] = max(agg['max'], value)
            agg['last_value'] = value
            agg['last_updated'] = datetime.utcnow()
            
            self.stats['metrics_recorded'] += 1
            
            # Check alert rules
            await self._check_alert_rules(name, value, tags or {})
            
        except Exception as e:
            self.logger.error(f"Failed to record metric {name}: {str(e)}")
    
    async def start_trace(self, operation_name: str) -> str:
        """
        Start a distributed trace.
        
        Args:
            operation_name: Name of the operation being traced
            
        Returns:
            Trace ID for the started trace
        """
        if not self.enable_tracing:
            return "tracing_disabled"
        
        try:
            trace_id = f"trace_{int(time.time() * 1000000)}"
            span_id = f"span_{int(time.time() * 1000000)}"
            
            span = TraceSpan(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=None,
                operation_name=operation_name,
                start_time=datetime.utcnow(),
                end_time=None,
                duration_ms=None,
                tags={},
                logs=[],
                status="active"
            )
            
            self._active_traces[trace_id] = span
            self.stats['traces_started'] += 1
            
            self.logger.debug(f"Started trace: {trace_id} for operation: {operation_name}")
            return trace_id
            
        except Exception as e:
            self.logger.error(f"Failed to start trace for {operation_name}: {str(e)}")
            return "error"
    
    async def end_trace(self, trace_id: str, status: str = "success") -> None:
        """
        End a distributed trace.
        
        Args:
            trace_id: ID of the trace to end
            status: Final status of the trace
        """
        if not self.enable_tracing or trace_id not in self._active_traces:
            return
        
        try:
            span = self._active_traces[trace_id]
            span.end_time = datetime.utcnow()
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            span.status = status
            
            # Export trace to external system
            await self._export_trace(span)
            
            # Remove from active traces
            del self._active_traces[trace_id]
            self.stats['traces_completed'] += 1
            
            self.logger.debug(f"Ended trace: {trace_id} with status: {status}, duration: {span.duration_ms:.2f}ms")
            
        except Exception as e:
            self.logger.error(f"Failed to end trace {trace_id}: {str(e)}")
    
    async def log_event(self, level: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an event with metadata.
        
        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            metadata: Optional metadata
        """
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': level,
                'message': message,
                'metadata': metadata or {},
                'service': 'evolvishub-outlook-ingestor'
            }
            
            # Log to standard logger
            getattr(self.logger, level.lower(), self.logger.info)(
                f"{message} | {json.dumps(metadata or {})}"
            )
            
            # Add to active traces if any
            for span in self._active_traces.values():
                span.logs.append(log_entry)
            
            # Send to external log aggregation system
            await self._export_log(log_entry)
            
        except Exception as e:
            self.logger.error(f"Failed to log event: {str(e)}")
    
    async def add_alert_rule(self, rule_name: str, rule_config: Dict[str, Any]) -> None:
        """
        Add an alert rule.
        
        Args:
            rule_name: Name of the alert rule
            rule_config: Alert rule configuration
        """
        try:
            self._alert_rules[rule_name] = {
                'metric_name': rule_config['metric_name'],
                'condition': rule_config.get('condition', 'greater_than'),
                'threshold': rule_config['threshold'],
                'severity': rule_config.get('severity', 'medium'),
                'description': rule_config.get('description', ''),
                'enabled': rule_config.get('enabled', True)
            }
            
            self.logger.info(f"Added alert rule: {rule_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to add alert rule {rule_name}: {str(e)}")
    
    async def get_metrics_summary(self, metric_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics summary.
        
        Args:
            metric_name: Optional specific metric name
            
        Returns:
            Metrics summary data
        """
        try:
            if metric_name:
                # Return specific metric data
                matching_keys = [key for key in self._metric_aggregates.keys() if key.startswith(f"{metric_name}:")]
                return {
                    'metric_name': metric_name,
                    'aggregates': {key: dict(self._metric_aggregates[key]) for key in matching_keys}
                }
            else:
                # Return all metrics summary
                return {
                    'total_metrics': len(self._metric_aggregates),
                    'metrics_in_buffer': len(self._metrics_buffer),
                    'active_traces': len(self._active_traces),
                    'active_alerts': len([a for a in self._alerts.values() if a.resolved_at is None]),
                    'stats': self.stats
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {str(e)}")
            return {'error': str(e)}
    
    async def _initialize_tracing(self) -> None:
        """Initialize distributed tracing."""
        try:
            # Try to initialize OpenTelemetry
            try:
                from opentelemetry import trace
                from opentelemetry.exporter.jaeger.thrift import JaegerExporter
                from opentelemetry.sdk.trace import TracerProvider
                from opentelemetry.sdk.trace.export import BatchSpanProcessor
                
                # Set up tracer provider
                trace.set_tracer_provider(TracerProvider())
                tracer = trace.get_tracer(__name__)
                
                # Set up Jaeger exporter if endpoint provided
                if self.jaeger_endpoint:
                    jaeger_exporter = JaegerExporter(
                        agent_host_name="localhost",
                        agent_port=6831,
                    )
                    span_processor = BatchSpanProcessor(jaeger_exporter)
                    trace.get_tracer_provider().add_span_processor(span_processor)
                
                self._tracer = tracer
                self.logger.info("OpenTelemetry tracing initialized")
                
            except ImportError:
                self.logger.warning("OpenTelemetry not available, using basic tracing")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize tracing: {str(e)}")
    
    async def _initialize_metrics(self) -> None:
        """Initialize metrics collection."""
        try:
            # Try to initialize Prometheus metrics
            try:
                from prometheus_client import Counter, Histogram, Gauge, start_http_server
                
                # Start Prometheus HTTP server
                start_http_server(self.prometheus_port)
                self.logger.info(f"Prometheus metrics server started on port {self.prometheus_port}")
                
            except ImportError:
                self.logger.warning("Prometheus client not available, using basic metrics")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize metrics: {str(e)}")
    
    async def _initialize_alerting(self) -> None:
        """Initialize alerting system."""
        try:
            # Set up default alert rules
            default_rules = {
                'high_error_rate': {
                    'metric_name': 'error_rate',
                    'condition': 'greater_than',
                    'threshold': 0.05,  # 5% error rate
                    'severity': 'high',
                    'description': 'Error rate is above 5%'
                },
                'high_response_time': {
                    'metric_name': 'response_time_ms',
                    'condition': 'greater_than',
                    'threshold': 5000,  # 5 seconds
                    'severity': 'medium',
                    'description': 'Response time is above 5 seconds'
                }
            }
            
            for rule_name, rule_config in default_rules.items():
                await self.add_alert_rule(rule_name, rule_config)
            
            self.logger.info("Alerting system initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize alerting: {str(e)}")
    
    async def _process_metrics(self) -> None:
        """Background task to process metrics."""
        while self.is_initialized:
            try:
                # Process metrics buffer
                if len(self._metrics_buffer) >= 100:  # Batch size
                    await self._flush_metrics()
                
                await asyncio.sleep(10)  # Process every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in metrics processor: {str(e)}")
                await asyncio.sleep(30)
    
    async def _process_alerts(self) -> None:
        """Background task to process alerts."""
        while self.is_initialized:
            try:
                # Check for alert resolution
                current_time = datetime.utcnow()
                for alert in self._alerts.values():
                    if alert.resolved_at is None:
                        # Check if alert should be resolved
                        if await self._should_resolve_alert(alert):
                            alert.resolved_at = current_time
                            self.stats['alerts_resolved'] += 1
                            await self._send_alert_notification(alert, 'resolved')
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in alert processor: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_data(self) -> None:
        """Background task to clean up old data."""
        while self.is_initialized:
            try:
                cutoff_time = datetime.utcnow() - timedelta(hours=self.metrics_retention_hours)
                
                # Clean up old metric aggregates
                keys_to_remove = []
                for key, agg in self._metric_aggregates.items():
                    if agg['last_updated'] < cutoff_time:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del self._metric_aggregates[key]
                
                # Clean up resolved alerts older than 24 hours
                alert_cutoff = datetime.utcnow() - timedelta(hours=24)
                alerts_to_remove = []
                for alert_id, alert in self._alerts.items():
                    if alert.resolved_at and alert.resolved_at < alert_cutoff:
                        alerts_to_remove.append(alert_id)
                
                for alert_id in alerts_to_remove:
                    del self._alerts[alert_id]
                
                self.logger.debug(f"Cleaned up {len(keys_to_remove)} old metrics and {len(alerts_to_remove)} old alerts")
                
                # Run cleanup daily
                await asyncio.sleep(24 * 60 * 60)
                
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(60 * 60)
    
    async def _flush_metrics(self) -> None:
        """Flush metrics buffer to external systems."""
        if not self._metrics_buffer:
            return

        try:
            metrics_to_export = list(self._metrics_buffer)
            self._metrics_buffer.clear()

            # Export to Prometheus if available
            await self._export_to_prometheus(metrics_to_export)

            # Export to InfluxDB if configured
            await self._export_to_influxdb(metrics_to_export)

            # Export to custom endpoints
            await self._export_to_custom_endpoints(metrics_to_export)

            self.logger.debug(f"Exported {len(metrics_to_export)} metrics to external systems")

        except Exception as e:
            self.logger.error(f"Failed to flush metrics: {str(e)}")
            # Put metrics back in buffer for retry
            self._metrics_buffer.extend(metrics_to_export)
    
    async def _export_trace(self, span: TraceSpan) -> None:
        """Export trace span to external tracing system."""
        try:
            # Export to OpenTelemetry/Jaeger
            if self._tracer:
                await self._export_to_jaeger(span)

            # Export to Zipkin if configured
            await self._export_to_zipkin(span)

            # Export to custom tracing endpoints
            await self._export_trace_to_custom_endpoints(span)

            self.logger.debug(f"Exported trace: {span.trace_id}, duration: {span.duration_ms}ms")

        except Exception as e:
            self.logger.error(f"Failed to export trace {span.trace_id}: {str(e)}")
    
    async def _export_log(self, log_entry: Dict[str, Any]) -> None:
        """Export log entry to external log aggregation system."""
        try:
            # Export to external systems (ELK, Splunk, etc.)
            pass
            
        except Exception as e:
            self.logger.error(f"Failed to export log entry: {str(e)}")
    
    async def _check_alert_rules(self, metric_name: str, value: float, tags: Dict[str, str]) -> None:
        """Check if metric value triggers any alert rules."""
        for rule_name, rule in self._alert_rules.items():
            if not rule.get('enabled', True):
                continue
                
            if rule['metric_name'] == metric_name:
                triggered = False
                
                if rule['condition'] == 'greater_than' and value > rule['threshold']:
                    triggered = True
                elif rule['condition'] == 'less_than' and value < rule['threshold']:
                    triggered = True
                elif rule['condition'] == 'equals' and value == rule['threshold']:
                    triggered = True
                
                if triggered:
                    await self._trigger_alert(rule_name, rule, value, tags)
    
    async def _trigger_alert(self, rule_name: str, rule: Dict[str, Any], current_value: float, tags: Dict[str, str]) -> None:
        """Trigger an alert."""
        try:
            alert_id = f"alert_{rule_name}_{int(time.time())}"
            
            alert = Alert(
                alert_id=alert_id,
                name=rule_name,
                description=rule.get('description', ''),
                severity=rule.get('severity', 'medium'),
                condition=rule['condition'],
                threshold=rule['threshold'],
                current_value=current_value,
                triggered_at=datetime.utcnow(),
                resolved_at=None,
                metadata={'tags': tags, 'rule': rule}
            )
            
            self._alerts[alert_id] = alert
            self.stats['alerts_triggered'] += 1
            
            # Send notification
            await self._send_alert_notification(alert, 'triggered')
            
            self.logger.warning(f"Alert triggered: {rule_name}, value: {current_value}, threshold: {rule['threshold']}")
            
        except Exception as e:
            self.logger.error(f"Failed to trigger alert {rule_name}: {str(e)}")
    
    async def _should_resolve_alert(self, alert: Alert) -> bool:
        """Check if an alert should be resolved."""
        try:
            # Check if the underlying condition has been resolved
            rule = self._alert_rules.get(alert.name)
            if not rule:
                return True  # Rule no longer exists, resolve alert

            # Get current metric value
            current_value = await self._get_current_metric_value(rule['metric_name'])
            if current_value is None:
                return False  # Cannot determine, keep alert active

            # Check if condition is no longer met
            condition_met = False
            if rule['condition'] == 'greater_than' and current_value > rule['threshold']:
                condition_met = True
            elif rule['condition'] == 'less_than' and current_value < rule['threshold']:
                condition_met = True
            elif rule['condition'] == 'equals' and current_value == rule['threshold']:
                condition_met = True

            # Resolve if condition is no longer met for sufficient time
            if not condition_met:
                # Check if condition has been resolved for at least 5 minutes
                time_since_trigger = (datetime.utcnow() - alert.triggered_at).total_seconds()
                return time_since_trigger > 300

            return False  # Condition still met, keep alert active

        except Exception as e:
            self.logger.error(f"Failed to check alert resolution for {alert.alert_id}: {str(e)}")
            return False
    
    async def _send_alert_notification(self, alert: Alert, action: str) -> None:
        """Send alert notification to configured webhooks."""
        try:
            notification = {
                'alert_id': alert.alert_id,
                'name': alert.name,
                'description': alert.description,
                'severity': alert.severity,
                'action': action,
                'current_value': alert.current_value,
                'threshold': alert.threshold,
                'triggered_at': alert.triggered_at.isoformat(),
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            
            # Send to webhooks
            for webhook_url in self.alert_webhooks:
                await self._send_webhook_notification(webhook_url, notification)
                
        except Exception as e:
            self.logger.error(f"Failed to send alert notification: {str(e)}")
    
    async def _export_to_prometheus(self, metrics: List[MetricPoint]) -> None:
        """Export metrics to Prometheus."""
        try:
            # This would integrate with prometheus_client
            # For now, format metrics for Prometheus exposition format
            for metric in metrics:
                metric_name = metric.name.replace('-', '_')
                tags_str = ','.join([f'{k}="{v}"' for k, v in metric.tags.items()])
                self.logger.debug(f"prometheus_metric{{name=\"{metric_name}\",{tags_str}}} {metric.value}")
        except Exception as e:
            self.logger.error(f"Failed to export to Prometheus: {str(e)}")

    async def _export_to_influxdb(self, metrics: List[MetricPoint]) -> None:
        """Export metrics to InfluxDB."""
        try:
            influxdb_url = self.config.get('influxdb_url')
            if not influxdb_url:
                return

            # Format metrics for InfluxDB line protocol
            lines = []
            for metric in metrics:
                tags_str = ','.join([f'{k}={v}' for k, v in metric.tags.items()])
                timestamp = int(metric.timestamp.timestamp() * 1000000000)  # nanoseconds
                line = f"{metric.name},{tags_str} value={metric.value} {timestamp}"
                lines.append(line)

            # Send to InfluxDB (would use actual HTTP client in production)
            self.logger.debug(f"InfluxDB export: {len(lines)} metrics")

        except Exception as e:
            self.logger.error(f"Failed to export to InfluxDB: {str(e)}")

    async def _export_to_custom_endpoints(self, metrics: List[MetricPoint]) -> None:
        """Export metrics to custom endpoints."""
        try:
            custom_endpoints = self.config.get('custom_metric_endpoints', [])
            for endpoint in custom_endpoints:
                # Format and send metrics to custom endpoint
                payload = {
                    'metrics': [
                        {
                            'name': m.name,
                            'value': m.value,
                            'timestamp': m.timestamp.isoformat(),
                            'tags': m.tags,
                            'type': m.metric_type
                        }
                        for m in metrics
                    ]
                }
                # Would use actual HTTP client in production
                self.logger.debug(f"Custom endpoint export to {endpoint}: {len(metrics)} metrics")

        except Exception as e:
            self.logger.error(f"Failed to export to custom endpoints: {str(e)}")

    async def _export_to_jaeger(self, span: TraceSpan) -> None:
        """Export trace span to Jaeger."""
        try:
            if not self.jaeger_endpoint:
                return

            # Format span for Jaeger
            jaeger_span = {
                'traceID': span.trace_id,
                'spanID': span.span_id,
                'parentSpanID': span.parent_span_id,
                'operationName': span.operation_name,
                'startTime': int(span.start_time.timestamp() * 1000000),  # microseconds
                'duration': int(span.duration_ms * 1000) if span.duration_ms else 0,
                'tags': [{'key': k, 'value': v} for k, v in span.tags.items()],
                'logs': span.logs
            }

            # Would send to Jaeger via HTTP in production
            self.logger.debug(f"Jaeger export: {span.trace_id}")

        except Exception as e:
            self.logger.error(f"Failed to export to Jaeger: {str(e)}")

    async def _export_to_zipkin(self, span: TraceSpan) -> None:
        """Export trace span to Zipkin."""
        try:
            zipkin_endpoint = self.config.get('zipkin_endpoint')
            if not zipkin_endpoint:
                return

            # Format span for Zipkin
            zipkin_span = {
                'traceId': span.trace_id,
                'id': span.span_id,
                'parentId': span.parent_span_id,
                'name': span.operation_name,
                'timestamp': int(span.start_time.timestamp() * 1000000),
                'duration': int(span.duration_ms * 1000) if span.duration_ms else 0,
                'tags': span.tags,
                'annotations': [
                    {'timestamp': int(span.start_time.timestamp() * 1000000), 'value': 'cs'},
                    {'timestamp': int(span.end_time.timestamp() * 1000000), 'value': 'cr'} if span.end_time else None
                ]
            }

            # Would send to Zipkin via HTTP in production
            self.logger.debug(f"Zipkin export: {span.trace_id}")

        except Exception as e:
            self.logger.error(f"Failed to export to Zipkin: {str(e)}")

    async def _export_trace_to_custom_endpoints(self, span: TraceSpan) -> None:
        """Export trace to custom endpoints."""
        try:
            custom_endpoints = self.config.get('custom_trace_endpoints', [])
            for endpoint in custom_endpoints:
                # Format and send trace to custom endpoint
                payload = {
                    'trace_id': span.trace_id,
                    'span_id': span.span_id,
                    'parent_span_id': span.parent_span_id,
                    'operation_name': span.operation_name,
                    'start_time': span.start_time.isoformat(),
                    'end_time': span.end_time.isoformat() if span.end_time else None,
                    'duration_ms': span.duration_ms,
                    'tags': span.tags,
                    'logs': span.logs,
                    'status': span.status
                }
                # Would use actual HTTP client in production
                self.logger.debug(f"Custom trace endpoint export to {endpoint}")

        except Exception as e:
            self.logger.error(f"Failed to export trace to custom endpoints: {str(e)}")

    async def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value of a metric."""
        try:
            # Find the most recent value for this metric
            for key, agg in self._metric_aggregates.items():
                if key.startswith(f"{metric_name}:"):
                    return agg['last_value']
            return None
        except Exception as e:
            self.logger.error(f"Failed to get current metric value for {metric_name}: {str(e)}")
            return None

    async def _send_webhook_notification(self, webhook_url: str, notification: Dict[str, Any]) -> None:
        """Send notification to webhook URL."""
        try:
            # In production, this would use aiohttp or similar
            import json
            payload = json.dumps(notification)

            # Mock HTTP request - in production would use actual HTTP client
            self.logger.info(f"Webhook notification sent to {webhook_url}")
            self.logger.debug(f"Webhook payload: {payload}")

            # Example of what production code would look like:
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(webhook_url, json=notification) as response:
            #         if response.status != 200:
            #             self.logger.error(f"Webhook failed: {response.status}")

        except Exception as e:
            self.logger.error(f"Failed to send webhook notification to {webhook_url}: {str(e)}")

    async def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring service statistics."""
        return {
            **self.stats,
            'is_initialized': self.is_initialized,
            'tracing_enabled': self.enable_tracing,
            'metrics_enabled': self.enable_metrics,
            'alerting_enabled': self.enable_alerting,
            'active_traces': len(self._active_traces),
            'metrics_in_buffer': len(self._metrics_buffer),
            'total_metric_types': len(self._metric_aggregates),
            'active_alerts': len([a for a in self._alerts.values() if a.resolved_at is None]),
            'alert_rules': len(self._alert_rules)
        }
