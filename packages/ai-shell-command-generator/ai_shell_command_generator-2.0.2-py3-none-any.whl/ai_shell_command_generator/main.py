"""AI Shell Command Generator - Main entry point."""

import os
from pathlib import Path
from dotenv import load_dotenv
from ai_shell_command_generator.cli.commands import main
from ai_shell_command_generator.utils.config_loader import load_env_file

__version__ = "2.0.2"

# Load API keys in explicit, predictable order:

# 1. Environment variables (highest priority) - already set by user
# 2. Current directory .env file (project-specific) - ONLY current dir, no parent search
current_dir_env = Path.cwd() / '.env'
if current_dir_env.exists():
    load_dotenv(dotenv_path=current_dir_env, override=False)

# 3. Global ~/.ai-shell-env file (user-specific)
home_env = Path.home() / '.ai-shell-env'
if home_env.exists():
    env_vars = load_env_file()
    for key, value in env_vars.items():
        # Only set if not already in environment (previous sources take precedence)
        if key not in os.environ:
            os.environ[key] = value

if __name__ == "__main__":
    main()
