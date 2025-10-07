"""
App Preparation Module
Handles getting applications ready for action
"""

from .app_launcher import launch_application
from .app_maximizer import maximize_application
from .app_verifier import verify_application_ready

__all__ = ['launch_application', 'maximize_application', 'verify_application_ready']
