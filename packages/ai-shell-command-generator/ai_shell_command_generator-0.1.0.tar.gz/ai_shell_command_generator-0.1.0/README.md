# AI Shell Command Generator

[![PyPI version](https://badge.fury.io/py/ai-shell-command-generator.svg)](https://badge.fury.io/py/ai-shell-command-generator)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI-powered shell command generator that creates accurate shell commands from natural language descriptions. Supports both cloud-based AI (Anthropic Claude) and local AI models (Ollama), with intelligent risk assessment and OS-aware command generation.

## ✨ Features

### 🤖 Dual AI Provider Support
- **Anthropic Claude 3.5 Haiku** - Fast, cloud-based AI for reliable command generation
- **Ollama Integration** - Use local models like OpenAI's gpt-oss, Qwen, DeepSeek, and more
- **Interactive Model Selection** - Discover and choose from available Ollama models
- Automatic model detection and fallback

### 🖥️ OS-Aware Command Generation
- Auto-detects macOS, Linux, and Windows
- Generates BSD vs GNU compatible commands
- Prevents platform-specific errors (e.g., avoids GNU `-printf` on macOS)

### ⚠️ AI-Powered Risk Assessment
- Analyzes every generated command for potential risks
- Color-coded warnings for dangerous operations
- Identifies data deletion, permission changes, system modifications, and more
- Can be disabled with `--no-risk-check` flag

### 💻 Flexible Usage Modes
- **Interactive Mode** - Guided command generation with safety prompts
- **Non-Interactive Mode** - Perfect for scripting and automation
- **Auto-Copy** - Automatically copy commands to clipboard

### 🛡️ Safety Features
- All warnings displayed in red for high visibility
- Risk levels: HIGH, MEDIUM, LOW
- Detailed explanations of potential dangers
- Optional risk assessment bypass for trusted automation

## 🚀 Installation

### From PyPI (Recommended)
```bash
pip install ai-shell-command-generator
```

### From Source
```bash
git clone https://github.com/codingthefuturewithai/ai-shell-command-generator.git
cd ai-shell-command-generator
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

**Requirements:** Python 3.10 or higher

### Development Setup
```bash
# Install all dependencies including test tools
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/unit/test_main.py -v
```

## ⚙️ Setup

### For Anthropic Claude (Cloud AI)
1. Get your API key from [Anthropic Console](https://console.anthropic.com/)
2. Create a `.env` file:
```bash
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

### For Ollama (Local AI)
1. Install Ollama: https://ollama.ai/
2. Pull a model (optional, defaults to gpt-oss:latest):
```bash
ollama pull gpt-oss:latest
ollama pull qwen2.5-coder:7b
ollama pull deepseek-r1:8b
```

## 📖 Usage

### Interactive Mode
```bash
ai-shell
# or
aisc
```

In interactive mode, you'll be prompted to:
1. **Select AI Provider** - Choose between Anthropic Claude or Ollama
2. **Select Shell Environment** - Choose cmd, powershell, or bash
3. **Select Ollama Model** (if using Ollama) - Choose from available models
4. **Enter Commands** - Describe what you want to do in natural language

### Non-Interactive Mode
```bash
# Basic usage
ai-shell -p anthropic -s bash -q "find all Python files modified today"

# With Ollama
ai-shell -p ollama -s bash -q "list running processes using more than 100MB RAM"

# Auto-copy to clipboard
ai-shell -p anthropic -s bash -q "backup my documents" --copy

# Use specific Ollama model
ai-shell -p ollama -m qwen2.5-coder:7b -s bash -q "analyze disk usage"

# Disable risk assessment (for automation)
ai-shell -p ollama -s bash -q "clean temp files" --no-risk-check
```

### Command Line Options
```bash
Options:
  -p, --provider [anthropic|ollama]    AI provider to use
  -s, --shell [cmd|powershell|bash]    Shell environment
  -q, --query TEXT                     Command query (non-interactive mode)
  -m, --model TEXT                     Specific Ollama model (default: gpt-oss:latest)
  --no-risk-check                      Disable risk assessment
  -c, --copy                           Automatically copy command to clipboard
  --help                               Show help message
```

## 🎯 Examples

### Safe Commands
```bash
$ ai-shell -p anthropic -s bash -q "list files in current directory"
ls

$ ai-shell -p ollama -s bash -q "show disk usage" --copy
df -h
# Command copied to clipboard!
```

### Risky Commands (with warnings)
```bash
$ ai-shell -p anthropic -s bash -q "delete all .log files"
# WARNING: HIGH risk - Recursively deletes all log files without confirmation
find . -type f -name "*.log" -delete

$ ai-shell -p ollama -s bash -q "change permissions to 777"
# WARNING: HIGH risk - Grants full permissions to all users, security vulnerability
chmod 777
```

### Complex Queries
```bash
# Find large files with grouping
ai-shell -p anthropic -s bash -q "find files larger than 50MB in ~/projects, group by extension, exclude node_modules"

# Process monitoring
ai-shell -p ollama -s bash -q "show processes using more than 100MB memory, sorted by usage"

# Text processing
ai-shell -p anthropic -s bash -q "search all JavaScript files for console.log statements, show line numbers"
```

## 🖼️ Screenshots

### Interactive Mode with Risk Assessment
![Interactive mode showing risk warnings](images/anthropic-interactive-with-warning.png)

### Interactive Ollama Model Selection
![Interactive Ollama model selection](images/ollama-interactive-with-model-select.png)
*Interactive mode with Ollama model discovery and selection - users can choose from all available models*

### Non-Interactive Mode
![Non-interactive mode with warnings](images/anthropic-non-interactive-with-warning.png)

### Ollama Integration with Auto-Copy
![Ollama integration with copy functionality](images/ollama-non-interactive-with-copy.png)

## 🔧 Advanced Configuration

### Environment Variables
```bash
# .env file
ANTHROPIC_API_KEY=your_anthropic_api_key
OLLAMA_HOST=localhost:11434  # Optional: custom Ollama host
```

### Available Ollama Models
The tool automatically detects available models, but you can specify any:
- `gpt-oss:latest` - OpenAI's open-source model
- `qwen2.5-coder:7b` - Qwen coding model
- `deepseek-r1:8b` - DeepSeek reasoning model
- `mistral-nemo:12b` - Mistral model
- Any other Ollama model

## 🏗️ Architecture

### Command Generation Flow
1. **Query Processing** - Natural language query analysis
2. **OS Detection** - Platform-specific command generation
3. **AI Generation** - Provider-specific command creation
4. **Risk Assessment** - Safety analysis of generated command
5. **User Interaction** - Display and clipboard options

### Risk Assessment Categories
- **Data Deletion** - `rm`, `dd`, destructive operations
- **Permission Changes** - `chmod`, `chown`, security implications
- **System Modifications** - Network changes, system files
- **Recursive Operations** - Potential for widespread changes
- **Network Exposure** - Security vulnerabilities

## 🧪 Testing

```bash
# Run unit tests
python -m unittest test_main.py -v

# Test specific functionality
python main.py -p anthropic -s bash -q "test command" --no-risk-check
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Anthropic](https://www.anthropic.com/) for Claude AI
- [Ollama](https://ollama.ai/) for local AI model support
- [Click](https://click.palletsprojects.com/) for CLI framework
- OpenAI for open-source models

## 📚 Documentation

For more detailed documentation, examples, and troubleshooting, visit our [GitHub repository](https://github.com/codingthefuturewithai/ai-shell-command-generator).

---

**Made with ❤️ for developers who want to work smarter, not harder.**