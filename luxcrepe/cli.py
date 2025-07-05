"""
Unified command-line interface for LuxCrepe with SEADOG Integration
"""

import argparse
import json
import sys
import logging
import asyncio
from pathlib import Path
from typing import List, Optional

from .core.scraper import LuxcrepeScraper
from .modes.interactive import InteractiveMode
from .modes.batch import BatchMode
from .modes.detail import DetailMode
from .core.config import load_config

# SEADOG Integration imports
from .integration import LuxcrepeSEADOGIntegration, IntegrationConfig
from .config import get_seadog_configurations, TargetType
from .validation import RealWorldValidator, validate_api_endpoints, validate_ecommerce_sites

logger = logging.getLogger(__name__)


def setup_cli_parser() -> argparse.ArgumentParser:
    """Setup command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="LuxCrepe: ML-Enhanced Universal E-commerce Product Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Core Scraping Examples:
  luxcrepe interactive                    # Interactive mode for manual URL input
  luxcrepe batch urls.txt                 # Batch process URLs from file
  luxcrepe detail https://example.com/product/123  # Scrape single product
  luxcrepe listing https://example.com/sale --pages 5  # Scrape listing with custom page limit
  luxcrepe --config custom_config.json batch urls.txt  # Use custom configuration

SEADOG Military Testing Examples:
  luxcrepe seadog recon https://demo-store.com --intensity MODERATE  # Reconnaissance operation
  luxcrepe seadog scrape https://api.example.com --intensity LIGHT   # Integrated scraping
  luxcrepe seadog validate --target-type ECOMMERCE --max-targets 2   # System validation
  luxcrepe seadog config list                                        # List configurations
  luxcrepe seadog config recommend https://shop.example.com          # Get recommendations
  luxcrepe seadog intel https://example.com --duration 60            # Intelligence gathering
        """
    )
    
    # Global options
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="luxcrepe_output.json",
        help="Output file path (default: luxcrepe_output.json)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except errors"
    )
    parser.add_argument(
        "--no-ml",
        action="store_true",
        help="Disable ML enhancement, use rule-based only"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="mode", help="Operation modes")
    
    # Interactive mode
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="Interactive mode for manual URL input"
    )
    interactive_parser.add_argument(
        "--max-urls",
        type=int,
        default=9,
        help="Maximum number of URLs to accept (default: 9)"
    )
    
    # Batch mode
    batch_parser = subparsers.add_parser(
        "batch",
        help="Batch process multiple URLs"
    )
    batch_parser.add_argument(
        "input",
        help="Input file with URLs (one per line) or comma-separated URLs"
    )
    batch_parser.add_argument(
        "--details",
        action="store_true",
        help="Scrape individual product detail pages"
    )
    batch_parser.add_argument(
        "--pages",
        type=int,
        help="Maximum pages per listing (overrides config)"
    )
    
    # Detail mode
    detail_parser = subparsers.add_parser(
        "detail",
        help="Scrape individual product detail pages"
    )
    detail_parser.add_argument(
        "urls",
        nargs="+",
        help="Product detail URLs to scrape"
    )
    
    # Listing mode
    listing_parser = subparsers.add_parser(
        "listing",
        help="Scrape product listing/collection pages"
    )
    listing_parser.add_argument(
        "urls",
        nargs="+",
        help="Listing/collection URLs to scrape"
    )
    listing_parser.add_argument(
        "--pages",
        type=int,
        help="Maximum pages per listing (overrides config)"
    )
    listing_parser.add_argument(
        "--details",
        action="store_true",
        help="Also scrape individual product detail pages"
    )
    
    # Stats mode
    stats_parser = subparsers.add_parser(
        "stats",
        help="Show scraper statistics and capabilities"
    )
    
    # SEADOG Test mode
    seadog_parser = subparsers.add_parser(
        "seadog",
        help="SEADOG military testing operations"
    )
    seadog_subparsers = seadog_parser.add_subparsers(dest="seadog_command", help="SEADOG operations")
    
    # SEADOG reconnaissance
    recon_parser = seadog_subparsers.add_parser(
        "recon",
        help="Conduct reconnaissance operations"
    )
    recon_parser.add_argument(
        "urls",
        nargs="+",
        help="Target URLs for reconnaissance"
    )
    recon_parser.add_argument(
        "--intensity",
        choices=["LIGHT", "MODERATE", "AGGRESSIVE"],
        default="MODERATE",
        help="Test intensity level (default: MODERATE)"
    )
    recon_parser.add_argument(
        "--parallel",
        action="store_true",
        help="Execute tests in parallel"
    )
    
    # SEADOG integrated scraping
    integrated_parser = seadog_subparsers.add_parser(
        "scrape",
        help="Integrated scraping with SEADOG testing"
    )
    integrated_parser.add_argument(
        "url",
        help="Target URL for integrated scraping"
    )
    integrated_parser.add_argument(
        "--intensity",
        choices=["LIGHT", "MODERATE", "AGGRESSIVE"],
        default="MODERATE",
        help="Test intensity level (default: MODERATE)"
    )
    integrated_parser.add_argument(
        "--no-testing",
        action="store_true",
        help="Disable SEADOG testing (scraping only)"
    )
    
    # SEADOG validation
    validate_parser = seadog_subparsers.add_parser(
        "validate",
        help="Validate system against real-world targets"
    )
    validate_parser.add_argument(
        "--target-type",
        choices=["ECOMMERCE", "API_ENDPOINT", "NEWS_MEDIA", "ALL"],
        default="ALL",
        help="Target type for validation (default: ALL)"
    )
    validate_parser.add_argument(
        "--max-targets",
        type=int,
        default=3,
        help="Maximum targets to test (default: 3)"
    )
    validate_parser.add_argument(
        "--export",
        type=str,
        help="Export validation results to file"
    )
    
    # SEADOG configuration
    config_parser = seadog_subparsers.add_parser(
        "config",
        help="SEADOG configuration management"
    )
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Configuration commands")
    
    # List configurations
    list_config_parser = config_subparsers.add_parser(
        "list",
        help="List available test configurations"
    )
    
    # Show configuration
    show_config_parser = config_subparsers.add_parser(
        "show",
        help="Show specific configuration details"
    )
    show_config_parser.add_argument(
        "config_name",
        help="Configuration name to display"
    )
    
    # Recommend configuration
    recommend_parser = config_subparsers.add_parser(
        "recommend",
        help="Get configuration recommendations for a URL"
    )
    recommend_parser.add_argument(
        "url",
        help="Target URL for recommendation"
    )
    recommend_parser.add_argument(
        "--risk-tolerance",
        choices=["LOW", "MODERATE", "HIGH"],
        default="MODERATE",
        help="Risk tolerance level (default: MODERATE)"
    )
    
    # SEADOG intelligence
    intel_parser = seadog_subparsers.add_parser(
        "intel",
        help="Intelligence and monitoring operations"
    )
    intel_parser.add_argument(
        "urls",
        nargs="+",
        help="URLs to monitor and analyze"
    )
    intel_parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Monitoring duration in seconds (default: 300)"
    )
    intel_parser.add_argument(
        "--export-intel",
        type=str,
        help="Export intelligence data to file"
    )
    
    return parser


def load_urls_from_input(input_str: str) -> List[str]:
    """Load URLs from file or comma-separated string"""
    input_path = Path(input_str)
    
    if input_path.exists():
        # Load from file
        with open(input_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        # Treat as comma-separated URLs
        urls = [url.strip() for url in input_str.split(',') if url.strip()]
    
    # Filter out empty URLs and comments
    urls = [url for url in urls if url and not url.startswith('#')]
    
    return urls


def save_results(results: List[dict], output_path: str, quiet: bool = False) -> None:
    """Save scraping results to JSON file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        if not quiet:
            print(f"Results saved to {output_path}")
            print(f"Total products: {len(results)}")
            
            # Show quality statistics
            quality_scores = [p.get('_quality_score', 0) for p in results]
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                print(f"Average quality score: {avg_quality:.2f}")
                
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        sys.exit(1)


def setup_logging_from_args(args) -> None:
    """Setup logging based on command-line arguments"""
    if args.quiet:
        level = logging.ERROR
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def handle_seadog_commands(args):
    """Handle SEADOG command operations"""
    
    if not args.seadog_command:
        print("❌ No SEADOG command specified. Use --help for available commands.")
        sys.exit(1)
    
    try:
        if args.seadog_command == "recon":
            return asyncio.run(handle_seadog_recon(args))
        elif args.seadog_command == "scrape":
            return asyncio.run(handle_seadog_scrape(args))
        elif args.seadog_command == "validate":
            return asyncio.run(handle_seadog_validate(args))
        elif args.seadog_command == "config":
            return handle_seadog_config(args)
        elif args.seadog_command == "intel":
            return asyncio.run(handle_seadog_intel(args))
        else:
            print(f"❌ Unknown SEADOG command: {args.seadog_command}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 SEADOG operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ SEADOG operation failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


async def handle_seadog_recon(args):
    """Handle SEADOG reconnaissance operations"""
    
    print("🔍 Starting SEADOG Reconnaissance Operations")
    print(f"   Targets: {len(args.urls)} URLs")
    print(f"   Intensity: {args.intensity}")
    print(f"   Parallel: {'Yes' if args.parallel else 'No'}")
    print("-" * 50)
    
    # Create integration configuration
    config = IntegrationConfig(
        intelligence_enabled=True,
        real_time_monitoring=True,
        test_suite_type="RECONNAISSANCE",
        parallel_execution=args.parallel,
        timeout_minutes=30 if args.intensity == "LIGHT" else 45
    )
    
    integration = LuxcrepeSEADOGIntegration(config)
    
    try:
        await integration.start_integration()
        
        # Execute reconnaissance mission
        results = await integration.execute_mission_test(args.urls, "RECONNAISSANCE")
        
        # Display results
        overall_metrics = results.get("overall_metrics", {})
        summary = results.get("summary", {})
        
        print(f"✅ Reconnaissance completed")
        print(f"   Status: {summary.get('test_status', 'UNKNOWN')}")
        print(f"   Success rate: {overall_metrics.get('success_rate', 0):.2%}")
        print(f"   Average time: {overall_metrics.get('average_scenario_time', 0):.1f}s")
        print(f"   Overall quality: {summary.get('overall_quality', 'UNKNOWN')}")
        
        # Show key findings
        key_findings = summary.get('key_findings', [])
        if key_findings:
            print("\n📋 Key Findings:")
            for finding in key_findings[:3]:
                print(f"   • {finding}")
        
        # Show recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations[:3]:
                print(f"   • {rec}")
        
        # Export detailed results
        timestamp = results.get("execution_metadata", {}).get("execution_start", "").replace(":", "-")
        results_file = f"seadog_recon_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
    finally:
        await integration.stop_integration()
    
    return None


async def handle_seadog_scrape(args):
    """Handle SEADOG integrated scraping operations"""
    
    print("🚀 Starting SEADOG Integrated Scraping")
    print(f"   Target: {args.url}")
    print(f"   Intensity: {args.intensity}")
    print(f"   Testing: {'Disabled' if args.no_testing else 'Enabled'}")
    print("-" * 50)
    
    # Create integration configuration
    config = IntegrationConfig(
        intelligence_enabled=True,
        real_time_monitoring=True,
        test_suite_type="RECONNAISSANCE",
        parallel_execution=False,  # Sequential for scraping
        timeout_minutes=20
    )
    
    integration = LuxcrepeSEADOGIntegration(config)
    
    try:
        await integration.start_integration()
        
        # Execute integrated scraping
        results = await integration.integrated_scrape_with_testing(
            args.url,
            enable_testing=not args.no_testing,
            test_intensity=args.intensity
        )
        
        # Display results
        scraping_results = results.get("scraping_results", [])
        performance_metrics = results.get("performance_metrics", {})
        
        print(f"✅ Integrated scraping completed")
        print(f"   Products extracted: {len(scraping_results)}")
        print(f"   Execution time: {performance_metrics.get('total_execution_time', 0):.1f}s")
        print(f"   Success: {'Yes' if performance_metrics.get('success', False) else 'No'}")
        
        if not args.no_testing:
            testing_results = results.get("testing_results", {})
            if testing_results:
                print(f"   SEADOG validation: Completed")
        
        # Show recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations[:3]:
                print(f"   • {rec}")
        
        return scraping_results
        
    finally:
        await integration.stop_integration()


async def handle_seadog_validate(args):
    """Handle SEADOG validation operations"""
    
    print("🧪 Starting SEADOG System Validation")
    print(f"   Target type: {args.target_type}")
    print(f"   Max targets: {args.max_targets}")
    print("-" * 50)
    
    # Determine validation type
    if args.target_type == "ECOMMERCE":
        results = await validate_ecommerce_sites()
    elif args.target_type == "API_ENDPOINT":
        results = await validate_api_endpoints()
    else:
        # Comprehensive validation
        validator = RealWorldValidator()
        target_filter = None if args.target_type == "ALL" else getattr(TargetType, args.target_type)
        results = await validator.run_comprehensive_validation(target_filter, args.max_targets)
    
    # Display results
    overall_metrics = results.get("overall_metrics", {})
    summary = results.get("summary", {})
    
    print(f"✅ Validation completed")
    print(f"   Status: {summary.get('validation_status', 'UNKNOWN')}")
    print(f"   Success rate: {summary.get('success_rate', 0):.2%}")
    print(f"   Average score: {summary.get('average_score', 0):.2f}")
    print(f"   Targets tested: {overall_metrics.get('total_targets', 0)}")
    
    # Show key findings
    key_findings = summary.get('key_findings', [])
    critical_issues = summary.get('critical_issues', [])
    
    if key_findings:
        print("\n📋 Key Findings:")
        for finding in key_findings:
            print(f"   • {finding}")
    
    if critical_issues:
        print("\n⚠️  Critical Issues:")
        for issue in critical_issues:
            print(f"   • {issue}")
    
    # Show recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        print("\n💡 Recommendations:")
        for rec in recommendations[:5]:
            print(f"   • {rec}")
    
    # Export results if requested
    if args.export:
        with open(args.export, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Validation results exported to: {args.export}")
    
    return None


def handle_seadog_config(args):
    """Handle SEADOG configuration operations"""
    
    if not args.config_command:
        print("❌ No configuration command specified. Use --help for available commands.")
        sys.exit(1)
    
    configs = get_seadog_configurations()
    
    if args.config_command == "list":
        print("📋 Available SEADOG Test Configurations:")
        print("=" * 50)
        
        available_configs = configs.list_configurations()
        for name, description in available_configs.items():
            config_obj = configs.get_configuration(name)
            risk_level = config_obj.risk_assessment if config_obj else "UNKNOWN"
            intensity = config_obj.test_intensity.value if config_obj else "UNKNOWN"
            
            print(f"🎯 {name}")
            print(f"   Description: {description}")
            print(f"   Risk Level: {risk_level}")
            print(f"   Intensity: {intensity}")
            print()
    
    elif args.config_command == "show":
        config = configs.get_configuration(args.config_name)
        if not config:
            print(f"❌ Configuration '{args.config_name}' not found")
            sys.exit(1)
        
        print(f"📋 Configuration: {args.config_name}")
        print("=" * 50)
        print(f"Description: {config.scenario_description}")
        print(f"Target Type: {config.target_type.value}")
        print(f"Test Intensity: {config.test_intensity.value}")
        print(f"Risk Assessment: {config.risk_assessment}")
        print(f"Timeout: {config.integration_config.timeout_minutes} minutes")
        print(f"Parallel Execution: {config.integration_config.parallel_execution}")
        
        print("\nRecommended Usage:")
        for usage in config.recommended_usage:
            print(f"   • {usage}")
        
        print("\nTest Parameters:")
        for key, value in config.test_parameters.items():
            print(f"   {key}: {value}")
    
    elif args.config_command == "recommend":
        recommendations = configs.recommend_configuration(
            args.url,
            risk_tolerance=args.risk_tolerance
        )
        
        print(f"🎯 Configuration Recommendations for: {args.url}")
        print(f"   Risk Tolerance: {args.risk_tolerance}")
        print("=" * 50)
        
        if not recommendations:
            print("❌ No suitable configurations found for the given criteria")
            return
        
        for i, config_name in enumerate(recommendations, 1):
            config = configs.get_configuration(config_name)
            print(f"{i}. {config_name}")
            print(f"   Risk: {config.risk_assessment}")
            print(f"   Intensity: {config.test_intensity.value}")
            print(f"   Description: {config.scenario_description[:80]}...")
            print()
    
    return None


async def handle_seadog_intel(args):
    """Handle SEADOG intelligence operations"""
    
    print("🕵️ Starting SEADOG Intelligence Operations")
    print(f"   Targets: {len(args.urls)} URLs")
    print(f"   Duration: {args.duration} seconds")
    print("-" * 50)
    
    # Create intelligence system
    from .intelligence import SEADOGIntelligenceSystem
    intel_system = SEADOGIntelligenceSystem("CLI_INTEL_001")
    
    try:
        await intel_system.start_system()
        
        print("📡 Intelligence collection started...")
        
        # Simulate intelligence gathering (in real implementation, this would monitor actual operations)
        await asyncio.sleep(min(args.duration, 30))  # Limit to 30 seconds for demo
        
        # Get system status
        status = intel_system.get_system_status()
        
        print(f"✅ Intelligence collection completed")
        print(f"   Collection time: {status.get('uptime', 'Unknown')}")
        print(f"   Metrics collected: {status.get('collection_stats', {}).get('total_metrics', 0)}")
        
        # Export intelligence data if requested
        if args.export_intel:
            intel_data = intel_system.export_intelligence_data()
            with open(args.export_intel, 'w') as f:
                f.write(intel_data)
            print(f"💾 Intelligence data exported to: {args.export_intel}")
        
    finally:
        await intel_system.stop_system()
    
    return None


def main():
    """Main CLI entry point"""
    parser = setup_cli_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging_from_args(args)
    
    # Load configuration
    config = None
    if args.config:
        config = load_config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
    
    # Initialize scraper
    scraper = LuxcrepeScraper(args.config)
    
    # Apply CLI overrides
    if args.no_ml:
        scraper.update_config(use_ml=False)
        logger.info("ML enhancement disabled")
    
    # Handle different modes
    results = []
    
    try:
        if args.mode == "interactive":
            mode = InteractiveMode(scraper)
            results = mode.run(max_urls=args.max_urls)
            
        elif args.mode == "batch":
            urls = load_urls_from_input(args.input)
            if not urls:
                print(f"No valid URLs found in {args.input}")
                sys.exit(1)
            
            mode = BatchMode(scraper)
            results = mode.run(
                urls=urls,
                scrape_details=args.details,
                max_pages=args.pages
            )
            
        elif args.mode == "detail":
            mode = DetailMode(scraper)
            results = mode.run(args.urls)
            
        elif args.mode == "listing":
            mode = BatchMode(scraper)  # Reuse batch mode for listings
            results = mode.run(
                urls=args.urls,
                scrape_details=args.details,
                max_pages=args.pages
            )
            
        elif args.mode == "stats":
            stats = scraper.get_scraper_stats()
            print(json.dumps(stats, indent=2))
            return
            
        elif args.mode == "seadog":
            # Handle SEADOG operations
            results = handle_seadog_commands(args)
            if results and isinstance(results, list):
                # Save scraping results if any
                save_results(results, args.output, args.quiet)
            return
            
        else:
            parser.print_help()
            sys.exit(1)
        
        # Save results
        if results:
            save_results(results, args.output, args.quiet)
        else:
            if not args.quiet:
                print("No products found")
    
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()