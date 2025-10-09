"""Display utilities for CLI output."""

import click
from click import style
from typing import Dict, List, Optional


def display_header(text: str, color: str = "cyan") -> None:
    """Display a header with styling."""
    click.echo()
    click.echo(style(text, fg=color, bold=True))
    click.echo("═" * len(text))


def display_command(command: str, mode: str = "normal") -> None:
    """Display a generated command."""
    if mode == "teaching":
        click.echo(style("\nCOMMAND:", fg="green", bold=True))
        click.echo(f"  {command}")
    else:
        click.echo(style(f"\nGenerated command:", fg="yellow", bold=True))
        click.echo(style(command, fg="green"))


def display_risk_warning(risk_info: Dict, detailed: bool = False) -> None:
    """Display risk warning."""
    if not risk_info.get('is_risky', False):
        return
    
    severity = risk_info.get('severity', 'medium')
    reason = risk_info.get('reason', 'Unknown risk')
    
    if severity == 'high':
        icon = '⚠️  DANGER'
        color = 'red'
    elif severity == 'medium':
        icon = '⚠️  WARNING'
        color = 'yellow'
    else:
        icon = '⚠️  CAUTION'
        color = 'yellow'
    
    click.echo()
    if detailed:
        click.echo(style(f"{icon}: This command may be risky!", fg=color, bold=True))
        click.echo(style(f"Risk level: {severity.upper()}", fg=color))
        click.echo(style(f"Reason: {reason}", fg=color))
    else:
        click.echo(style(f"# WARNING: {severity.upper()} risk - {reason}", fg=color, bold=True))
    click.echo()


def display_teaching_output(teaching_response: Dict) -> None:
    """Display teaching mode output."""
    click.echo()
    click.echo(style("═" * 60, fg="cyan"))
    click.echo(style("📚 TEACHING MODE", fg="cyan", bold=True))
    click.echo(style("═" * 60, fg="cyan"))
    
    # Display command
    if teaching_response.get('command'):
        click.echo()
        click.echo(style("COMMAND:", fg="green", bold=True))
        click.echo(style(f"  {teaching_response['command']}", fg="white", bold=True))
    
    # Display breakdown
    if teaching_response.get('breakdown'):
        click.echo()
        click.echo(style("BREAKDOWN:", fg="yellow", bold=True))
        # Indent each line for better readability
        for line in teaching_response['breakdown'].split('\n'):
            if line.strip():
                click.echo(f"  {line}")
    
    # Display OS notes
    if teaching_response.get('os_notes'):
        click.echo()
        click.echo(style("OS NOTES:", fg="blue", bold=True))
        for line in teaching_response['os_notes'].split('\n'):
            if line.strip():
                click.echo(f"  {line}")
    
    # Display safer approach
    if teaching_response.get('safer_approach'):
        click.echo()
        click.echo(style("SAFER APPROACH:", fg="magenta", bold=True))
        for line in teaching_response['safer_approach'].split('\n'):
            if line.strip():
                click.echo(f"  {line}")
    
    # Display what was learned
    if teaching_response.get('learned') and len(teaching_response['learned']) > 0:
        click.echo()
        click.echo(style("WHAT YOU LEARNED:", fg="green", bold=True))
        for point in teaching_response['learned']:
            if point.strip():
                click.echo(style(f"  ✓ {point}", fg="green"))
    
    click.echo()
    click.echo(style("═" * 60, fg="cyan"))


def display_success(message: str) -> None:
    """Display success message."""
    click.echo(style(f"✓ {message}", fg="green"))


def display_error(message: str) -> None:
    """Display error message."""
    click.echo(style(f"✗ {message}", fg="red"))


def display_info(message: str) -> None:
    """Display info message."""
    click.echo(style(f"ℹ  {message}", fg="blue"))


def display_provider_info(provider: str, model: str) -> None:
    """Display provider initialization info."""
    from ai_shell_command_generator.providers.models import ModelRegistry
    model_info = ModelRegistry.get_model_info(provider, model)
    
    if model_info:
        click.echo(style(f"\nShell Command Generator initialized with {provider.capitalize()} ({model_info.display_name})", fg="green", bold=True))
    else:
        click.echo(style(f"\nShell Command Generator initialized with {provider.capitalize()} ({model})", fg="green", bold=True))


def display_command_for_copy(command: str) -> None:
    """Display command again for easy copy-paste."""
    click.echo(style("\nCommand (for easy copy-paste):", fg="cyan"))
    click.echo(command)


def display_models_list(provider: str) -> None:
    """Display list of available models for a provider."""
    from ai_shell_command_generator.providers.models import ModelRegistry
    from ai_shell_command_generator.providers.factory import ProviderFactory
    
    click.echo(style(f"\nAvailable {provider.capitalize()} Models:", fg="cyan", bold=True))
    click.echo()
    
    # Special handling for Ollama - query live models
    if provider.lower() == 'ollama':
        try:
            import ollama
            models_response = ollama.list()
            
            if models_response and 'models' in models_response:
                models_list = models_response['models']
                if models_list:
                    for model_info in models_list:
                        model_name = model_info.get('name', model_info.get('model', 'unknown'))
                        size = model_info.get('size', 0)
                        size_gb = size / (1024**3) if size else 0
                        modified = model_info.get('modified_at', 'unknown')
                        
                        click.echo(f"• {model_name}")
                        if size_gb > 0:
                            click.echo(f"  Size: {size_gb:.2f} GB")
                        click.echo(f"  Modified: {modified}")
                        click.echo()
                else:
                    click.echo(style("No Ollama models found. Pull a model with: ollama pull <model-name>", fg="yellow"))
            else:
                click.echo(style("No Ollama models found. Pull a model with: ollama pull <model-name>", fg="yellow"))
                
        except Exception as e:
            click.echo(style(f"Error connecting to Ollama: {str(e)}", fg="red"))
            click.echo(style("Make sure Ollama is running: ollama serve", fg="yellow"))
        return
    
    # For Anthropic and OpenAI, use ModelRegistry
    models = ModelRegistry.get_models_for_provider(provider)
    
    sorted_models = sorted(models.items(), key=lambda x: x[1].cost_per_1m_input)
    
    for model_id, info in sorted_models:
        click.echo(f"• {info.display_name} ({info.released})")
        click.echo(f"  {info.description}")
        click.echo(f"  Cost: ${info.cost_per_1m_input:.2f}/${info.cost_per_1m_output:.2f} per 1M tokens")
        click.echo(f"  Best for: {', '.join(info.recommended_for)}")
        click.echo()


def display_clarification(clarification: str) -> None:
    """Display clarification response."""
    click.echo(style(f"\n💡 {clarification}", fg="blue"))


def display_examples(examples: str) -> None:
    """Display examples."""
    click.echo(style(f"\n📖 EXAMPLES:", fg="cyan", bold=True))
    click.echo(examples)


def display_alternatives(alternatives: str) -> None:
    """Display alternative approaches."""
    click.echo(style(f"\n🔄 ALTERNATIVE APPROACH:", fg="magenta", bold=True))
    click.echo(alternatives)


def display_config_info(config_path: str) -> None:
    """Display configuration file information."""
    click.echo(style(f"Using configuration file: {config_path}", fg="blue"))


def display_help_text() -> None:
    """Display help text for the application."""
    help_text = """
AI Shell Command Generator - Generate shell commands using AI

USAGE:
  ai-shell                    # Interactive mode
  ai-shell -q "query"         # Non-interactive mode
  ai-shell --teach            # Teaching mode
  ai-shell --list-models      # List available models

PROVIDERS:
  -p, --provider [anthropic|openai|ollama]    AI provider
  -m, --model MODEL                           Specific model to use
  -s, --shell [bash|cmd|powershell]           Shell environment

FEATURES:
  -t, --teach                                 Teaching mode with explanations
  -c, --copy                                  Auto-copy to clipboard
  --no-risk-check                             Disable risk assessment
  --list-models PROVIDER                      List models for provider

EXAMPLES:
  ai-shell -p openai -m gpt-5-mini -q "find large files"
  ai-shell --teach -p anthropic -s bash
  ai-shell --list-models openai
"""
    click.echo(help_text)
