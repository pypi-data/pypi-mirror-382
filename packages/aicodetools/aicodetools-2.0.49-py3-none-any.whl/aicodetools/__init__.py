"""
aicodetools: Simple, lightweight AI code tools with Docker-only support.

This package provides a simplified CodeToolsClient that communicates with a
Docker-based server to execute file operations and commands. No complex
dependencies, just four core tools: read, write, edit, run.

Usage:
    from aicodetools import CodeToolsClient

    # Auto-starts Docker server if needed
    client = CodeToolsClient(auto_start=True)

    # Use the four core tools
    result = client.read_file("example.py")
    result = client.write_file("test.py", "print('hello')")
    result = client.edit_file("test.py", "hello", "world")
    result = client.run_command("python test.py")

    # Clean up when done
    client.stop_server()
"""

from .client import CodeToolsClient
from .client_manager import ClientManager
from .tools import ReadTool, WriteTool, EditTool, RunTool

__version__ = "2.0.0"
__author__ = "balajidinesh"

__all__ = ["CodeToolsClient", "ClientManager", "ReadTool", "WriteTool", "EditTool", "RunTool"]