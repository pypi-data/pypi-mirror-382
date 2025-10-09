"""Interactive prompts for CLI."""

import click
from click import style
from typing import Optional, Tuple
from ai_shell_command_generator.providers.models import ModelRegistry
from ai_shell_command_generator.providers.factory import ProviderFactory


def select_provider_and_model() -> Tuple[str, str]:
    """
    Select provider and model interactively with focused options.
    Returns: (provider_name, model_name)
    """
    click.echo(style("\nSelect AI Provider:", fg="cyan", bold=True))
    
    providers = [
        ("OpenAI GPT-5", "openai", "GPT-5 models"),
        ("Anthropic Claude", "anthropic", "Claude 4.1+ and 3.5 Haiku"),
        ("Ollama (Local)", "ollama", "Privacy-focused, offline, free"),
    ]
    
    for i, (display, name, desc) in enumerate(providers, 1):
        click.echo(f"{i}. {display} - {desc}")
    
    # Get provider selection
    while True:
        try:
            choice = int(click.prompt("Select your preferred AI provider"))
            if 1 <= choice <= len(providers):
                provider = providers[choice - 1][1]
                break
        except ValueError:
            pass
        click.echo("Invalid choice. Please try again.")
    
    # Handle Ollama separately (has its own model discovery)
    if provider == 'ollama':
        return provider, select_ollama_model()
    
    # Get models for selected provider
    models = ModelRegistry.get_models_for_provider(provider)
    
    click.echo(style(f"\n📋 Available {provider.capitalize()} Models:", fg="cyan", bold=True))
    click.echo()
    
    # Sort by cost (cheapest first) for better UX
    sorted_models = sorted(models.items(), key=lambda x: x[1].cost_per_1m_input)
    
    for i, (model_id, info) in enumerate(sorted_models, 1):
        click.echo(f"{i}. {info.display_name} ({info.released})")
        click.echo(f"   {info.description}")
        click.echo(f"   Cost: ${info.cost_per_1m_input:.2f}/${info.cost_per_1m_output:.2f} per 1M tokens")
        click.echo(f"   Best for: {', '.join(info.recommended_for)}")
        if i < len(sorted_models):
            click.echo()
    
    # Get model selection
    while True:
        try:
            choice = int(click.prompt(f"Select your preferred {provider.capitalize()} model"))
            if 1 <= choice <= len(sorted_models):
                selected_model = sorted_models[choice - 1][0]
                break
        except ValueError:
            pass
        click.echo("Invalid choice. Please try again.")
    
    return provider, selected_model


def confirm_shell_selection() -> str:
    """
    Detect shell and ask user to confirm or override.
    
    Returns:
        Selected shell
    """
    from ai_shell_command_generator.core.os_detection import detect_shell
    
    detected_shell, method = detect_shell()
    
    click.echo(style(f"\n🔍 Detected shell: {detected_shell} ({method})", fg="yellow"))
    click.echo(style("Is this correct?", fg="cyan", bold=True))
    click.echo(f"1. Yes, use {detected_shell}")
    click.echo("2. No, let me choose")
    
    choice = click.prompt("Select option", type=click.IntRange(1, 2), default=1)
    
    if choice == 1:
        return detected_shell
    else:
        return select_shell()


def select_shell(shells: list[str] = None, input_func=click.prompt) -> str:
    """
    Prompts the user to select their preferred shell environment.
    
    Args:
        shells: List of available shells
        input_func: Function to use for user input (for testing purposes)
    
    Returns:
        The selected shell environment
    """
    if shells is None:
        shells = ['cmd', 'powershell', 'bash']
    
    click.echo(style("\nSelect Shell Environment:", fg="cyan", bold=True))
    for i, shell in enumerate(shells, 1):
        click.echo(f"{i}. {shell}")
    
    while True:
        try:
            choice = int(input_func("Select your preferred shell environment"))
            if 1 <= choice <= len(shells):
                return shells[choice - 1]
        except ValueError:
            pass
        click.echo("Invalid choice. Please try again.")


def select_ollama_model(input_func=click.prompt) -> Optional[str]:
    """
    Prompts the user to select an available Ollama model.
    
    Args:
        input_func: Function to use for user input (for testing purposes)
    
    Returns:
        The selected Ollama model name, or None if no models available
    """
    try:
        import ollama
        click.echo(style("\nDiscovering available Ollama models...", fg="cyan"))
        models = ollama.list()
        
        if not models or not models.models:
            click.echo(style("⚠️  No Ollama models found. Please pull a model first:", fg="yellow"))
            click.echo("   Example: ollama pull gpt-oss:latest")
            return None
        
        available_models = [m.model for m in models.models]
        
        click.echo(style("\nAvailable Ollama Models:", fg="cyan", bold=True))
        for i, model in enumerate(available_models, 1):
            click.echo(f"{i}. {model}")
        
        while True:
            try:
                choice = int(input_func("Select your preferred Ollama model"))
                if 1 <= choice <= len(available_models):
                    return available_models[choice - 1]
            except ValueError:
                pass
            click.echo("Invalid choice. Please try again.")
    
    except Exception as e:
        click.echo(style(f"⚠️  Error connecting to Ollama: {str(e)}", fg="yellow"))
        click.echo("Make sure Ollama is running: ollama serve")
        return None


def select_mode() -> bool:
    """
    Select between quick mode and teaching mode.
    
    Returns:
        True for teaching mode, False for quick mode
    """
    click.echo(style("\nSelect Mode:", fg="cyan", bold=True))
    click.echo("1. Quick Mode - Generate command and exit")
    click.echo("2. Teaching Mode - Learn while generating commands")
    
    while True:
        try:
            choice = int(click.prompt("Select mode"))
            if choice == 1:
                return False
            elif choice == 2:
                return True
        except ValueError:
            pass
        click.echo("Invalid choice. Please try again.")


def prompt_for_query() -> str:
    """
    Prompt user for command query.
    
    Returns:
        User's command query
    """
    return click.prompt(style("Enter your command query (or 'quit' to exit)", fg="cyan"))


def confirm_copy() -> bool:
    """
    Ask user if they want to copy command to clipboard.
    
    Returns:
        True if user wants to copy, False otherwise
    """
    click.echo(style("\nCopy to clipboard?", fg="cyan", bold=True))
    click.echo("1. Yes")
    click.echo("2. No")
    
    choice = click.prompt("Select option", type=click.IntRange(1, 2), default=1)
    
    return choice == 1


def confirm_explain() -> bool:
    """
    Ask user if they want to understand the command better.
    
    Returns:
        True if user wants explanation, False otherwise
    """
    click.echo(style("\nWant to understand this command better?", fg="cyan", bold=True))
    click.echo("1. Yes, explain it")
    click.echo("2. No, I'm good")
    
    choice = click.prompt("Select option", type=click.IntRange(1, 2), default=2)
    
    return choice == 1


def prompt_for_clarification() -> str:
    """
    Ask user what part of the command needs clarification.
    
    Returns:
        User's clarification question
    """
    return click.prompt(
        "What part needs clarification? (or press Enter for examples)",
        default="",
        show_default=False
    )


def select_teaching_option() -> str:
    """
    Present teaching mode options to user.
    
    Returns:
        Selected option: 'yes', 'explain', 'explain-more', 'what-if', 'no'
    """
    click.echo(style("\nWhat would you like to do?", fg="cyan", bold=True))
    click.echo("1. Use this command")
    click.echo("2. Explain more")
    click.echo("3. Explore what-if scenarios")
    click.echo("4. Try a different approach")
    
    choice = click.prompt("Select option", type=click.IntRange(1, 4), default=1)
    
    return {1: 'yes', 2: 'explain-more', 3: 'what-if', 4: 'no'}[choice]


def prompt_for_api_key(provider_name: str) -> Optional[str]:
    """
    Prompt user to enter API key for a provider.
    
    Args:
        provider_name: 'openai' or 'anthropic'
        
    Returns:
        API key entered by user, or None if they skip
    """
    provider_display = provider_name.capitalize()
    
    click.echo()
    click.echo(style(f"🔑 {provider_display} API Key Required", fg="yellow", bold=True))
    click.echo(f"\nTo use {provider_display}, you need an API key.")
    click.echo(f"Get one at: https://platform.{provider_name}.com/api-keys" if provider_name == 'openai' else "https://console.anthropic.com/")
    click.echo()
    click.echo(style("What would you like to do?", fg="cyan", bold=True))
    click.echo(f"1. Enter my {provider_display} API key now (I'll save it for you)")
    click.echo(f"2. I'll set it manually via environment variable")
    click.echo("3. Use Ollama instead (free, no API key needed)")
    
    choice = click.prompt("Select option", type=click.IntRange(1, 3), default=3)
    
    if choice == 1:
        api_key = click.prompt(
            f"Enter your {provider_display} API key",
            hide_input=True,
            type=str
        ).strip()
        
        if api_key:
            # Save it
            from ai_shell_command_generator.utils.config_loader import save_api_key, get_env_file_path
            
            key_name = f"{provider_name.upper()}_API_KEY"
            if save_api_key(key_name, api_key):
                env_path = get_env_file_path()
                click.echo(style(f"\n✓ API key saved to {env_path}", fg="green"))
                click.echo(style("  This will be loaded automatically next time.", fg="green"))
                return api_key
            else:
                click.echo(style("\n✗ Failed to save API key. You'll need to set it manually.", fg="red"))
                return None
        else:
            return None
            
    elif choice == 2:
        # User will set manually
        key_name = f"{provider_name.upper()}_API_KEY"
        click.echo(style(f"\nSet your API key with:", fg="cyan"))
        click.echo(f"  export {key_name}='your-key-here'")
        click.echo(f"\nOr add to ~/.bashrc or ~/.zshrc for persistence")
        return None
        
    else:  # choice == 3
        click.echo(style("\n💡 Switching to Ollama (free, local AI)", fg="green"))
        click.echo("   Make sure Ollama is installed: https://ollama.com")
        return None


def select_teaching_option_initial() -> str:
    """
    Present initial teaching mode options to user.
    
    Returns:
        Selected option: 'yes', 'explain', 'no'
    """
    click.echo(style("\nWhat would you like to do?", fg="cyan", bold=True))
    click.echo("1. Use this command")
    click.echo("2. Explain how it works")
    click.echo("3. Try a different approach")
    
    choice = click.prompt("Select option", type=click.IntRange(1, 3), default=1)
    
    return {1: 'yes', 2: 'explain', 3: 'no'}[choice]
