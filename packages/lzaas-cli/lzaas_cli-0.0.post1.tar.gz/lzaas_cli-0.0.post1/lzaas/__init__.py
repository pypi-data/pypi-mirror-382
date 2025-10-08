"""
LZaaS CLI - Landing Zone as a Service
AWS Account Factory Automation Tool
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("lzaas-cli")
except importlib.metadata.PackageNotFoundError:
    # Fallback for development installations
    __version__ = "1.0.0-dev"

__author__ = "Platform Team"
__email__ = "platform@company.com"
