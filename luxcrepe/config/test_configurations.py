"""
SEADOG Test Configurations for Different Scenarios
Pre-configured testing scenarios for various use cases and target types
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from ..integration.seadog_integration import IntegrationConfig
from ..tests.scenarios import TestSuite


class TargetType(Enum):
    """Types of target websites"""
    ECOMMERCE = "ECOMMERCE"
    NEWS_MEDIA = "NEWS_MEDIA"
    BLOG = "BLOG"
    CORPORATE = "CORPORATE"
    API_ENDPOINT = "API_ENDPOINT"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    MARKETPLACE = "MARKETPLACE"
    UNKNOWN = "UNKNOWN"


class TestIntensity(Enum):
    """Test intensity levels"""
    LIGHT = "LIGHT"           # Basic reconnaissance only
    MODERATE = "MODERATE"     # Reconnaissance + basic testing
    AGGRESSIVE = "AGGRESSIVE" # Full spectrum testing
    STEALTH = "STEALTH"       # Maximum stealth, minimal detection


@dataclass
class ScenarioConfig:
    """Configuration for a specific test scenario"""
    scenario_name: str
    scenario_description: str
    target_type: TargetType
    test_intensity: TestIntensity
    integration_config: IntegrationConfig
    test_parameters: Dict[str, Any]
    expected_outcomes: Dict[str, Any]
    risk_assessment: str
    recommended_usage: List[str]


class SEADOGTestConfigurations:
    """Pre-configured SEADOG test scenarios for different use cases"""
    
    def __init__(self):
        self.configurations = {}
        self._initialize_default_configurations()
    
    def _initialize_default_configurations(self):
        """Initialize default test configurations"""
        
        # E-commerce reconnaissance configuration
        self.configurations["ecommerce_recon"] = ScenarioConfig(
            scenario_name="E-commerce Reconnaissance",
            scenario_description="Comprehensive reconnaissance for e-commerce websites",
            target_type=TargetType.ECOMMERCE,
            test_intensity=TestIntensity.MODERATE,
            integration_config=IntegrationConfig(
                intelligence_enabled=True,
                real_time_monitoring=True,
                auto_recovery=True,
                test_suite_type="RECONNAISSANCE",
                parallel_execution=True,
                timeout_minutes=20
            ),
            test_parameters={
                "reconnaissance": {
                    "depth": "COMPREHENSIVE",
                    "opsec_level": "COVERT",
                    "intelligence_requirements": [
                        "PRODUCT_STRUCTURE_ANALYSIS",
                        "PAGINATION_DETECTION",
                        "RATE_LIMITING_ASSESSMENT",
                        "SECURITY_HEADERS_ANALYSIS"
                    ]
                },
                "target_analysis": {
                    "product_page_detection": True,
                    "category_page_detection": True,
                    "search_functionality": True,
                    "api_endpoint_discovery": True
                }
            },
            expected_outcomes={
                "min_success_rate": 0.85,
                "max_avg_response_time": 8.0,
                "intelligence_confidence": 0.8,
                "stealth_score": 0.9
            },
            risk_assessment="LOW",
            recommended_usage=[
                "Initial e-commerce site analysis",
                "Product extraction planning",
                "Rate limiting assessment",
                "Security posture evaluation"
            ]
        )
        
        # High-intensity full spectrum testing
        self.configurations["full_spectrum_aggressive"] = ScenarioConfig(
            scenario_name="Full Spectrum Aggressive Testing",
            scenario_description="Complete testing suite with maximum coverage",
            target_type=TargetType.UNKNOWN,
            test_intensity=TestIntensity.AGGRESSIVE,
            integration_config=IntegrationConfig(
                intelligence_enabled=True,
                real_time_monitoring=True,
                auto_recovery=True,
                test_suite_type="FULL_SPECTRUM",
                parallel_execution=False,  # Sequential for thorough testing
                timeout_minutes=60
            ),
            test_parameters={
                "reconnaissance": {
                    "depth": "DEEP_ANALYSIS",
                    "opsec_level": "ACTIVE",
                    "intelligence_requirements": [
                        "COMPREHENSIVE_INFRASTRUCTURE_MAPPING",
                        "VULNERABILITY_ASSESSMENT",
                        "TECHNOLOGY_FINGERPRINTING",
                        "BEHAVIORAL_ANALYSIS"
                    ]
                },
                "penetration_testing": {
                    "intensity": "HIGH",
                    "scope": "COMPREHENSIVE",
                    "test_vectors": [
                        "RATE_LIMITING_BYPASS",
                        "HEADER_MANIPULATION",
                        "SESSION_HANDLING",
                        "CONTENT_EXTRACTION"
                    ]
                },
                "stress_testing": {
                    "load_level": "HIGH",
                    "duration": 300,  # 5 minutes
                    "concurrent_requests": 10,
                    "escalation_pattern": "GRADUAL"
                }
            },
            expected_outcomes={
                "min_success_rate": 0.75,
                "max_avg_response_time": 15.0,
                "comprehensive_coverage": 0.95,
                "vulnerability_detection": 0.9
            },
            risk_assessment="HIGH",
            recommended_usage=[
                "Comprehensive system validation",
                "Security assessment",
                "Performance boundary testing",
                "Pre-deployment validation"
            ]
        )
        
        # Stealth reconnaissance for sensitive targets
        self.configurations["stealth_recon"] = ScenarioConfig(
            scenario_name="Stealth Reconnaissance",
            scenario_description="Maximum stealth reconnaissance with minimal detection risk",
            target_type=TargetType.UNKNOWN,
            test_intensity=TestIntensity.STEALTH,
            integration_config=IntegrationConfig(
                intelligence_enabled=True,
                real_time_monitoring=True,
                auto_recovery=True,
                test_suite_type="RECONNAISSANCE",
                parallel_execution=False,  # Sequential for stealth
                timeout_minutes=30
            ),
            test_parameters={
                "reconnaissance": {
                    "depth": "CAREFUL_ANALYSIS",
                    "opsec_level": "GHOST_MODE",
                    "stealth_techniques": [
                        "RANDOMIZED_USER_AGENTS",
                        "VARIABLE_REQUEST_TIMING",
                        "PROXY_ROTATION",
                        "MINIMAL_FOOTPRINT"
                    ],
                    "intelligence_requirements": [
                        "PASSIVE_RECONNAISSANCE",
                        "BEHAVIORAL_PATTERN_ANALYSIS",
                        "MINIMAL_INTERACTION_INTEL"
                    ]
                },
                "operational_security": {
                    "detection_avoidance": "MAXIMUM",
                    "request_spacing": "WIDE",
                    "session_management": "ISOLATED",
                    "error_handling": "SILENT"
                }
            },
            expected_outcomes={
                "min_success_rate": 0.9,
                "max_avg_response_time": 5.0,
                "stealth_score": 0.95,
                "detection_probability": 0.05
            },
            risk_assessment="MINIMAL",
            recommended_usage=[
                "Sensitive target analysis",
                "Preliminary reconnaissance",
                "Low-profile intelligence gathering",
                "Risk assessment operations"
            ]
        )
        
        # API endpoint testing
        self.configurations["api_testing"] = ScenarioConfig(
            scenario_name="API Endpoint Testing",
            scenario_description="Specialized testing for API endpoints and services",
            target_type=TargetType.API_ENDPOINT,
            test_intensity=TestIntensity.MODERATE,
            integration_config=IntegrationConfig(
                intelligence_enabled=True,
                real_time_monitoring=True,
                auto_recovery=True,
                test_suite_type="RECONNAISSANCE",
                parallel_execution=True,
                timeout_minutes=15
            ),
            test_parameters={
                "api_analysis": {
                    "endpoint_discovery": True,
                    "authentication_analysis": True,
                    "rate_limiting_detection": True,
                    "response_format_analysis": True,
                    "error_handling_assessment": True
                },
                "reconnaissance": {
                    "depth": "API_FOCUSED",
                    "opsec_level": "CAREFUL",
                    "intelligence_requirements": [
                        "API_STRUCTURE_MAPPING",
                        "AUTHENTICATION_REQUIREMENTS",
                        "RATE_LIMITING_RULES",
                        "DATA_FORMAT_ANALYSIS"
                    ]
                }
            },
            expected_outcomes={
                "min_success_rate": 0.9,
                "max_avg_response_time": 3.0,
                "api_coverage": 0.8,
                "structure_accuracy": 0.9
            },
            risk_assessment="LOW",
            recommended_usage=[
                "API endpoint validation",
                "Rate limiting assessment",
                "Authentication analysis",
                "Data format verification"
            ]
        )
        
        # News/Media site testing
        self.configurations["news_media_testing"] = ScenarioConfig(
            scenario_name="News Media Testing",
            scenario_description="Optimized testing for news and media websites",
            target_type=TargetType.NEWS_MEDIA,
            test_intensity=TestIntensity.LIGHT,
            integration_config=IntegrationConfig(
                intelligence_enabled=True,
                real_time_monitoring=True,
                auto_recovery=True,
                test_suite_type="RECONNAISSANCE",
                parallel_execution=True,
                timeout_minutes=10
            ),
            test_parameters={
                "content_analysis": {
                    "article_structure_detection": True,
                    "headline_extraction": True,
                    "author_information": True,
                    "publication_date": True,
                    "content_categorization": True
                },
                "reconnaissance": {
                    "depth": "CONTENT_FOCUSED",
                    "opsec_level": "RESPECTFUL",
                    "intelligence_requirements": [
                        "CONTENT_STRUCTURE_ANALYSIS",
                        "PUBLICATION_PATTERNS",
                        "PAGINATION_ASSESSMENT",
                        "MULTIMEDIA_DETECTION"
                    ]
                }
            },
            expected_outcomes={
                "min_success_rate": 0.9,
                "max_avg_response_time": 4.0,
                "content_extraction_accuracy": 0.85,
                "structure_recognition": 0.9
            },
            risk_assessment="MINIMAL",
            recommended_usage=[
                "News article extraction",
                "Content structure analysis",
                "Publication pattern assessment",
                "Media site reconnaissance"
            ]
        )
        
        # Marketplace testing
        self.configurations["marketplace_testing"] = ScenarioConfig(
            scenario_name="Marketplace Testing",
            scenario_description="Comprehensive testing for marketplace platforms",
            target_type=TargetType.MARKETPLACE,
            test_intensity=TestIntensity.MODERATE,
            integration_config=IntegrationConfig(
                intelligence_enabled=True,
                real_time_monitoring=True,
                auto_recovery=True,
                test_suite_type="RECONNAISSANCE",
                parallel_execution=True,
                timeout_minutes=25
            ),
            test_parameters={
                "marketplace_analysis": {
                    "vendor_detection": True,
                    "product_categorization": True,
                    "pricing_structure": True,
                    "review_system_analysis": True,
                    "search_functionality": True
                },
                "reconnaissance": {
                    "depth": "MARKETPLACE_COMPREHENSIVE",
                    "opsec_level": "CAREFUL",
                    "intelligence_requirements": [
                        "VENDOR_ECOSYSTEM_MAPPING",
                        "PRODUCT_TAXONOMY_ANALYSIS",
                        "PRICING_PATTERN_DETECTION",
                        "REVIEW_SYSTEM_ASSESSMENT"
                    ]
                }
            },
            expected_outcomes={
                "min_success_rate": 0.8,
                "max_avg_response_time": 10.0,
                "vendor_detection_rate": 0.9,
                "product_categorization_accuracy": 0.85
            },
            risk_assessment="MODERATE",
            recommended_usage=[
                "Marketplace analysis",
                "Vendor ecosystem mapping",
                "Product comparison research",
                "Competitive intelligence"
            ]
        )
    
    def get_configuration(self, config_name: str) -> Optional[ScenarioConfig]:
        """Get a specific test configuration"""
        return self.configurations.get(config_name)
    
    def get_configurations_by_target_type(self, target_type: TargetType) -> List[ScenarioConfig]:
        """Get configurations suitable for a specific target type"""
        return [
            config for config in self.configurations.values()
            if config.target_type == target_type or config.target_type == TargetType.UNKNOWN
        ]
    
    def get_configurations_by_intensity(self, intensity: TestIntensity) -> List[ScenarioConfig]:
        """Get configurations by test intensity"""
        return [
            config for config in self.configurations.values()
            if config.test_intensity == intensity
        ]
    
    def list_configurations(self) -> Dict[str, str]:
        """List all available configurations with descriptions"""
        return {
            name: config.scenario_description
            for name, config in self.configurations.items()
        }
    
    def recommend_configuration(self, target_url: str, 
                              target_type: Optional[TargetType] = None,
                              risk_tolerance: str = "MODERATE") -> List[str]:
        """Recommend configurations based on target and risk tolerance"""
        
        # Auto-detect target type if not provided
        if target_type is None:
            target_type = self._detect_target_type(target_url)
        
        # Get suitable configurations
        suitable_configs = self.get_configurations_by_target_type(target_type)
        
        # Filter by risk tolerance
        risk_filtered = []
        for config in suitable_configs:
            if risk_tolerance.upper() == "LOW" and config.risk_assessment in ["MINIMAL", "LOW"]:
                risk_filtered.append(config)
            elif risk_tolerance.upper() == "MODERATE" and config.risk_assessment in ["MINIMAL", "LOW", "MODERATE"]:
                risk_filtered.append(config)
            elif risk_tolerance.upper() == "HIGH":
                risk_filtered.append(config)
        
        # Return configuration names sorted by risk (lowest first)
        risk_order = {"MINIMAL": 0, "LOW": 1, "MODERATE": 2, "HIGH": 3}
        sorted_configs = sorted(risk_filtered, key=lambda c: risk_order.get(c.risk_assessment, 4))
        
        return [self._get_config_name(config) for config in sorted_configs]
    
    def _detect_target_type(self, url: str) -> TargetType:
        """Auto-detect target type from URL"""
        
        url_lower = url.lower()
        
        # E-commerce indicators
        ecommerce_indicators = ['shop', 'store', 'cart', 'product', 'buy', 'ecommerce', 'commerce']
        if any(indicator in url_lower for indicator in ecommerce_indicators):
            return TargetType.ECOMMERCE
        
        # API indicators
        api_indicators = ['api', 'rest', 'graphql', 'endpoint', 'service']
        if any(indicator in url_lower for indicator in api_indicators):
            return TargetType.API_ENDPOINT
        
        # News/Media indicators
        news_indicators = ['news', 'media', 'blog', 'article', 'press', 'journal']
        if any(indicator in url_lower for indicator in news_indicators):
            return TargetType.NEWS_MEDIA
        
        # Marketplace indicators
        marketplace_indicators = ['marketplace', 'market', 'vendor', 'seller', 'ebay', 'amazon', 'etsy']
        if any(indicator in url_lower for indicator in marketplace_indicators):
            return TargetType.MARKETPLACE
        
        return TargetType.UNKNOWN
    
    def _get_config_name(self, config: ScenarioConfig) -> str:
        """Get configuration name from config object"""
        for name, stored_config in self.configurations.items():
            if stored_config == config:
                return name
        return "unknown"
    
    def create_custom_configuration(self, name: str, config: ScenarioConfig):
        """Add a custom configuration"""
        self.configurations[name] = config
    
    def export_configuration(self, config_name: str, format: str = "json") -> str:
        """Export a configuration to file format"""
        
        config = self.get_configuration(config_name)
        if not config:
            return f"Configuration '{config_name}' not found"
        
        if format.lower() == "json":
            import json
            return json.dumps(asdict(config), indent=2, default=str)
        elif format.lower() == "yaml":
            try:
                import yaml
                return yaml.dump(asdict(config), default_flow_style=False)
            except ImportError:
                return "YAML export requires PyYAML package"
        
        return "Unsupported format"
    
    def save_configuration_file(self, config_name: str, filepath: str, format: str = "json"):
        """Save configuration to file"""
        
        content = self.export_configuration(config_name, format)
        
        if content.startswith("Configuration") or content.startswith("Unsupported"):
            raise ValueError(content)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(content)


# Configuration factory functions
def get_seadog_configurations() -> SEADOGTestConfigurations:
    """Get initialized SEADOG test configurations"""
    return SEADOGTestConfigurations()


def quick_config_for_ecommerce(stealth_level: str = "MODERATE") -> IntegrationConfig:
    """Quick configuration for e-commerce testing"""
    
    configs = get_seadog_configurations()
    
    if stealth_level.upper() == "HIGH":
        return configs.get_configuration("stealth_recon").integration_config
    else:
        return configs.get_configuration("ecommerce_recon").integration_config


def quick_config_for_api(timeout_minutes: int = 15) -> IntegrationConfig:
    """Quick configuration for API testing"""
    
    configs = get_seadog_configurations()
    config = configs.get_configuration("api_testing").integration_config
    config.timeout_minutes = timeout_minutes
    
    return config


def quick_config_for_news_media() -> IntegrationConfig:
    """Quick configuration for news/media testing"""
    
    configs = get_seadog_configurations()
    return configs.get_configuration("news_media_testing").integration_config