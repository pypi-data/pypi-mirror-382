"""
OSDU Performance Testing Framework - Core Library
"""

from .core.base_service import BaseService
from .core.service_orchestrator import ServiceOrchestrator
from .core.input_handler import InputHandler
from .core.auth import AzureTokenManager
from .utils.environment import detect_environment
from .core.user_base import PerformanceUser

__version__ = "1.0.11"
__author__ = "Janraj CJ"
__email__ = "janrajcj@microsoft.com"

__all__ = [
    "BaseService",
    "ServiceOrchestrator", 
    "InputHandler",
    "AzureTokenManager",
    "PerformanceUser",
    "detect_environment"
]
