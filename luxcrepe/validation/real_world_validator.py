"""
Real-World Validation System for SEADOG-Luxcrepe Integration
Test the integrated system against real websites with comprehensive validation
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

from ..integration import LuxcrepeSEADOGIntegration, IntegrationConfig
from ..config import get_seadog_configurations, TargetType


@dataclass
class ValidationTarget:
    """Real-world validation target definition"""
    url: str
    target_type: TargetType
    description: str
    expected_data_fields: List[str]
    validation_criteria: Dict[str, Any]
    risk_level: str
    test_notes: str


@dataclass
class ValidationResult:
    """Validation result for a specific target"""
    target: ValidationTarget
    test_timestamp: datetime
    integration_results: Optional[Dict[str, Any]]
    seadog_results: Optional[Dict[str, Any]]
    validation_score: float
    passed_checks: List[str]
    failed_checks: List[str]
    performance_metrics: Dict[str, Any]
    recommendations: List[str]
    error_details: Optional[str]


class RealWorldValidator:
    """Real-world validation system for SEADOG-Luxcrepe integration"""
    
    def __init__(self):
        self.logger = logging.getLogger("Luxcrepe.Validation.RealWorld")
        
        # Validation targets (safe, publicly accessible sites for testing)
        self.validation_targets = self._initialize_validation_targets()
        
        # Validation criteria
        self.validation_criteria = {
            "min_success_rate": 0.8,
            "max_avg_response_time": 10.0,
            "min_data_extraction_rate": 0.7,
            "max_error_rate": 0.2,
            "min_stealth_score": 0.8
        }
        
        self.logger.info("Real-world validator initialized")
    
    def _initialize_validation_targets(self) -> List[ValidationTarget]:
        """Initialize safe validation targets for testing"""
        
        targets = []
        
        # Example e-commerce site (publicly accessible)
        targets.append(ValidationTarget(
            url="https://demo.opencart.com/",
            target_type=TargetType.ECOMMERCE,
            description="OpenCart Demo Store - E-commerce testing",
            expected_data_fields=["name", "price", "description", "image"],
            validation_criteria={
                "min_products_found": 10,
                "product_completeness_rate": 0.8,
                "price_extraction_accuracy": 0.9
            },
            risk_level="LOW",
            test_notes="Public demo site - safe for testing"
        ))
        
        # Example news/blog site
        targets.append(ValidationTarget(
            url="https://jsonplaceholder.typicode.com/",
            target_type=TargetType.API_ENDPOINT,
            description="JSONPlaceholder API - API endpoint testing",
            expected_data_fields=["title", "body", "userId", "id"],
            validation_criteria={
                "api_response_validation": True,
                "json_structure_compliance": True,
                "response_time_threshold": 3.0
            },
            risk_level="MINIMAL",
            test_notes="Public testing API - completely safe"
        ))
        
        # Example corporate site
        targets.append(ValidationTarget(
            url="https://httpbin.org/",
            target_type=TargetType.API_ENDPOINT,
            description="HTTPBin - HTTP testing service",
            expected_data_fields=["headers", "origin", "url"],
            validation_criteria={
                "http_methods_support": True,
                "header_handling": True,
                "response_format_validation": True
            },
            risk_level="MINIMAL",
            test_notes="HTTP testing service - designed for testing"
        ))
        
        return targets
    
    async def run_comprehensive_validation(self, 
                                         target_filter: Optional[TargetType] = None,
                                         max_targets: int = 3) -> Dict[str, Any]:
        """Run comprehensive validation against real-world targets"""
        
        self.logger.info("Starting comprehensive real-world validation")
        
        # Filter targets if specified
        targets_to_test = self.validation_targets
        if target_filter:
            targets_to_test = [t for t in targets_to_test if t.target_type == target_filter]
        
        # Limit number of targets
        targets_to_test = targets_to_test[:max_targets]
        
        validation_results = []
        overall_metrics = {
            "total_targets": len(targets_to_test),
            "successful_validations": 0,
            "failed_validations": 0,
            "average_validation_score": 0.0,
            "total_validation_time": 0.0,
            "start_time": datetime.now()
        }
        
        # Test each target
        for target in targets_to_test:
            try:
                self.logger.info(f"Validating target: {target.description}")
                
                start_time = time.time()
                result = await self._validate_single_target(target)
                validation_time = time.time() - start_time
                
                result.performance_metrics["validation_time"] = validation_time
                validation_results.append(result)
                
                if result.validation_score >= 0.7:
                    overall_metrics["successful_validations"] += 1
                else:
                    overall_metrics["failed_validations"] += 1
                
                overall_metrics["total_validation_time"] += validation_time
                
                self.logger.info(f"Target validation completed: {target.description} - Score: {result.validation_score:.2f}")
                
                # Brief pause between targets to be respectful
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Validation failed for {target.description}: {str(e)}")
                
                # Create failed result
                failed_result = ValidationResult(
                    target=target,
                    test_timestamp=datetime.now(),
                    integration_results=None,
                    seadog_results=None,
                    validation_score=0.0,
                    passed_checks=[],
                    failed_checks=["VALIDATION_EXECUTION_FAILED"],
                    performance_metrics={"validation_time": time.time() - start_time},
                    recommendations=["Investigate validation failure"],
                    error_details=str(e)
                )
                validation_results.append(failed_result)
                overall_metrics["failed_validations"] += 1
        
        # Calculate overall metrics
        if validation_results:
            overall_metrics["average_validation_score"] = sum(
                r.validation_score for r in validation_results
            ) / len(validation_results)
        
        overall_metrics["end_time"] = datetime.now()
        overall_metrics["total_duration"] = str(overall_metrics["end_time"] - overall_metrics["start_time"])
        
        # Generate comprehensive report
        validation_report = {
            "validation_id": f"REALWORLD_VALIDATION_{int(time.time())}",
            "overall_metrics": overall_metrics,
            "target_results": [asdict(result) for result in validation_results],
            "summary": self._generate_validation_summary(validation_results, overall_metrics),
            "recommendations": self._generate_overall_recommendations(validation_results)
        }
        
        self.logger.info("Comprehensive validation completed")
        return validation_report
    
    async def _validate_single_target(self, target: ValidationTarget) -> ValidationResult:
        """Validate a single target using SEADOG integration"""
        
        # Get appropriate configuration for target type
        configs = get_seadog_configurations()
        suitable_configs = configs.get_configurations_by_target_type(target.target_type)
        
        # Use the first suitable configuration with LOW or MINIMAL risk
        integration_config = None
        for config in suitable_configs:
            if config.risk_assessment in ["MINIMAL", "LOW"]:
                integration_config = config.integration_config
                break
        
        if not integration_config:
            # Fallback to default safe configuration
            integration_config = IntegrationConfig(
                intelligence_enabled=True,
                real_time_monitoring=True,
                test_suite_type="RECONNAISSANCE",
                parallel_execution=False,  # Sequential for safety
                timeout_minutes=10
            )
        
        # Create integration instance
        integration = LuxcrepeSEADOGIntegration(integration_config)
        
        try:
            await integration.start_integration()
            
            # Run integrated scrape test with light intensity
            integration_results = await integration.integrated_scrape_with_testing(
                target.url, 
                enable_testing=True, 
                test_intensity="LIGHT"  # Use light intensity for safety
            )
            
            # Run SEADOG reconnaissance
            seadog_results = await integration.execute_mission_test([target.url], "RECONNAISSANCE")
            
            # Validate results
            validation_score, passed_checks, failed_checks = self._evaluate_target_results(
                target, integration_results, seadog_results
            )
            
            # Generate recommendations
            recommendations = self._generate_target_recommendations(
                target, integration_results, seadog_results, failed_checks
            )
            
            return ValidationResult(
                target=target,
                test_timestamp=datetime.now(),
                integration_results=integration_results,
                seadog_results=seadog_results,
                validation_score=validation_score,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                performance_metrics=integration_results.get("performance_metrics", {}),
                recommendations=recommendations,
                error_details=None
            )
            
        finally:
            await integration.stop_integration()
    
    def _evaluate_target_results(self, target: ValidationTarget, 
                               integration_results: Dict[str, Any],
                               seadog_results: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Evaluate validation results for a target"""
        
        passed_checks = []
        failed_checks = []
        score_components = []
        
        # Check integration results
        if integration_results and not integration_results.get("error"):
            passed_checks.append("INTEGRATION_EXECUTION_SUCCESS")
            score_components.append(0.3)
            
            # Check scraping results
            scraping_results = integration_results.get("scraping_results", [])
            if scraping_results:
                passed_checks.append("DATA_EXTRACTION_SUCCESS")
                score_components.append(0.2)
                
                # Check data quality for e-commerce targets
                if target.target_type == TargetType.ECOMMERCE:
                    data_quality_score = self._evaluate_ecommerce_data_quality(scraping_results, target)
                    if data_quality_score >= 0.7:
                        passed_checks.append("DATA_QUALITY_ACCEPTABLE")
                        score_components.append(data_quality_score * 0.2)
                    else:
                        failed_checks.append("LOW_DATA_QUALITY")
            else:
                failed_checks.append("NO_DATA_EXTRACTED")
            
            # Check performance metrics
            perf_metrics = integration_results.get("performance_metrics", {})
            if perf_metrics.get("success", False):
                passed_checks.append("PERFORMANCE_SUCCESS")
                
                execution_time = perf_metrics.get("total_execution_time", 0)
                if execution_time <= self.validation_criteria["max_avg_response_time"]:
                    passed_checks.append("ACCEPTABLE_RESPONSE_TIME")
                    score_components.append(0.1)
                else:
                    failed_checks.append("SLOW_RESPONSE_TIME")
            else:
                failed_checks.append("PERFORMANCE_FAILURE")
        else:
            failed_checks.append("INTEGRATION_EXECUTION_FAILED")
        
        # Check SEADOG results
        if seadog_results and seadog_results.get("summary", {}).get("test_status") == "PASSED":
            passed_checks.append("SEADOG_TESTING_SUCCESS")
            score_components.append(0.2)
            
            overall_metrics = seadog_results.get("overall_metrics", {})
            success_rate = overall_metrics.get("success_rate", 0)
            
            if success_rate >= self.validation_criteria["min_success_rate"]:
                passed_checks.append("ACCEPTABLE_SUCCESS_RATE")
                score_components.append(success_rate * 0.1)
            else:
                failed_checks.append("LOW_SUCCESS_RATE")
        else:
            failed_checks.append("SEADOG_TESTING_FAILED")
        
        # Calculate overall validation score
        validation_score = sum(score_components) if score_components else 0.0
        validation_score = min(validation_score, 1.0)  # Cap at 1.0
        
        return validation_score, passed_checks, failed_checks
    
    def _evaluate_ecommerce_data_quality(self, scraping_results: List[Dict[str, Any]], 
                                       target: ValidationTarget) -> float:
        """Evaluate data quality for e-commerce scraping results"""
        
        if not scraping_results:
            return 0.0
        
        quality_scores = []
        expected_fields = target.expected_data_fields
        
        for product in scraping_results:
            field_completeness = sum(1 for field in expected_fields if product.get(field)) / len(expected_fields)
            quality_scores.append(field_completeness)
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
    def _generate_target_recommendations(self, target: ValidationTarget,
                                       integration_results: Dict[str, Any],
                                       seadog_results: Dict[str, Any],
                                       failed_checks: List[str]) -> List[str]:
        """Generate recommendations for a specific target"""
        
        recommendations = []
        
        # Integration-specific recommendations
        if "INTEGRATION_EXECUTION_FAILED" in failed_checks:
            recommendations.append("Review integration configuration for target type")
        
        if "NO_DATA_EXTRACTED" in failed_checks:
            recommendations.append("Optimize extraction rules for target website structure")
        
        if "LOW_DATA_QUALITY" in failed_checks:
            recommendations.append("Improve data extraction accuracy for required fields")
        
        if "SLOW_RESPONSE_TIME" in failed_checks:
            recommendations.append("Optimize request timing and reduce processing overhead")
        
        # SEADOG-specific recommendations
        if "SEADOG_TESTING_FAILED" in failed_checks:
            recommendations.append("Review SEADOG testing configuration and parameters")
        
        if "LOW_SUCCESS_RATE" in failed_checks:
            recommendations.append("Investigate agent reliability and error handling")
        
        # Target-specific recommendations
        if target.target_type == TargetType.ECOMMERCE:
            recommendations.append("Consider implementing e-commerce specific extraction rules")
        elif target.target_type == TargetType.API_ENDPOINT:
            recommendations.append("Optimize API request handling and response parsing")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _generate_validation_summary(self, validation_results: List[ValidationResult],
                                   overall_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary"""
        
        summary = {
            "validation_status": "PASSED" if overall_metrics["average_validation_score"] >= 0.7 else "FAILED",
            "success_rate": overall_metrics["successful_validations"] / overall_metrics["total_targets"] if overall_metrics["total_targets"] > 0 else 0,
            "average_score": overall_metrics["average_validation_score"],
            "total_targets_tested": overall_metrics["total_targets"],
            "key_findings": [],
            "critical_issues": []
        }
        
        # Analyze results for key findings
        high_scoring_targets = [r for r in validation_results if r.validation_score >= 0.8]
        low_scoring_targets = [r for r in validation_results if r.validation_score < 0.5]
        
        if high_scoring_targets:
            summary["key_findings"].append(f"{len(high_scoring_targets)} targets achieved high validation scores")
        
        if low_scoring_targets:
            summary["critical_issues"].append(f"{len(low_scoring_targets)} targets failed validation")
        
        # Common failure patterns
        common_failures = {}
        for result in validation_results:
            for failure in result.failed_checks:
                common_failures[failure] = common_failures.get(failure, 0) + 1
        
        if common_failures:
            most_common_failure = max(common_failures.items(), key=lambda x: x[1])
            summary["critical_issues"].append(f"Most common failure: {most_common_failure[0]} ({most_common_failure[1]} targets)")
        
        return summary
    
    def _generate_overall_recommendations(self, validation_results: List[ValidationResult]) -> List[str]:
        """Generate overall recommendations from all validation results"""
        
        recommendations = []
        
        # Analyze overall performance
        avg_score = sum(r.validation_score for r in validation_results) / len(validation_results) if validation_results else 0
        
        if avg_score < 0.7:
            recommendations.append("URGENT: Overall validation score below acceptable threshold")
        
        # Count failure types
        failure_counts = {}
        for result in validation_results:
            for failure in result.failed_checks:
                failure_counts[failure] = failure_counts.get(failure, 0) + 1
        
        # Recommend improvements for common failures
        if failure_counts.get("NO_DATA_EXTRACTED", 0) > 1:
            recommendations.append("Improve data extraction reliability across target types")
        
        if failure_counts.get("SLOW_RESPONSE_TIME", 0) > 1:
            recommendations.append("Optimize system performance and response times")
        
        if failure_counts.get("LOW_SUCCESS_RATE", 0) > 1:
            recommendations.append("Enhance SEADOG agent reliability and error handling")
        
        # Target-specific recommendations
        target_types = [r.target.target_type for r in validation_results]
        if TargetType.ECOMMERCE in target_types:
            recommendations.append("Consider specialized e-commerce optimization configurations")
        
        if TargetType.API_ENDPOINT in target_types:
            recommendations.append("Implement API-specific testing and validation protocols")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def get_validation_targets(self) -> List[ValidationTarget]:
        """Get all available validation targets"""
        return self.validation_targets
    
    def add_custom_target(self, target: ValidationTarget):
        """Add a custom validation target"""
        self.validation_targets.append(target)
        self.logger.info(f"Custom validation target added: {target.description}")
    
    async def quick_validation(self, target_url: str) -> ValidationResult:
        """Quick validation of a single URL"""
        
        # Create a temporary target
        temp_target = ValidationTarget(
            url=target_url,
            target_type=TargetType.UNKNOWN,
            description=f"Quick validation: {target_url}",
            expected_data_fields=["title", "content"],
            validation_criteria={"basic_extraction": True},
            risk_level="UNKNOWN",
            test_notes="Quick validation target"
        )
        
        return await self._validate_single_target(temp_target)
    
    def export_validation_report(self, validation_report: Dict[str, Any], 
                               filepath: str, format: str = "json"):
        """Export validation report to file"""
        
        if format.lower() == "json":
            with open(filepath, 'w') as f:
                json.dump(validation_report, f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Validation report exported to: {filepath}")


# Convenience functions
async def run_quick_validation(target_urls: List[str]) -> Dict[str, Any]:
    """Quick validation of multiple URLs"""
    
    validator = RealWorldValidator()
    results = []
    
    for url in target_urls:
        try:
            result = await validator.quick_validation(url)
            results.append(result)
        except Exception as e:
            # Create failed result
            failed_result = ValidationResult(
                target=ValidationTarget(
                    url=url,
                    target_type=TargetType.UNKNOWN,
                    description=f"Quick validation: {url}",
                    expected_data_fields=[],
                    validation_criteria={},
                    risk_level="UNKNOWN",
                    test_notes="Quick validation failed"
                ),
                test_timestamp=datetime.now(),
                integration_results=None,
                seadog_results=None,
                validation_score=0.0,
                passed_checks=[],
                failed_checks=["VALIDATION_FAILED"],
                performance_metrics={},
                recommendations=["Investigate validation failure"],
                error_details=str(e)
            )
            results.append(failed_result)
    
    return {
        "validation_type": "QUICK_VALIDATION",
        "results": [asdict(r) for r in results],
        "summary": {
            "total_urls": len(target_urls),
            "successful_validations": sum(1 for r in results if r.validation_score > 0.5),
            "average_score": sum(r.validation_score for r in results) / len(results) if results else 0
        }
    }


async def validate_ecommerce_sites() -> Dict[str, Any]:
    """Validate against e-commerce specific sites"""
    
    validator = RealWorldValidator()
    return await validator.run_comprehensive_validation(TargetType.ECOMMERCE, max_targets=2)


async def validate_api_endpoints() -> Dict[str, Any]:
    """Validate against API endpoints"""
    
    validator = RealWorldValidator()
    return await validator.run_comprehensive_validation(TargetType.API_ENDPOINT, max_targets=2)