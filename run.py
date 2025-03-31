#!/usr/bin/env python
"""
Run script for the Ogent application.

This script starts the microservices using docker-compose.
"""

import os
import argparse
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Create parser
    parser = argparse.ArgumentParser(description="Run the Ogent microservices")
    
    parser.add_argument("--detach", "-d", action="store_true", help="Run containers in the background")
    parser.add_argument("--build", "-b", action="store_true", help="Build containers before starting")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--services", "-s", nargs="+", help="Specific services to start (default: all)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Prepare docker-compose command
    cmd = ["docker-compose", "up"]
    
    if args.detach:
        cmd.append("-d")
        
    if args.build:
        cmd.append("--build")
        
    if args.debug:
        os.environ["DEBUG"] = "True"
        
    if args.services:
        cmd.extend(args.services)
    
    # Print info
    print("Starting Ogent microservices...")
    print(f"Debug mode: {'enabled' if args.debug else 'disabled'}")
    print(f"Detached mode: {'enabled' if args.detach else 'disabled'}")
    
    if args.services:
        print(f"Starting specific services: {', '.join(args.services)}")
    else:
        print("Starting all services")
    
    # Run docker-compose
    try:
        subprocess.run(cmd, check=True)
        print("Services started successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error starting services: {e}")
        exit(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")
        subprocess.run(["docker-compose", "down"], check=True)
        print("Services stopped successfully") 