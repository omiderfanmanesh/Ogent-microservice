#!/usr/bin/env python3
"""
Command Execution Service Full Verification Tool

This script runs a comprehensive verification of the Command Execution Service,
including both direct API testing and integration with the Agent Service.

Usage:
    python verify_all.py [--skip-integration]

Options:
    --skip-integration    Skip integration tests with Agent Service

Requirements:
    requests
"""

import os
import sys
import logging
import importlib.util
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def load_module(module_path, module_name):
    """Dynamically load a module from file path"""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec:
        logger.error(f"Could not load module from {module_path}")
        return None
        
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_verify_service():
    """Run the verify_service.py script"""
    logger.info("===== Running Command Execution Service Verification =====")
    
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load and run the verify_service.py module
    verify_service_path = os.path.join(current_dir, "verify_service.py")
    verify_service = load_module(verify_service_path, "verify_service")
    
    if verify_service and hasattr(verify_service, "main"):
        success = verify_service.main()
        return success
    else:
        logger.error("Could not run verify_service.py")
        return False

def run_verify_integration():
    """Run the verify_integration.py script"""
    logger.info("\n===== Running Integration Verification =====")
    
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load and run the verify_integration.py module
    verify_integration_path = os.path.join(current_dir, "verify_integration.py")
    verify_integration = load_module(verify_integration_path, "verify_integration")
    
    if verify_integration and hasattr(verify_integration, "main"):
        success = verify_integration.main()
        return success
    else:
        logger.error("Could not run verify_integration.py")
        return False

def main():
    """Main function to run all verification tests"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Verify Command Execution Service")
    parser.add_argument("--skip-integration", action="store_true", 
                      help="Skip integration tests with Agent Service")
    args = parser.parse_args()
    
    logger.info("Starting Command Execution Service full verification...")
    
    # Run verify_service.py
    service_success = run_verify_service()
    
    # Run verify_integration.py unless skipped
    integration_success = True
    if not args.skip_integration:
        integration_success = run_verify_integration()
    else:
        logger.info("Skipping integration tests as requested")
    
    # Print summary
    logger.info("\n=========== Full Verification Summary ===========")
    service_status = "✅ PASSED" if service_success else "❌ FAILED"
    logger.info(f"Command Service Verification: {service_status}")
    
    if not args.skip_integration:
        integration_status = "✅ PASSED" if integration_success else "❌ FAILED"
        logger.info(f"Integration Verification: {integration_status}")
    
    overall_success = service_success and (args.skip_integration or integration_success)
    overall_status = "✅ PASSED" if overall_success else "❌ FAILED"
    logger.info(f"Overall Verification: {overall_status}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 