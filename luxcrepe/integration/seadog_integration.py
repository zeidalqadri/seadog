"""
SEADOG-Luxcrepe Integration Module
Connects the SEADOG military testing framework with the Luxcrepe scraper
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass

from ..core.scraper import LuxcrepeScraper
from ..tests.base_agent import BaseAgent, MissionStatus, ThreatLevel, ReportPriority
from ..tests.scenarios import SEADOGTestRunner, TestConfiguration, TestSuite
from ..tests.scenarios import create_reconnaissance_test_config, create_full_spectrum_test_config
from ..intelligence import SEADOGIntelligenceSystem


@dataclass
class IntegrationConfig:
    """Configuration for SEADOG-Luxcrepe integration"""
    scraper_config_path: Optional[str] = None
    intelligence_enabled: bool = True
    real_time_monitoring: bool = True
    auto_recovery: bool = True
    test_suite_type: str = "RECONNAISSANCE"
    output_directory: str = "./seadog_test_results"
    parallel_execution: bool = True
    timeout_minutes: int = 30


class LuxcrepeSEADOGIntegration:
    """Integration layer between Luxcrepe scraper and SEADOG testing framework"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.logger = logging.getLogger("Luxcrepe.SEADOG.Integration")
        
        # Initialize components
        self.scraper = LuxcrepeScraper(config.scraper_config_path)
        self.intelligence_system: Optional[SEADOGIntelligenceSystem] = None
        self.test_runner: Optional[SEADOGTestRunner] = None
        
        # Integration state
        self.is_active = False
        self.integration_id = f"LUXCREPE_SEADOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_missions: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_execution_time": 0.0
        }
        
        # Initialize intelligence system if enabled
        if config.intelligence_enabled:
            self.intelligence_system = SEADOGIntelligenceSystem(f"{self.integration_id}_INTELLIGENCE")
        
        self.logger.info(f"SEADOG-Luxcrepe integration initialized: {self.integration_id}")
    
    async def start_integration(self):
        """Start the SEADOG-Luxcrepe integration"""
        
        if self.is_active:
            self.logger.warning("Integration already active")
            return
        
        self.is_active = True
        
        # Start intelligence system
        if self.intelligence_system:
            await self.intelligence_system.start_system()
        
        self.logger.info("SEADOG-Luxcrepe integration started")
    
    async def stop_integration(self):
        """Stop the SEADOG-Luxcrepe integration"""
        
        if not self.is_active:
            self.logger.warning("Integration not active")
            return
        
        self.is_active = False
        
        # Stop intelligence system
        if self.intelligence_system:
            await self.intelligence_system.stop_system()
        
        self.logger.info("SEADOG-Luxcrepe integration stopped")
    
    async def execute_mission_test(self, target_urls: List[str], 
                                 mission_type: str = "RECONNAISSANCE") -> Dict[str, Any]:
        """Execute a SEADOG mission test against target URLs"""
        
        mission_id = f"MISSION_{int(time.time())}"
        self.logger.info(f"Executing SEADOG mission test: {mission_id}")
        
        # Create test configuration
        if mission_type.upper() == "FULL_SPECTRUM":
            test_config = create_full_spectrum_test_config(target_urls, self.config.output_directory)
        else:
            test_config = create_reconnaissance_test_config(target_urls, self.config.output_directory)
        
        # Override configuration settings
        test_config.parallel_execution = self.config.parallel_execution
        test_config.execution_timeout = self.config.timeout_minutes
        
        # Create and run test
        self.test_runner = SEADOGTestRunner(test_config)
        
        # Track mission
        mission_data = {
            "mission_id": mission_id,
            "target_urls": target_urls,
            "mission_type": mission_type,
            "start_time": datetime.now(),
            "status": "EXECUTING"
        }
        self.active_missions[mission_id] = mission_data
        
        try:
            # Execute test suite
            test_results = await self.test_runner.run_test_suite()
            
            # Update mission status
            mission_data["status"] = "COMPLETED"
            mission_data["end_time"] = datetime.now()
            mission_data["results"] = test_results
            
            # Record intelligence metrics if enabled
            if self.intelligence_system:
                await self._record_mission_intelligence(mission_id, test_results)
            
            self.logger.info(f"SEADOG mission test completed: {mission_id}")
            return test_results
            
        except Exception as e:
            mission_data["status"] = "FAILED"
            mission_data["error"] = str(e)
            mission_data["end_time"] = datetime.now()
            
            self.logger.error(f"SEADOG mission test failed: {mission_id} - {str(e)}")
            raise
    
    async def integrated_scrape_with_testing(self, url: str, 
                                           enable_testing: bool = True,
                                           test_intensity: str = "MODERATE") -> Dict[str, Any]:
        """Perform integrated scraping with SEADOG testing"""
        
        scrape_id = f"SCRAPE_{int(time.time())}"
        self.logger.info(f"Starting integrated scrape with testing: {scrape_id}")
        
        start_time = time.time()
        results = {
            "scrape_id": scrape_id,
            "url": url,
            "scraping_results": None,
            "testing_results": None,
            "performance_metrics": {},
            "recommendations": []
        }
        
        try:
            # Phase 1: Pre-scraping reconnaissance (if testing enabled)
            if enable_testing and test_intensity in ["MODERATE", "AGGRESSIVE"]:
                self.logger.info("Phase 1: Pre-scraping reconnaissance")
                recon_results = await self.execute_mission_test([url], "RECONNAISSANCE")
                results["testing_results"] = {"reconnaissance": recon_results}
                
                # Analyze reconnaissance for scraping optimization
                scraping_recommendations = self._analyze_reconnaissance_for_scraping(recon_results)
                results["recommendations"].extend(scraping_recommendations)
            
            # Phase 2: Execute scraping with monitoring
            self.logger.info("Phase 2: Executing scraping operation")
            scraping_start = time.time()
            
            # Record pre-scraping metrics
            if self.intelligence_system:
                self.intelligence_system.record_agent_metric(
                    agent_id="LUXCREPE_SCRAPER",
                    metric_type="scraping_start",
                    value=1,
                    tags=["scraping", "start"],
                    metadata={"url": url, "scrape_id": scrape_id}
                )
            
            # Perform scraping (listing or single page based on URL analysis)
            if self._is_listing_url(url):
                scraping_results = self.scraper.scrape_listing(url)
            else:
                scraping_results = [self.scraper.scrape_product(url)]
            
            scraping_time = time.time() - scraping_start
            results["scraping_results"] = scraping_results
            
            # Record post-scraping metrics
            if self.intelligence_system:
                self.intelligence_system.record_agent_metric(
                    agent_id="LUXCREPE_SCRAPER",
                    metric_type="scraping_completed",
                    value=len(scraping_results),
                    tags=["scraping", "completed"],
                    metadata={
                        "url": url, 
                        "scrape_id": scrape_id,
                        "products_count": len(scraping_results),
                        "execution_time": scraping_time
                    }
                )
                
                self.intelligence_system.record_agent_metric(
                    agent_id="LUXCREPE_SCRAPER",
                    metric_type="response_time",
                    value=scraping_time,
                    tags=["performance", "response_time"],
                    metadata={"url": url, "success": len(scraping_results) > 0}
                )
            
            # Phase 3: Post-scraping validation (if testing enabled)
            if enable_testing and test_intensity == "AGGRESSIVE":
                self.logger.info("Phase 3: Post-scraping validation")
                validation_results = await self._validate_scraping_results(url, scraping_results)
                if "testing_results" not in results:
                    results["testing_results"] = {}
                results["testing_results"]["validation"] = validation_results
            
            # Calculate performance metrics
            total_time = time.time() - start_time
            results["performance_metrics"] = {
                "total_execution_time": total_time,
                "scraping_time": scraping_time,
                "products_extracted": len(scraping_results),
                "extraction_rate": len(scraping_results) / scraping_time if scraping_time > 0 else 0,
                "success": len(scraping_results) > 0
            }
            
            # Update global performance metrics
            self._update_performance_metrics(total_time, len(scraping_results) > 0)
            
            self.logger.info(f"Integrated scrape completed: {scrape_id} - {len(scraping_results)} products")
            return results
            
        except Exception as e:
            # Record error metrics
            if self.intelligence_system:
                self.intelligence_system.record_agent_metric(
                    agent_id="LUXCREPE_SCRAPER",
                    metric_type="error",
                    value=1,
                    tags=["error", "scraping_failed"],
                    metadata={"url": url, "error": str(e), "scrape_id": scrape_id}
                )
            
            total_time = time.time() - start_time
            self._update_performance_metrics(total_time, False)
            
            results["error"] = str(e)
            results["performance_metrics"] = {
                "total_execution_time": total_time,
                "success": False
            }
            
            self.logger.error(f"Integrated scrape failed: {scrape_id} - {str(e)}")
            return results
    
    async def run_comprehensive_test_suite(self, target_urls: List[str]) -> Dict[str, Any]:
        """Run comprehensive SEADOG test suite against target URLs"""
        
        self.logger.info(f"Running comprehensive test suite against {len(target_urls)} URLs")
        
        comprehensive_results = {
            "test_suite_id": f"COMPREHENSIVE_{int(time.time())}",
            "target_urls": target_urls,
            "test_phases": {},
            "overall_metrics": {},
            "recommendations": []
        }
        
        # Phase 1: Reconnaissance
        self.logger.info("Phase 1: Reconnaissance testing")
        recon_results = await self.execute_mission_test(target_urls, "RECONNAISSANCE")
        comprehensive_results["test_phases"]["reconnaissance"] = recon_results
        
        # Phase 2: Full spectrum testing
        self.logger.info("Phase 2: Full spectrum testing")
        full_spectrum_results = await self.execute_mission_test(target_urls, "FULL_SPECTRUM")
        comprehensive_results["test_phases"]["full_spectrum"] = full_spectrum_results
        
        # Phase 3: Integrated scraping validation
        self.logger.info("Phase 3: Integrated scraping validation")
        scraping_validation = {}
        
        for url in target_urls[:3]:  # Test first 3 URLs to avoid overload
            try:
                scrape_result = await self.integrated_scrape_with_testing(url, True, "AGGRESSIVE")
                scraping_validation[url] = scrape_result
            except Exception as e:
                scraping_validation[url] = {"error": str(e)}
        
        comprehensive_results["test_phases"]["scraping_validation"] = scraping_validation
        
        # Generate overall metrics and recommendations
        overall_metrics = self._calculate_comprehensive_metrics(comprehensive_results)
        comprehensive_results["overall_metrics"] = overall_metrics
        
        recommendations = self._generate_comprehensive_recommendations(comprehensive_results)
        comprehensive_results["recommendations"] = recommendations
        
        self.logger.info("Comprehensive test suite completed")
        return comprehensive_results
    
    async def _record_mission_intelligence(self, mission_id: str, test_results: Dict[str, Any]):
        """Record mission intelligence data"""
        
        if not self.intelligence_system:
            return
        
        # Record mission completion
        self.intelligence_system.record_agent_metric(
            agent_id="SEADOG_MISSION_ORCHESTRATOR",
            metric_type="mission_completed",
            value=1,
            tags=["mission", "completed"],
            metadata={"mission_id": mission_id, "results": test_results}
        )
        
        # Record test metrics
        overall_metrics = test_results.get("overall_metrics", {})
        
        if "success_rate" in overall_metrics:
            self.intelligence_system.record_agent_metric(
                agent_id="SEADOG_TEST_RUNNER",
                metric_type="success_rate",
                value=overall_metrics["success_rate"],
                tags=["testing", "success_rate"],
                metadata={"mission_id": mission_id}
            )
        
        if "average_scenario_time" in overall_metrics:
            self.intelligence_system.record_agent_metric(
                agent_id="SEADOG_TEST_RUNNER",
                metric_type="response_time",
                value=overall_metrics["average_scenario_time"],
                tags=["testing", "performance"],
                metadata={"mission_id": mission_id}
            )
    
    def _analyze_reconnaissance_for_scraping(self, recon_results: Dict[str, Any]) -> List[str]:
        """Analyze reconnaissance results to provide scraping recommendations"""
        
        recommendations = []
        
        # Analyze test status
        test_status = recon_results.get("summary", {}).get("test_status", "UNKNOWN")
        if test_status == "FAILED":
            recommendations.append("CAUTION: Reconnaissance testing indicated potential issues")
        
        # Analyze success rate
        overall_metrics = recon_results.get("overall_metrics", {})
        success_rate = overall_metrics.get("success_rate", 0.0)
        
        if success_rate < 0.8:
            recommendations.append("REDUCE_SCRAPING_INTENSITY: Low reconnaissance success rate")
        elif success_rate > 0.95:
            recommendations.append("INCREASE_SCRAPING_RATE: High reconnaissance success rate")
        
        # Analyze performance
        avg_time = overall_metrics.get("average_scenario_time", 0.0)
        if avg_time > 10.0:
            recommendations.append("IMPLEMENT_DELAYS: Slow response times detected")
        
        return recommendations
    
    async def _validate_scraping_results(self, url: str, scraping_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate scraping results using SEADOG testing"""
        
        validation_results = {
            "validation_type": "POST_SCRAPING_VALIDATION",
            "url": url,
            "products_validated": len(scraping_results),
            "validation_metrics": {},
            "issues_found": [],
            "recommendations": []
        }
        
        # Basic validation metrics
        if scraping_results:
            # Check data completeness
            complete_products = sum(1 for p in scraping_results if self._is_product_complete(p))
            completeness_rate = complete_products / len(scraping_results)
            
            validation_results["validation_metrics"]["completeness_rate"] = completeness_rate
            validation_results["validation_metrics"]["complete_products"] = complete_products
            validation_results["validation_metrics"]["total_products"] = len(scraping_results)
            
            if completeness_rate < 0.8:
                validation_results["issues_found"].append("LOW_DATA_COMPLETENESS")
                validation_results["recommendations"].append("IMPROVE_EXTRACTION_RULES")
            
            # Check for duplicate products
            unique_products = len(set(p.get('name', '') for p in scraping_results if p.get('name')))
            if unique_products < len(scraping_results):
                validation_results["issues_found"].append("DUPLICATE_PRODUCTS_DETECTED")
                validation_results["recommendations"].append("IMPLEMENT_DEDUPLICATION")
        
        else:
            validation_results["issues_found"].append("NO_PRODUCTS_EXTRACTED")
            validation_results["recommendations"].append("REVIEW_EXTRACTION_LOGIC")
        
        return validation_results
    
    def _is_listing_url(self, url: str) -> bool:
        """Determine if URL is a listing/collection page"""
        
        listing_indicators = [
            'collection', 'category', 'products', 'catalog', 
            'search', 'browse', 'shop', 'list'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in listing_indicators)
    
    def _is_product_complete(self, product: Dict[str, Any]) -> bool:
        """Check if a product has complete data"""
        
        required_fields = ['name', 'price']
        return all(product.get(field) for field in required_fields)
    
    def _update_performance_metrics(self, execution_time: float, success: bool):
        """Update global performance metrics"""
        
        self.performance_metrics["total_requests"] += 1
        self.performance_metrics["total_execution_time"] += execution_time
        
        if success:
            self.performance_metrics["successful_requests"] += 1
        else:
            self.performance_metrics["failed_requests"] += 1
        
        # Calculate average response time
        if self.performance_metrics["total_requests"] > 0:
            self.performance_metrics["average_response_time"] = (
                self.performance_metrics["total_execution_time"] / 
                self.performance_metrics["total_requests"]
            )
    
    def _calculate_comprehensive_metrics(self, comprehensive_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall metrics from comprehensive test results"""
        
        metrics = {
            "overall_success_rate": 0.0,
            "average_execution_time": 0.0,
            "total_tests_executed": 0,
            "scraping_success_rate": 0.0,
            "data_quality_score": 0.0
        }
        
        # Analyze test phases
        test_phases = comprehensive_results.get("test_phases", {})
        
        # Reconnaissance metrics
        recon_results = test_phases.get("reconnaissance", {})
        recon_metrics = recon_results.get("overall_metrics", {})
        
        # Full spectrum metrics  
        full_spectrum_results = test_phases.get("full_spectrum", {})
        full_spectrum_metrics = full_spectrum_results.get("overall_metrics", {})
        
        # Calculate weighted averages
        success_rates = []
        if "success_rate" in recon_metrics:
            success_rates.append(recon_metrics["success_rate"])
        if "success_rate" in full_spectrum_metrics:
            success_rates.append(full_spectrum_metrics["success_rate"])
        
        if success_rates:
            metrics["overall_success_rate"] = sum(success_rates) / len(success_rates)
        
        # Scraping validation metrics
        scraping_validation = test_phases.get("scraping_validation", {})
        successful_scrapes = sum(1 for result in scraping_validation.values() 
                               if result.get("performance_metrics", {}).get("success", False))
        total_scrapes = len(scraping_validation)
        
        if total_scrapes > 0:
            metrics["scraping_success_rate"] = successful_scrapes / total_scrapes
        
        return metrics
    
    def _generate_comprehensive_recommendations(self, comprehensive_results: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations"""
        
        recommendations = []
        overall_metrics = comprehensive_results.get("overall_metrics", {})
        
        # Success rate recommendations
        overall_success_rate = overall_metrics.get("overall_success_rate", 0.0)
        if overall_success_rate < 0.8:
            recommendations.append("IMPROVE_OVERALL_SYSTEM_RELIABILITY")
        
        scraping_success_rate = overall_metrics.get("scraping_success_rate", 0.0)
        if scraping_success_rate < 0.9:
            recommendations.append("OPTIMIZE_SCRAPING_CONFIGURATION")
        
        # Performance recommendations
        if overall_metrics.get("average_execution_time", 0) > 30:
            recommendations.append("OPTIMIZE_EXECUTION_PERFORMANCE")
        
        # Add phase-specific recommendations
        test_phases = comprehensive_results.get("test_phases", {})
        for phase_name, phase_results in test_phases.items():
            phase_recommendations = phase_results.get("recommendations", [])
            recommendations.extend([f"{phase_name.upper()}: {rec}" for rec in phase_recommendations[:2]])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        
        status = {
            "integration_id": self.integration_id,
            "is_active": self.is_active,
            "intelligence_system_active": self.intelligence_system.is_active if self.intelligence_system else False,
            "active_missions": len(self.active_missions),
            "performance_metrics": self.performance_metrics,
            "configuration": {
                "intelligence_enabled": self.config.intelligence_enabled,
                "real_time_monitoring": self.config.real_time_monitoring,
                "auto_recovery": self.config.auto_recovery,
                "test_suite_type": self.config.test_suite_type,
                "parallel_execution": self.config.parallel_execution,
                "timeout_minutes": self.config.timeout_minutes
            }
        }
        
        # Add intelligence system status if available
        if self.intelligence_system:
            status["intelligence_status"] = self.intelligence_system.get_system_status()
        
        return status
    
    async def export_integration_data(self, format: str = "json") -> str:
        """Export integration data and results"""
        
        export_data = {
            "integration_status": self.get_integration_status(),
            "active_missions": self.active_missions,
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Add intelligence data if available
        if self.intelligence_system:
            export_data["intelligence_data"] = self.intelligence_system.export_intelligence_data("dict")
        
        if format.lower() == "json":
            import json
            return json.dumps(export_data, indent=2, default=str)
        
        return "Unsupported format"


# Convenience functions for quick integration
async def quick_reconnaissance_test(target_urls: List[str], 
                                  output_dir: str = "./seadog_results") -> Dict[str, Any]:
    """Quick reconnaissance test using SEADOG"""
    
    config = IntegrationConfig(
        test_suite_type="RECONNAISSANCE",
        output_directory=output_dir,
        parallel_execution=True,
        timeout_minutes=15
    )
    
    integration = LuxcrepeSEADOGIntegration(config)
    await integration.start_integration()
    
    try:
        results = await integration.execute_mission_test(target_urls, "RECONNAISSANCE")
        return results
    finally:
        await integration.stop_integration()


async def integrated_scrape_test(url: str, 
                               test_intensity: str = "MODERATE") -> Dict[str, Any]:
    """Integrated scraping with SEADOG testing"""
    
    config = IntegrationConfig(
        intelligence_enabled=True,
        real_time_monitoring=True,
        test_suite_type="RECONNAISSANCE"
    )
    
    integration = LuxcrepeSEADOGIntegration(config)
    await integration.start_integration()
    
    try:
        results = await integration.integrated_scrape_with_testing(url, True, test_intensity)
        return results
    finally:
        await integration.stop_integration()