import os
import platform
import click
import pyperclip
from dotenv import load_dotenv
from anthropic import Anthropic
from click import style
import ollama

__version__ = "1.0.0"

load_dotenv()  # Load environment variables from .env file

def get_os_info():
    """Get OS information for command generation context."""
    system = platform.system()
    if system == 'Darwin':
        return 'macOS (use BSD-compatible tools, avoid GNU-specific flags like -printf)'
    elif system == 'Linux':
        return 'Linux (GNU tools available)'
    elif system == 'Windows':
        return 'Windows'
    else:
        return system

def select_shell(shells=['cmd', 'powershell', 'bash'], input_func=click.prompt):
    """
    Prompts the user to select their preferred shell environment from a list of options.
    
    Args:
        shells (list): List of available shells.
        input_func (function): Function to use for user input (for testing purposes).
    
    Returns:
        str: The selected shell environment.
    """
    for i, shell in enumerate(shells, 1):
        click.echo(f"{i}. {shell}")
    while True:
        choice = input_func("Select your preferred shell environment")
        try:
            choice = int(choice)
            if 1 <= choice <= len(shells):
                return shells[choice - 1]
        except ValueError:
            pass
        click.echo("Invalid choice. Please try again.")

def select_provider(providers=['anthropic', 'ollama'], input_func=click.prompt):
    """
    Prompts the user to select their preferred AI provider.
    
    Args:
        providers (list): List of available AI providers.
        input_func (function): Function to use for user input (for testing purposes).
    
    Returns:
        str: The selected AI provider.
    """
    click.echo(style("\nSelect AI Provider:", fg="cyan", bold=True))
    for i, provider in enumerate(providers, 1):
        click.echo(f"{i}. {provider.capitalize()}")
    while True:
        choice = input_func("Select your preferred AI provider")
        try:
            choice = int(choice)
            if 1 <= choice <= len(providers):
                return providers[choice - 1]
        except ValueError:
            pass
        click.echo("Invalid choice. Please try again.")

def select_ollama_model(input_func=click.prompt):
    """
    Prompts the user to select an available Ollama model.
    
    Args:
        input_func (function): Function to use for user input (for testing purposes).
    
    Returns:
        str: The selected Ollama model name, or None if no models available.
    """
    try:
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
            choice = input_func("Select your preferred Ollama model")
            try:
                choice = int(choice)
                if 1 <= choice <= len(available_models):
                    return available_models[choice - 1]
            except ValueError:
                pass
            click.echo("Invalid choice. Please try again.")
    
    except Exception as e:
        click.echo(style(f"⚠️  Error connecting to Ollama: {str(e)}", fg="yellow"))
        click.echo("Make sure Ollama is running: ollama serve")
        return None

def generate_command_anthropic(client, shell, query) -> str:
    """
    Generate a shell command based on a user's query using the Anthropic API.
    
    Args:
        client (Anthropic): An Anthropic API client instance.
        shell (str): The user's preferred shell environment.
        query (str): The user's command query.
    
    Returns:
        str: The generated shell command.
    """
    os_info = get_os_info()
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f"Generate a valid {shell} command for {os_info} for the following query: {query}. Return ONLY the command, without any explanation."
            }
        ]
    )
    # Extract the command from the response
    command = response.content[0].text.strip()
    
    # Remove markdown code blocks if present
    if command.startswith('```'):
        lines = command.split('\n')
        command = '\n'.join(lines[1:-1]) if len(lines) > 2 else command
        command = command.strip()
    
    # Ensure the command is not empty and looks valid
    if not command or command.lower().startswith(('here', 'you can', 'to ', 'this ', 'the ')):
        command = f"echo 'Unable to generate a valid command for: {query}'"
    return command

def generate_command_ollama(model, shell, query) -> str:
    """
    Generate a shell command based on a user's query using Ollama (local AI).
    
    Args:
        model (str): The Ollama model name to use (e.g., 'gpt-oss:latest').
        shell (str): The user's preferred shell environment.
        query (str): The user's command query.
    
    Returns:
        str: The generated shell command.
    """
    os_info = get_os_info()
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a valid {shell} command for {os_info} for the following query: {query}. Return ONLY the command, without any explanation."
                }
            ]
        )
        # Extract the command from the response
        command = response['message']['content'].strip()
        
        # Remove markdown code blocks if present
        if command.startswith('```'):
            lines = command.split('\n')
            command = '\n'.join(lines[1:-1]) if len(lines) > 2 else command
            command = command.strip()
        
        # Ensure the command is not empty and looks valid
        if not command or command.lower().startswith(('here', 'you can', 'to ', 'this ', 'the ')):
            command = f"echo 'Unable to generate a valid command for: {query}'"
        return command
    except Exception as e:
        return f"echo 'Error connecting to Ollama: {str(e)}'"

def assess_command_risk(provider, client_or_model, shell, command) -> dict:
    """
    Assess if a command is risky to execute using the AI provider.
    
    Args:
        provider (str): 'anthropic' or 'ollama'
        client_or_model: Anthropic client or Ollama model name
        shell (str): Shell environment
        command (str): The command to assess
    
    Returns:
        dict: {'is_risky': bool, 'reason': str, 'severity': str}
    """
    risk_prompt = f"""Analyze this {shell} command for potential risks:

Command: {command}

Respond ONLY with a JSON object in this exact format:
{{"is_risky": true/false, "severity": "low/medium/high", "reason": "brief explanation"}}

Consider risks like: data deletion (rm, dd), permission changes (chmod, chown), 
system modifications, network exposure, recursive operations, etc."""

    try:
        if provider == 'anthropic':
            response = client_or_model.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": risk_prompt}]
            )
            result_text = response.content[0].text.strip()
        else:  # ollama
            response = ollama.chat(
                model=client_or_model,
                messages=[{"role": "user", "content": risk_prompt}]
            )
            result_text = response['message']['content'].strip()
        
        # Parse JSON response
        import json
        # Extract JSON from response (in case there's extra text)
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start != -1 and end > start:
            result_text = result_text[start:end]
        
        return json.loads(result_text)
    except Exception as e:
        # If assessment fails, default to safe
        return {'is_risky': False, 'severity': 'low', 'reason': f'Assessment failed: {e}'}

def copy_to_clipboard(text):
    pyperclip.copy(text)
    click.echo(style("Command copied to clipboard!", fg="green"))

@click.command()
@click.option('--provider', '-p', type=click.Choice(['anthropic', 'ollama'], case_sensitive=False), 
              help='AI provider to use (anthropic or ollama)')
@click.option('--shell', '-s', type=click.Choice(['cmd', 'powershell', 'bash'], case_sensitive=False),
              help='Shell environment (cmd, powershell, or bash)')
@click.option('--query', '-q', type=str, help='Command query (non-interactive mode)')
@click.option('--model', '-m', type=str, help='Specific Ollama model to use (default: gpt-oss:latest)')
@click.option('--no-risk-check', is_flag=True, help='Disable risk assessment of generated commands')
@click.option('--copy', '-c', is_flag=True, help='Automatically copy command to clipboard')
def main(provider, shell, query, model, no_risk_check, copy):
    # Select AI provider (interactive if not provided)
    if not provider:
        provider = select_provider()
    
    # Select shell (interactive if not provided)
    if not shell:
        shell = select_shell()
    
    # Initialize the appropriate client based on provider
    client = None
    ollama_model = None
    
    if provider == 'anthropic':
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        client = Anthropic(api_key=api_key)
        click.echo(style(f"\nShell Command Generator initialized with Anthropic Claude for {shell}.", fg="green", bold=True))
    else:  # ollama
        # Use provided model or detect available models
        if model:
            # Model explicitly provided via command line
            ollama_model = model
            click.echo(style(f"\nShell Command Generator initialized with Ollama ({ollama_model}) for {shell}.", fg="green", bold=True))
        elif query:
            # Non-interactive mode without explicit model: auto-detect
            try:
                models = ollama.list()
                available_models = [m.model for m in models.models]
                if 'gpt-oss:latest' in available_models:
                    ollama_model = 'gpt-oss:latest'
                elif any('gpt-oss' in m for m in available_models):
                    ollama_model = next(m for m in available_models if 'gpt-oss' in m)
                else:
                    # Fallback to first available model
                    ollama_model = available_models[0] if available_models else 'gpt-oss:latest'
                click.echo(style(f"\nShell Command Generator initialized with Ollama ({ollama_model}) for {shell}.", fg="green", bold=True))
            except Exception as e:
                click.echo(style(f"Warning: Could not list Ollama models: {e}", fg="yellow"))
                ollama_model = 'gpt-oss:latest'
                click.echo(style(f"Using default model: {ollama_model}", fg="yellow"))
        else:
            # Interactive mode without explicit model: let user select
            ollama_model = select_ollama_model()
            if not ollama_model:
                click.echo(style("Cannot proceed without a model. Exiting.", fg="red"))
                return
            click.echo(style(f"\nShell Command Generator initialized with Ollama ({ollama_model}) for {shell}.", fg="green", bold=True))
    
    # Non-interactive mode: process single query and exit
    if query:
        # Generate command based on provider
        if provider == 'anthropic':
            command = generate_command_anthropic(client, shell, query)
        else:  # ollama
            command = generate_command_ollama(ollama_model, shell, query)
        
        # Assess command risk even in non-interactive mode (unless disabled)
        if not no_risk_check:
            risk_assessment = assess_command_risk(
                provider,
                client if provider == 'anthropic' else ollama_model,
                shell,
                command
            )
            
            # Show warning to stderr if risky (so command on stdout is clean for piping)
            if risk_assessment.get('is_risky', False):
                severity = risk_assessment.get('severity', 'medium')
                reason = risk_assessment.get('reason', 'Unknown risk')
                click.echo(style(f"# WARNING: {severity.upper()} risk - {reason}", fg="red", bold=True), err=True)
        
        # Auto-copy to clipboard if requested
        if copy:
            pyperclip.copy(command)
            click.echo("# Command copied to clipboard!", err=True)
        
        # In non-interactive mode, just print the command to stdout
        click.echo(command)
        return
    
    # Interactive mode: command generation loop
    while True:
        user_query = click.prompt(style("Enter your command query (or 'x' to quit)", fg="cyan"))
        if user_query.lower() == 'x':
            break
        
        # Generate command based on provider
        if provider == 'anthropic':
            command = generate_command_anthropic(client, shell, user_query)
        else:  # ollama
            command = generate_command_ollama(ollama_model, shell, user_query)
        
        click.echo(style(f"\nGenerated command for {shell}:", fg="yellow", bold=True))
        click.echo(style(command, fg="green"))  # Print the command with green styling
        
        # Assess command risk (unless disabled)
        if not no_risk_check:
            risk_assessment = assess_command_risk(
                provider, 
                client if provider == 'anthropic' else ollama_model,
                shell,
                command
            )
            
            # Show warning if risky
            if risk_assessment.get('is_risky', False):
                severity = risk_assessment.get('severity', 'medium')
                reason = risk_assessment.get('reason', 'Unknown risk')
                
                if severity == 'high':
                    icon = '⚠️  DANGER'
                elif severity == 'medium':
                    icon = '⚠️  WARNING'
                else:
                    icon = '⚠️  CAUTION'
                
                click.echo()
                click.echo(style(f"{icon}: This command may be risky!", fg="red", bold=True))
                click.echo(style(f"Risk level: {severity.upper()}", fg="red"))
                click.echo(style(f"Reason: {reason}", fg="red"))
                click.echo()
        
        # Auto-copy if flag is set, otherwise prompt
        if copy:
            copy_to_clipboard(command)
        elif click.confirm(style("Do you want to copy this command to clipboard?", fg="cyan")):
            copy_to_clipboard(command)
        
        click.echo(style("\nCommand (for easy copy-paste):", fg="cyan"))
        click.echo(command)  # Print the command again without styling for easy copy-paste
        
        click.echo()  # Add an empty line for better readability

    click.echo(style("Exiting Shell Command Generator.", fg="red", bold=True))

if __name__ == "__main__":
    main()
