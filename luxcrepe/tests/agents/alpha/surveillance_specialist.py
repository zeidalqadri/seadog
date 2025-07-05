"""
Surveillance Specialist Agent - Alpha Squad
Continuous monitoring and situational awareness operations
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import threading

from ...base_agent import BaseAgent, MissionStatus, ThreatLevel, ReportPriority, SITREPReport


class SurveillanceSpecialistAgent(BaseAgent):
    """Surveillance Specialist - Continuous Monitoring and Awareness
    
    Responsibilities:
    - Continuous target monitoring
    - Real-time situation assessment
    - Performance surveillance
    - Anomaly detection
    - Alert generation and escalation
    """
    
    def __init__(self):
        super().__init__(
            agent_id="ALPHA-003",
            call_sign="RADIO",
            squad="alpha"
        )
        
        # Surveillance capabilities
        self.weapons_systems = [
            "CONTINUOUS_MONITORING",
            "ANOMALY_DETECTION", 
            "PERFORMANCE_SURVEILLANCE",
            "ALERT_SYSTEMS"
        ]
        
        self.equipment = {
            "surveillance_array": "OPERATIONAL",
            "monitoring_station": "ACTIVE", 
            "alert_system": "ARMED",
            "comm_relay": "BROADCASTING"
        }
        
        self.intelligence_sources = [
            "REAL_TIME_METRICS",
            "PERFORMANCE_DATA",
            "ERROR_PATTERNS",
            "SYSTEM_ALERTS",
            "OPERATIONAL_STATUS"
        ]
        
        # Surveillance-specific attributes
        self.surveillance_active = False
        self.monitoring_data: List[Dict[str, Any]] = []
        self.alert_history: List[Dict[str, Any]] = []
        self.performance_baselines: Dict[str, float] = {}
        self.anomaly_thresholds: Dict[str, float] = {
            "response_time": 5.0,
            "error_rate": 0.1,
            "success_rate": 0.8
        }
        
        # Surveillance thread
        self.surveillance_thread: Optional[threading.Thread] = None
        self.stop_surveillance = threading.Event()
        
        self.logger.info("RADIO: Surveillance specialist initialized - Overwatch ready")
    
    def get_capabilities(self) -> List[str]:
        """Return surveillance capabilities"""
        return [
            "continuous_monitoring",
            "real_time_surveillance",
            "anomaly_detection",
            "performance_tracking",
            "alert_generation",
            "situation_assessment",
            "communication_relay",
            "escalation_protocols"
        ]
    
    async def execute_mission(self, mission_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute surveillance mission"""
        
        self.logger.info("RADIO: Initiating surveillance operations")
        
        surveillance_duration = mission_parameters.get("surveillance_duration", 300)  # 5 minutes default
        targets = mission_parameters.get("target_urls", [])
        monitoring_frequency = mission_parameters.get("monitoring_frequency", 10)  # 10 seconds
        
        # Surveillance Phase 1: Establish Overwatch
        overwatch_status = await self._establish_overwatch(targets)
        
        # Surveillance Phase 2: Begin Continuous Monitoring
        monitoring_results = await self._begin_continuous_monitoring(
            targets, surveillance_duration, monitoring_frequency
        )
        
        # Surveillance Phase 3: Analyze Surveillance Data
        surveillance_analysis = await self._analyze_surveillance_data()
        
        # Surveillance Phase 4: Generate Intelligence Report
        intelligence_summary = await self._generate_surveillance_intelligence()
        
        self.logger.info("RADIO: Surveillance mission complete - Intelligence package ready")
        
        return {
            "overwatch_establishment": overwatch_status,
            "monitoring_results": monitoring_results,
            "surveillance_analysis": surveillance_analysis,
            "intelligence_summary": intelligence_summary,
            "surveillance_metadata": {
                "agent": self.call_sign,
                "surveillance_duration": surveillance_duration,
                "monitoring_points": len(self.monitoring_data),
                "alerts_generated": len(self.alert_history)
            }
        }
    
    async def _establish_overwatch(self, targets: List[str]) -> Dict[str, Any]:
        """Establish surveillance overwatch on targets"""
        
        self.logger.info("RADIO: Establishing surveillance overwatch")
        
        overwatch = {
            "status": "ESTABLISHED",
            "targets_under_surveillance": len(targets),
            "surveillance_positions": [],
            "baseline_measurements": {},
            "overwatch_timestamp": datetime.now().isoformat()
        }
        
        # Establish baseline measurements for each target
        for i, target in enumerate(targets):
            baseline = await self._establish_baseline(target)
            position_id = f"OVERWATCH_{i+1}"
            
            overwatch["surveillance_positions"].append({
                "position_id": position_id,
                "target": target,
                "baseline_established": baseline is not None,
                "surveillance_ready": True
            })
            
            if baseline:
                overwatch["baseline_measurements"][position_id] = baseline
                # Store in performance baselines for anomaly detection
                self.performance_baselines[target] = baseline.get("baseline_response_time", 2.0)
        
        self.surveillance_active = True
        self.logger.info(f"RADIO: Overwatch established on {len(targets)} targets")
        
        return overwatch
    
    async def _establish_baseline(self, target: str) -> Optional[Dict[str, Any]]:
        """Establish performance baseline for target"""
        
        self.logger.debug(f"RADIO: Establishing baseline for {target}")
        
        try:
            import requests
            
            # Conduct baseline measurements
            response_times = []
            status_codes = []
            
            for _ in range(3):
                start_time = time.time()
                response = requests.head(target, timeout=10)
                response_time = time.time() - start_time
                
                response_times.append(response_time)
                status_codes.append(response.status_code)
                
                await asyncio.sleep(1)
            
            baseline = {
                "target": target,
                "baseline_response_time": sum(response_times) / len(response_times),
                "baseline_status_code": max(set(status_codes), key=status_codes.count),
                "measurement_consistency": max(response_times) - min(response_times),
                "baseline_timestamp": datetime.now().isoformat()
            }
            
            return baseline
            
        except Exception as e:
            self.logger.warning(f"RADIO: Failed to establish baseline for {target}: {str(e)}")
            return None
    
    async def _begin_continuous_monitoring(self, targets: List[str], 
                                         duration: int, frequency: int) -> Dict[str, Any]:
        """Begin continuous monitoring operations"""
        
        self.logger.info(f"RADIO: Beginning {duration}s continuous monitoring")
        
        monitoring_results = {
            "monitoring_duration": duration,
            "monitoring_frequency": frequency,
            "total_monitoring_cycles": 0,
            "targets_monitored": len(targets),
            "anomalies_detected": 0,
            "alerts_triggered": 0
        }
        
        # Start surveillance in background thread
        self.stop_surveillance.clear()
        self.surveillance_thread = threading.Thread(
            target=self._surveillance_worker,
            args=(targets, frequency)
        )
        self.surveillance_thread.start()
        
        # Monitor for specified duration
        end_time = time.time() + duration
        cycle_count = 0
        
        while time.time() < end_time and self.surveillance_active:
            await asyncio.sleep(frequency)
            cycle_count += 1
            
            # Check for new alerts
            new_alerts = len(self.alert_history) - monitoring_results["alerts_triggered"]
            monitoring_results["alerts_triggered"] = len(self.alert_history)
            
            if new_alerts > 0:
                self.logger.info(f"RADIO: {new_alerts} new alerts detected during surveillance")
        
        # Stop surveillance
        self.stop_surveillance.set()
        if self.surveillance_thread:
            self.surveillance_thread.join(timeout=5)
        
        monitoring_results["total_monitoring_cycles"] = cycle_count
        monitoring_results["anomalies_detected"] = self._count_anomalies()
        
        self.logger.info(f"RADIO: Continuous monitoring complete - {cycle_count} cycles executed")
        
        return monitoring_results
    
    def _surveillance_worker(self, targets: List[str], frequency: int):
        """Background surveillance worker thread"""
        
        self.logger.debug("RADIO: Surveillance worker active")
        
        while not self.stop_surveillance.is_set():
            try:
                # Monitor each target
                for target in targets:
                    if self.stop_surveillance.is_set():
                        break
                    
                    monitoring_point = self._collect_monitoring_data(target)
                    if monitoring_point:
                        self.monitoring_data.append(monitoring_point)
                        
                        # Check for anomalies
                        self._check_for_anomalies(monitoring_point)
                
                # Wait for next monitoring cycle
                self.stop_surveillance.wait(frequency)
                
            except Exception as e:
                self.logger.error(f"RADIO: Surveillance error: {str(e)}")
                self.stop_surveillance.wait(frequency)
        
        self.logger.debug("RADIO: Surveillance worker terminated")
    
    def _collect_monitoring_data(self, target: str) -> Optional[Dict[str, Any]]:
        """Collect monitoring data for a target"""
        
        try:
            import requests
            
            start_time = time.time()
            response = requests.head(target, timeout=5)
            response_time = time.time() - start_time
            
            monitoring_point = {
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "response_time": response_time,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "headers": dict(response.headers)
            }
            
            return monitoring_point
            
        except Exception as e:
            # Record failed monitoring attempt
            monitoring_point = {
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "response_time": None,
                "status_code": None,
                "success": False,
                "error": str(e)
            }
            
            return monitoring_point
    
    def _check_for_anomalies(self, monitoring_point: Dict[str, Any]):
        """Check monitoring point for anomalies"""
        
        target = monitoring_point["target"]
        
        # Response time anomaly
        if monitoring_point.get("response_time"):
            response_time = monitoring_point["response_time"]
            baseline = self.performance_baselines.get(target, 2.0)
            
            if response_time > baseline * 3 or response_time > self.anomaly_thresholds["response_time"]:
                self._generate_alert("RESPONSE_TIME_ANOMALY", {
                    "target": target,
                    "response_time": response_time,
                    "baseline": baseline,
                    "threshold": self.anomaly_thresholds["response_time"]
                })
        
        # Status code anomaly
        if not monitoring_point.get("success"):
            self._generate_alert("STATUS_CODE_ANOMALY", {
                "target": target,
                "status_code": monitoring_point.get("status_code"),
                "error": monitoring_point.get("error")
            })
        
        # Calculate recent error rate
        recent_points = [p for p in self.monitoring_data[-10:] if p["target"] == target]
        if len(recent_points) >= 5:
            error_rate = sum(1 for p in recent_points if not p.get("success")) / len(recent_points)
            
            if error_rate > self.anomaly_thresholds["error_rate"]:
                self._generate_alert("HIGH_ERROR_RATE", {
                    "target": target,
                    "error_rate": error_rate,
                    "threshold": self.anomaly_thresholds["error_rate"],
                    "recent_failures": sum(1 for p in recent_points if not p.get("success"))
                })
    
    def _generate_alert(self, alert_type: str, details: Dict[str, Any]):
        """Generate surveillance alert"""
        
        alert = {
            "alert_id": f"ALERT_{len(self.alert_history) + 1}",
            "alert_type": alert_type,
            "severity": self._determine_alert_severity(alert_type),
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "agent": self.call_sign
        }
        
        self.alert_history.append(alert)
        
        # Log alert based on severity
        severity = alert["severity"]
        if severity == "CRITICAL":
            self.logger.error(f"RADIO: CRITICAL ALERT - {alert_type}: {details}")
        elif severity == "HIGH":
            self.logger.warning(f"RADIO: HIGH ALERT - {alert_type}: {details}")
        else:
            self.logger.info(f"RADIO: {severity} ALERT - {alert_type}: {details}")
    
    def _determine_alert_severity(self, alert_type: str) -> str:
        """Determine severity level for alert type"""
        
        severity_map = {
            "RESPONSE_TIME_ANOMALY": "MEDIUM",
            "STATUS_CODE_ANOMALY": "HIGH", 
            "HIGH_ERROR_RATE": "CRITICAL",
            "CONNECTION_FAILURE": "HIGH",
            "PERFORMANCE_DEGRADATION": "MEDIUM"
        }
        
        return severity_map.get(alert_type, "LOW")
    
    def _count_anomalies(self) -> int:
        """Count total anomalies detected"""
        
        anomaly_types = ["RESPONSE_TIME_ANOMALY", "STATUS_CODE_ANOMALY", "HIGH_ERROR_RATE"]
        return len([alert for alert in self.alert_history if alert["alert_type"] in anomaly_types])
    
    async def _analyze_surveillance_data(self) -> Dict[str, Any]:
        """Analyze collected surveillance data"""
        
        self.logger.info("RADIO: Analyzing surveillance data")
        
        analysis = {
            "total_monitoring_points": len(self.monitoring_data),
            "target_performance": {},
            "trend_analysis": {},
            "anomaly_summary": {},
            "operational_insights": []
        }
        
        # Group data by target
        targets = list(set(point["target"] for point in self.monitoring_data))
        
        for target in targets:
            target_data = [point for point in self.monitoring_data if point["target"] == target]
            analysis["target_performance"][target] = self._analyze_target_performance(target_data)
        
        # Trend analysis
        analysis["trend_analysis"] = self._analyze_performance_trends()
        
        # Anomaly summary
        analysis["anomaly_summary"] = {
            "total_anomalies": self._count_anomalies(),
            "alert_breakdown": self._breakdown_alerts_by_type(),
            "most_problematic_target": self._identify_most_problematic_target()
        }
        
        # Generate operational insights
        analysis["operational_insights"] = self._generate_operational_insights()
        
        return analysis
    
    def _analyze_target_performance(self, target_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance for specific target"""
        
        if not target_data:
            return {"error": "No data available"}
        
        successful_points = [point for point in target_data if point.get("success")]
        response_times = [point["response_time"] for point in successful_points if point.get("response_time")]
        
        performance = {
            "total_monitoring_points": len(target_data),
            "successful_requests": len(successful_points),
            "success_rate": len(successful_points) / len(target_data),
            "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "performance_grade": "UNKNOWN"
        }
        
        # Assign performance grade
        if performance["success_rate"] >= 0.95 and performance["average_response_time"] < 2.0:
            performance["performance_grade"] = "EXCELLENT"
        elif performance["success_rate"] >= 0.9 and performance["average_response_time"] < 3.0:
            performance["performance_grade"] = "GOOD"
        elif performance["success_rate"] >= 0.8 and performance["average_response_time"] < 5.0:
            performance["performance_grade"] = "ACCEPTABLE"
        else:
            performance["performance_grade"] = "POOR"
        
        return performance
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        
        trends = {
            "overall_trend": "STABLE",
            "response_time_trend": "STABLE",
            "success_rate_trend": "STABLE",
            "degradation_detected": False
        }
        
        if len(self.monitoring_data) < 10:
            return trends
        
        # Split data into first and second half for trend analysis
        mid_point = len(self.monitoring_data) // 2
        first_half = self.monitoring_data[:mid_point]
        second_half = self.monitoring_data[mid_point:]
        
        # Calculate metrics for each half
        first_success_rate = sum(1 for p in first_half if p.get("success")) / len(first_half)
        second_success_rate = sum(1 for p in second_half if p.get("success")) / len(second_half)
        
        first_response_times = [p["response_time"] for p in first_half if p.get("response_time")]
        second_response_times = [p["response_time"] for p in second_half if p.get("response_time")]
        
        # Analyze trends
        if second_success_rate < first_success_rate - 0.1:
            trends["success_rate_trend"] = "DECLINING"
            trends["degradation_detected"] = True
        elif second_success_rate > first_success_rate + 0.1:
            trends["success_rate_trend"] = "IMPROVING"
        
        if first_response_times and second_response_times:
            first_avg = sum(first_response_times) / len(first_response_times)
            second_avg = sum(second_response_times) / len(second_response_times)
            
            if second_avg > first_avg * 1.2:
                trends["response_time_trend"] = "DEGRADING"
                trends["degradation_detected"] = True
            elif second_avg < first_avg * 0.8:
                trends["response_time_trend"] = "IMPROVING"
        
        # Overall trend assessment
        if trends["degradation_detected"]:
            trends["overall_trend"] = "DECLINING"
        elif trends["success_rate_trend"] == "IMPROVING" or trends["response_time_trend"] == "IMPROVING":
            trends["overall_trend"] = "IMPROVING"
        
        return trends
    
    def _breakdown_alerts_by_type(self) -> Dict[str, int]:
        """Breakdown alerts by type"""
        
        breakdown = {}
        for alert in self.alert_history:
            alert_type = alert["alert_type"]
            breakdown[alert_type] = breakdown.get(alert_type, 0) + 1
        
        return breakdown
    
    def _identify_most_problematic_target(self) -> Optional[str]:
        """Identify target with most issues"""
        
        target_issues = {}
        
        for alert in self.alert_history:
            target = alert["details"].get("target")
            if target:
                target_issues[target] = target_issues.get(target, 0) + 1
        
        if target_issues:
            return max(target_issues.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _generate_operational_insights(self) -> List[str]:
        """Generate operational insights from surveillance"""
        
        insights = []
        
        # Analysis based on alert patterns
        alert_types = [alert["alert_type"] for alert in self.alert_history]
        
        if "HIGH_ERROR_RATE" in alert_types:
            insights.append("Target stability issues detected - recommend enhanced error handling")
        
        if "RESPONSE_TIME_ANOMALY" in alert_types:
            insights.append("Performance inconsistencies detected - consider load balancing strategies")
        
        if len(self.alert_history) > 5:
            insights.append("Multiple alerts generated - recommend comprehensive system review")
        
        # Analysis based on trends
        trend_analysis = self._analyze_performance_trends()
        if trend_analysis["degradation_detected"]:
            insights.append("Performance degradation trend detected - recommend immediate attention")
        
        # Data volume insights
        if len(self.monitoring_data) > 100:
            insights.append("Extensive monitoring data collected - sufficient for statistical analysis")
        
        # Default insights
        if not insights:
            insights.append("Surveillance operations nominal - no significant issues detected")
        
        return insights
    
    async def _generate_surveillance_intelligence(self) -> Dict[str, Any]:
        """Generate comprehensive surveillance intelligence report"""
        
        self.logger.info("RADIO: Generating surveillance intelligence report")
        
        intelligence = {
            "surveillance_summary": {
                "monitoring_duration": self._calculate_surveillance_duration(),
                "targets_monitored": len(set(point["target"] for point in self.monitoring_data)),
                "total_data_points": len(self.monitoring_data),
                "alerts_generated": len(self.alert_history),
                "anomalies_detected": self._count_anomalies()
            },
            "key_findings": self._extract_key_findings(),
            "threat_assessment": self._assess_threats_from_surveillance(),
            "recommendations": self._generate_surveillance_recommendations(),
            "intelligence_confidence": self._calculate_intelligence_confidence()
        }
        
        return intelligence
    
    def _calculate_surveillance_duration(self) -> str:
        """Calculate total surveillance duration"""
        
        if not self.monitoring_data:
            return "0 minutes"
        
        first_point = min(self.monitoring_data, key=lambda x: x["timestamp"])
        last_point = max(self.monitoring_data, key=lambda x: x["timestamp"])
        
        try:
            first_time = datetime.fromisoformat(first_point["timestamp"])
            last_time = datetime.fromisoformat(last_point["timestamp"])
            duration = last_time - first_time
            
            return f"{duration.total_seconds() / 60:.1f} minutes"
        except:
            return "Unknown duration"
    
    def _extract_key_findings(self) -> List[str]:
        """Extract key findings from surveillance"""
        
        findings = []
        
        # Performance findings
        all_response_times = [p["response_time"] for p in self.monitoring_data if p.get("response_time")]
        if all_response_times:
            avg_response = sum(all_response_times) / len(all_response_times)
            if avg_response > 3.0:
                findings.append(f"Average response time elevated: {avg_response:.2f}s")
            elif avg_response < 1.0:
                findings.append(f"Excellent response times observed: {avg_response:.2f}s")
        
        # Success rate findings
        success_rate = sum(1 for p in self.monitoring_data if p.get("success")) / len(self.monitoring_data) if self.monitoring_data else 0
        if success_rate < 0.9:
            findings.append(f"Success rate below optimal: {success_rate:.1%}")
        elif success_rate >= 0.98:
            findings.append(f"Excellent success rate maintained: {success_rate:.1%}")
        
        # Alert findings
        if len(self.alert_history) == 0:
            findings.append("No anomalies detected during surveillance period")
        elif len(self.alert_history) > 3:
            findings.append(f"Multiple anomalies detected: {len(self.alert_history)} alerts generated")
        
        return findings
    
    def _assess_threats_from_surveillance(self) -> Dict[str, Any]:
        """Assess threats based on surveillance data"""
        
        threat_assessment = {
            "overall_threat_level": "LOW",
            "identified_threats": [],
            "threat_indicators": []
        }
        
        # Analyze alert patterns for threats
        high_severity_alerts = [alert for alert in self.alert_history if alert["severity"] in ["HIGH", "CRITICAL"]]
        
        if len(high_severity_alerts) > 2:
            threat_assessment["overall_threat_level"] = "MODERATE"
            threat_assessment["identified_threats"].append("OPERATIONAL_INSTABILITY")
        
        if any(alert["alert_type"] == "HIGH_ERROR_RATE" for alert in self.alert_history):
            threat_assessment["overall_threat_level"] = "HIGH"
            threat_assessment["identified_threats"].append("SYSTEM_DEGRADATION")
        
        # Check for connection issues
        connection_failures = sum(1 for p in self.monitoring_data if not p.get("success"))
        if connection_failures > len(self.monitoring_data) * 0.2:
            threat_assessment["identified_threats"].append("CONNECTIVITY_ISSUES")
        
        return threat_assessment
    
    def _generate_surveillance_recommendations(self) -> List[str]:
        """Generate recommendations based on surveillance"""
        
        recommendations = []
        
        # Based on alerts
        if len(self.alert_history) > 5:
            recommendations.append("Implement enhanced monitoring and alerting systems")
        
        # Based on performance
        response_times = [p["response_time"] for p in self.monitoring_data if p.get("response_time")]
        if response_times and sum(response_times) / len(response_times) > 3.0:
            recommendations.append("Optimize request timing and implement delays")
        
        # Based on success rates
        success_rate = sum(1 for p in self.monitoring_data if p.get("success")) / len(self.monitoring_data) if self.monitoring_data else 1
        if success_rate < 0.9:
            recommendations.append("Investigate and resolve connectivity issues")
        
        # General recommendations
        recommendations.extend([
            "Continue surveillance monitoring for trend analysis",
            "Maintain real-time alerting for anomaly detection",
            "Regular review of performance baselines"
        ])
        
        return recommendations
    
    def _calculate_intelligence_confidence(self) -> str:
        """Calculate confidence level in intelligence"""
        
        data_points = len(self.monitoring_data)
        surveillance_duration = self._calculate_surveillance_duration()
        
        if data_points > 50 and "minute" in surveillance_duration and float(surveillance_duration.split()[0]) > 10:
            return "HIGH"
        elif data_points > 20:
            return "MODERATE"
        else:
            return "LOW"
    
    def stop_surveillance_operations(self):
        """Stop all surveillance operations"""
        
        self.surveillance_active = False
        self.stop_surveillance.set()
        
        if self.surveillance_thread and self.surveillance_thread.is_alive():
            self.surveillance_thread.join(timeout=5)
        
        self.logger.info("RADIO: Surveillance operations terminated")