"""Teaching mode functionality."""

from ai_shell_command_generator.teaching.prompts import build_teaching_prompt, build_clarification_prompt
from ai_shell_command_generator.teaching.formatter import parse_teaching_response, format_teaching_output
from ai_shell_command_generator.teaching.interactive import teaching_loop

__all__ = [
    'build_teaching_prompt',
    'build_clarification_prompt', 
    'parse_teaching_response',
    'format_teaching_output',
    'teaching_loop'
]
