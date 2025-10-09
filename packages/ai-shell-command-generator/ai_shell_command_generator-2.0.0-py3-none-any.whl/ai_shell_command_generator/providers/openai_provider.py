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
        prompt = self._build_command_prompt(query, shell, os_info)
        
        try:
            # Use max_completion_tokens for newer models
            # GPT-5 models use reasoning tokens, so we need more total tokens
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=2000,  # Increased to account for reasoning + output
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Check if we got a valid response
            if not response.choices or not response.choices[0].message.content:
                return f"echo 'OpenAI returned empty response'"
            
            command = response.choices[0].message.content.strip()
            
            # If command is empty after stripping, return error
            if not command:
                return f"echo 'OpenAI returned empty command'"
            
            return self._clean_command(command)
        except Exception as e:
            return f"echo 'Error generating command with OpenAI: {str(e)}'"
    
    def generate_teaching_response(self, query: str, shell: str, os_info: str) -> Dict:
        """Generate command with teaching explanation."""
        prompt = self._build_teaching_prompt(query, shell, os_info)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=4000,  # More tokens for teaching content + reasoning
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.choices[0].message.content.strip()
            
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
        """Assess command risk using OpenAI."""
        risk_prompt = self._build_risk_prompt(command, shell)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=1000,  # Account for reasoning + JSON output
                messages=[{"role": "user", "content": risk_prompt}]
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
    
    def _build_command_prompt(self, query: str, shell: str, os_info: str) -> str:
        """Build prompt for command generation."""
        # Make shell instructions VERY explicit
        if shell == 'cmd':
            shell_instruction = """Windows Command Prompt (CMD.EXE) batch command.

CRITICAL: Use ONLY Windows CMD/DOS syntax:
- Use 'dir' NOT 'ls'
- Use 'copy' NOT 'cp'  
- Use 'del' NOT 'rm'
- Use 'move' NOT 'mv'
- Use '%USERPROFILE%' NOT '~'
- Use backslashes '\\' NOT forward slashes '/'
- This is NOT bash, NOT Unix, NOT PowerShell"""
        
        elif shell == 'powershell':
            shell_instruction = """Windows PowerShell command.

Use PowerShell cmdlets and syntax:
- Use 'Get-ChildItem' (or 'gci', 'ls') NOT bash ls
- Use 'Copy-Item' NOT bash cp
- Use 'Remove-Item' NOT bash rm
- Use '$env:USERPROFILE' or '$HOME' for home directory
- Use PowerShell pipeline and object syntax"""
        
        else:  # bash
            shell_instruction = f"Bash/sh shell command for {os_info}"
        
        return f"""{shell_instruction}

Task: {query}

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
