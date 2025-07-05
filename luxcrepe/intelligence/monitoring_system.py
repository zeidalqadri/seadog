"""
SEADOG Intelligence and Monitoring System
Comprehensive intelligence gathering, analysis, and monitoring framework
"""

import asyncio
import logging
import time
import json
import threading
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from concurrent.futures import ThreadPoolExecutor

from ..tests.base_agent import BaseAgent, MissionStatus, ThreatLevel, ReportPriority


class MonitoringLevel(Enum):
    """Monitoring intensity levels"""
    PASSIVE = "PASSIVE"
    ACTIVE = "ACTIVE"
    AGGRESSIVE = "AGGRESSIVE"
    STEALTH = "STEALTH"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class IntelligenceMetric:
    """Intelligence metric data structure"""
    metric_id: str
    metric_name: str
    metric_type: str
    value: Union[int, float, str, bool]
    timestamp: datetime
    source_agent: str
    confidence_level: float
    tags: List[str]
    metadata: Dict[str, Any]


@dataclass
class MonitoringAlert:
    """Monitoring alert data structure"""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    source: str
    affected_targets: List[str]
    recommended_actions: List[str]
    correlation_id: Optional[str] = None


@dataclass
class IntelligenceReport:
    """Intelligence report data structure"""
    report_id: str
    report_type: str
    title: str
    summary: str
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_score: float
    threat_level: ThreatLevel
    created_at: datetime
    valid_until: datetime
    sources: List[str]
    classification: str


class IntelligenceCollector:
    """Intelligence data collector and aggregator"""
    
    def __init__(self, collector_id: str):
        self.collector_id = collector_id
        self.logger = logging.getLogger(f"SEADOG.Intelligence.Collector.{collector_id}")
        
        # Data storage
        self.metrics: deque = deque(maxlen=10000)  # Last 10k metrics
        self.alerts: deque = deque(maxlen=1000)    # Last 1k alerts
        self.reports: List[IntelligenceReport] = []
        
        # Collection state
        self.is_collecting = False
        self.collection_start: Optional[datetime] = None
        self.collection_stats = {
            "total_metrics": 0,
            "alerts_generated": 0,
            "reports_created": 0,
            "collection_duration": 0.0
        }
        
        # Event handlers
        self.metric_handlers: List[Callable] = []
        self.alert_handlers: List[Callable] = []
        
        self.logger.info(f"Intelligence collector {collector_id} initialized")
    
    def start_collection(self):
        """Start intelligence collection"""
        self.is_collecting = True
        self.collection_start = datetime.now()
        self.logger.info("Intelligence collection started")
    
    def stop_collection(self):
        """Stop intelligence collection"""
        self.is_collecting = False
        if self.collection_start:
            self.collection_stats["collection_duration"] = (datetime.now() - self.collection_start).total_seconds()
        self.logger.info("Intelligence collection stopped")
    
    def add_metric(self, metric: IntelligenceMetric):
        """Add intelligence metric"""
        if self.is_collecting:
            self.metrics.append(metric)
            self.collection_stats["total_metrics"] += 1
            
            # Trigger metric handlers
            for handler in self.metric_handlers:
                try:
                    handler(metric)
                except Exception as e:
                    self.logger.error(f"Metric handler error: {str(e)}")
    
    def add_alert(self, alert: MonitoringAlert):
        """Add monitoring alert"""
        self.alerts.append(alert)
        self.collection_stats["alerts_generated"] += 1
        
        # Trigger alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler error: {str(e)}")
        
        self.logger.warning(f"Alert generated: {alert.alert_type} - {alert.severity.value}")
    
    def add_report(self, report: IntelligenceReport):
        """Add intelligence report"""
        self.reports.append(report)
        self.collection_stats["reports_created"] += 1
        self.logger.info(f"Intelligence report added: {report.report_id}")
    
    def register_metric_handler(self, handler: Callable):
        """Register metric event handler"""
        self.metric_handlers.append(handler)
    
    def register_alert_handler(self, handler: Callable):
        """Register alert event handler"""
        self.alert_handlers.append(handler)
    
    def get_metrics_by_type(self, metric_type: str, time_window: Optional[timedelta] = None) -> List[IntelligenceMetric]:
        """Get metrics by type within time window"""
        cutoff_time = datetime.now() - time_window if time_window else datetime.min
        
        return [
            metric for metric in self.metrics
            if metric.metric_type == metric_type and metric.timestamp >= cutoff_time
        ]
    
    def get_alerts_by_severity(self, severity: AlertSeverity, time_window: Optional[timedelta] = None) -> List[MonitoringAlert]:
        """Get alerts by severity within time window"""
        cutoff_time = datetime.now() - time_window if time_window else datetime.min
        
        return [
            alert for alert in self.alerts
            if alert.severity == severity and alert.timestamp >= cutoff_time
        ]
    
    def get_collection_summary(self) -> Dict[str, Any]:
        """Get collection summary statistics"""
        return {
            "collector_id": self.collector_id,
            "is_collecting": self.is_collecting,
            "collection_start": self.collection_start.isoformat() if self.collection_start else None,
            "metrics_collected": len(self.metrics),
            "alerts_generated": len(self.alerts),
            "reports_created": len(self.reports),
            "collection_stats": self.collection_stats
        }


class PerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self, monitor_id: str):
        self.monitor_id = monitor_id
        self.logger = logging.getLogger(f"SEADOG.Performance.Monitor.{monitor_id}")
        
        # Performance metrics
        self.response_times: deque = deque(maxlen=1000)
        self.success_rates: deque = deque(maxlen=100)
        self.error_counts: defaultdict = defaultdict(int)
        self.throughput_data: deque = deque(maxlen=100)
        
        # Monitoring configuration
        self.monitoring_interval = 10  # seconds
        self.alert_thresholds = {
            "response_time_warning": 5.0,
            "response_time_critical": 10.0,
            "success_rate_warning": 0.85,
            "success_rate_critical": 0.7,
            "error_rate_warning": 0.1,
            "error_rate_critical": 0.2
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.alert_callbacks: List[Callable] = []
        
        self.logger.info(f"Performance monitor {monitor_id} initialized")
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("Performance monitoring stopped")
    
    def record_response_time(self, response_time: float, success: bool):
        """Record response time and success status"""
        self.response_times.append(response_time)
        
        # Update success rate
        current_time = datetime.now()
        success_entry = {"timestamp": current_time, "success": success}
        self.success_rates.append(success_entry)
        
        # Check for alerts
        self._check_response_time_alerts(response_time)
        self._check_success_rate_alerts()
    
    def record_error(self, error_type: str):
        """Record error occurrence"""
        self.error_counts[error_type] += 1
        self._check_error_rate_alerts()
    
    def record_throughput(self, operations_per_second: float):
        """Record throughput measurement"""
        throughput_entry = {
            "timestamp": datetime.now(),
            "ops_per_second": operations_per_second
        }
        self.throughput_data.append(throughput_entry)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        stats = {
            "response_time_stats": self._calculate_response_time_stats(),
            "success_rate_stats": self._calculate_success_rate_stats(),
            "error_stats": self._calculate_error_stats(),
            "throughput_stats": self._calculate_throughput_stats()
        }
        return stats
    
    def _calculate_response_time_stats(self) -> Dict[str, float]:
        """Calculate response time statistics"""
        if not self.response_times:
            return {"avg": 0.0, "min": 0.0, "max": 0.0, "p95": 0.0, "p99": 0.0}
        
        times = list(self.response_times)
        return {
            "avg": statistics.mean(times),
            "min": min(times),
            "max": max(times),
            "p95": statistics.quantiles(times, n=20)[18] if len(times) > 20 else max(times),
            "p99": statistics.quantiles(times, n=100)[98] if len(times) > 100 else max(times)
        }
    
    def _calculate_success_rate_stats(self) -> Dict[str, float]:
        """Calculate success rate statistics"""
        if not self.success_rates:
            return {"current": 1.0, "avg_1min": 1.0, "avg_5min": 1.0}
        
        now = datetime.now()
        one_min_ago = now - timedelta(minutes=1)
        five_min_ago = now - timedelta(minutes=5)
        
        # Recent success rates
        recent_1min = [entry for entry in self.success_rates if entry["timestamp"] >= one_min_ago]
        recent_5min = [entry for entry in self.success_rates if entry["timestamp"] >= five_min_ago]
        
        current_rate = sum(entry["success"] for entry in recent_1min) / len(recent_1min) if recent_1min else 1.0
        avg_1min = sum(entry["success"] for entry in recent_1min) / len(recent_1min) if recent_1min else 1.0
        avg_5min = sum(entry["success"] for entry in recent_5min) / len(recent_5min) if recent_5min else 1.0
        
        return {
            "current": current_rate,
            "avg_1min": avg_1min,
            "avg_5min": avg_5min
        }
    
    def _calculate_error_stats(self) -> Dict[str, Any]:
        """Calculate error statistics"""
        total_errors = sum(self.error_counts.values())
        total_operations = len(self.response_times)
        
        error_rate = total_errors / total_operations if total_operations > 0 else 0.0
        
        return {
            "total_errors": total_errors,
            "error_rate": error_rate,
            "error_breakdown": dict(self.error_counts)
        }
    
    def _calculate_throughput_stats(self) -> Dict[str, float]:
        """Calculate throughput statistics"""
        if not self.throughput_data:
            return {"current": 0.0, "avg": 0.0, "peak": 0.0}
        
        throughputs = [entry["ops_per_second"] for entry in self.throughput_data]
        
        return {
            "current": throughputs[-1] if throughputs else 0.0,
            "avg": statistics.mean(throughputs),
            "peak": max(throughputs)
        }
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Perform periodic health checks
                stats = self.get_performance_stats()
                
                # Log performance summary
                self.logger.debug(f"Performance stats: {stats}")
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                time.sleep(5)  # Brief pause before retry
    
    def _check_response_time_alerts(self, response_time: float):
        """Check for response time alerts"""
        if response_time >= self.alert_thresholds["response_time_critical"]:
            self._trigger_alert("RESPONSE_TIME_CRITICAL", f"Critical response time: {response_time:.2f}s")
        elif response_time >= self.alert_thresholds["response_time_warning"]:
            self._trigger_alert("RESPONSE_TIME_WARNING", f"High response time: {response_time:.2f}s")
    
    def _check_success_rate_alerts(self):
        """Check for success rate alerts"""
        stats = self._calculate_success_rate_stats()
        current_rate = stats["current"]
        
        if current_rate <= self.alert_thresholds["success_rate_critical"]:
            self._trigger_alert("SUCCESS_RATE_CRITICAL", f"Critical success rate: {current_rate:.2%}")
        elif current_rate <= self.alert_thresholds["success_rate_warning"]:
            self._trigger_alert("SUCCESS_RATE_WARNING", f"Low success rate: {current_rate:.2%}")
    
    def _check_error_rate_alerts(self):
        """Check for error rate alerts"""
        stats = self._calculate_error_stats()
        error_rate = stats["error_rate"]
        
        if error_rate >= self.alert_thresholds["error_rate_critical"]:
            self._trigger_alert("ERROR_RATE_CRITICAL", f"Critical error rate: {error_rate:.2%}")
        elif error_rate >= self.alert_thresholds["error_rate_warning"]:
            self._trigger_alert("ERROR_RATE_WARNING", f"High error rate: {error_rate:.2%}")
    
    def _trigger_alert(self, alert_type: str, message: str):
        """Trigger performance alert"""
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, message)
            except Exception as e:
                self.logger.error(f"Alert callback error: {str(e)}")
    
    def register_alert_callback(self, callback: Callable):
        """Register alert callback"""
        self.alert_callbacks.append(callback)


class IntelligenceAnalyzer:
    """Intelligence analysis and correlation engine"""
    
    def __init__(self, analyzer_id: str):
        self.analyzer_id = analyzer_id
        self.logger = logging.getLogger(f"SEADOG.Intelligence.Analyzer.{analyzer_id}")
        
        # Analysis configuration
        self.correlation_window = timedelta(minutes=15)
        self.confidence_threshold = 0.7
        self.threat_escalation_rules = {}
        
        # Analysis state
        self.active_correlations: Dict[str, List[IntelligenceMetric]] = {}
        self.threat_patterns: Dict[str, Dict[str, Any]] = {}
        self.analysis_history: List[Dict[str, Any]] = []
        
        self.logger.info(f"Intelligence analyzer {analyzer_id} initialized")
    
    async def analyze_metrics(self, metrics: List[IntelligenceMetric]) -> List[IntelligenceReport]:
        """Analyze intelligence metrics and generate reports"""
        
        reports = []
        
        # Correlation analysis
        correlations = await self._perform_correlation_analysis(metrics)
        
        # Threat analysis
        threats = await self._perform_threat_analysis(metrics, correlations)
        
        # Pattern analysis
        patterns = await self._perform_pattern_analysis(metrics)
        
        # Generate reports based on analysis
        if correlations:
            correlation_report = self._generate_correlation_report(correlations)
            reports.append(correlation_report)
        
        if threats:
            threat_report = self._generate_threat_report(threats)
            reports.append(threat_report)
        
        if patterns:
            pattern_report = self._generate_pattern_report(patterns)
            reports.append(pattern_report)
        
        return reports
    
    async def _perform_correlation_analysis(self, metrics: List[IntelligenceMetric]) -> Dict[str, List[IntelligenceMetric]]:
        """Perform correlation analysis on metrics"""
        
        correlations = {}
        
        # Group metrics by time windows
        time_windows = self._create_time_windows(metrics)
        
        for window_id, window_metrics in time_windows.items():
            # Look for correlated events
            correlated_metrics = self._find_correlated_metrics(window_metrics)
            
            if correlated_metrics:
                correlations[window_id] = correlated_metrics
        
        return correlations
    
    async def _perform_threat_analysis(self, metrics: List[IntelligenceMetric], correlations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform threat analysis"""
        
        threats = []
        
        # Analyze individual metrics for threat indicators
        for metric in metrics:
            threat_indicators = self._identify_threat_indicators(metric)
            
            if threat_indicators:
                threat = {
                    "threat_id": f"THREAT_{int(time.time())}",
                    "threat_type": threat_indicators.get("type", "UNKNOWN"),
                    "severity": threat_indicators.get("severity", "MEDIUM"),
                    "confidence": threat_indicators.get("confidence", 0.5),
                    "source_metric": metric.metric_id,
                    "indicators": threat_indicators
                }
                threats.append(threat)
        
        # Analyze correlations for compound threats
        for correlation_id, correlated_metrics in correlations.items():
            compound_threat = self._analyze_compound_threat(correlated_metrics)
            
            if compound_threat:
                threats.append(compound_threat)
        
        return threats
    
    async def _perform_pattern_analysis(self, metrics: List[IntelligenceMetric]) -> List[Dict[str, Any]]:
        """Perform pattern analysis"""
        
        patterns = []
        
        # Analyze temporal patterns
        temporal_patterns = self._analyze_temporal_patterns(metrics)
        patterns.extend(temporal_patterns)
        
        # Analyze behavioral patterns
        behavioral_patterns = self._analyze_behavioral_patterns(metrics)
        patterns.extend(behavioral_patterns)
        
        # Analyze anomaly patterns
        anomaly_patterns = self._analyze_anomaly_patterns(metrics)
        patterns.extend(anomaly_patterns)
        
        return patterns
    
    def _create_time_windows(self, metrics: List[IntelligenceMetric]) -> Dict[str, List[IntelligenceMetric]]:
        """Create time windows for correlation analysis"""
        
        windows = defaultdict(list)
        
        for metric in metrics:
            # Create window ID based on time
            window_start = metric.timestamp.replace(second=0, microsecond=0)
            window_id = window_start.isoformat()
            
            windows[window_id].append(metric)
        
        return dict(windows)
    
    def _find_correlated_metrics(self, metrics: List[IntelligenceMetric]) -> List[IntelligenceMetric]:
        """Find correlated metrics within a time window"""
        
        # Simple correlation based on source agents and metric types
        correlated = []
        
        if len(metrics) >= 2:
            # Look for metrics from different agents with similar patterns
            agent_metrics = defaultdict(list)
            
            for metric in metrics:
                agent_metrics[metric.source_agent].append(metric)
            
            # If multiple agents report similar metrics, consider them correlated
            if len(agent_metrics) >= 2:
                correlated = metrics
        
        return correlated
    
    def _identify_threat_indicators(self, metric: IntelligenceMetric) -> Optional[Dict[str, Any]]:
        """Identify threat indicators in a metric"""
        
        threat_indicators = None
        
        # Check for specific threat patterns
        if metric.metric_type == "error_rate" and isinstance(metric.value, (int, float)):
            if metric.value > 0.2:  # 20% error rate
                threat_indicators = {
                    "type": "HIGH_ERROR_RATE",
                    "severity": "HIGH",
                    "confidence": 0.8
                }
        
        elif metric.metric_type == "response_time" and isinstance(metric.value, (int, float)):
            if metric.value > 10.0:  # 10 second response time
                threat_indicators = {
                    "type": "SLOW_RESPONSE",
                    "severity": "MEDIUM",
                    "confidence": 0.7
                }
        
        elif metric.metric_type == "security_score" and isinstance(metric.value, (int, float)):
            if metric.value < 0.5:  # Low security score
                threat_indicators = {
                    "type": "SECURITY_WEAKNESS",
                    "severity": "HIGH",
                    "confidence": 0.9
                }
        
        return threat_indicators
    
    def _analyze_compound_threat(self, correlated_metrics: List[IntelligenceMetric]) -> Optional[Dict[str, Any]]:
        """Analyze compound threats from correlated metrics"""
        
        # Look for patterns that indicate coordinated attacks or systemic issues
        metric_types = [metric.metric_type for metric in correlated_metrics]
        
        # Example: High error rate + slow response time + low security score
        if ("error_rate" in metric_types and 
            "response_time" in metric_types and 
            "security_score" in metric_types):
            
            return {
                "threat_id": f"COMPOUND_THREAT_{int(time.time())}",
                "threat_type": "SYSTEMIC_DEGRADATION",
                "severity": "CRITICAL",
                "confidence": 0.85,
                "source_metrics": [metric.metric_id for metric in correlated_metrics],
                "description": "Multiple performance and security indicators suggest systemic issues"
            }
        
        return None
    
    def _analyze_temporal_patterns(self, metrics: List[IntelligenceMetric]) -> List[Dict[str, Any]]:
        """Analyze temporal patterns in metrics"""
        
        patterns = []
        
        # Group metrics by type and analyze time series
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.metric_type].append(metric)
        
        for metric_type, type_metrics in metric_groups.items():
            if len(type_metrics) >= 3:  # Need at least 3 points for pattern
                # Sort by timestamp
                sorted_metrics = sorted(type_metrics, key=lambda m: m.timestamp)
                
                # Look for trends
                trend = self._detect_trend(sorted_metrics)
                
                if trend:
                    patterns.append({
                        "pattern_type": "TEMPORAL_TREND",
                        "metric_type": metric_type,
                        "trend": trend,
                        "confidence": 0.7
                    })
        
        return patterns
    
    def _analyze_behavioral_patterns(self, metrics: List[IntelligenceMetric]) -> List[Dict[str, Any]]:
        """Analyze behavioral patterns"""
        
        patterns = []
        
        # Analyze agent behavior patterns
        agent_behaviors = defaultdict(list)
        
        for metric in metrics:
            agent_behaviors[metric.source_agent].append(metric)
        
        for agent, agent_metrics in agent_behaviors.items():
            behavior_pattern = self._analyze_agent_behavior(agent_metrics)
            
            if behavior_pattern:
                patterns.append({
                    "pattern_type": "BEHAVIORAL_PATTERN",
                    "source_agent": agent,
                    "behavior": behavior_pattern,
                    "confidence": 0.6
                })
        
        return patterns
    
    def _analyze_anomaly_patterns(self, metrics: List[IntelligenceMetric]) -> List[Dict[str, Any]]:
        """Analyze anomaly patterns"""
        
        patterns = []
        
        # Simple anomaly detection based on statistical outliers
        for metric_type in set(metric.metric_type for metric in metrics):
            type_metrics = [m for m in metrics if m.metric_type == metric_type]
            
            if len(type_metrics) >= 5:  # Need enough data for statistical analysis
                anomalies = self._detect_statistical_anomalies(type_metrics)
                
                if anomalies:
                    patterns.append({
                        "pattern_type": "ANOMALY_PATTERN",
                        "metric_type": metric_type,
                        "anomalies": anomalies,
                        "confidence": 0.8
                    })
        
        return patterns
    
    def _detect_trend(self, sorted_metrics: List[IntelligenceMetric]) -> Optional[str]:
        """Detect trend in time series data"""
        
        # Simple trend detection for numeric values
        numeric_values = []
        for metric in sorted_metrics:
            if isinstance(metric.value, (int, float)):
                numeric_values.append(metric.value)
        
        if len(numeric_values) >= 3:
            # Calculate simple trend
            increasing = sum(1 for i in range(1, len(numeric_values)) if numeric_values[i] > numeric_values[i-1])
            decreasing = sum(1 for i in range(1, len(numeric_values)) if numeric_values[i] < numeric_values[i-1])
            
            total_comparisons = len(numeric_values) - 1
            
            if increasing / total_comparisons > 0.7:
                return "INCREASING"
            elif decreasing / total_comparisons > 0.7:
                return "DECREASING"
            else:
                return "STABLE"
        
        return None
    
    def _analyze_agent_behavior(self, agent_metrics: List[IntelligenceMetric]) -> Optional[str]:
        """Analyze agent behavior patterns"""
        
        # Simple behavior analysis
        if len(agent_metrics) >= 3:
            confidence_levels = [m.confidence_level for m in agent_metrics]
            avg_confidence = sum(confidence_levels) / len(confidence_levels)
            
            if avg_confidence > 0.8:
                return "HIGH_CONFIDENCE"
            elif avg_confidence < 0.5:
                return "LOW_CONFIDENCE"
            else:
                return "NORMAL"
        
        return None
    
    def _detect_statistical_anomalies(self, metrics: List[IntelligenceMetric]) -> List[Dict[str, Any]]:
        """Detect statistical anomalies"""
        
        anomalies = []
        
        # Extract numeric values
        numeric_values = []
        for metric in metrics:
            if isinstance(metric.value, (int, float)):
                numeric_values.append((metric, metric.value))
        
        if len(numeric_values) >= 5:
            values = [v for _, v in numeric_values]
            mean_val = statistics.mean(values)
            stdev_val = statistics.stdev(values) if len(values) > 1 else 0
            
            # Identify outliers (> 2 standard deviations from mean)
            for metric, value in numeric_values:
                if stdev_val > 0 and abs(value - mean_val) > 2 * stdev_val:
                    anomalies.append({
                        "metric_id": metric.metric_id,
                        "value": value,
                        "deviation": abs(value - mean_val) / stdev_val,
                        "type": "STATISTICAL_OUTLIER"
                    })
        
        return anomalies
    
    def _generate_correlation_report(self, correlations: Dict[str, Any]) -> IntelligenceReport:
        """Generate correlation analysis report"""
        
        findings = []
        for correlation_id, correlated_metrics in correlations.items():
            findings.append({
                "finding_type": "METRIC_CORRELATION",
                "correlation_id": correlation_id,
                "metrics_count": len(correlated_metrics),
                "agents_involved": list(set(m.source_agent for m in correlated_metrics)),
                "time_window": correlation_id
            })
        
        return IntelligenceReport(
            report_id=f"CORRELATION_REPORT_{int(time.time())}",
            report_type="CORRELATION_ANALYSIS",
            title="Metric Correlation Analysis",
            summary=f"Identified {len(correlations)} correlation patterns across multiple agents",
            findings=findings,
            recommendations=["Monitor correlated events for potential systemic issues"],
            confidence_score=0.7,
            threat_level=ThreatLevel.MODERATE,
            created_at=datetime.now(),
            valid_until=datetime.now() + timedelta(hours=24),
            sources=[self.analyzer_id],
            classification="INTERNAL"
        )
    
    def _generate_threat_report(self, threats: List[Dict[str, Any]]) -> IntelligenceReport:
        """Generate threat analysis report"""
        
        high_threats = [t for t in threats if t.get("severity") == "HIGH"]
        critical_threats = [t for t in threats if t.get("severity") == "CRITICAL"]
        
        threat_level = ThreatLevel.HIGH if critical_threats else (ThreatLevel.MODERATE if high_threats else ThreatLevel.LOW)
        
        return IntelligenceReport(
            report_id=f"THREAT_REPORT_{int(time.time())}",
            report_type="THREAT_ANALYSIS",
            title="Threat Assessment Report",
            summary=f"Identified {len(threats)} potential threats ({len(critical_threats)} critical, {len(high_threats)} high)",
            findings=[{"finding_type": "THREAT_IDENTIFICATION", "threats": threats}],
            recommendations=["Investigate high-priority threats immediately", "Implement additional monitoring"],
            confidence_score=0.8,
            threat_level=threat_level,
            created_at=datetime.now(),
            valid_until=datetime.now() + timedelta(hours=12),
            sources=[self.analyzer_id],
            classification="INTERNAL"
        )
    
    def _generate_pattern_report(self, patterns: List[Dict[str, Any]]) -> IntelligenceReport:
        """Generate pattern analysis report"""
        
        return IntelligenceReport(
            report_id=f"PATTERN_REPORT_{int(time.time())}",
            report_type="PATTERN_ANALYSIS",
            title="Intelligence Pattern Analysis",
            summary=f"Identified {len(patterns)} behavioral and temporal patterns",
            findings=[{"finding_type": "PATTERN_IDENTIFICATION", "patterns": patterns}],
            recommendations=["Monitor identified patterns for future predictions"],
            confidence_score=0.6,
            threat_level=ThreatLevel.LOW,
            created_at=datetime.now(),
            valid_until=datetime.now() + timedelta(days=7),
            sources=[self.analyzer_id],
            classification="INTERNAL"
        )


class SEADOGIntelligenceSystem:
    """SEADOG Comprehensive Intelligence and Monitoring System"""
    
    def __init__(self, system_id: str = "SEADOG_INTELLIGENCE_001"):
        self.system_id = system_id
        self.logger = logging.getLogger(f"SEADOG.Intelligence.System")
        
        # System components
        self.collector = IntelligenceCollector(f"{system_id}_COLLECTOR")
        self.performance_monitor = PerformanceMonitor(f"{system_id}_PERFORMANCE")
        self.analyzer = IntelligenceAnalyzer(f"{system_id}_ANALYZER")
        
        # System state
        self.is_active = False
        self.start_time: Optional[datetime] = None
        
        # Agent registration
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.agent_monitors: Dict[str, Dict[str, Any]] = {}
        
        # Analysis scheduler
        self.analysis_interval = 60  # seconds
        self.analysis_task: Optional[asyncio.Task] = None
        
        self.logger.info(f"SEADOG Intelligence System {system_id} initialized")
    
    async def start_system(self):
        """Start the intelligence system"""
        
        if self.is_active:
            self.logger.warning("Intelligence system already active")
            return
        
        self.is_active = True
        self.start_time = datetime.now()
        
        # Start components
        self.collector.start_collection()
        self.performance_monitor.start_monitoring()
        
        # Start analysis scheduler
        self.analysis_task = asyncio.create_task(self._analysis_scheduler())
        
        # Register alert handlers
        self.performance_monitor.register_alert_callback(self._handle_performance_alert)
        
        self.logger.info("SEADOG Intelligence System started")
    
    async def stop_system(self):
        """Stop the intelligence system"""
        
        if not self.is_active:
            self.logger.warning("Intelligence system not active")
            return
        
        self.is_active = False
        
        # Stop components
        self.collector.stop_collection()
        self.performance_monitor.stop_monitoring()
        
        # Stop analysis scheduler
        if self.analysis_task:
            self.analysis_task.cancel()
            try:
                await self.analysis_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("SEADOG Intelligence System stopped")
    
    def register_agent(self, agent: BaseAgent):
        """Register agent for monitoring"""
        
        self.registered_agents[agent.agent_id] = agent
        self.agent_monitors[agent.agent_id] = {
            "registration_time": datetime.now(),
            "last_activity": datetime.now(),
            "metrics_count": 0,
            "status": "ACTIVE"
        }
        
        self.logger.info(f"Agent registered: {agent.call_sign} ({agent.agent_id})")
    
    def record_agent_metric(self, agent_id: str, metric_type: str, value: Any, 
                          confidence: float = 1.0, tags: List[str] = None, 
                          metadata: Dict[str, Any] = None):
        """Record metric from agent"""
        
        if agent_id not in self.registered_agents:
            self.logger.warning(f"Metric from unregistered agent: {agent_id}")
            return
        
        # Create metric
        metric = IntelligenceMetric(
            metric_id=f"{agent_id}_{metric_type}_{int(time.time())}",
            metric_name=metric_type,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            source_agent=agent_id,
            confidence_level=confidence,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Record metric
        self.collector.add_metric(metric)
        
        # Update agent monitoring
        if agent_id in self.agent_monitors:
            self.agent_monitors[agent_id]["last_activity"] = datetime.now()
            self.agent_monitors[agent_id]["metrics_count"] += 1
        
        # Record performance data if applicable
        if metric_type == "response_time" and isinstance(value, (int, float)):
            success = metadata.get("success", True) if metadata else True
            self.performance_monitor.record_response_time(value, success)
        
        elif metric_type == "error" and metadata:
            error_type = metadata.get("error_type", "UNKNOWN")
            self.performance_monitor.record_error(error_type)
    
    async def _analysis_scheduler(self):
        """Periodic analysis scheduler"""
        
        while self.is_active:
            try:
                await asyncio.sleep(self.analysis_interval)
                
                if self.is_active:
                    await self._perform_periodic_analysis()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Analysis scheduler error: {str(e)}")
    
    async def _perform_periodic_analysis(self):
        """Perform periodic intelligence analysis"""
        
        self.logger.info("Performing periodic intelligence analysis")
        
        # Get recent metrics
        time_window = timedelta(minutes=15)
        recent_metrics = [
            metric for metric in self.collector.metrics
            if datetime.now() - metric.timestamp <= time_window
        ]
        
        if recent_metrics:
            # Analyze metrics
            reports = await self.analyzer.analyze_metrics(recent_metrics)
            
            # Store reports
            for report in reports:
                self.collector.add_report(report)
                self.logger.info(f"Intelligence report generated: {report.report_id}")
    
    def _handle_performance_alert(self, alert_type: str, message: str):
        """Handle performance alerts"""
        
        alert = MonitoringAlert(
            alert_id=f"PERF_ALERT_{int(time.time())}",
            alert_type=alert_type,
            severity=AlertSeverity.WARNING if "WARNING" in alert_type else AlertSeverity.CRITICAL,
            message=message,
            timestamp=datetime.now(),
            source="PERFORMANCE_MONITOR",
            affected_targets=[],
            recommended_actions=["Investigate performance degradation"]
        )
        
        self.collector.add_alert(alert)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        return {
            "system_id": self.system_id,
            "is_active": self.is_active,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime": str(datetime.now() - self.start_time) if self.start_time else None,
            "registered_agents": len(self.registered_agents),
            "collection_stats": self.collector.get_collection_summary(),
            "performance_stats": self.performance_monitor.get_performance_stats(),
            "agent_status": {
                agent_id: {
                    "call_sign": agent.call_sign,
                    "squad": agent.squad,
                    **monitor_data
                }
                for agent_id, agent in self.registered_agents.items()
                for monitor_data in [self.agent_monitors.get(agent_id, {})]
            }
        }
    
    def export_intelligence_data(self, format: str = "json") -> str:
        """Export intelligence data"""
        
        if format.lower() == "json":
            data = {
                "system_status": self.get_system_status(),
                "metrics": [asdict(metric) for metric in list(self.collector.metrics)],
                "alerts": [asdict(alert) for alert in list(self.collector.alerts)],
                "reports": [asdict(report) for report in self.collector.reports],
                "export_timestamp": datetime.now().isoformat()
            }
            
            return json.dumps(data, indent=2, default=str)
        
        return "Unsupported format"