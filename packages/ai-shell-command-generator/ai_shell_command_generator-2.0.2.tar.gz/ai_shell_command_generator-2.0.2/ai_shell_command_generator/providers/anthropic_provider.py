"""Anthropic Claude provider implementation."""

import os
import json
from typing import Dict, List, Optional
from ai_shell_command_generator.providers.base import BaseProvider
from ai_shell_command_generator.providers.models import ModelRegistry


class AnthropicProvider(BaseProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Anthropic provider.
        
        Args:
            model: The Claude model to use
            api_key: Anthropic API key (optional, can use env var)
            **kwargs: Additional arguments
        """
        super().__init__(model, **kwargs)
        
        # Validate model
        if not ModelRegistry.is_valid_model('anthropic', model):
            raise ValueError(f"Invalid Anthropic model: {model}")
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        # If no key found, prompt user interactively
        if not self.api_key:
            try:
                from ai_shell_command_generator.cli.prompts import prompt_for_api_key
                prompted_key = prompt_for_api_key('anthropic')
                if prompted_key:
                    self.api_key = prompted_key
                    # Set in environment for this session
                    os.environ['ANTHROPIC_API_KEY'] = prompted_key
                else:
                    raise ValueError("Anthropic API key required but not provided")
            except ImportError:
                # If prompts not available (testing?), raise error
                raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        
        # Initialize client
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic provider requires anthropic package. Install with: pip install anthropic")
    
    def generate_command(self, query: str, shell: str, os_info: str) -> str:
        """Generate command using Anthropic Claude."""
        prompt = self._build_command_prompt(query, shell, os_info)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            command = response.content[0].text.strip()
            return self._clean_command(command)
        except Exception as e:
            return f"echo 'Error generating command with Anthropic: {str(e)}'"
    
    def generate_teaching_response(self, query: str, shell: str, os_info: str) -> Dict:
        """Generate command with teaching explanation."""
        prompt = self._build_teaching_prompt(query, shell, os_info)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,  # More tokens for teaching content
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.content[0].text.strip()
            
            # Use the shared parser from teaching.formatter
            from ai_shell_command_generator.teaching.formatter import parse_teaching_response
            return parse_teaching_response(response_text)
            
        except Exception as e:
            return {
                'command': f"echo 'Error generating teaching response: {str(e)}'",
                'breakdown': 'Error occurred during generation',
                'os_notes': '',
                'safer_approach': '',
                'learned': []
            }
    
    def assess_risk(self, command: str, shell: str) -> Dict:
        """Assess command risk using Anthropic."""
        risk_prompt = self._build_risk_prompt(command, shell)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": risk_prompt}]
            )
            result_text = response.content[0].text.strip()
            return self._parse_risk_response(result_text)
        except Exception as e:
            return {'is_risky': False, 'severity': 'low', 'reason': f'Assessment failed: {e}'}
    
    def list_available_models(self) -> List[str]:
        """List available Anthropic models."""
        return list(ModelRegistry.ANTHROPIC_MODELS.keys())
    
    @property
    def requires_api_key(self) -> bool:
        """Anthropic requires API key."""
        return True
    
    @property
    def supports_streaming(self) -> bool:
        """Anthropic supports streaming."""
        return True
    
    def _build_command_prompt(self, query: str, shell: str, os_info: str) -> str:
        """Build prompt for command generation."""
        if shell == 'cmd':
            shell_desc = "Windows CMD.EXE batch command"
        elif shell == 'powershell':
            shell_desc = "Windows PowerShell command"
        else:
            shell_desc = f"{os_info} shell command"
        
        return f"""Generate a {shell_desc} for this task: {query}

Return ONLY the command, without any explanation or markdown formatting."""
    
    def _build_teaching_prompt(self, query: str, shell: str, os_info: str) -> str:
        """Build prompt for teaching response."""
        return f"""Generate a {shell} command for {os_info} that: {query}

Format your response as follows:

COMMAND:
[the exact command to run]

BREAKDOWN:
[explain each part of the command with proper indentation]

OS NOTES:
[platform-specific considerations for {os_info}]
[BSD vs GNU differences if relevant]
[any gotchas or limitations]

SAFER APPROACH:
[if the command is risky, show a safer alternative or preview step]

WHAT YOU LEARNED:
[key concepts from this command - 3-5 bullet points]

Be concise but clear. Teach the user to understand, not just copy."""
    
    def _build_risk_prompt(self, command: str, shell: str) -> str:
        """Build prompt for risk assessment."""
        return f"""Analyze this {shell} command for potential risks:

Command: {command}

Respond ONLY with a JSON object in this exact format:
{{"is_risky": true/false, "severity": "low/medium/high", "reason": "brief explanation"}}

Consider risks like: data deletion (rm, dd), permission changes (chmod, chown), 
system modifications, network exposure, recursive operations, etc."""
    
    def _parse_risk_response(self, response_text: str) -> Dict:
        """Parse risk assessment response."""
        try:
            # Extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                json_text = response_text[start:end]
                return json.loads(json_text)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Fallback parsing
        return {'is_risky': False, 'severity': 'low', 'reason': 'Could not parse risk assessment'}
