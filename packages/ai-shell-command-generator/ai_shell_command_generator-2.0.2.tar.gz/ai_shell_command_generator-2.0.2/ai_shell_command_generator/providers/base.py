"""Base provider interface for AI providers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseProvider(ABC):
    """Base class for all AI providers."""
    
    def __init__(self, model: str, **kwargs):
        """
        Initialize the provider.
        
        Args:
            model: The model name to use
            **kwargs: Additional provider-specific arguments
        """
        self.model = model
        self.kwargs = kwargs
    
    @abstractmethod
    def generate_command(self, query: str, shell: str, os_info: str) -> str:
        """
        Generate a shell command.
        
        Args:
            query: The user's command query
            shell: The shell environment (bash, cmd, powershell)
            os_info: OS-specific information
            
        Returns:
            The generated command
        """
        pass
    
    @abstractmethod
    def generate_teaching_response(self, query: str, shell: str, os_info: str) -> Dict:
        """
        Generate command with teaching explanation.
        
        Args:
            query: The user's command query
            shell: The shell environment
            os_info: OS-specific information
            
        Returns:
            Dictionary with command and teaching sections
        """
        pass
    
    @abstractmethod
    def assess_risk(self, command: str, shell: str) -> Dict:
        """
        Assess command risk.
        
        Args:
            command: The command to assess
            shell: The shell environment
            
        Returns:
            Dictionary with risk assessment
        """
        pass
    
    @abstractmethod
    def list_available_models(self) -> List[str]:
        """
        List available models for this provider.
        
        Returns:
            List of model names
        """
        pass
    
    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        """Whether this provider requires an API key."""
        pass
    
    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether this provider supports streaming responses."""
        pass
    
    def _clean_command(self, command: str) -> str:
        """
        Clean up command output - only remove markdown formatting.
        
        Args:
            command: Raw command from AI
            
        Returns:
            Cleaned command
        """
        command = command.strip()
        
        # Remove markdown code blocks if present
        if command.startswith('```'):
            lines = command.split('\n')
            # Remove first line (```bash or similar) and last line (```)
            if len(lines) > 2:
                command = '\n'.join(lines[1:-1])
            command = command.strip()
        
        return command
