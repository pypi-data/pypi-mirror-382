"""
OS Forge - Multi-Platform System Hardening Tool

A cross-platform security hardening tool that supports Windows, Ubuntu, and CentOS.
Automates compliance checking, remediation, and reporting against industry standards.

Key Features:
- Multi-platform support (Windows 10/11, Ubuntu 20.04+, CentOS 7+)
- Automated security hardening based on CIS Benchmarks
- CLI and Web GUI interfaces
- Compliance reporting and audit trails
- Rollback capability
- Docker deployment ready

Usage:
    pip install os-forge
    os-forge --help
    os-forge check --level basic
    os-forge server
"""

__version__ = "1.0.0"
__author__ = "Aayushman"
__email__ = "aayushman2702@gmail.com"
__license__ = "MIT"

# Import main functionality for easy access
from .main import main

__all__ = ["main", "__version__"]
