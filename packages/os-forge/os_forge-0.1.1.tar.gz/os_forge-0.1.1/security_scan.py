#!/usr/bin/env python3
"""
OS Forge Security Scanner Wrapper
Provides easy access to enhanced security features from project root
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Main entry point for security scanner wrapper"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    enhanced_dir = script_dir / "security" / "enhanced"
    
    # Change to enhanced directory
    os.chdir(enhanced_dir)
    
    # Get the command to run
    if len(sys.argv) < 2:
        print("OS Forge Enhanced Security Features")
        print()
        print("Available commands:")
        print("  python3 security_scan.py vulnerability [args...]")
        print("  python3 security_scan.py secrets [args...]")
        print("  python3 security_scan.py monitor [args...]")
        print("  python3 security_scan.py config [args...]")
        print("  python3 security_scan.py integration [args...]")
        print()
        print("Examples:")
        print("  python3 security_scan.py vulnerability --directory ./ --format html")
        print("  python3 security_scan.py secrets list")
        print("  python3 security_scan.py config policy list")
        print("  python3 security_scan.py integration scan --directory ./")
        return 1
    
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Map commands to scripts
    script_map = {
        'vulnerability': 'vulnerability_scanner.py',
        'secrets': 'secrets_manager.py',
        'monitor': 'security_monitor.py',
        'config': 'security_config.py',
        'integration': 'security_integration.py'
    }
    
    if command not in script_map:
        print(f"Unknown command: {command}")
        print("Available commands: vulnerability, secrets, monitor, config, integration")
        return 1
    
    script = script_map[command]
    
    # Run the script
    try:
        result = subprocess.run(['python3', script] + args)
        return result.returncode
    except Exception as e:
        print(f"Error running {script}: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
