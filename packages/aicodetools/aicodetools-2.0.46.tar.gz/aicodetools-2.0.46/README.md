# aicodetools

Simple, lightweight AI code tools with Docker-only support. No complex dependencies.

Provides four essential tools for AI agents: **read**, **write**, **edit**, and **run** commands.
Runs in a secure Docker container with automatic setup and management.


## Installation

You can install the package using pip:

```bash
pip install aicodetools
```

Or for development:

```bash
pip install -e .
```

## Quick Start

```python
from aicodetools.client import CodeToolsClient

# Auto-starts Docker server if needed (uses python:3.11-slim + pip install)
client = CodeToolsClient(auto_start=True)

# Get simple functional tools
tools = client.tools(selection_list=["read_file", "write_file", "edit_file", "run_command"])
read, write, edit, run_cmd = tools

# Read a file with smart token management
result = read("example.py")
print(result["content"])

# Write a file (with safety checks)
write("hello.py", "print('Hello, World!')")

# Edit file using string replacement
edit("hello.py", "Hello", "Hi")

# Run commands (non-interactive)
result = run_cmd("python hello.py", interactive=False)
print(result["stdout"])

# Interactive commands still available on client
client.run_command("python -i", interactive=True)
client.send_input("2 + 2")
output = client.get_output()

# Clean up when done
client.stop_server()
```

## Docker Configuration

### Using Custom Docker Images

The framework automatically installs `aicodetools` via pip inside any Python container:

```python
from aicodetools import CodeToolsClient

# Default: uses python:3.11-slim + pip install aicodetools
client = CodeToolsClient(auto_start=True)

# Use different Python version
client = CodeToolsClient(
    auto_start=True,
    docker_image="python:3.12-alpine"
)

# Use custom port (default is 18080 to avoid conflicts)
client = CodeToolsClient(
    auto_start=True,
    port=19080
)

# Use your own custom Python image
client = CodeToolsClient(
    auto_start=True,
    docker_image="my-company/python-base:latest"
)
```

### Docker Image Requirements

Your custom Docker image only needs:
- Python 3.10+ installed
- `pip` available
- Internet access (to install aicodetools package)

### Example Custom Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies if needed
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Pre-install aicodetools (optional - will be installed automatically if not present)
RUN pip install aicodetools

# Optional: Pre-install common packages for your use case
RUN pip install numpy pandas requests beautifulsoup4

# Set working directory
WORKDIR /workspace

CMD ["/bin/bash"]
```

### Manual Docker Usage

If you prefer to manage Docker yourself:

```bash
# Use any Python image and install aicodetools
docker run -d -p 18080:8080 --name my-aicodetools --rm python:3.11-slim \
  bash -c "pip install --break-system-packages aicodetools && python -m aicodetools.server --host 0.0.0.0 --port 8080"

# Then connect without auto_start
client = CodeToolsClient(auto_start=False, server_url="http://localhost:18080")

# Or use a different port
docker run -d -p 19080:8080 --name my-aicodetools-alt --rm python:3.12-alpine \
  bash -c "pip install --break-system-packages aicodetools && python -m aicodetools.server --host 0.0.0.0 --port 8080"
client = CodeToolsClient(auto_start=False, server_url="http://localhost:19080")

# With your own custom image
docker run -d -p 20080:8080 --name my-custom --rm my-company/python-base:latest \
  bash -c "pip install --break-system-packages aicodetools && python -m aicodetools.server --host 0.0.0.0 --port 8080"
```

## Core Tools

Four essential tools, designed for simplicity and reliability:

### 📖 **Read Tool**
- Smart file reading with tiered token management (4k/10k modes)
- Regex pattern matching with context lines
- Line range support for targeted reading
- Automatic compression for long lines (6k max per line)

### ✏️ **Write Tool**
- Safe file writing with read-first validation for existing files
- Automatic backup creation with timestamps
- UTF-8 encoding by default (simplified for Linux containers)
- Directory creation if needed

### ✂️ **Edit Tool**
- String-based find and replace editing
- Support for single or all occurrences (replace_all flag)
- Automatic backup before editing
- Detailed change reporting with diffs

### ⚡ **Run Tool**
- **Single function**: `run_command(command, timeout=300, interactive=False)`
- **Non-interactive**: Auto-kill on timeout, return complete results
- **Interactive**: Stream output, agent controls (get_output, send_input, stop_process)
- **Single command limit**: Only one command at a time (prevents agent confusion)

## Usage Examples

### Context Manager Usage

```python
from aicodetools.client import CodeToolsClient

# Recommended: Use context manager for automatic cleanup
with CodeToolsClient(auto_start=True) as client:
    # Get functional tools
    tools = client.tools(selection_list=["read_file", "write_file", "edit_file", "run_command"])
    read, write, edit, run_cmd = tools

    # Read file with regex pattern matching
    matches = read("example.py", regex=r"def \w+")

    # Safe file editing workflow
    read("config.py")  # Read first for safety
    edit("config.py", "DEBUG = False", "DEBUG = True")

    # Execute multiple commands (non-interactive)
    run_cmd("pip install requests", interactive=False)
    result = run_cmd("python -c 'import requests; print(requests.__version__)'", interactive=False)
    print(f"Requests version: {result['stdout']}")

# Server automatically stops when exiting context
```

### Interactive Command Example

```python
from aicodetools import CodeToolsClient
import time

client = CodeToolsClient(auto_start=True)

# Start a Python REPL (interactive mode)
result = client.run_command("python -i", interactive=True)
print(f"Python REPL started: {result['success']}")

# Send commands and get output
client.send_input("x = 10")
client.send_input("y = 20")
client.send_input("print(x + y)")

# Get accumulated output
time.sleep(1)  # Wait for commands to execute
output = client.get_output()
print("Python REPL output:", output["recent_stdout"])

# Stop the process
client.stop_process()
client.stop_server()
```

### AI Agent Integration

```python
from aicodetools.client import CodeToolsClient

def create_tool_functions():
    """Create tool functions for AI agent integration."""
    client = CodeToolsClient(auto_start=True)

    # Get the simplified functional tools
    tools = client.tools(selection_list=["read_file", "write_file", "edit_file", "run_command"])
    read, write, edit, run_cmd = tools

    return [read, write, edit, run_cmd], client

# Use with your favorite AI framework
tools, client = create_tool_functions()
read, write, edit, run_cmd = tools

# Your AI agent can now use these simple functions
# agent = YourAIAgent(tools=tools)
# response = agent.run("Create a Python script that calculates fibonacci numbers")

# Example usage:
content = read("example.py")  # Read file content
write("fibonacci.py", "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)")  # Write file
edit("fibonacci.py", "fib", "fibonacci")  # Edit file
result = run_cmd("python fibonacci.py", timeout=10)  # Run command

# Clean up when done
client.stop_server()
```

## Multi-Agent Support with ClientManager

The `ClientManager` enables multiple AI agents to work concurrently, each with isolated Docker environments.

### Basic Multi-Agent Setup

```python
from aicodetools import ClientManager

# Create manager with organized logging
manager = ClientManager(
    docker_image="python:3.11-slim",
    base_log_dir="./agent_logs"
)

# Get clients for different agents
data_agent = manager.get_client("data_processor")     # Logs: ./agent_logs/data_processor/
code_agent = manager.get_client("code_reviewer")      # Logs: ./agent_logs/code_reviewer/
test_agent = manager.get_client("test_writer")        # Logs: ./agent_logs/test_writer/

# Each agent gets isolated Docker container with unique ports
# Container names: aicodetools-data_processor-abc123, etc.

# Use agents normally - each has separate environment
data_tools = data_agent.tools(["read_file", "write_file", "run_command"])
code_tools = code_agent.tools(["read_file", "edit_file", "run_command"])

# Clean up when done
manager.close_all_clients()
```

### Parallel Agent Execution

```python
import threading
from aicodetools import ClientManager

def agent_worker(manager, agent_id, task):
    """Worker function for parallel agent execution."""
    client = manager.get_client(agent_id)
    tools = client.tools(["read_file", "write_file", "edit_file", "run_command"])
    read, write, edit, run_cmd = tools

    # Agent performs its task
    write(f"{agent_id}_output.py", f"# Task: {task}\nprint('Completed by {agent_id}')")
    result = run_cmd(f"python {agent_id}_output.py")
    print(f"{agent_id}: {result['stdout'].strip()}")

# Create manager for parallel execution
with ClientManager(base_log_dir="./parallel_logs") as manager:
    # Define agents and their tasks
    agents = [
        ("frontend_dev", "Build UI components"),
        ("backend_dev", "Implement API endpoints"),
        ("database_dev", "Design database schema"),
        ("tester", "Write comprehensive tests")
    ]

    # Start all agents in parallel
    threads = []
    for agent_id, task in agents:
        thread = threading.Thread(
            target=agent_worker,
            args=(manager, agent_id, task)
        )
        threads.append(thread)
        thread.start()

    # Wait for all agents to complete
    for thread in threads:
        thread.join()

    print("All agents completed!")
    # Auto-cleanup when exiting context manager
```

### ClientManager Features

```python
from aicodetools import ClientManager

manager = ClientManager(base_log_dir="./my_logs")

# Client lifecycle management
client = manager.get_client("worker_1")
info = manager.get_client_info("worker_1")
print(f"Worker 1: port={info['port']}, container={info['container_name']}")

# List all active clients
clients = manager.list_clients()
for client_id, info in clients.items():
    status = "✅ Running" if info['is_running'] else "❌ Stopped"
    print(f"{client_id}: {status} (port {info['port']})")

# Selective cleanup
manager.close_client("worker_1")  # Stop specific client
manager.close_all_clients()       # Stop all clients

# Thread-safe operations
# Multiple threads can safely call get_client() simultaneously
```

### Key Benefits

- **Isolation**: Each agent runs in its own Docker container with unique ports
- **Threading**: Thread-safe client creation and management
- **Organized Logs**: Separate log directories per agent (`{base_dir}/{agent_id}/tool_calls.txt`)
- **Zero Conflicts**: Automatic port allocation prevents conflicts
- **Backward Compatible**: Existing `CodeToolsClient` code works unchanged

## Architecture

### 🐳 **Docker-Only Design**
- Simplified deployment: Only Docker containers supported
- Auto-fallback: Creates base container if Docker not running
- Secure isolation: All operations run in containerized environment
- No complex environment management

### 🏗️ **Server-Client Model**
- **Server**: Runs in Docker container, handles tool execution
- **Client**: Python interface, communicates via HTTP/JSON API
- **Auto-start**: Client automatically manages Docker server lifecycle
- **Stateless**: Clean separation between client and execution environment

### 🎯 **Key Benefits**
- **Simplicity**: 4 core tools vs 14+ complex tools in v1
- **Reliability**: Docker-only, predictable environment
- **Maintainability**: Simple codebase, clear architecture
- **Performance**: Lightweight, fast startup
- **Agent-Friendly**: Better error messages, token awareness

## Requirements

- Python 3.10+
- Docker (required - no local fallback)
- Minimal dependencies: `requests`, `tiktoken`

## Development

### Code Quality 🧹

- `make style` to format the code
- `make check_code_quality` to check code quality (PEP8 basically)
- `black .`
- `ruff . --fix`

### Tests 🧪

[`pytests`](https://docs.pytest.org/en/7.1.x/) is used to run our tests.

### Publishing 🚀

```bash
poetry build
poetry publish
```

## License

MIT
