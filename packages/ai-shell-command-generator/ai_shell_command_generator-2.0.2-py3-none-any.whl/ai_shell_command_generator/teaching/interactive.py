"""Interactive teaching loop functionality."""

import click
from typing import Optional
from .prompts import (
    build_clarification_prompt, build_alternatives_prompt, 
    build_examples_prompt, build_risk_explanation_prompt
)
from ai_shell_command_generator.cli.prompts import (
    select_teaching_option, prompt_for_clarification
)
from ai_shell_command_generator.cli.display import (
    display_clarification, display_examples, display_alternatives
)


def teaching_loop(command: str, query: str, config, provider) -> bool:
    """
    Handle the teaching/understanding loop before proceeding to copy/execute.
    Returns True if user is ready to proceed, False to cancel/retry.
    """
    while True:
        choice = select_teaching_option()
        
        if choice == 'yes':
            return True  # Proceed to copy/execute
            
        elif choice == 'no':
            return False  # Cancel this command
            
        elif choice == 'explain-more':
            # Deeper dive
            focus = prompt_for_clarification()
            
            if focus:
                # Targeted explanation of specific part
                clarification = get_command_clarification(
                    command, focus, provider
                )
                display_clarification(clarification)
            else:
                # Show practical examples
                examples = get_command_examples(command, provider)
                display_examples(examples)
            # Loop continues
            
        elif choice == 'what-if':
            # Explore variations
            variation_query = click.prompt("What if you wanted to")
            
            # Generate related command
            variation_response = generate_variation_command(
                query, variation_query, config, provider
            )
            
            if variation_response:
                display_alternatives(variation_response)
                
                # Ask if they want the original or the variation
                click.echo(style("\nWhich command would you like to use?", fg="cyan", bold=True))
                click.echo("1. Original command")
                click.echo("2. Alternative command")
                click.echo("3. Neither (keep exploring)")
                
                which_choice = click.prompt("Select option", type=click.IntRange(1, 3), default=1)
                which = {1: 'original', 2: 'alternative', 3: 'neither'}[which_choice]
                
                if which == 'alternative':
                    return True  # They can proceed with the alternative
                elif which == 'original':
                    return True  # They can proceed with the original
                # else (neither): loop continues
            else:
                click.echo("Could not generate alternative. Let's continue with the original.")
                # Loop continues


def get_command_clarification(command: str, question: str, provider) -> str:
    """Ask AI to clarify a specific part of the command."""
    prompt = build_clarification_prompt(command, question)
    
    try:
        # Use a simple prompt that all providers can handle
        # We'll use the provider's client directly for a simple text response
        from ai_shell_command_generator.providers.anthropic_provider import AnthropicProvider
        from ai_shell_command_generator.providers.openai_provider import OpenAIProvider
        from ai_shell_command_generator.providers.ollama_provider import OllamaProvider
        
        if isinstance(provider, AnthropicProvider):
            response = provider.client.messages.create(
                model=provider.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        elif isinstance(provider, OpenAIProvider):
            response = provider.client.chat.completions.create(
                model=provider.model,
                max_completion_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        elif isinstance(provider, OllamaProvider):
            response = provider.ollama.chat(
                model=provider.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content'].strip()
        else:
            return "Provider not supported for clarification"
    except Exception as e:
        return f"Could not get clarification: {str(e)}"


def get_command_examples(command: str, provider) -> str:
    """Get practical examples of using the command."""
    prompt = build_examples_prompt(command)
    
    try:
        from ai_shell_command_generator.providers.anthropic_provider import AnthropicProvider
        from ai_shell_command_generator.providers.openai_provider import OpenAIProvider
        from ai_shell_command_generator.providers.ollama_provider import OllamaProvider
        
        if isinstance(provider, AnthropicProvider):
            response = provider.client.messages.create(
                model=provider.model,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        elif isinstance(provider, OpenAIProvider):
            response = provider.client.chat.completions.create(
                model=provider.model,
                max_completion_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        elif isinstance(provider, OllamaProvider):
            response = provider.ollama.chat(
                model=provider.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content'].strip()
        else:
            return "Provider not supported for examples"
    except Exception as e:
        return f"Could not get examples: {str(e)}"


def get_command_alternatives(command: str, query: str, provider) -> str:
    """Get alternative approaches to the command."""
    prompt = build_alternatives_prompt(command, query)
    
    try:
        from ai_shell_command_generator.providers.anthropic_provider import AnthropicProvider
        from ai_shell_command_generator.providers.openai_provider import OpenAIProvider
        from ai_shell_command_generator.providers.ollama_provider import OllamaProvider
        
        if isinstance(provider, AnthropicProvider):
            response = provider.client.messages.create(
                model=provider.model,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        elif isinstance(provider, OpenAIProvider):
            response = provider.client.chat.completions.create(
                model=provider.model,
                max_completion_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        elif isinstance(provider, OllamaProvider):
            response = provider.ollama.chat(
                model=provider.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content'].strip()
        else:
            return "Provider not supported for alternatives"
    except Exception as e:
        return f"Could not get alternatives: {str(e)}"


def generate_variation_command(original_query: str, variation_query: str, config, provider) -> Optional[str]:
    """Generate a variation of the original command."""
    combined_query = f"{original_query} but {variation_query}"
    
    try:
        from ai_shell_command_generator.core.os_detection import get_os_info
        os_info = get_os_info()
        
        if config.teach_mode:
            # Generate teaching response for variation
            teaching_response = provider.generate_teaching_response(combined_query, config.shell, os_info)
            return teaching_response.get('command', '')
        else:
            # Generate simple command
            return provider.generate_command(combined_query, config.shell, os_info)
    except Exception as e:
        click.echo(f"Could not generate variation: {str(e)}")
        return None


def explain_risk_in_detail(command: str, risk_info: dict, provider) -> str:
    """Get detailed explanation of command risks."""
    prompt = build_risk_explanation_prompt(command, risk_info)
    
    try:
        if hasattr(provider, 'client') and hasattr(provider.client, 'messages'):
            # Anthropic-style client
            response = provider.client.messages.create(
                model=provider.model,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        else:
            # Ollama-style client
            response = provider.ollama.chat(
                model=provider.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content'].strip()
    except Exception as e:
        return f"Could not explain risks: {str(e)}"
