"""Ollama local AI provider implementation."""

import json
from typing import Dict, List, Optional
from ai_shell_command_generator.providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    """Ollama local AI provider."""
    
    def __init__(self, model: str, host: str = "localhost:11434", **kwargs):
        """
        Initialize Ollama provider.
        
        Args:
            model: The Ollama model to use
            host: Ollama host address
            **kwargs: Additional arguments
        """
        super().__init__(model, **kwargs)
        self.host = host
        
        # Initialize ollama client
        try:
            import ollama
            self.ollama = ollama
        except ImportError:
            raise ImportError("Ollama provider requires ollama package. Install with: pip install ollama")
    
    def generate_command(self, query: str, shell: str, os_info: str) -> str:
        """Generate command using Ollama."""
        prompt = self._build_command_prompt(query, shell, os_info)
        
        try:
            response = self.ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            command = response['message']['content'].strip()
            return self._clean_command(command)
        except Exception as e:
            return f"echo 'Error connecting to Ollama: {str(e)}'"
    
    def generate_teaching_response(self, query: str, shell: str, os_info: str) -> Dict:
        """Generate command with teaching explanation."""
        prompt = self._build_teaching_prompt(query, shell, os_info)
        
        try:
            response = self.ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response['message']['content'].strip()
            
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
        """Assess command risk using Ollama."""
        risk_prompt = self._build_risk_prompt(command, shell)
        
        try:
            response = self.ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": risk_prompt}]
            )
            result_text = response['message']['content'].strip()
            return self._parse_risk_response(result_text)
        except Exception as e:
            return {'is_risky': False, 'severity': 'low', 'reason': f'Assessment failed: {e}'}
    
    def list_available_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            models = self.ollama.list()
            if models and models.models:
                return [model.model for model in models.models]
            return []
        except Exception:
            return []
    
    @property
    def requires_api_key(self) -> bool:
        """Ollama doesn't require API key."""
        return False
    
    @property
    def supports_streaming(self) -> bool:
        """Ollama supports streaming."""
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
