"""
Framework utilities for FAAS QA Testing
"""

from .environment import get_base_url, get_environment, is_ci, is_local
from .reporting import QAReporter
from .test_orchestrator import TestOrchestrator
from .notifications import send_slack_notification, send_email_notification

__all__ = [
    'get_base_url',
    'get_environment',
    'is_ci',
    'is_local',
    'QAReporter',
    'TestOrchestrator',
    'send_slack_notification',
    'send_email_notification',
]
