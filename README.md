# SmolD

<div align="center">

**A Lightweight Code Assistant with Powerful Tool Integration**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](#testing)
[![GitHub Issues](https://img.shields.io/badge/feedback-welcome-brightgreen.svg)](https://github.com/fabiopauli/smold-gemini/issues)

*Built on HuggingFace's smolagents framework with Google Gemini 2.5 Flash integration*

</div>

---

## 📑 Table of Contents

- [SmolD](#smold)
  - [📑 Table of Contents](#-table-of-contents)
  - [🚀 Quick Start](#-quick-start)
  - [🚀 Overview](#-overview)
    - [✨ Key Features](#-key-features)
  - [🏗️ Architecture](#️-architecture)
    - [🔧 Available Tools](#-available-tools)
    - [🏛️ Council of AI Specialists](#️-council-of-ai-specialists)
  - [📦 Installation](#-installation)
    - [Prerequisites](#prerequisites)
    - [Quick Setup](#quick-setup)
  - [🎯 Usage Guide](#-usage-guide)
    - [Command-Line Interface](#command-line-interface)
    - [💡 Example Use Cases](#-example-use-cases)
    - [🎛️ Advanced Features](#️-advanced-features)
  - [🧪 Testing](#-testing)
  - [🏛️ Project Structure](#️-project-structure)
  - [🔧 Configuration](#-configuration)
    - [Environment Variables](#environment-variables)
  - [🐛 Troubleshooting](#-troubleshooting)
  - [🔗 Related Projects](#-related-projects)
  - [📄 License](#-license)
  - [🙏 Acknowledgments](#-acknowledgments)
  - [🐳 Docker Deployment](#-docker-deployment)
    - [🚀 Quick Docker Start](#-quick-docker-start)
      - [Production Dockerfile](#production-dockerfile)
      - [Docker Compose Setup](#docker-compose-setup)
      - [Building and Running](#building-and-running)
      - [Development Setup](#development-setup)
      - [Environment Variables](#environment-variables-1)
      - [Production Considerations](#production-considerations)
  - [](#)

---

## 🚀 Quick Start

Get SmolD running in under 5 minutes:

```bash
# 1. Clone and enter directory
git clone https://github.com/fabiopauli/smold-gemini.git && cd smold-gemini

# 2. Create virtual environment and activate
python -m venv venv && source venv/bin/activate  # Unix/Linux/macOS
# python -m venv venv && venv\Scripts\activate   # Windows

# 3. Install dependencies (using uv for speed)
pip install uv && uv pip install -e .

# 4. Set your API key
echo "GEMINI_API_KEY=your_key_here" > .env

# 5. Start coding assistance!
python main.py -i
```

**Need help?** See our [detailed installation guide](#-installation) or [report issues](https://github.com/fabiopauli/smold-gemini/issues).

---

## 🚀 Overview

SmolD is a sophisticated yet lightweight command-line code assistant that combines the power of Large Language Models with a comprehensive suite of development tools. Whether you're exploring codebases, refactoring code, running tests, or managing files, SmolD provides an intelligent interface that understands context and executes tasks efficiently.

### ✨ Key Features

- **🧠 Intelligent Code Understanding** - Deep codebase analysis and context-aware responses
- **💭 Advanced Context Management** - Remembers last 8 interactions with automatic token management under 100k
- **🏛️ Council of AI Specialists** - Multi-model consultation system (OpenAI o4-mini, Gemini 2.5 Pro, DeepSeek Reasoner)
- **🛠️ Comprehensive Tool Suite** - File operations, search, shell commands, and more
- **🖥️ Cross-Platform Support** - Works seamlessly on Windows (PowerShell) and Unix (Bash)
- **⚡ Interactive & Batch Modes** - Flexible usage patterns for different workflows
- **🔍 Advanced Search Capabilities** - Regex-powered content search and glob pattern matching
- **📁 Smart Directory Management** - Context-aware file and directory operations
- **🔒 Security-First Design** - Built-in command filtering and safety measures
- **🧪 Comprehensive Testing** - 43+ unit tests ensuring reliability across platforms

## 🏗️ Architecture

SmolD leverages a modular architecture built around three core components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Interface │    │   Agent Core     │    │   Tool System   │
│                 │─ ─▶│                  │───▶│                 │
│ • Interactive   │    │ • Gemini 2.5Flash│    │ • Platform-     │
│ • Single Query  │    │ • LiteLLM        │    │   specific      │
│ • Directory     │    │ • Context Mgmt   │    │ • Extensible    │
│   Context       │    │ • System Prompt  │    │ • Type-safe     │
│ • AI Council    │    │ • Memory (4 int) │    │ • 10 Tools      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🔧 Available Tools

| Tool | Platform | Description | Use Cases |
|------|----------|-------------|-----------|
| **BashTool** | Unix/Linux | Execute bash commands with persistent sessions | Running scripts, git operations, system commands |
| **PowerShellTool** | Windows | Execute PowerShell commands with safety checks | Windows-specific tasks, administration, file operations |
| **EditTool** | All | Precise file editing with string replacement | Code refactoring, bug fixes, content updates |
| **ViewTool** | All | Read files with line numbers and pagination | Code review, file inspection, content analysis |
| **GrepTool** | All | Advanced regex-based content search | Finding functions, classes, patterns in code |
| **GlobTool** | All | File pattern matching with recursive search | Locating files by name, extension, or path patterns |
| **LSTool** | All | Tree-structured directory listings | Project exploration, file structure analysis |
| **ReplaceTool** | All | Create or completely replace file contents | Template generation, file creation |
| **CDTool** | All | Smart directory navigation with error handling | Workspace navigation, path management |
| **UserInputTool** | All | Interactive user prompts during execution | Confirmation dialogs, parameter collection |

### 🏛️ Council of AI Specialists

SmolD includes a powerful consultation system that leverages multiple AI models for superior advice:

```bash
# Consult the Council of AI Specialists
python smold/council.py --prompt "How can I optimize this React component for performance?"

# Include context from files
python smold/council.py --context-file "component.jsx" --prompt "Review this code"

# Add additional context
python smold/council.py --context "Using React 18" --prompt "Best practices for state management"
```

**Council Members:**
- **OpenAI o4-mini** - General software engineering expertise and reasoning
- **Gemini 2.5 Pro** - Advanced reasoning with Google Search capabilities  
- **DeepSeek Reasoner** - Deep analytical reasoning and complex problem solving

The council runs parallel consultations and provides a comprehensive report with insights from all three specialists, helping you make more informed technical decisions.

## 📦 Installation

### Prerequisites

- **Python 3.11 or higher** - Required for modern async support and type hints
  - Tested on Python 3.11, 3.12, and 3.13
  - Older versions (3.10 and below) are not supported
- **Google Gemini API Key** - Get yours at [Google AI Studio](https://makersuite.google.com/app/apikey)
  - 🔒 **Security Note**: Never commit API keys to version control
  - Use `.env` files or environment variables for key management
- **Git** (optional) - For enhanced git repository features and project cloning

### Quick Setup

1. **Clone and Navigate**
   ```bash
   git clone https://github.com/fabiopauli/smold-gemini.git
   cd smold-gemini
   ```

2. **Environment Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate (Unix/Linux/macOS)
   source venv/bin/activate
   
   # Activate (Windows)
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   
   **Option A: Using uv (recommended - faster)**
   ```bash
   # Install uv if you haven't already
   pip install uv
   
   # Install dependencies and SmolD
   uv pip install -e .
   ```
   
   **Option B: Using pip (traditional)**
   ```bash
   # Install from requirements.txt
   pip install -r requirements.txt
   
   # Install SmolD in development mode
   pip install -e .
   ```

4. **Configure API Access** 🔒
   ```bash
   # Create .env file with required API keys (SECURE METHOD)
   echo "GEMINI_API_KEY=your_gemini_key_here" > .env
   echo "OPENAI_API_KEY=your_openai_key_here" >> .env  # For council.py
   echo "GEMINI_API_KEY=your_gemini_key_here" >> .env  # For council.py
   
   # Set proper permissions (Unix/Linux/macOS)
   chmod 600 .env
   
   # Verify .env is in .gitignore (important!)
   echo ".env" >> .gitignore
   ```
   
   **🔐 Security Best Practices:**
   - ✅ Use `.env` files for local development
   - ✅ Set environment variables in production
   - ✅ Never commit API keys to version control
   - ✅ Rotate keys regularly
   - ❌ Don't hardcode keys in source code

## 🎯 Usage Guide

### Command-Line Interface

**Single Query Mode**
```bash
# Analyze current directory
python main.py "What files are in this project?"

# Code analysis
python main.py "Find all TODO comments in Python files"

# Refactoring assistance
python main.py "Rename the function 'old_name' to 'new_name' in utils.py"
```

**Interactive Mode** (now with conversation memory!)
```bash
# Start interactive session with context retention
python main.py -i

# Session in specific directory
python main.py --cwd /path/to/project -i

# Use new context management commands:
# - "context" to view conversation state and token usage
# - "clear" to reset conversation history
```

**Directory-Specific Operations**
```bash
# Run query in specific directory
python main.py --cwd ./src "List all TypeScript files"

# Automatic context switching
python main.py --cwd ~/projects/myapp "Run the test suite"
```

### 💡 Example Use Cases

<details>
<summary>🔍 <strong>Codebase Exploration</strong></summary>

```bash
# Understand project structure
> "Analyze this codebase and explain its architecture"

# Find specific implementations
> "Where is the user authentication logic implemented?"

# Locate configuration files
> "Find all configuration files in this project"
```
</details>

<details>
<summary>🛠️ <strong>Development Tasks</strong></summary>

```bash
# Refactoring
> "Rename all instances of 'getUserData' to 'fetchUserProfile'"

# Bug fixing
> "Find and fix the syntax error in main.py"

# Code quality
> "Add type hints to all functions in the utils module"
```
</details>

<details>
<summary>🧪 <strong>Testing & CI/CD</strong></summary>

```bash
# Run tests
> "Execute the test suite and show results"

# Check code quality
> "Run linting and type checking"

# Build processes
> "Build the project and handle any errors"
```
</details>

<details>
<summary>📁 <strong>File Management</strong></summary>

```bash
# Bulk operations
> "Create a .gitignore file for a Python project"

# Content generation
> "Generate a basic setup.py file for this package"

# Documentation
> "Create API documentation for all public functions"
```
</details>

### 🎛️ Advanced Features

**Enhanced Context Management**
- **Conversation Memory**: Remembers last 4 interactions for better continuity
- **Smart Token Management**: Automatically manages context under 100k tokens using tiktoken
- **Project Context**: Automatically includes directory structure and git status in system prompt
- **Dynamic Context**: Updates context when changing directories with `cd` command

**Interactive Commands**
```bash
# Context management in interactive mode
> context     # View current conversation state and token usage
> clear       # Clear conversation history to start fresh
> cd <path>   # Change directory and update agent context
> help        # Show all available commands and capabilities
```

**Smart Command Recognition**
```bash
# These all work naturally:
> "ls"                    # Lists current directory
> "dir"                   # Windows directory listing  
> "git status"            # Git repository status
> "npm test"              # Run Node.js tests
> "pytest"               # Run Python tests
```

**Safety Features**
- Automatic command validation and safety checks
- Banned command filtering (prevents dangerous operations)
- Confirmation prompts for destructive actions
- Sandbox-aware execution environment

## 🧪 Testing

SmolD includes a comprehensive test suite covering all tools and platforms:

```bash
# Run all tests
python smold/run_tool_tests.py

# Run specific tool tests
python smold/run_tool_tests.py --tool bash

# Verbose output
python smold/run_tool_tests.py --verbose

# Alternative test runner
python -m unittest discover smold/tools/tests/
```

**Test Coverage**
- ✅ 43 total tests across all tools
- ✅ Cross-platform compatibility testing
- ✅ Error handling and edge cases
- ✅ Security and safety feature validation
- ✅ Performance and timeout testing

## 🏛️ Project Structure

```
smold/
├── 📁 smold/                    # Core package
│   ├── 🔧 agent.py              # Enhanced agent with conversation history
│   ├── 💭 context_manager.py    # Conversation memory & token management
│   ├── 🏛️ council.py            # Multi-model AI consultation system
│   ├── 📝 system_prompt.py      # Dynamic prompt generation
│   ├── 📄 system_message.txt    # Base system message template
│   └── 🛠️ tools/               # Tool implementations
│       ├── 🐚 bash_tool.py      # Unix shell commands
│       ├── 💻 powershell_tool.py # Windows shell commands
│       ├── ✏️ edit_tool.py       # File editing
│       ├── 👀 view_tool.py       # File reading
│       ├── 🔍 grep_tool.py       # Content search
│       ├── 📂 glob_tool.py       # File pattern matching
│       ├── 📋 ls_tool.py         # Directory listing
│       ├── 📝 replace_tool.py    # File creation/replacement
│       ├── 📁 cd_tool.py         # Directory navigation
│       ├── 💬 user_input_tool.py # User interaction
│       └── 🧪 tests/            # Comprehensive test suite
├── 🚀 main.py                   # CLI entry point with context commands
├── 🧪 test_context.py           # Context system test suite
├── ⚙️ pyproject.toml            # Project configuration
├── 📋 requirements.txt          # Dependencies
├── 📖 README.md                 # This file
├── 📄 LICENSE                   # MIT License
└── 🔧 CLAUDE.md                 # Development guidelines
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key (main agent) | None |
| `OPENAI_API_KEY` | ⚪ | OpenAI API key (for council.py) | None |
| `GEMINI_API_KEY` | ⚪ | Google Gemini API key (for council.py) | None |

## 🐛 Troubleshooting

<details>
<summary><strong>🔑 API Key Issues</strong></summary>

**API Key Not Found**
```bash
# Verify API key is set
echo $GEMINI_API_KEY  # Unix/Linux/macOS
echo %GEMINI_API_KEY% # Windows

# Test API connectivity
python -c "import os; print('Key found' if os.getenv('GEMINI_API_KEY') else 'Key missing')"

# Check .env file exists and has correct format
cat .env | grep GEMINI_API_KEY
```

**API Authentication Errors**
```bash
# Test your API key validity
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.deepseek.com/v1/models

# If council.py fails, check OpenAI/Gemini keys
python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY'))); print('Gemini:', bool(os.getenv('GEMINI_API_KEY')))"
```
</details>

<details>
<summary><strong>🛠️ Installation & Dependency Issues</strong></summary>

**Virtual Environment Problems**
```bash
# Recreate virtual environment
rm -rf venv  # Remove existing venv
python -m venv venv

# Activate properly
source venv/bin/activate  # Unix/Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Verify you're in the virtual environment
which python  # Should show path to venv/bin/python
```

**Package Installation Failures**
```bash
# Update pip first
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Install with verbose output for debugging
pip install -v -e .

# Alternative: Use uv for faster installs
pip install uv && uv pip install -e .
```

**Tool Loading Failures**
```bash
# Check tool imports
python -c "from smold.agent import get_available_tools; print(len(get_available_tools()))"

# Verbose tool loading
python main.py "test" --verbose

# Check specific tool
python -c "from smold.tools.bash_tool import bash_tool; print('Bash tool OK')"
```
</details>

<details>
<summary><strong>⚙️ Runtime & Performance Issues</strong></summary>

**Memory/Token Errors**
```bash
# Check conversation context
python main.py -i
> context  # Shows current token usage

# Clear conversation history
> clear    # Resets context

# Reduce context if needed (edit system_prompt.py)
# Consider using shorter directory structures
```

**Command Execution Issues**
```bash
# Test bash/powershell directly
bash -c "echo 'Bash test'"        # Unix/Linux/macOS
powershell -c "echo 'PS test'"    # Windows

# Check PATH and permissions
echo $PATH  # Unix/Linux/macOS
echo $env:PATH  # Windows PowerShell

# Verify working directory
pwd && ls -la
```
</details>

<details>
<summary><strong>🔧 Permission & File Access Errors</strong></summary>

**File Permission Errors**
```bash
# Fix script permissions
chmod +x main.py run_tool_tests.sh

# Check file ownership
ls -la main.py smold/

# Run with elevated privileges (if needed)
sudo python main.py "system command"  # Unix/Linux/macOS
# Run PowerShell as Administrator  # Windows
```

**Directory Access Issues**
```bash
# Check directory permissions
ls -ld $(pwd)

# Verify you can write to current directory
touch test_write && rm test_write

# Use absolute paths if relative paths fail
python main.py --cwd /full/path/to/project "your query"
```
</details>

<details>
<summary><strong>🖥️ Platform-Specific Issues</strong></summary>

**Windows Specific**
```powershell
# PowerShell execution policy issues
Get-ExecutionPolicy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Use 'py' launcher if 'python' doesn't work
py --version
py main.py "your query"

# Path separator issues in file operations
# Use forward slashes even on Windows: "src/main.py"
```

**macOS Specific**
```bash
# Install Python via Homebrew (recommended)
brew install python@3.11

# Fix zsh/bash compatibility
echo $SHELL  # Check current shell
bash        # Switch to bash if needed

# Xcode command line tools (may be required)
xcode-select --install
```

**Linux Specific**
```bash
# Ensure bash is available
which bash  # Should return /bin/bash

# Install Python development headers (if needed)
sudo apt-get install python3-dev  # Ubuntu/Debian
sudo yum install python3-devel    # CentOS/RHEL
```
</details>

<details>
<summary><strong>🆘 Getting Help</strong></summary>

**Before Reporting Issues:**
1. ✅ Check this troubleshooting guide
2. ✅ Verify your Python version: `python --version`
3. ✅ Confirm API keys are properly set
4. ✅ Try running with `--debug` flag for detailed logs
5. ✅ Test with a fresh virtual environment

**Report Issues:**
- 🐛 [GitHub Issues](https://github.com/fabiopauli/smold-gemini/issues) - Bug reports and feature requests
- 📚 Include your OS, Python version, and error messages
- 🔍 Use `--debug` output for better diagnostics

**Get Verbose Output:**
```bash
# Maximum debugging information
python main.py --debug --verbose "your query"

# Check agent initialization
python -c "from smold.agent import create_agent; agent = create_agent(); print('Agent created successfully')"
```
</details>

## 🔗 Related Projects

- [smolagents](https://github.com/huggingface/smolagents) - The underlying agent framework
- [LiteLLM](https://github.com/BerriAI/litellm) - Multi-provider LLM interface

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **HuggingFace** for the excellent smolagents framework
- **Google Gemini** for providing powerful and affordable LLM APIs
- **The Python Community** for the amazing ecosystem of tools and libraries

## 🐳 Docker Deployment

SmolD supports containerized deployment for consistent environments and easy distribution across different platforms.

### 🚀 Quick Docker Start

<details>
<summary><strong>One-Command Setup</strong></summary>

#### Production Dockerfile

Create a `Dockerfile` in your project root:

```dockerfile
# Multi-stage build for smaller image size
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml ./
COPY requirements.txt ./
COPY uv.lock ./

# Install Python dependencies
# Option 1: Using uv (faster, recommended)
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -r requirements.txt

# Option 2: Using standard pip (uncomment if you prefer)
# RUN pip install --no-cache-dir --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    bash \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 smold

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory and copy source
WORKDIR /app
COPY --chown=smold:smold . .

# Install SmolD in development mode
RUN pip install -e .

# Create directories for logs and context
RUN mkdir -p /app/council-logs && \
    chown -R smold:smold /app

# Switch to non-root user
USER smold

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from smold import create_agent; print('OK')" || exit 1

# Default command (interactive mode)
CMD ["python", "main.py", "-i"]
```

#### Docker Compose Setup

Create a `docker-compose.yml` for complete environment management:

```yaml
version: '3.8'

services:
  smold:
    build: .
    container_name: smold-assistant
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      # Mount your project directory for development
      - ./workspace:/workspace
      # Persist conversation logs
      - smold-logs:/app/council-logs
      # Mount .env file for API keys
      - ./.env:/app/.env:ro
    working_dir: /workspace
    stdin_open: true
    tty: true
    restart: unless-stopped

volumes:
  smold-logs:
    driver: local
```

#### Building and Running

**Quick Start:**
```bash
# Build the image
docker build -t smold:latest .

# Run interactive session
docker run -it --rm \
  -e DEEPSEEK_API_KEY=your_key_here \
  -v $(pwd):/workspace \
  smold:latest

# Run single query
docker run --rm \
  -e DEEPSEEK_API_KEY=your_key_here \
  -v $(pwd):/workspace \
  smold:latest python main.py "What files are in this directory?"
```

**Using Docker Compose:**
```bash
# Start the service
docker-compose up -d

# Access interactive mode
docker-compose exec smold bash

# View logs
docker-compose logs -f smold

# Run council consultation
docker-compose exec smold python smold/council.py --prompt "Review my code"

# Stop and cleanup
docker-compose down -v
```

#### Development Setup

For development with live code reloading:

```dockerfile
# Development Dockerfile (Dockerfile.dev)
FROM python:3.11-slim

RUN apt-get update && apt-get install -y git bash curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for faster dependency management
RUN pip install uv

# Copy dependency files
COPY requirements.txt .
COPY pyproject.toml .

# Install dependencies (including dev tools)
RUN uv pip install --system -r requirements.txt

# Install in development mode when container starts (uses mounted volume)
CMD ["bash", "-c", "uv pip install --system -e . && python main.py -i"]
```

```yaml
# Development docker-compose.override.yml
version: '3.8'

services:
  smold:
    build:
      dockerfile: Dockerfile.dev
    volumes:
      # Live code reloading
      - .:/app
      - ./workspace:/workspace
    environment:
      - PYTHONPATH=/app
      - DEVELOPMENT=true
```

#### Environment Variables

Create a `.env` file for secure API key management:

```bash
# .env file
DEEPSEEK_API_KEY=your_deepseek_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Configure council consultation limits
COUNCIL_MAX_TOKENS=60000
COUNCIL_TIMEOUT=300
```

#### Production Considerations

**Security:**
- Uses non-root user (`smold`) for container execution
- API keys loaded from environment variables or mounted secrets
- Read-only filesystem where possible

**Performance:**
- Multi-stage build reduces final image size
- Layer caching optimizes build times
- Health checks ensure service availability

**Monitoring:**
```bash
# Monitor resource usage
docker stats smold-assistant

# Check health status
docker inspect --format='{{.State.Health.Status}}' smold-assistant

# Access conversation logs
docker exec smold-assistant ls -la council-logs/
```
</details>
---