"""Teaching response formatting utilities."""

from typing import Dict, List


def parse_teaching_response(response_text: str) -> Dict:
    """
    Parse teaching response into structured format.
    Handles both structured (COMMAND:/BREAKDOWN:) and unstructured responses.
    Also handles markdown formatting (**COMMAND:** or `COMMAND:`).
    """
    sections = {
        'command': '',
        'breakdown': '',
        'os_notes': '',
        'safer_approach': '',
        'learned': []
    }
    
    # If response is empty, return empty sections
    if not response_text or not response_text.strip():
        return sections
    
    current_section = None
    current_content = []
    
    lines = response_text.split('\n')
    
    for line in lines:
        stripped_line = line.strip()
        
        # Remove markdown formatting from line for checking
        clean_line = stripped_line.replace('**', '').replace('`', '').strip()
        
        # Skip markdown code block markers
        if clean_line in ['bash', 'sh', 'shell', '']:
            continue
        
        # Check for section headers (case-insensitive, with markdown support)
        if clean_line.upper().startswith('COMMAND:'):
            if current_section and current_content:
                _save_section(sections, current_section, current_content)
            current_section = 'command'
            current_content = []
            # Capture content on same line as header
            if ':' in clean_line:
                content_after_header = clean_line.split(':', 1)[1].strip()
                if content_after_header:
                    current_content.append(content_after_header)
                
        elif clean_line.upper().startswith('BREAKDOWN:'):
            if current_section and current_content:
                _save_section(sections, current_section, current_content)
            current_section = 'breakdown'
            current_content = []
            
        elif clean_line.upper().startswith('OS NOTES:'):
            if current_section and current_content:
                _save_section(sections, current_section, current_content)
            current_section = 'os_notes'
            current_content = []
            
        elif clean_line.upper().startswith('SAFER APPROACH:'):
            if current_section and current_content:
                _save_section(sections, current_section, current_content)
            current_section = 'safer_approach'
            current_content = []
            
        elif clean_line.upper().startswith('WHAT YOU LEARNED:') or clean_line.upper().startswith('KEY CONCEPTS:'):
            if current_section and current_content:
                _save_section(sections, current_section, current_content)
            current_section = 'learned'
            current_content = []
            
        elif current_section:
            # Add line to current section (preserve original formatting but clean markdown)
            if line.strip() and not line.strip().startswith('```'):
                # Remove markdown bold/italic but keep content
                cleaned = line.replace('**', '').replace('`', '')
                if cleaned.strip():
                    current_content.append(cleaned)
    
    # Handle the last section
    if current_section and current_content:
        _save_section(sections, current_section, current_content)
    
    # If no structured sections found, treat entire response as breakdown
    if not any(sections.values()):
        sections['breakdown'] = response_text.strip()
    
    return sections


def _save_section(sections: Dict, section_name: str, content: List[str]) -> None:
    """Helper to save a section's content."""
    if section_name == 'learned':
        # Parse bullet points for learned section
        sections[section_name] = [
            item.lstrip('•-*').strip() 
            for item in content 
            if item.strip() and not item.strip().startswith('#')
        ]
    else:
        # Join lines preserving some formatting
        sections[section_name] = '\n'.join(content).strip()


def format_teaching_output(sections: Dict) -> str:
    """Format teaching sections into display string."""
    output = []
    
    if sections.get('command'):
        output.append(f"COMMAND:\n  {sections['command']}")
    
    if sections.get('breakdown'):
        output.append(f"\nBREAKDOWN:\n{sections['breakdown']}")
    
    if sections.get('os_notes'):
        output.append(f"\nOS NOTES:\n{sections['os_notes']}")
    
    if sections.get('safer_approach'):
        output.append(f"\nSAFER APPROACH:\n{sections['safer_approach']}")
    
    if sections.get('learned'):
        output.append(f"\nWHAT YOU LEARNED:")
        for point in sections['learned']:
            output.append(f"  ✓ {point}")
    
    return '\n'.join(output)


def format_command_breakdown(command: str, explanation: str) -> str:
    """Format command breakdown with proper indentation."""
    lines = []
    lines.append(f"COMMAND: {command}")
    lines.append("")
    lines.append("BREAKDOWN:")
    
    for line in explanation.split('\n'):
        if line.strip():
            lines.append(f"  {line}")
    
    return '\n'.join(lines)


def format_learning_points(points: List[str]) -> str:
    """Format learning points as bullet list."""
    formatted_points = []
    for point in points:
        formatted_points.append(f"  ✓ {point}")
    return '\n'.join(formatted_points)


def format_alternatives(alternatives: str) -> str:
    """Format alternative approaches."""
    return f"ALTERNATIVE APPROACHES:\n{alternatives}"


def format_examples(examples: str) -> str:
    """Format examples section."""
    return f"EXAMPLES:\n{examples}"


def format_clarification(question: str, answer: str) -> str:
    """Format clarification Q&A."""
    return f"Q: {question}\nA: {answer}"
