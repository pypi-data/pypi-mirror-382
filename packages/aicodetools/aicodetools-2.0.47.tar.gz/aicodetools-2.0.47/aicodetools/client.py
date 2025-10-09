"""
AI Code Tools Client - Python interface for communicating with the server.

Provides a simple Python API that communicates with the Docker-based server
via HTTP requests. Handles connection management and response formatting.
"""

import json
import time
import subprocess
import requests
from typing import Dict, Any, Optional, List, Callable, Union
import os
import logging
import functools
import re
import tempfile
from datetime import datetime

# Import tool classes to extract docstrings
from aicodetools.tools import ReadTool, WriteTool, EditTool, RunTool


# Tool names for tools() method
# Available tools: "read_file", "write_file", "edit_file", "run_command"


class CodeToolsClient:
    """Client interface for AI Code Tools server."""

    def __init__(self, server_url: str = "http://localhost:18080", auto_start: bool = True,
                 docker_image: str = "python:3.11-slim", port: int = 18080,
                 log_folder: Optional[str] = None, verbose: bool = False,
                 container_name: Optional[str] = None):
        self.server_url = server_url.rstrip('/')
        # Configure session with better connection handling
        self.session = requests.Session()

        # Set connection pooling and keep-alive for better performance
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=requests.adapters.Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # Set keep-alive headers
        self.session.headers.update({
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=30, max=100'
        })
        self.docker_container = None
        self.docker_image = docker_image
        self.port = port
        self.container_name = container_name or "aicodetools-container"

        # Logging configuration
        self.log_folder = log_folder
        self.verbose = verbose
        self.jsonl_buffer = []  # Buffer for JSONL entries

        # Initialize log files if log_folder is provided
        if self.log_folder:
            os.makedirs(self.log_folder, exist_ok=True)
            self.txt_log_path = os.path.join(self.log_folder, "tool_calls.txt")
            self.jsonl_log_path = os.path.join(self.log_folder, "tool_calls.json")

        if auto_start:
            self._ensure_server_running()

    @staticmethod
    def _sanitize_image_name(image_name: str) -> str:
        """
        Sanitize Docker image name for use in derived image tags.

        Converts: python:3.11-slim -> python-3.11-slim
        Converts: myregistry.com/myimage:v1.2.3 -> myregistry-com-myimage-v1-2-3
        """
        # Replace non-alphanumeric characters with hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9.-]', '-', image_name)
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        return sanitized.lower()

    def _get_prebuilt_image_name(self) -> str:
        """Get the name of the pre-built image for the current base image."""
        sanitized_base = self._sanitize_image_name(self.docker_image)
        return f"aicodetools-{sanitized_base}"

    def _prebuilt_image_exists(self) -> bool:
        """Check if pre-built image already exists."""
        prebuilt_image = self._get_prebuilt_image_name()
        try:
            result = subprocess.run(
                ['docker', 'images', '-q', prebuilt_image],
                capture_output=True, text=True, timeout=10
            )
            return bool(result.stdout.strip())
        except Exception as e:
            logging.warning(f"Failed to check for pre-built image: {e}")
            return False

    def _build_prebuilt_image(self) -> bool:
        """Build pre-built image with aicodetools installed."""
        prebuilt_image = self._get_prebuilt_image_name()

        logging.info(f"Building pre-built image '{prebuilt_image}' (one-time operation)...")

        # Create Dockerfile content
        dockerfile_content = f"""FROM {self.docker_image}
RUN pip install --break-system-packages aicodetools
CMD ["python", "-m", "aicodetools.server", "--host", "0.0.0.0", "--port", "8080"]
"""

        try:
            # Create temporary directory for build context
            with tempfile.TemporaryDirectory() as tmpdir:
                dockerfile_path = os.path.join(tmpdir, 'Dockerfile')

                # Write Dockerfile
                with open(dockerfile_path, 'w') as f:
                    f.write(dockerfile_content)

                # Build image
                build_cmd = [
                    'docker', 'build',
                    '-t', prebuilt_image,
                    '-f', dockerfile_path,
                    tmpdir
                ]

                logging.info(f"Running: docker build -t {prebuilt_image} ...")
                result = subprocess.run(
                    build_cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout for build
                )

                if result.returncode != 0:
                    logging.error(f"Failed to build pre-built image: {result.stderr}")
                    return False

                logging.info(f"Successfully built pre-built image '{prebuilt_image}'")
                return True

        except Exception as e:
            logging.error(f"Error building pre-built image: {e}")
            return False

    def _ensure_server_running(self) -> bool:
        """Ensure the server is running, start if necessary."""
        # Try to connect to existing server with retries
        for attempt in range(3):
            try:
                response = self.session.get(f"{self.server_url}/api/status", timeout=2)
                if response.status_code == 200:
                    logging.info("Server is already running")
                    return True
            except requests.exceptions.ConnectionError:
                # Connection refused - server not running
                if attempt < 2:
                    time.sleep(0.5)  # Brief delay before retry
                    continue
                break  # Server definitely not running
            except requests.exceptions.RequestException:
                pass

        # Try to start server using Docker
        return self._start_docker_server()

    def _start_docker_server(self) -> bool:
        """Start the server using Docker."""
        try:
            logging.info("Starting AI Code Tools server in Docker...")

            # Check if Docker service is running
            try:
                result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    logging.error("Docker service is not running. Please start Docker.")
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logging.error("Docker not found or not running. Please install and start Docker.")
                return False

            # Determine which image to use
            image_to_use = self.docker_image
            use_prebuilt = False

            # Check if pre-built image exists
            if self._prebuilt_image_exists():
                image_to_use = self._get_prebuilt_image_name()
                use_prebuilt = True
                logging.info(f"Using pre-built image: {image_to_use}")
            else:
                # Check if base image exists, pull if needed
                check_result = subprocess.run(['docker', 'images', '-q', self.docker_image],
                                            capture_output=True, text=True, timeout=10)

                if not check_result.stdout.strip():
                    # Base image doesn't exist - try to pull it
                    logging.info(f"Pulling base image: {self.docker_image}")
                    pull_result = subprocess.run(['docker', 'pull', self.docker_image],
                                               capture_output=True, text=True, timeout=120)
                    if pull_result.returncode != 0:
                        logging.error(f"Image '{self.docker_image}' not found. Please ensure it exists or use a standard Python image like 'python:3.11-slim'.")
                        return False

                # Build pre-built image for future use
                if not self._build_prebuilt_image():
                    logging.warning("Failed to build pre-built image, falling back to on-demand installation")
                    use_prebuilt = False
                else:
                    image_to_use = self._get_prebuilt_image_name()
                    use_prebuilt = True

            # Clean up existing container
            subprocess.run(['docker', 'stop', self.container_name], capture_output=True, text=True, timeout=10)
            subprocess.run(['docker', 'rm', self.container_name], capture_output=True, text=True, timeout=10)

            # Start container
            if use_prebuilt:
                # Pre-built image already has aicodetools installed
                run_cmd = [
                    'docker', 'run', '-d', '--name', self.container_name,
                    '-p', f'{self.port}:8080',
                    '--rm',  # Auto-remove container when stopped
                    image_to_use
                ]
                exact_cmd = f"docker run -d --name {self.container_name} -p {self.port}:8080 --rm {image_to_use}"
            else:
                # Fall back to on-demand installation
                cmd_string = f'pip install --break-system-packages aicodetools && python -m aicodetools.server --host 0.0.0.0 --port 8080'
                run_cmd = [
                    'docker', 'run', '-d', '--name', self.container_name,
                    '-p', f'{self.port}:8080',
                    '--rm',  # Auto-remove container when stopped
                    image_to_use,
                    'bash', '-c', cmd_string
                ]
                exact_cmd = f"docker run -d --name {self.container_name} -p {self.port}:8080 --rm {image_to_use} bash -c \"{cmd_string}\""

            logging.info(f"Starting container: {exact_cmd}")
            run_result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=120)
            if run_result.returncode != 0:
                if "port is already allocated" in run_result.stderr or "address already in use" in run_result.stderr:
                    # Port binding failed - raise specific error
                    raise RuntimeError(f"Port {self.port} is already allocated")
                elif "permission denied" in run_result.stderr:
                    logging.error("Docker permission denied. Try running as administrator or add user to docker group.")
                else:
                    logging.error(f"Container failed to start: {run_result.stderr}")
                return False

            self.docker_container = self.container_name

            # Add initial delay to let server start
            # Pre-built images start faster, but still need a moment
            initial_delay = 3 if use_prebuilt else 8
            logging.info(f"Waiting {initial_delay} seconds for server to initialize...")
            time.sleep(initial_delay)

            # Wait for server to start with retry logic
            connection_attempts = 0
            max_connection_attempts = 3

            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = self.session.get(f"{self.server_url}/api/status", timeout=2)
                    if response.status_code == 200:
                        logging.info("Server started successfully")
                        return True
                except requests.exceptions.ConnectionError:
                    # Connection refused - server not ready yet or failed
                    connection_attempts += 1

                    # After several connection refused, check if container is still running
                    if connection_attempts > max_connection_attempts and i > 10:
                        check_result = subprocess.run(
                            ['docker', 'ps', '--filter', f'name={self.container_name}', '--format', '{{.Names}}'],
                            capture_output=True, text=True, timeout=5
                        )
                        if self.container_name not in check_result.stdout:
                            # Container crashed - get logs
                            logs_result = subprocess.run(
                                ['docker', 'logs', self.container_name],
                                capture_output=True, text=True, timeout=5
                            )
                            logging.error(f"Container crashed. Logs:\n{logs_result.stdout}\n{logs_result.stderr}")
                            return False
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)

            # Timeout reached - check container status
            check_result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={self.container_name}', '--format', '{{.Names}}'],
                capture_output=True, text=True, timeout=5
            )
            if self.container_name in check_result.stdout:
                logging.error("Server container is running but not responding to requests")
            else:
                logging.error("Server container failed to start or crashed")

            return False

        except Exception as e:
            logging.error(f"Failed to start Docker server: {e}")
            return False

    def _truncate_string(self, text: str, max_length: int) -> str:
        """Truncate string to max_length, adding ellipsis if truncated."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def _log_tool_call(self, endpoint: str, data: Optional[Dict[str, Any]] = None):
        """Log tool call with truncated args for console and append to txt log."""
        if not (self.verbose or self.log_folder):
            return

        # Map endpoint to tool name
        tool_name = endpoint
        if endpoint == "read":
            tool_name = "read_file"
        elif endpoint == "write":
            tool_name = "write_file"
        elif endpoint == "edit":
            tool_name = "edit_file"
        elif endpoint == "run":
            tool_name = "run_command"

        timestamp = datetime.now().isoformat()

        # Format log entry
        log_entry = f"tool-call -> {tool_name}\n"

        if data:
            for key, value in data.items():
                value_str = str(value)
                if self.verbose:
                    # Truncate for console output
                    truncated_value = self._truncate_string(value_str, 200)
                    log_entry += f"  {key}: {truncated_value}\n"
                else:
                    # Full value for txt log only
                    log_entry += f"  {key}: {value_str}\n"

        log_entry += "----------\n"

        # Console output if verbose
        if self.verbose:
            print(log_entry.rstrip())

        # Append to txt log immediately
        if self.log_folder:
            self._append_to_txt_log(log_entry)

        # Add to JSONL buffer
        if self.log_folder:
            self._add_to_jsonl_buffer({
                "timestamp": timestamp,
                "type": "tool_call",
                "tool": tool_name,
                "args": data or {}
            })

    def _log_tool_result(self, endpoint: str, result: Dict[str, Any]):
        """Log tool result with truncated output for console and append to txt log."""
        if not (self.verbose or self.log_folder):
            return

        # Map endpoint to tool name
        tool_name = endpoint
        if endpoint == "read":
            tool_name = "read_file"
        elif endpoint == "write":
            tool_name = "write_file"
        elif endpoint == "edit":
            tool_name = "edit_file"
        elif endpoint == "run":
            tool_name = "run_command"

        timestamp = datetime.now().isoformat()
        result_json = json.dumps(result)

        # Format log entry
        if self.verbose:
            # Truncated for console
            truncated_result = self._truncate_string(result_json, 400)
            log_entry = f"tool results -> {truncated_result}\n\n"
            print(log_entry.rstrip())

        # Full result for txt log
        if self.log_folder:
            log_entry = f"tool results -> {result_json}\n\n"
            self._append_to_txt_log(log_entry)

        # Add to JSONL buffer
        if self.log_folder:
            self._add_to_jsonl_buffer({
                "timestamp": timestamp,
                "type": "tool_result",
                "tool": tool_name,
                "result": result
            })

    def _append_to_txt_log(self, content: str):
        """Append content to the txt log file immediately."""
        if not self.log_folder:
            return

        try:
            with open(self.txt_log_path, 'a', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Failed to write to txt log: {e}")

    def _add_to_jsonl_buffer(self, entry: Dict[str, Any]):
        """Add entry to JSONL buffer for later export."""
        if not self.log_folder:
            return
        self.jsonl_buffer.append(entry)

    def export_logs(self):
        """Export buffered JSONL entries to file."""
        if not self.log_folder or not self.jsonl_buffer:
            return

        try:
            with open(self.jsonl_log_path, 'w', encoding='utf-8') as f:
                for entry in self.jsonl_buffer:
                    f.write(json.dumps(entry) + '\n')
            # Clear buffer after successful export
            self.jsonl_buffer.clear()
        except Exception as e:
            logging.error(f"Failed to export JSONL logs: {e}")

    def _run_command_with_polling(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run command with polling for very long operations."""
        import time

        # Start the command with shorter initial timeout for interactive mode
        initial_data = data.copy()
        initial_data["timeout"] = 30  # Start with 30s to get initial response
        initial_data["interactive"] = True

        # Start the command
        result = self._make_request("run", initial_data)

        # If it completed quickly, return result
        if result.get("success") and "timeout" not in result.get("message", ""):
            return result

        # If it's running, poll for completion
        max_polls = data["timeout"] // 30  # Poll every 30 seconds
        for _ in range(max_polls):
            time.sleep(30)

            # Continue the command
            continue_result = self._make_request("run", {"command": "", "timeout": 30, "interactive": True})

            # If completed, return result
            if continue_result.get("success") and "timeout" not in continue_result.get("message", ""):
                return continue_result

            # If failed or tool error, return result
            if not continue_result.get("success"):
                return continue_result

        # Timeout reached, kill the process
        kill_result = self._make_request("run", {"command": "C-c", "timeout": 30, "interactive": True})
        return kill_result

    def _make_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None, method: str = 'POST') -> Dict[str, Any]:
        """Make HTTP request to server with dynamic timeout."""
        # Log the tool call
        self._log_tool_call(endpoint, data)

        try:
            url = f"{self.server_url}/api/{endpoint}"

            # Dynamic timeout: use command timeout + buffer for long-running commands
            if endpoint == "run" and data and "timeout" in data:
                # Command timeout + 30 second buffer for processing
                http_timeout = data["timeout"] + 30
                # Cap at reasonable maximum (2 hours)
                http_timeout = min(http_timeout, 7200)
            else:
                # Default timeout for other operations
                http_timeout = 30

            if method == 'GET':
                response = self.session.get(url, timeout=http_timeout)
            else:
                response = self.session.post(url, json=data or {}, timeout=http_timeout)

            response.raise_for_status()
            result = response.json()

            # Log the tool result
            self._log_tool_result(endpoint, result)

            return result

        except requests.exceptions.Timeout:
            error_result = {"success": False, "error": "Request timed out"}
            self._log_tool_result(endpoint, error_result)
            return error_result
        except requests.exceptions.ConnectionError as e:
            # Connection refused - try to provide helpful context
            error_msg = "Failed to connect to server"
            if "Connection refused" in str(e) or "ConnectionRefusedError" in str(e):
                # Check if Docker container is still running
                if self.docker_container:
                    try:
                        check_result = subprocess.run(
                            ['docker', 'ps', '--filter', f'name={self.container_name}', '--format', '{{.Names}}'],
                            capture_output=True, text=True, timeout=5
                        )
                        if self.container_name not in check_result.stdout:
                            error_msg = "Server container has stopped or crashed"
                        else:
                            error_msg = "Server is not responding (connection refused)"
                    except Exception:
                        pass
            error_result = {"success": False, "error": error_msg}
            self._log_tool_result(endpoint, error_result)
            return error_result
        except requests.exceptions.RequestException as e:
            error_result = {"success": False, "error": f"Request failed: {str(e)}"}
            self._log_tool_result(endpoint, error_result)
            return error_result
        except json.JSONDecodeError:
            error_result = {"success": False, "error": "Invalid JSON response from server"}
            self._log_tool_result(endpoint, error_result)
            return error_result

    # Tool Interface

    def tools(self, selection_list: List[str]) -> List[Callable]:
        """
        Get wrapped tool functions based on selection list.

        Args:
            selection_list: List of tool names (e.g., ["read_file", "write_file", "edit_file", "run_command"])

        Returns:
            List of wrapped tool functions in the same order as selection_list

        Usage:
            tools = client.tools(selection_list=["read_file", "write_file", "edit_file", "run_command"])
            read, write, edit, run_command = tools
        """
        # Map tool names to their wrapped versions
        tool_map = {
            "read_file": self._create_read_tool(),
            "write_file": self._create_write_tool(),
            "edit_file": self._create_edit_tool(),
            "run_command": self._create_run_tool()
        }

        return [tool_map[name] for name in selection_list]

    def _create_read_tool(self) -> Callable:
        """Create read tool function with docstring from tools/read.py"""
        def read_file_tool(file_path: str, lines_start: Optional[int] = None,
                          lines_end: Optional[int] = None, regex: Optional[str] = None) -> Dict[str, Any]:
            data = {"file_path": file_path}

            # Add optional parameters if provided
            if lines_start is not None:
                data["lines_start"] = lines_start
            if lines_end is not None:
                data["lines_end"] = lines_end
            if regex is not None:
                data["regex"] = regex

            return self._make_request("read", data)

        # Copy docstring from actual ReadTool.read_file method
        read_file_tool.__doc__ = ReadTool.read_file.__doc__
        read_file_tool.__name__ = "read_file"

        return read_file_tool

    def _create_write_tool(self) -> Callable:
        """Create write tool function with docstring from tools/write.py"""
        def write_file_tool(file_path: str, content: str) -> Dict[str, Any]:
            data = {"file_path": file_path, "content": content}
            return self._make_request("write", data)

        # Copy docstring from actual WriteTool.write_file method
        write_file_tool.__doc__ = WriteTool.write_file.__doc__
        write_file_tool.__name__ = "write_file"

        return write_file_tool

    def _create_edit_tool(self) -> Callable:
        """Create edit tool function with docstring from tools/edit.py"""
        def edit_file_tool(file_path: str, old_string: str, new_string: str,
                          replace_all: bool = False) -> Dict[str, Any]:
            data = {
                "file_path": file_path,
                "old_string": old_string,
                "new_string": new_string,
                "replace_all": replace_all
            }
            return self._make_request("edit", data)

        # Copy docstring from actual EditTool.edit_file method
        edit_file_tool.__doc__ = EditTool.edit_file.__doc__
        edit_file_tool.__name__ = "edit_file"

        return edit_file_tool

    def _create_run_tool(self) -> Callable:
        """Create run tool function with docstring from tools/run.py"""
        def run_command_tool(command: str, timeout: int = 300, interactive: bool = False) -> Dict[str, Any]:
            data = {
                "command": command,
                "timeout": timeout,
                "interactive": interactive
            }

            # For very long timeouts, use polling approach to avoid HTTP timeouts
            if timeout > 3600:  # 1 hour
                return self._run_command_with_polling(data)
            else:
                return self._make_request("run", data)

        # Copy docstring from actual RunTool.run_command method
        run_command_tool.__doc__ = RunTool.run_command.__doc__
        run_command_tool.__name__ = "run_command"

        return run_command_tool

    def get_output(self, max_lines: int = 100) -> Dict[str, Any]:
        """Get output from active interactive process."""
        data = {"max_lines": max_lines}
        return self._make_request("get_output", data)

    def send_input(self, input_text: str) -> Dict[str, Any]:
        """Send input to active interactive process."""
        data = {"input_text": input_text}
        return self._make_request("send_input", data)

    def stop_process(self, force: bool = False) -> Dict[str, Any]:
        """Stop active interactive process."""
        data = {"force": force}
        return self._make_request("stop_process", data)

    def get_process_status(self) -> Dict[str, Any]:
        """Get status of active process."""
        return self._make_request("get_status", method='GET')

    # Server Management

    def get_status(self) -> Dict[str, Any]:
        """Get server status."""
        return self._make_request("status", method='GET')

    def stop_server(self) -> bool:
        """Stop the Docker server."""
        if self.docker_container:
            try:
                result = subprocess.run(['docker', 'stop', self.docker_container],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    subprocess.run(['docker', 'rm', self.docker_container],
                                 capture_output=True, text=True)
                    self.docker_container = None
                    return True
            except Exception as e:
                logging.error(f"Failed to stop server: {e}")

        return False

    def restart_server(self) -> bool:
        """Restart the Docker server."""
        self.stop_server()
        time.sleep(2)
        return self._ensure_server_running()

    # Context Manager Support

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Export logs before stopping server
        if self.log_folder:
            self.export_logs()
        self.stop_server()

