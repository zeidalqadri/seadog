"""
Base Test Scenario - SEADOG Military Testing Framework
Foundation for all test scenarios and validation protocols
"""

import asyncio
import logging
import time
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..base_agent import BaseAgent, MissionStatus, ThreatLevel, ReportPriority


class ScenarioType(Enum):
    """Types of test scenarios"""
    RECONNAISSANCE = "RECONNAISSANCE"
    PENETRATION_TEST = "PENETRATION_TEST"
    STRESS_TEST = "STRESS_TEST"
    VULNERABILITY_ASSESSMENT = "VULNERABILITY_ASSESSMENT"
    PERFORMANCE_BENCHMARK = "PERFORMANCE_BENCHMARK"
    OPERATIONAL_VALIDATION = "OPERATIONAL_VALIDATION"
    INTEGRATION_TEST = "INTEGRATION_TEST"
    COMPLIANCE_AUDIT = "COMPLIANCE_AUDIT"


class ScenarioStatus(Enum):
    """Scenario execution status"""
    PLANNING = "PLANNING"
    READY = "READY"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


@dataclass
class ScenarioObjective:
    """Scenario objective definition"""
    objective_id: str
    objective_type: str
    description: str
    success_criteria: Dict[str, Any]
    validation_method: str
    priority: ReportPriority
    estimated_duration: int  # minutes


@dataclass
class ScenarioResult:
    """Scenario execution result"""
    scenario_id: str
    status: ScenarioStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[timedelta]
    objectives_met: List[str]
    objectives_failed: List[str]
    performance_metrics: Dict[str, Any]
    agent_reports: List[Dict[str, Any]]
    validation_results: Dict[str, Any]
    recommendations: List[str]
    artifacts: List[str]


class BaseScenario(ABC):
    """Base class for all test scenarios"""
    
    def __init__(self, scenario_id: str, scenario_type: ScenarioType):
        self.scenario_id = scenario_id
        self.scenario_type = scenario_type
        self.status = ScenarioStatus.PLANNING
        self.logger = logging.getLogger(f"SEADOG.Scenario.{scenario_id}")
        
        # Scenario configuration
        self.objectives: List[ScenarioObjective] = []
        self.participating_agents: List[BaseAgent] = []
        self.target_urls: List[str] = []
        self.scenario_parameters: Dict[str, Any] = {}
        self.validation_protocols: List[Dict[str, Any]] = []
        
        # Execution tracking
        self.execution_start: Optional[datetime] = None
        self.execution_end: Optional[datetime] = None
        self.results: Optional[ScenarioResult] = None
        self.agent_reports: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
        
        # Scenario metadata
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "scenario_version": "1.0.0",
            "framework_version": "SEADOG-1.0.0",
            "compliance_standards": [],
            "risk_assessment": "MODERATE"
        }
        
        self.logger.info(f"Base scenario {scenario_id} initialized")
    
    @abstractmethod
    async def setup_scenario(self) -> bool:
        """Setup scenario environment and prerequisites"""
        pass
    
    @abstractmethod
    async def execute_scenario(self) -> ScenarioResult:
        """Execute the scenario"""
        pass
    
    @abstractmethod
    async def validate_results(self) -> Dict[str, Any]:
        """Validate scenario results"""
        pass
    
    @abstractmethod
    async def cleanup_scenario(self) -> bool:
        """Cleanup scenario environment"""
        pass
    
    def add_objective(self, objective: ScenarioObjective):
        """Add objective to scenario"""
        self.objectives.append(objective)
        self.logger.info(f"Objective added: {objective.objective_id}")
    
    def add_agent(self, agent: BaseAgent):
        """Add agent to scenario"""
        self.participating_agents.append(agent)
        self.logger.info(f"Agent added: {agent.call_sign} ({agent.agent_id})")
    
    def add_target_url(self, url: str):
        """Add target URL to scenario"""
        self.target_urls.append(url)
        self.logger.info(f"Target URL added: {url}")
    
    def set_parameter(self, key: str, value: Any):
        """Set scenario parameter"""
        self.scenario_parameters[key] = value
        self.logger.info(f"Parameter set: {key} = {value}")
    
    def add_validation_protocol(self, protocol: Dict[str, Any]):
        """Add validation protocol"""
        self.validation_protocols.append(protocol)
        self.logger.info(f"Validation protocol added: {protocol.get('protocol_id', 'UNKNOWN')}")
    
    async def run_scenario(self) -> ScenarioResult:
        """Run complete scenario lifecycle"""
        
        self.logger.info(f"Starting scenario {self.scenario_id}")
        self.status = ScenarioStatus.EXECUTING
        self.execution_start = datetime.now()
        
        try:
            # Setup phase
            setup_success = await self.setup_scenario()
            if not setup_success:
                self.status = ScenarioStatus.FAILED
                self.logger.error("Scenario setup failed")
                return self._create_failure_result("Setup failed")
            
            # Execution phase
            self.logger.info("Beginning scenario execution")
            result = await self.execute_scenario()
            
            # Validation phase
            self.logger.info("Validating scenario results")
            validation_results = await self.validate_results()
            result.validation_results = validation_results
            
            # Cleanup phase
            cleanup_success = await self.cleanup_scenario()
            if not cleanup_success:
                self.logger.warning("Scenario cleanup encountered issues")
            
            self.execution_end = datetime.now()
            result.end_time = self.execution_end
            result.duration = self.execution_end - self.execution_start
            
            self.status = ScenarioStatus.COMPLETED
            self.results = result
            
            self.logger.info(f"Scenario {self.scenario_id} completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Scenario execution failed: {str(e)}")
            self.status = ScenarioStatus.FAILED
            self.execution_end = datetime.now()
            
            # Attempt cleanup even on failure
            try:
                await self.cleanup_scenario()
            except Exception as cleanup_error:
                self.logger.error(f"Cleanup failed: {str(cleanup_error)}")
            
            return self._create_failure_result(str(e))
    
    def _create_failure_result(self, error_message: str) -> ScenarioResult:
        """Create failure result"""
        return ScenarioResult(
            scenario_id=self.scenario_id,
            status=ScenarioStatus.FAILED,
            start_time=self.execution_start or datetime.now(),
            end_time=datetime.now(),
            duration=None,
            objectives_met=[],
            objectives_failed=[obj.objective_id for obj in self.objectives],
            performance_metrics={},
            agent_reports=[],
            validation_results={"error": error_message},
            recommendations=[f"Investigate failure: {error_message}"],
            artifacts=[]
        )
    
    async def execute_agents(self) -> List[Dict[str, Any]]:
        """Execute all participating agents"""
        
        self.logger.info(f"Executing {len(self.participating_agents)} agents")
        agent_results = []
        
        # Execute agents concurrently
        tasks = []
        for agent in self.participating_agents:
            task = self._execute_agent_mission(agent)
            tasks.append(task)
        
        # Wait for all agents to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            agent = self.participating_agents[i]
            
            if isinstance(result, Exception):
                self.logger.error(f"Agent {agent.call_sign} failed: {str(result)}")
                agent_result = {
                    "agent_id": agent.agent_id,
                    "call_sign": agent.call_sign,
                    "squad": agent.squad,
                    "status": "FAILED",
                    "error": str(result),
                    "execution_time": 0
                }
            else:
                agent_result = {
                    "agent_id": agent.agent_id,
                    "call_sign": agent.call_sign,
                    "squad": agent.squad,
                    "status": "COMPLETED",
                    "result": result,
                    "execution_time": result.get("execution_time", 0)
                }
            
            agent_results.append(agent_result)
        
        self.agent_reports = agent_results
        return agent_results
    
    async def _execute_agent_mission(self, agent: BaseAgent) -> Dict[str, Any]:
        """Execute individual agent mission"""
        
        start_time = time.time()
        
        # Prepare mission parameters
        mission_params = {
            "scenario_id": self.scenario_id,
            "target_urls": self.target_urls,
            "scenario_parameters": self.scenario_parameters,
            "objectives": [obj.objective_id for obj in self.objectives]
        }
        
        # Execute agent mission
        result = await agent.execute_mission(mission_params)
        
        execution_time = time.time() - start_time
        result["execution_time"] = execution_time
        
        return result
    
    def calculate_performance_metrics(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics from agent results"""
        
        metrics = {
            "total_agents": len(agent_results),
            "successful_agents": 0,
            "failed_agents": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0,
            "max_execution_time": 0.0,
            "min_execution_time": float('inf'),
            "throughput": 0.0,  # agents per minute
            "success_rate": 0.0
        }
        
        execution_times = []
        
        for result in agent_results:
            if result.get("status") == "COMPLETED":
                metrics["successful_agents"] += 1
            else:
                metrics["failed_agents"] += 1
            
            exec_time = result.get("execution_time", 0)
            execution_times.append(exec_time)
            metrics["total_execution_time"] += exec_time
            
            if exec_time > metrics["max_execution_time"]:
                metrics["max_execution_time"] = exec_time
            if exec_time < metrics["min_execution_time"]:
                metrics["min_execution_time"] = exec_time
        
        # Calculate derived metrics
        if execution_times:
            metrics["average_execution_time"] = sum(execution_times) / len(execution_times)
            metrics["min_execution_time"] = min(execution_times)
            
            if metrics["average_execution_time"] > 0:
                metrics["throughput"] = 60 / metrics["average_execution_time"]  # agents per minute
        
        if metrics["total_agents"] > 0:
            metrics["success_rate"] = metrics["successful_agents"] / metrics["total_agents"]
        
        return metrics
    
    def evaluate_objectives(self, agent_results: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Evaluate scenario objectives"""
        
        objectives_met = []
        objectives_failed = []
        
        for objective in self.objectives:
            if self._evaluate_objective(objective, agent_results):
                objectives_met.append(objective.objective_id)
            else:
                objectives_failed.append(objective.objective_id)
        
        return objectives_met, objectives_failed
    
    def _evaluate_objective(self, objective: ScenarioObjective, agent_results: List[Dict[str, Any]]) -> bool:
        """Evaluate individual objective"""
        
        success_criteria = objective.success_criteria
        
        # Basic success criteria evaluation
        if "min_success_rate" in success_criteria:
            min_success_rate = success_criteria["min_success_rate"]
            metrics = self.calculate_performance_metrics(agent_results)
            if metrics["success_rate"] < min_success_rate:
                return False
        
        if "max_execution_time" in success_criteria:
            max_exec_time = success_criteria["max_execution_time"]
            metrics = self.calculate_performance_metrics(agent_results)
            if metrics["average_execution_time"] > max_exec_time:
                return False
        
        if "required_agents" in success_criteria:
            required_agents = success_criteria["required_agents"]
            successful_agents = sum(1 for r in agent_results if r.get("status") == "COMPLETED")
            if successful_agents < required_agents:
                return False
        
        return True
    
    def generate_recommendations(self, agent_results: List[Dict[str, Any]], 
                               validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on results"""
        
        recommendations = []
        
        # Performance-based recommendations
        metrics = self.calculate_performance_metrics(agent_results)
        
        if metrics["success_rate"] < 0.9:
            recommendations.append("IMPROVE_AGENT_RELIABILITY")
        
        if metrics["average_execution_time"] > 30:
            recommendations.append("OPTIMIZE_AGENT_PERFORMANCE")
        
        if metrics["failed_agents"] > 0:
            recommendations.append("INVESTIGATE_AGENT_FAILURES")
        
        # Validation-based recommendations
        if validation_results.get("validation_errors"):
            recommendations.append("ADDRESS_VALIDATION_ISSUES")
        
        if validation_results.get("compliance_issues"):
            recommendations.append("IMPROVE_COMPLIANCE_ADHERENCE")
        
        return recommendations
    
    def get_scenario_summary(self) -> Dict[str, Any]:
        """Get scenario summary"""
        
        return {
            "scenario_id": self.scenario_id,
            "scenario_type": self.scenario_type.value,
            "status": self.status.value,
            "objectives_count": len(self.objectives),
            "agents_count": len(self.participating_agents),
            "target_urls_count": len(self.target_urls),
            "validation_protocols_count": len(self.validation_protocols),
            "execution_duration": str(self.execution_end - self.execution_start) if self.execution_end and self.execution_start else None,
            "created_at": self.metadata["created_at"],
            "framework_version": self.metadata["framework_version"]
        }
    
    def export_results(self, format: str = "json") -> str:
        """Export scenario results"""
        
        if not self.results:
            return json.dumps({"error": "No results available"})
        
        if format.lower() == "json":
            return json.dumps({
                "scenario_summary": self.get_scenario_summary(),
                "results": {
                    "status": self.results.status.value,
                    "duration": str(self.results.duration) if self.results.duration else None,
                    "objectives_met": self.results.objectives_met,
                    "objectives_failed": self.results.objectives_failed,
                    "performance_metrics": self.results.performance_metrics,
                    "validation_results": self.results.validation_results,
                    "recommendations": self.results.recommendations
                },
                "agent_reports": self.agent_reports,
                "metadata": self.metadata
            }, indent=2)
        
        return "Unsupported format"