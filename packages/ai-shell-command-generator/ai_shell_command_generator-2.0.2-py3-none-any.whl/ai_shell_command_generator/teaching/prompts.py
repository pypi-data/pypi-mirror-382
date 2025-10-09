"""Teaching-specific AI prompts."""


def build_teaching_prompt(query: str, shell: str, os_info: str) -> str:
    """Build prompt for teaching mode command generation."""
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


def build_clarification_prompt(command: str, question: str) -> str:
    """Build prompt for clarifying a specific part of a command."""
    return f"""The user is learning about this command: {command}

They need clarification on: {question}

Provide a brief, clear explanation (2-3 sentences) focused on their question.
Use simple language and give practical examples if helpful."""


def build_alternatives_prompt(command: str, query: str = "") -> str:
    """Build prompt for showing alternative approaches."""
    context = f" (original goal: {query})" if query else ""
    return f"""Show 2-3 alternative ways to accomplish the same goal as this command: {command}{context}

For each alternative:
- Show the command
- Explain when to use it
- Highlight key differences

Keep it concise and practical."""


def build_examples_prompt(command: str) -> str:
    """Build prompt for showing practical examples."""
    return f"""Provide 2-3 practical examples of using this command: {command}

Show variations with different options and explain when to use each.
Format as:
Example 1: [command variation]
  Use when: [scenario]
  
Keep it concise."""


def build_risk_explanation_prompt(command: str, risk_info: dict) -> str:
    """Build prompt for explaining risks in detail."""
    severity = risk_info.get('severity', 'medium')
    reason = risk_info.get('reason', 'Unknown risk')
    
    return f"""Explain this command's risk in detail: {command}

Risk Level: {severity.upper()}
Reason: {reason}

Provide:
1. What makes this command risky
2. What could go wrong
3. How to make it safer
4. Alternative approaches

Keep it educational and helpful."""
