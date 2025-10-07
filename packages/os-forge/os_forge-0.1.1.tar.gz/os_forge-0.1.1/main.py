#!/usr/bin/env python3
"""
OS Forge - Multi-Platform System Hardening Tool
Modular Architecture Entry Point

This is the main entry point for the refactored OS Forge application.
The monolithic structure has been broken down into modular components:

- core/: API and CLI interfaces
- security/: Secure command execution and authentication  
- policies/: Policy engine and rule management
- database/: Data models and database management
- reporting/: Report generation

Usage:
    python main.py [command] [options]
    
Examples:
    python main.py info                    # System information
    python main.py check --level basic     # Run security check
    python main.py server                  # Start web server
    python main.py report                  # Generate report
"""

import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from core.cli import cli

def main():
    """Entry point for console script"""
    cli()

if __name__ == "__main__":
    main()

