"""Configuration and API key management utilities."""

import os
from pathlib import Path
from typing import Dict, Optional


def get_env_file_path() -> Path:
    """
    Get the path to the global .ai-shell-env file.
    
    Returns:
        Path to ~/.ai-shell-env
    """
    return Path.home() / '.ai-shell-env'


def load_env_file() -> Dict[str, str]:
    """
    Load API keys and settings from ~/.ai-shell-env file.
    
    Returns:
        Dictionary of key=value pairs
    """
    env_file = get_env_file_path()
    env_vars = {}
    
    if not env_file.exists():
        return env_vars
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"Warning: Could not load ~/.ai-shell-env: {e}")
    
    return env_vars


def save_api_key(key_name: str, key_value: str) -> bool:
    """
    Save an API key to ~/.ai-shell-env file.
    
    Args:
        key_name: Environment variable name (e.g., 'OPENAI_API_KEY')
        key_value: The API key value
        
    Returns:
        True if successful, False otherwise
    """
    env_file = get_env_file_path()
    
    try:
        # Load existing keys
        existing_vars = load_env_file()
        
        # Update with new key
        existing_vars[key_name] = key_value
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.write("# AI Shell Command Generator - API Keys\n")
            f.write("# This file is automatically managed by ai-shell\n")
            f.write("# You can edit or delete this file anytime\n\n")
            
            for key, value in existing_vars.items():
                f.write(f"{key}={value}\n")
        
        # Set file permissions to user-only (security)
        # Note: chmod only works on Unix-like systems (macOS, Linux, WSL)
        try:
            env_file.chmod(0o600)
        except (OSError, NotImplementedError):
            # Windows doesn't support Unix permissions, that's okay
            pass
        
        return True
        
    except Exception as e:
        print(f"Error saving API key: {e}")
        return False


def get_api_key_from_env_file(key_name: str) -> Optional[str]:
    """
    Get a specific API key from ~/.ai-shell-env file.
    
    Args:
        key_name: Environment variable name (e.g., 'OPENAI_API_KEY')
        
    Returns:
        API key value or None if not found
    """
    env_vars = load_env_file()
    return env_vars.get(key_name)
