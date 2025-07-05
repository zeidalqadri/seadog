"""
SEADOG Test Runner - Military Testing Framework
Comprehensive test orchestration and execution system
"""

import asyncio
import logging
import json
import time
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .base_scenario import BaseScenario, ScenarioResult, ScenarioStatus
from .reconnaissance_scenario import ReconnaissanceScenario


class TestSuite(Enum):
    """Test suite categories"""
    RECONNAISSANCE = "RECONNAISSANCE"
    PENETRATION_TESTING = "PENETRATION_TESTING"
    STRESS_TESTING = "STRESS_TESTING"
    PERFORMANCE_TESTING = "PERFORMANCE_TESTING"
    COMPLIANCE_TESTING = "COMPLIANCE_TESTING"
    INTEGRATION_TESTING = "INTEGRATION_TESTING"
    OPERATIONAL_TESTING = "OPERATIONAL_TESTING"
    FULL_SPECTRUM = "FULL_SPECTRUM"


@dataclass
class TestConfiguration:
    """Test configuration settings"""
    suite_type: TestSuite
    target_urls: List[str]
    test_parameters: Dict[str, Any]
    execution_timeout: int  # minutes
    parallel_execution: bool
    report_format: str
    output_directory: str


class SEADOGTestRunner:
    """SEADOG Military Testing Framework Test Runner"""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.logger = logging.getLogger("SEADOG.TestRunner")
        
        # Test execution tracking
        self.test_execution_id = f"SEADOG_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.scenarios: List[BaseScenario] = []
        self.test_results: List[ScenarioResult] = []
        self.execution_start: Optional[datetime] = None
        self.execution_end: Optional[datetime] = None
        
        # Test metrics
        self.overall_metrics = {
            "total_scenarios": 0,
            "successful_scenarios": 0,
            "failed_scenarios": 0,
            "total_execution_time": 0.0,
            "average_scenario_time": 0.0,
            "success_rate": 0.0,
            "overall_score": 0.0
        }
        
        self.logger.info(f"SEADOG Test Runner initialized - Execution ID: {self.test_execution_id}")
    
    async def run_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite"""
        
        self.logger.info(f"Starting SEADOG test suite: {self.config.suite_type.value}")
        self.execution_start = datetime.now()
        
        try:
            # Initialize test scenarios
            await self._initialize_test_scenarios()
            
            # Execute test scenarios
            if self.config.parallel_execution:
                test_results = await self._execute_scenarios_parallel()
            else:
                test_results = await self._execute_scenarios_sequential()
            
            self.test_results = test_results
            
            # Calculate overall metrics
            self._calculate_overall_metrics()
            
            # Generate test report
            test_report = await self._generate_test_report()
            
            # Save test results
            await self._save_test_results(test_report)
            
            self.execution_end = datetime.now()
            
            self.logger.info(f"SEADOG test suite completed: {len(test_results)} scenarios executed")
            return test_report
            
        except Exception as e:
            self.logger.error(f"Test suite execution failed: {str(e)}")
            self.execution_end = datetime.now()
            
            return {
                "execution_id": self.test_execution_id,
                "status": "FAILED",
                "error": str(e),
                "execution_time": str(self.execution_end - self.execution_start) if self.execution_start else None
            }
    
    async def _initialize_test_scenarios(self):
        """Initialize test scenarios based on suite type"""
        
        self.logger.info(f"Initializing scenarios for suite: {self.config.suite_type.value}")
        
        if self.config.suite_type == TestSuite.RECONNAISSANCE:
            await self._initialize_reconnaissance_scenarios()
        elif self.config.suite_type == TestSuite.PENETRATION_TESTING:
            await self._initialize_penetration_scenarios()
        elif self.config.suite_type == TestSuite.STRESS_TESTING:
            await self._initialize_stress_scenarios()
        elif self.config.suite_type == TestSuite.PERFORMANCE_TESTING:
            await self._initialize_performance_scenarios()
        elif self.config.suite_type == TestSuite.COMPLIANCE_TESTING:
            await self._initialize_compliance_scenarios()
        elif self.config.suite_type == TestSuite.INTEGRATION_TESTING:
            await self._initialize_integration_scenarios()
        elif self.config.suite_type == TestSuite.OPERATIONAL_TESTING:
            await self._initialize_operational_scenarios()
        elif self.config.suite_type == TestSuite.FULL_SPECTRUM:
            await self._initialize_full_spectrum_scenarios()
        
        self.logger.info(f"Initialized {len(self.scenarios)} test scenarios")
    
    async def _initialize_reconnaissance_scenarios(self):
        """Initialize reconnaissance test scenarios"""
        
        # Basic reconnaissance scenario
        recon_scenario = ReconnaissanceScenario("RECON_BASIC_001")
        for url in self.config.target_urls:
            recon_scenario.add_target_url(url)
        
        # Set reconnaissance parameters
        recon_params = self.config.test_parameters.get("reconnaissance", {})
        recon_scenario.set_reconnaissance_depth(recon_params.get("depth", "COMPREHENSIVE"))
        recon_scenario.set_operational_security_level(recon_params.get("opsec_level", "COVERT"))
        
        self.scenarios.append(recon_scenario)
        
        # Advanced intelligence gathering scenario
        intel_scenario = ReconnaissanceScenario("INTEL_ADVANCED_001")
        intel_scenario.set_reconnaissance_depth("DEEP_ANALYSIS")
        intel_scenario.set_operational_security_level("DEEP_COVER")
        
        for url in self.config.target_urls:
            intel_scenario.add_target_url(url)
        
        # Add intelligence requirements
        intel_scenario.add_intelligence_requirement({
            "requirement_id": "INTEL_REQ_001",
            "requirement_type": "THREAT_ASSESSMENT",
            "priority": "HIGH",
            "scope": "COMPREHENSIVE"
        })
        
        self.scenarios.append(intel_scenario)
    
    async def _initialize_penetration_scenarios(self):
        """Initialize penetration testing scenarios"""
        # Placeholder for penetration testing scenarios
        self.logger.info("Penetration testing scenarios not yet implemented")
    
    async def _initialize_stress_scenarios(self):
        """Initialize stress testing scenarios"""
        # Placeholder for stress testing scenarios
        self.logger.info("Stress testing scenarios not yet implemented")
    
    async def _initialize_performance_scenarios(self):
        """Initialize performance testing scenarios"""
        # Placeholder for performance testing scenarios
        self.logger.info("Performance testing scenarios not yet implemented")
    
    async def _initialize_compliance_scenarios(self):
        """Initialize compliance testing scenarios"""
        # Placeholder for compliance testing scenarios
        self.logger.info("Compliance testing scenarios not yet implemented")
    
    async def _initialize_integration_scenarios(self):
        """Initialize integration testing scenarios"""
        # Placeholder for integration testing scenarios
        self.logger.info("Integration testing scenarios not yet implemented")
    
    async def _initialize_operational_scenarios(self):
        """Initialize operational testing scenarios"""
        # Placeholder for operational testing scenarios
        self.logger.info("Operational testing scenarios not yet implemented")
    
    async def _initialize_full_spectrum_scenarios(self):
        """Initialize full spectrum testing scenarios"""
        
        # Include all scenario types
        await self._initialize_reconnaissance_scenarios()
        await self._initialize_penetration_scenarios()
        await self._initialize_stress_scenarios()
        await self._initialize_performance_scenarios()
        await self._initialize_compliance_scenarios()
        await self._initialize_integration_scenarios()
        await self._initialize_operational_scenarios()
    
    async def _execute_scenarios_parallel(self) -> List[ScenarioResult]:
        """Execute scenarios in parallel"""
        
        self.logger.info(f"Executing {len(self.scenarios)} scenarios in parallel")
        
        # Create tasks for all scenarios
        tasks = []
        for scenario in self.scenarios:
            task = asyncio.create_task(self._execute_single_scenario(scenario))
            tasks.append(task)
        
        # Execute all scenarios concurrently with timeout
        timeout_seconds = self.config.execution_timeout * 60
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout_seconds
            )
            
            # Process results
            scenario_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Scenario {self.scenarios[i].scenario_id} failed: {str(result)}")
                    # Create failure result
                    failure_result = self._create_scenario_failure_result(self.scenarios[i], str(result))
                    scenario_results.append(failure_result)
                else:
                    scenario_results.append(result)
            
            return scenario_results
            
        except asyncio.TimeoutError:
            self.logger.error(f"Test execution timed out after {self.config.execution_timeout} minutes")
            
            # Create timeout results for all scenarios
            timeout_results = []
            for scenario in self.scenarios:
                timeout_result = self._create_scenario_timeout_result(scenario)
                timeout_results.append(timeout_result)
            
            return timeout_results
    
    async def _execute_scenarios_sequential(self) -> List[ScenarioResult]:
        """Execute scenarios sequentially"""
        
        self.logger.info(f"Executing {len(self.scenarios)} scenarios sequentially")
        
        scenario_results = []
        
        for scenario in self.scenarios:
            try:
                result = await self._execute_single_scenario(scenario)
                scenario_results.append(result)
                
                self.logger.info(f"Scenario {scenario.scenario_id} completed: {result.status.value}")
                
            except Exception as e:
                self.logger.error(f"Scenario {scenario.scenario_id} failed: {str(e)}")
                failure_result = self._create_scenario_failure_result(scenario, str(e))
                scenario_results.append(failure_result)
        
        return scenario_results
    
    async def _execute_single_scenario(self, scenario: BaseScenario) -> ScenarioResult:
        """Execute single scenario with monitoring"""
        
        self.logger.info(f"Executing scenario: {scenario.scenario_id}")
        
        start_time = time.time()
        
        try:
            result = await scenario.run_scenario()
            execution_time = time.time() - start_time
            
            self.logger.info(f"Scenario {scenario.scenario_id} completed in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Scenario {scenario.scenario_id} failed after {execution_time:.2f} seconds: {str(e)}")
            raise
    
    def _create_scenario_failure_result(self, scenario: BaseScenario, error_message: str) -> ScenarioResult:
        """Create failure result for scenario"""
        
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            status=ScenarioStatus.FAILED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=timedelta(seconds=0),
            objectives_met=[],
            objectives_failed=[obj.objective_id for obj in scenario.objectives],
            performance_metrics={},
            agent_reports=[],
            validation_results={"error": error_message},
            recommendations=[f"Investigate scenario failure: {error_message}"],
            artifacts=[]
        )
    
    def _create_scenario_timeout_result(self, scenario: BaseScenario) -> ScenarioResult:
        """Create timeout result for scenario"""
        
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            status=ScenarioStatus.ABORTED,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration=timedelta(minutes=self.config.execution_timeout),
            objectives_met=[],
            objectives_failed=[obj.objective_id for obj in scenario.objectives],
            performance_metrics={},
            agent_reports=[],
            validation_results={"error": "Execution timeout"},
            recommendations=["Optimize scenario execution time", "Increase timeout limit"],
            artifacts=[]
        )
    
    def _calculate_overall_metrics(self):
        """Calculate overall test metrics"""
        
        self.overall_metrics["total_scenarios"] = len(self.test_results)
        
        successful_count = 0
        failed_count = 0
        total_execution_time = 0.0
        quality_scores = []
        
        for result in self.test_results:
            if result.status == ScenarioStatus.COMPLETED:
                successful_count += 1
                
                # Add quality score if available
                validation_results = result.validation_results
                if "quality_score" in validation_results:
                    quality_scores.append(validation_results["quality_score"])
                
            else:
                failed_count += 1
            
            # Calculate execution time
            if result.duration:
                total_execution_time += result.duration.total_seconds()
        
        self.overall_metrics["successful_scenarios"] = successful_count
        self.overall_metrics["failed_scenarios"] = failed_count
        self.overall_metrics["total_execution_time"] = total_execution_time
        
        # Calculate derived metrics
        if self.overall_metrics["total_scenarios"] > 0:
            self.overall_metrics["success_rate"] = successful_count / self.overall_metrics["total_scenarios"]
            self.overall_metrics["average_scenario_time"] = total_execution_time / self.overall_metrics["total_scenarios"]
        
        if quality_scores:
            self.overall_metrics["overall_score"] = sum(quality_scores) / len(quality_scores)
    
    async def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        self.logger.info("Generating test report")
        
        report = {
            "execution_metadata": {
                "execution_id": self.test_execution_id,
                "suite_type": self.config.suite_type.value,
                "execution_start": self.execution_start.isoformat() if self.execution_start else None,
                "execution_end": self.execution_end.isoformat() if self.execution_end else None,
                "total_duration": str(self.execution_end - self.execution_start) if self.execution_end and self.execution_start else None,
                "parallel_execution": self.config.parallel_execution,
                "framework_version": "SEADOG-1.0.0"
            },
            
            "test_configuration": {
                "target_urls": self.config.target_urls,
                "test_parameters": self.config.test_parameters,
                "execution_timeout": self.config.execution_timeout,
                "report_format": self.config.report_format,
                "output_directory": self.config.output_directory
            },
            
            "overall_metrics": self.overall_metrics,
            
            "scenario_results": [],
            
            "summary": {
                "test_status": "PASSED" if self.overall_metrics["success_rate"] >= 0.8 else "FAILED",
                "overall_quality": self._assess_overall_quality(),
                "key_findings": self._extract_key_findings(),
                "recommendations": self._generate_overall_recommendations()
            }
        }
        
        # Add detailed scenario results
        for result in self.test_results:
            scenario_report = {
                "scenario_id": result.scenario_id,
                "status": result.status.value,
                "duration": str(result.duration) if result.duration else None,
                "objectives_met": result.objectives_met,
                "objectives_failed": result.objectives_failed,
                "performance_metrics": result.performance_metrics,
                "validation_results": result.validation_results,
                "recommendations": result.recommendations,
                "artifacts": result.artifacts
            }
            report["scenario_results"].append(scenario_report)
        
        return report
    
    def _assess_overall_quality(self) -> str:
        """Assess overall test quality"""
        
        overall_score = self.overall_metrics.get("overall_score", 0.0)
        success_rate = self.overall_metrics.get("success_rate", 0.0)
        
        # Weighted quality assessment
        quality_score = (overall_score * 0.7) + (success_rate * 0.3)
        
        if quality_score >= 0.9:
            return "EXCELLENT"
        elif quality_score >= 0.8:
            return "GOOD"
        elif quality_score >= 0.6:
            return "ACCEPTABLE"
        elif quality_score >= 0.4:
            return "POOR"
        else:
            return "CRITICAL"
    
    def _extract_key_findings(self) -> List[str]:
        """Extract key findings from test results"""
        
        findings = []
        
        # Success rate findings
        success_rate = self.overall_metrics.get("success_rate", 0.0)
        if success_rate < 0.8:
            findings.append(f"LOW_SUCCESS_RATE: {success_rate:.2%} of scenarios failed")
        
        # Performance findings
        avg_time = self.overall_metrics.get("average_scenario_time", 0.0)
        if avg_time > 300:  # 5 minutes
            findings.append(f"SLOW_EXECUTION: Average scenario time {avg_time:.1f} seconds")
        
        # Quality findings
        overall_score = self.overall_metrics.get("overall_score", 0.0)
        if overall_score < 0.7:
            findings.append(f"LOW_QUALITY_SCORE: Overall quality score {overall_score:.2%}")
        
        # Scenario-specific findings
        failed_scenarios = [r for r in self.test_results if r.status != ScenarioStatus.COMPLETED]
        if failed_scenarios:
            findings.append(f"SCENARIO_FAILURES: {len(failed_scenarios)} scenarios failed")
        
        return findings
    
    def _generate_overall_recommendations(self) -> List[str]:
        """Generate overall recommendations"""
        
        recommendations = []
        
        # Success rate recommendations
        success_rate = self.overall_metrics.get("success_rate", 0.0)
        if success_rate < 0.9:
            recommendations.append("IMPROVE_SCENARIO_RELIABILITY")
        
        # Performance recommendations
        avg_time = self.overall_metrics.get("average_scenario_time", 0.0)
        if avg_time > 180:  # 3 minutes
            recommendations.append("OPTIMIZE_SCENARIO_EXECUTION")
        
        # Quality recommendations
        overall_score = self.overall_metrics.get("overall_score", 0.0)
        if overall_score < 0.8:
            recommendations.append("ENHANCE_TEST_QUALITY")
        
        # Coverage recommendations
        if len(self.config.target_urls) < 5:
            recommendations.append("EXPAND_TEST_COVERAGE")
        
        # Agent performance recommendations
        agent_failures = 0
        for result in self.test_results:
            for agent_report in result.agent_reports:
                if agent_report.get("status") != "COMPLETED":
                    agent_failures += 1
        
        if agent_failures > 0:
            recommendations.append("IMPROVE_AGENT_PERFORMANCE")
        
        return recommendations
    
    async def _save_test_results(self, test_report: Dict[str, Any]):
        """Save test results to file"""
        
        # Ensure output directory exists
        os.makedirs(self.config.output_directory, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"seadog_test_report_{self.config.suite_type.value.lower()}_{timestamp}.json"
        filepath = os.path.join(self.config.output_directory, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(test_report, f, indent=2, default=str)
            
            self.logger.info(f"Test report saved to: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save test report: {str(e)}")
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get test execution summary"""
        
        return {
            "execution_id": self.test_execution_id,
            "suite_type": self.config.suite_type.value,
            "total_scenarios": self.overall_metrics.get("total_scenarios", 0),
            "successful_scenarios": self.overall_metrics.get("successful_scenarios", 0),
            "failed_scenarios": self.overall_metrics.get("failed_scenarios", 0),
            "success_rate": f"{self.overall_metrics.get('success_rate', 0.0):.2%}",
            "overall_quality": self._assess_overall_quality(),
            "execution_time": str(self.execution_end - self.execution_start) if self.execution_end and self.execution_start else None
        }


# Utility functions for creating test configurations
def create_reconnaissance_test_config(target_urls: List[str], output_dir: str = "./test_results") -> TestConfiguration:
    """Create reconnaissance test configuration"""
    
    return TestConfiguration(
        suite_type=TestSuite.RECONNAISSANCE,
        target_urls=target_urls,
        test_parameters={
            "reconnaissance": {
                "depth": "COMPREHENSIVE",
                "opsec_level": "COVERT",
                "intelligence_requirements": ["THREAT_ASSESSMENT", "INFRASTRUCTURE_MAPPING"]
            }
        },
        execution_timeout=30,  # 30 minutes
        parallel_execution=True,
        report_format="json",
        output_directory=output_dir
    )


def create_full_spectrum_test_config(target_urls: List[str], output_dir: str = "./test_results") -> TestConfiguration:
    """Create full spectrum test configuration"""
    
    return TestConfiguration(
        suite_type=TestSuite.FULL_SPECTRUM,
        target_urls=target_urls,
        test_parameters={
            "reconnaissance": {
                "depth": "COMPREHENSIVE",
                "opsec_level": "COVERT"
            },
            "penetration_testing": {
                "intensity": "MODERATE",
                "scope": "LIMITED"
            },
            "stress_testing": {
                "load_level": "HIGH",
                "duration": 300  # 5 minutes
            }
        },
        execution_timeout=60,  # 60 minutes
        parallel_execution=False,  # Sequential for full spectrum
        report_format="json",
        output_directory=output_dir
    )