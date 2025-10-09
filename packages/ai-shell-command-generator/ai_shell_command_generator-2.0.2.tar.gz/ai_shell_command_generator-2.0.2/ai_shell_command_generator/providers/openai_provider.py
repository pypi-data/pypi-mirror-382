"""OpenAI GPT-5 provider implementation."""

import os
import json
from typing import Dict, List, Optional
from ai_shell_command_generator.providers.base import BaseProvider
from ai_shell_command_generator.providers.models import ModelRegistry


class OpenAIProvider(BaseProvider):
    """OpenAI GPT-5 API provider."""
    
    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        """
        Initialize OpenAI provider.
        
        Args:
            model: The GPT model to use
            api_key: OpenAI API key (optional, can use env var)
            **kwargs: Additional arguments
        """
        super().__init__(model, **kwargs)
        
        # Validate model
        if not ModelRegistry.is_valid_model('openai', model):
            raise ValueError(f"Invalid OpenAI model: {model}")
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # If no key found, prompt user interactively
        if not self.api_key:
            try:
                from ai_shell_command_generator.cli.prompts import prompt_for_api_key
                prompted_key = prompt_for_api_key('openai')
                if prompted_key:
                    self.api_key = prompted_key
                    # Set in environment for this session
                    os.environ['OPENAI_API_KEY'] = prompted_key
                else:
                    raise ValueError("OpenAI API key required but not provided")
            except ImportError:
                # If prompts not available (testing?), raise error
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        # Initialize client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI provider requires openai package. Install with: pip install openai")
    
    def generate_command(self, query: str, shell: str, os_info: str) -> str:
        """Generate command using OpenAI."""
        # Build system message
        if shell == 'cmd':
            system_msg = "You are a Windows CMD.EXE command generator. Output ONLY the command, nothing else."
        elif shell == 'powershell':
            system_msg = "You are a Windows PowerShell command generator. Output ONLY the command, nothing else."
        else:
            system_msg = f"You are a {os_info} shell command generator. Output ONLY the command, nothing else."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=2000,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": query}
                ]
            )
            
            if not response.choices or not response.choices[0].message.content:
                return f"echo 'OpenAI returned empty response'"
            
            command = response.choices[0].message.content.strip()
            if not command:
                return f"echo 'OpenAI returned empty command'"
            
            return self._clean_command(command)
        except Exception as e:
            return f"echo 'Error generating command with OpenAI: {str(e)}'"
    
    def generate_teaching_response(self, query: str, shell: str, os_info: str) -> Dict:
        """Generate command with teaching explanation."""
        if shell == 'cmd':
            shell_desc = "Windows CMD.EXE"
        elif shell == 'powershell':
            shell_desc = "Windows PowerShell"
        else:
            shell_desc = f"{os_info} shell"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=8000,
                messages=[
                    {"role": "system", "content": "You are a shell command teacher. Explain commands clearly with examples."},
                    {"role": "user", "content": f"""Generate a {shell_desc} command for: {query}

Explain it in this format:

COMMAND:
[the command]

BREAKDOWN:
[explain each part]

OS NOTES:
[platform-specific notes]

SAFER APPROACH:
[if risky, show safer alternative]

WHAT YOU LEARNED:
[3-5 key concepts]"""}
                ]
            )
            
            response_text = response.choices[0].message.content.strip()
            
            from ai_shell_command_generator.teaching.formatter import parse_teaching_response
            return parse_teaching_response(response_text)
            
        except Exception as e:
            return {
                'command': f"echo 'Error: {str(e)}'",
                'breakdown': 'Error occurred',
                'os_notes': '',
                'safer_approach': '',
                'learned': []
            }
    
    def assess_risk(self, command: str, shell: str) -> Dict:
        """Assess command risk using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=1500,
                messages=[
                    {"role": "system", "content": "You are a command safety analyzer. Respond with JSON only."},
                    {"role": "user", "content": f"""Analyze this {shell} command: {command}

Respond with JSON:
{{"is_risky": true/false, "severity": "low/medium/high", "reason": "explanation"}}"""}
                ]
            )
            result_text = response.choices[0].message.content.strip()
            return self._parse_risk_response(result_text)
        except Exception as e:
            return {'is_risky': False, 'severity': 'low', 'reason': f'Assessment failed: {e}'}
    
    def list_available_models(self) -> List[str]:
        """List available OpenAI models."""
        return list(ModelRegistry.OPENAI_MODELS.keys())
    
    @property
    def requires_api_key(self) -> bool:
        """OpenAI requires API key."""
        return True
    
    @property
    def supports_streaming(self) -> bool:
        """OpenAI supports streaming."""
        return True
    
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
