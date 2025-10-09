"""OS detection and platform-specific utilities."""

import os
import platform
from typing import Dict, Tuple


def detect_shell() -> Tuple[str, str]:
    """
    Detect the current shell with confidence level.
    
    Returns:
        Tuple of (shell_name, detection_method)
    """
    # Try to detect from SHELL environment variable (most reliable)
    shell_env = os.environ.get('SHELL', '').lower()
    
    # High confidence detections from $SHELL
    if 'pwsh' in shell_env or shell_env.endswith('powershell'):
        return 'powershell', 'detected from $SHELL'
    elif 'cmd' in shell_env or shell_env.endswith('cmd.exe'):
        return 'cmd', 'detected from $SHELL'
    elif 'bash' in shell_env:
        return 'bash', 'detected from $SHELL'
    elif 'zsh' in shell_env:
        return 'bash', 'detected zsh (using bash-compatible mode)'
    
    # Fallback to OS-based detection (lower confidence)
    system = platform.system()
    if system == 'Windows':
        return 'powershell', 'guessed from Windows OS'
    elif system == 'Darwin':
        return 'bash', 'guessed from macOS'
    else:
        return 'bash', 'guessed from Linux'


def get_os_type() -> str:
    """Get the OS type."""
    system = platform.system()
    if system == 'Darwin':
        return 'macOS'
    elif system == 'Linux':
        return 'Linux'
    elif system == 'Windows':
        return 'Windows'
    else:
        return system


def get_os_info() -> str:
    """Get detailed OS information for command generation context."""
    system = platform.system()
    if system == 'Darwin':
        return 'macOS (use BSD-compatible tools, avoid GNU-specific flags like -printf)'
    elif system == 'Linux':
        return 'Linux (GNU tools available)'
    elif system == 'Windows':
        return 'Windows'
    else:
        return system


def is_bsd() -> bool:
    """Check if the system is BSD-based (macOS)."""
    return platform.system() == 'Darwin'


def get_platform_notes(os_type: str) -> str:
    """Get platform-specific notes for command generation."""
    notes = {
        'macOS': 'Use BSD-compatible commands, avoid GNU-specific flags',
        'Linux': 'GNU tools available, can use advanced features',
        'Windows': 'Use cmd or PowerShell commands'
    }
    return notes.get(os_type, '')


def get_shell_compatibility(os_type: str, shell: str) -> Dict[str, str]:
    """Get shell compatibility notes for OS."""
    compatibility = {
        'macOS': {
            'bash': 'Native bash available',
            'zsh': 'Default shell on newer macOS',
            'cmd': 'Not available',
            'powershell': 'Available via PowerShell Core'
        },
        'Linux': {
            'bash': 'Standard shell',
            'zsh': 'Available if installed',
            'cmd': 'Not available',
            'powershell': 'Available via PowerShell Core'
        },
        'Windows': {
            'bash': 'Available via WSL or Git Bash',
            'zsh': 'Available via WSL',
            'cmd': 'Native command prompt',
            'powershell': 'Native PowerShell'
        }
    }
    
    return compatibility.get(os_type, {}).get(shell, 'Unknown compatibility')
