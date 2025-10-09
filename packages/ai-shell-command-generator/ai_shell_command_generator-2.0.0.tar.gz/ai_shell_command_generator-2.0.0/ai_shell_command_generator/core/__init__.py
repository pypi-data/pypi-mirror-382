"""Core functionality for AI Shell Command Generator."""

from ai_shell_command_generator.core.config import CommandConfig, ProviderConfig
from ai_shell_command_generator.core.os_detection import get_os_info, get_os_type, is_bsd

__all__ = [
    'CommandConfig',
    'ProviderConfig', 
    'get_os_info',
    'get_os_type',
    'is_bsd'
]
