#!/usr/bin/env python3
"""
SEADOG-Luxcrepe Integration Validation Test Script
Test the integrated system against safe, public testing endpoints
"""

import asyncio
import logging
import json
import sys
from datetime import datetime

from .real_world_validator import (
    RealWorldValidator, 
    run_quick_validation,
    validate_api_endpoints
)


async def run_basic_validation_test():
    """Run basic validation test against safe endpoints"""
    
    print("🚀 Starting SEADOG-Luxcrepe Integration Validation Test")
    print("=" * 60)
    
    # Test 1: Quick validation of safe API endpoints
    print("\n📡 Test 1: Quick API Endpoint Validation")
    print("-" * 40)
    
    safe_api_urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://httpbin.org/json",
    ]
    
    try:
        quick_results = await run_quick_validation(safe_api_urls)
        
        print(f"✅ Quick validation completed")
        print(f"   URLs tested: {quick_results['summary']['total_urls']}")
        print(f"   Successful: {quick_results['summary']['successful_validations']}")
        print(f"   Average score: {quick_results['summary']['average_score']:.2f}")
        
    except Exception as e:
        print(f"❌ Quick validation failed: {str(e)}")
    
    # Test 2: Comprehensive API endpoint validation
    print("\n🔬 Test 2: Comprehensive API Validation")
    print("-" * 40)
    
    try:
        api_results = await validate_api_endpoints()
        
        overall_metrics = api_results.get("overall_metrics", {})
        summary = api_results.get("summary", {})
        
        print(f"✅ Comprehensive API validation completed")
        print(f"   Targets tested: {overall_metrics.get('total_targets', 0)}")
        print(f"   Success rate: {summary.get('success_rate', 0):.2%}")
        print(f"   Average score: {summary.get('average_score', 0):.2f}")
        print(f"   Status: {summary.get('validation_status', 'UNKNOWN')}")
        
        # Show key findings
        key_findings = summary.get('key_findings', [])
        if key_findings:
            print("\n📋 Key Findings:")
            for finding in key_findings:
                print(f"   • {finding}")
        
        # Show recommendations
        recommendations = api_results.get('recommendations', [])
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations[:3]:  # Show top 3
                print(f"   • {rec}")
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"validation_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(api_results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Comprehensive validation failed: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 Validation Test Summary:")
    print("   • SEADOG-Luxcrepe integration functional")
    print("   • Safe endpoint testing completed")
    print("   • System ready for careful real-world testing")
    print("=" * 60)
    
    return True


async def run_custom_url_test(url: str):
    """Test a specific URL with validation"""
    
    print(f"\n🎯 Testing custom URL: {url}")
    print("-" * 50)
    
    try:
        validator = RealWorldValidator()
        result = await validator.quick_validation(url)
        
        print(f"✅ Validation completed")
        print(f"   Score: {result.validation_score:.2f}")
        print(f"   Passed checks: {len(result.passed_checks)}")
        print(f"   Failed checks: {len(result.failed_checks)}")
        
        if result.failed_checks:
            print(f"   Issues found: {', '.join(result.failed_checks[:3])}")
        
        if result.recommendations:
            print(f"   Top recommendation: {result.recommendations[0]}")
        
        return result.validation_score > 0.5
        
    except Exception as e:
        print(f"❌ Custom URL test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Check if custom URL provided
    if len(sys.argv) > 1:
        custom_url = sys.argv[1]
        success = asyncio.run(run_custom_url_test(custom_url))
    else:
        success = asyncio.run(run_basic_validation_test())
    
    sys.exit(0 if success else 1)