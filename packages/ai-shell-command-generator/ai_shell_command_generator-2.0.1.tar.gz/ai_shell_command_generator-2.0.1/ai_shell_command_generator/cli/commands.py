"""Click command definitions."""

import click
from typing import Optional
from ai_shell_command_generator.core.config import CommandConfig
from ai_shell_command_generator.providers.factory import ProviderFactory
from ai_shell_command_generator.core.os_detection import get_os_info
from ai_shell_command_generator.cli.prompts import (
    select_provider_and_model, select_shell, prompt_for_query,
    confirm_copy, select_teaching_option_initial, select_teaching_option,
    confirm_explain, prompt_for_clarification
)
from ai_shell_command_generator.cli.display import (
    display_command, display_risk_warning, display_provider_info,
    display_command_for_copy, display_models_list, display_help_text,
    display_teaching_output, display_clarification, display_examples,
    display_alternatives, display_success, display_error
)
from ai_shell_command_generator.utils.clipboard import copy_to_clipboard
from ai_shell_command_generator.teaching.interactive import teaching_loop


@click.command()
@click.option('--provider', '-p', type=click.Choice(['anthropic', 'openai', 'ollama'], case_sensitive=False), 
              help='AI provider to use (anthropic, openai, or ollama)')
@click.option('--shell', '-s', type=click.Choice(['cmd', 'powershell', 'bash'], case_sensitive=False),
              help='Shell environment (cmd, powershell, or bash)')
@click.option('--query', '-q', type=str, help='Command query (non-interactive mode)')
@click.option('--model', '-m', type=str, help='Specific model to use (default: provider default)')
@click.option('--no-risk-check', is_flag=True, help='Disable risk assessment of generated commands')
@click.option('--copy', '-c', is_flag=True, help='Automatically copy command to clipboard')
@click.option('--teach', '-t', is_flag=True, help='Teaching mode with explanations')
@click.option('--list-models', type=click.Choice(['anthropic', 'openai', 'ollama'], case_sensitive=False),
              help='List available models for provider')
@click.option('--config', type=str, help='Path to configuration file')
@click.option('--show-config', is_flag=True, help='Show current configuration')
@click.help_option('-h', '--help')
def main(provider, shell, query, model, no_risk_check, copy, teach, list_models, config, show_config):
    """AI Shell Command Generator - Generate shell commands using AI."""
    
    try:
        # Handle list models command
        if list_models:
            display_models_list(list_models)
            return
        
        # Handle show config command
        if show_config:
            # TODO: Implement show config
            click.echo("Configuration display not yet implemented")
            return
        
        # Create configuration
        config_obj = CommandConfig.from_cli_args(
            provider=provider,
            shell=shell,
            query=query,
            model=model,
            no_risk_check=no_risk_check,
            copy=copy,
            teach=teach
        )
        
        # Load from config file if specified
        if config:
            # TODO: Load from config file
            pass
        
        # Validate configuration
        config_obj.validate()
        
        # Merge with environment variables
        config_obj = config_obj.merge_with_env()
        
        # Handle non-interactive mode
        if query:
            run_non_interactive_mode(config_obj, query)
        else:
            run_interactive_mode(config_obj)
            
    except Exception as e:
        display_error(f"Error: {str(e)}")
        raise click.Abort()


def run_non_interactive_mode(config: CommandConfig, query: str) -> None:
    """Run in non-interactive mode."""
    # Create provider
    provider = ProviderFactory.create_provider(
        config.provider,
        model=config.model,
        api_key=config.get_api_key(config.provider)
    )
    
    # Display provider info
    display_provider_info(config.provider, config.model)
    
    # Generate command
    os_info = get_os_info()
    
    if config.teach_mode:
        # Teaching mode
        teaching_response = provider.generate_teaching_response(query, config.shell, os_info)
        display_teaching_output(teaching_response)
        command = teaching_response.get('command', '')
    else:
        # Normal mode
        command = provider.generate_command(query, config.shell, os_info)
        display_command(command)
        
        # Risk assessment
        if config.risk_check:
            risk_info = provider.assess_risk(command, config.shell)
            display_risk_warning(risk_info, detailed=False)
    
    # Auto-copy if requested
    if config.auto_copy:
        if copy_to_clipboard(command):
            display_success("Command copied to clipboard!")
        else:
            display_error("Failed to copy to clipboard")
    
    # Print command for stdout (for piping)
    click.echo(command)


def run_interactive_mode(config: CommandConfig) -> None:
    """Run in interactive mode."""
    # Interactive setup if not provided
    if not config.provider:
        config.provider, config.model = select_provider_and_model()
    
    if not config.shell:
        # Import the new confirmation function
        from ai_shell_command_generator.cli.prompts import confirm_shell_selection
        config.shell = confirm_shell_selection()
    
    # Create provider
    provider = ProviderFactory.create_provider(
        config.provider,
        model=config.model,
        api_key=config.get_api_key(config.provider)
    )
    
    # Display provider info
    display_provider_info(config.provider, config.model)
    
    # Main interactive loop
    while True:
        try:
            query = prompt_for_query()
            if query.lower() in ['quit', 'exit', 'q', 'x']:
                break
            
            # Generate command
            os_info = get_os_info()
            
            if config.teach_mode:
                # Teaching mode
                teaching_response = provider.generate_teaching_response(query, config.shell, os_info)
                display_teaching_output(teaching_response)
                command = teaching_response.get('command', '')
                
                # Teaching interaction loop
                ready = teaching_loop(
                    command, query, config, provider
                )
                
                if ready:
                    # Proceed to copy
                    if config.auto_copy:
                        if copy_to_clipboard(command):
                            display_success("Command copied to clipboard!")
                    elif confirm_copy():
                        if copy_to_clipboard(command):
                            display_success("Command copied to clipboard!")
                        else:
                            display_error("Failed to copy to clipboard")
                else:
                    click.echo("Let's try something different.")
                
            else:
                # Normal mode
                command = provider.generate_command(query, config.shell, os_info)
                display_command(command)
                
                # Risk assessment
                if config.risk_check:
                    risk_info = provider.assess_risk(command, config.shell)
                    display_risk_warning(risk_info, detailed=True)
                
                # Interactive teaching loop for normal mode
                ready = interactive_teaching_loop_normal(command, query, config, provider)
                
                if ready:
                    # Proceed to copy
                    if config.auto_copy:
                        if copy_to_clipboard(command):
                            display_success("Command copied to clipboard!")
                    elif confirm_copy():
                        if copy_to_clipboard(command):
                            display_success("Command copied to clipboard!")
                        else:
                            display_error("Failed to copy to clipboard")
                else:
                    click.echo("Let's try something different.")
                
                # Display command for copy
                display_command_for_copy(command)
                
        except KeyboardInterrupt:
            click.echo("\nExiting...")
            break
        except Exception as e:
            display_error(f"Error: {str(e)}")
            continue
        
        click.echo()  # Add spacing between commands


def interactive_teaching_loop_normal(command: str, query: str, config: CommandConfig, provider) -> bool:
    """Interactive teaching loop for normal mode."""
    while True:
        choice = select_teaching_option_initial()
        
        if choice == 'yes':
            return True
        elif choice == 'no':
            return False
        elif choice == 'explain':
            # Switch to teaching mode for this command
            os_info = get_os_info()
            teaching_response = provider.generate_teaching_response(query, config.shell, os_info)
            display_teaching_output(teaching_response)
            config.teach_mode = True  # Switch to teach mode
            
            # Continue with teaching loop
            return teaching_loop(
                teaching_response.get('command', command), query, config, provider
            )
    
    return True
