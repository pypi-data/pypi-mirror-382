"""
Run Tool - 2-State command execution for AI agents.

Features:
- Single run_command() entry point with unified command handling
- States: IDLE (no process) and RUNNING (active process)
- Non-interactive: Auto-kill on timeout, return results immediately
- Interactive: Wait for timeout, return output + control choices
- Special command handling: '', 'C-c', '>>> input', new commands
- Automatic state refresh and process completion detection
"""

import os
import subprocess
import time
import select
import sys
import threading
import queue
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class RunTool:
    """2-State command execution tool with unified interface."""

    def __init__(self):
        self.active_process: Optional[Dict] = None  # Process info when RUNNING
        self.last_output_time: Optional[datetime] = None  # Track output collection
        self.completed_process_output: Optional[Dict] = None  # Output from completed process
        self.default_timeout = 300

    def _force_cleanup_and_reset(self):
        """Force complete cleanup and reset of tool state."""
        if self.active_process is not None:
            try:
                process = self.active_process["process"]
                # Force terminate/kill any running process
                try:
                    process.terminate()
                    process.wait(timeout=2.0)
                except (subprocess.TimeoutExpired, Exception):
                    try:
                        process.kill()
                        process.wait(timeout=1.0)
                    except:
                        pass
            except:
                pass

        # Reset all state
        self.active_process = None
        self.last_output_time = None
        self.completed_process_output = None

    def _format_duration(self, duration_seconds: float) -> str:
        """Format duration in human readable format."""
        if duration_seconds < 1:
            return f"{duration_seconds:.2f}sec"
        elif duration_seconds < 60:
            return f"{duration_seconds:.1f}sec"
        else:
            minutes = int(duration_seconds // 60)
            seconds = duration_seconds % 60
            return f"{minutes}m {seconds:.1f}sec"

    def _combine_output(self, stdout: str, stderr: str, exit_code: Optional[int] = None) -> str:
        """Combine stdout/stderr with exit code prepended."""
        output_parts = []

        # Prepend exit code if available
        if exit_code is not None:
            output_parts.append(f"Exit code: {exit_code}")

        # Add stdout if present
        if stdout and stdout.strip():
            output_parts.append(stdout.strip())

        # Add stderr if present
        if stderr and stderr.strip():
            output_parts.append(stderr.strip())

        return "\n".join(output_parts)

    def run_command(
        self,
        command: str,
        timeout: int = 300,
        interactive: bool = False
    ) -> Dict[str, Any]:
        """
        Execute shell commands in the Docker workspace environment.

        SUCCESS MEANING:
        - success=True: Command executed (exit code 0 or non-zero doesn't matter)
        - success=False: Tool error (timeout, invalid state, process management issue)

        MODES:

        NON-INTERACTIVE (default, interactive=False):
        - Use for: Quick commands that complete in seconds
        - Behavior: Runs command, waits for completion (up to timeout)
        - On timeout: Automatically kills process and returns partial output
        - Examples: ls, cat, grep, python script.py, npm install

        INTERACTIVE (interactive=True):
        - Use for: Long-running commands, training loops, servers
        - Behavior: Runs command, returns control after timeout with options
        - On timeout: Keeps process running, you can continue/kill/send input
        - Examples: python train.py, npm start, watch mode commands

        EXAMPLES:

        # Basic commands (non-interactive)
        run_command('ls -la /workspace')
        run_command('python test.py', timeout=60)
        run_command('cat /workspace/config.json')
        run_command('grep -r "TODO" /workspace', timeout=30)

        # Long-running commands (interactive)
        run_command('python train.py --epochs 100', timeout=300, interactive=True)
        # ... after timeout, returns with control options ...
        run_command('')  # Continue for another timeout period
        run_command('C-c')  # Kill the process

        # Commands with input (interactive)
        run_command('python -c "x = input(\\'Enter: \\'); print(x)"',
                    timeout=30, interactive=True)
        # ... after timeout ...
        run_command('>>> hello')  # Send "hello" as input

        # Install packages
        run_command('pip install numpy pandas', timeout=120)
        run_command('npm install', timeout=180)

        # File operations
        run_command('mkdir -p /workspace/data')
        run_command('cp source.txt dest.txt')
        run_command('rm -rf /tmp/cache')

        # Git operations
        run_command('git status')
        run_command('git diff HEAD~1')

        CONTROL COMMANDS (use after interactive timeout):
        - '' (empty string): Continue process for another timeout period
        - 'C-c': Kill the running process immediately
        - '>>> text': Send "text" as input to the process (like typing and pressing Enter)

        IMPORTANT NOTES:
        - Commands run in Docker container at /workspace directory
        - Timeout in seconds (default 300 = 5 minutes)
        - Output includes both stdout and stderr combined
        - Exit code is prepended to output (e.g., "Exit code: 0")
        - Process is fully cleaned up after completion/timeout/kill
        - Only ONE command can run at a time

        CHOOSING TIMEOUT:
        - Quick commands (ls, cat, grep): 10-30 seconds
        - Package installs (pip, npm): 120-300 seconds
        - Tests/builds: 60-600 seconds
        - Training/long tasks: 300-3600 seconds (use interactive=True)

        UNDERSTANDING OUTPUT:
        The "output" field contains:
        - Exit code (e.g., "Exit code: 0" or "Exit code: 1")
        - Combined stdout and stderr

        The "message" field contains:
        - Execution time (e.g., "executed in 2.5sec")
        - Process status (e.g., "Process finished and cleaned")
        - Control suggestions if interactive timeout

        RETURN FORMAT:
        {
            "success": true/false,
            "output": "Exit code: 0\\ncommand output here...",
            "message": "executed in 5.2sec\\nProcess finished and cleaned"
        }

        COMMON PATTERNS:
        # Check if file exists
        run_command('test -f /workspace/file.txt && echo "exists" || echo "not found"')

        # Count lines in file
        run_command('wc -l /workspace/data.csv')

        # Find files
        run_command('find /workspace -name "*.py"')

        # Run tests
        run_command('pytest tests/', timeout=120)

        # Start training (interactive)
        run_command('python train.py', timeout=600, interactive=True)

        Args:
            command: Shell command to execute or control command ('', 'C-c', '>>> input')
            timeout: Maximum time in seconds before returning control (default: 300)
            interactive: False=auto-kill on timeout, True=return control with options
        Returns:
            Dict with success, output (with exit code), and execution message
        """
        # Step 1: Check current state
        current_state = self._get_state()

        # Step 2: Refresh state (detect completion)
        state_changed = self._refresh_state()

        # Step 3: Get new state after refresh
        new_state = self._get_state()

        # Step 4: Route command based on state and command type
        if command.startswith('>>> '):
            return self._handle_input(command[4:], timeout, current_state, new_state)
        elif command == 'C-c':
            return self._handle_kill(current_state, new_state)
        elif command == '':
            return self._handle_continue(timeout, current_state, new_state)
        else:
            return self._handle_new_command(command, timeout, interactive, current_state, new_state)

    def _get_state(self) -> str:
        """Get current state: IDLE or RUNNING."""
        return "RUNNING" if self.active_process is not None else "IDLE"

    def _refresh_state(self) -> bool:
        """Check if RUNNING process has completed. Returns True if state changed."""
        if self.active_process is None:
            return False

        process = self.active_process["process"]
        return_code = process.poll()

        if return_code is not None:
            # Process completed - mark completion and preserve output for later retrieval
            self._mark_process_completed()

            # Save the completed process info for unread output handling
            self.completed_process_output = self._get_unread_output()

            # Clear active process to transition to IDLE state
            self.active_process = None
            return True  # State changed from RUNNING to IDLE

        return False  # Still running

    def _collect_available_output(self):
        """Enhanced non-blocking collection of available output optimized for Linux/WSL."""
        if self.active_process is None:
            return [], []

        process = self.active_process["process"]
        proc_info = self.active_process
        new_stdout = []
        new_stderr = []

        try:
            # Linux/WSL optimized approach with better timing
            import select
            import sys

            # Use threading approach for reliable output collection
            # Increased timeout for better WSL/Linux compatibility
            try:
                if process.stdout.readable():
                    import threading
                    import queue

                    def read_lines_robust(pipe, q, max_lines=10):
                        """Read multiple lines with better error handling."""
                        try:
                            lines_read = 0
                            while lines_read < max_lines:
                                line = pipe.readline()
                                if line:
                                    q.put(line.rstrip())
                                    lines_read += 1
                                else:
                                    break
                        except:
                            pass

                    # Try stdout with increased timeout
                    q = queue.Queue()
                    t = threading.Thread(target=read_lines_robust, args=(process.stdout, q))
                    t.daemon = True
                    t.start()
                    t.join(0.2)  # Increased from 50ms to 200ms for better WSL compatibility

                    try:
                        while True:
                            line = q.get_nowait()
                            new_stdout.append(line)
                            proc_info["stdout_lines"].append(line)
                    except queue.Empty:
                        pass

                    # Try stderr with increased timeout
                    q = queue.Queue()
                    t = threading.Thread(target=read_lines_robust, args=(process.stderr, q))
                    t.daemon = True
                    t.start()
                    t.join(0.2)  # Increased from 50ms to 200ms for better WSL compatibility

                    try:
                        while True:
                            line = q.get_nowait()
                            new_stderr.append(line)
                            proc_info["stderr_lines"].append(line)
                    except queue.Empty:
                        pass

            except:
                # Fallback to select-based approach
                try:
                    ready, _, _ = select.select([process.stdout, process.stderr], [], [], 0.2)

                    for pipe in ready:
                        try:
                            # Try to read multiple lines when available
                            for _ in range(5):  # Read up to 5 lines per call
                                line = pipe.readline()
                                if line:
                                    line = line.rstrip()
                                    if pipe == process.stdout:
                                        new_stdout.append(line)
                                        proc_info["stdout_lines"].append(line)
                                    else:
                                        new_stderr.append(line)
                                        proc_info["stderr_lines"].append(line)
                                else:
                                    break
                        except:
                            pass
                except:
                    pass

        except:
            # If anything fails, just return what we have
            pass

        return new_stdout, new_stderr

    def _mark_process_completed(self):
        """Mark process as completed without complex output collection."""
        if self.active_process is None:
            return

        process = self.active_process["process"]
        proc_info = self.active_process

        # Just mark the completion - don't try to collect remaining output
        proc_info["end_time"] = datetime.now()
        proc_info["return_code"] = process.returncode

    def _get_unread_output(self) -> Dict[str, Any]:
        """Get output since last collection time."""
        if self.active_process is None:
            # If no active process, check if we have saved completed process output
            if self.completed_process_output is not None:
                output = self.completed_process_output
                self.completed_process_output = None  # Clear after retrieval
                return output
            return {"stdout": [], "stderr": []}

        proc_info = self.active_process
        last_time = self.last_output_time or proc_info["start_time"]

        # For now, return all output (can be refined to track read positions)
        return {
            "stdout": proc_info["stdout_lines"],
            "stderr": proc_info["stderr_lines"],
            "return_code": proc_info.get("return_code"),
            "duration": (proc_info.get("end_time", datetime.now()) - proc_info["start_time"]).total_seconds()
        }

    def _handle_new_command(self, command: str, timeout: int, interactive: bool,
                           current_state: str, new_state: str) -> Dict[str, Any]:
        """Handle new command execution based on state."""
        # Check for state transition (RUNNING -> IDLE)
        if current_state == "RUNNING" and new_state == "IDLE":
            # Process just completed, force cleanup and reject new command
            self._force_cleanup_and_reset()
            return {
                "success": False,
                "output": "",
                "message": "tool error: previous command completed with unread output\nPlease try your command again"
            }

        # Reject if still RUNNING
        if new_state == "RUNNING":
            active_cmd = self.active_process.get("command", "unknown") if self.active_process else "unknown"
            return {
                "success": False,
                "output": "",
                "message": f"tool error: another command running ({active_cmd})\nUse '' to continue, 'C-c' to kill, or '>>> input' to send input"
            }

        # State is IDLE, can execute new command
        if interactive:
            return self._start_interactive(command, timeout)
        else:
            return self._run_non_interactive(command, timeout)

    def _handle_continue(self, timeout: int, current_state: str, new_state: str) -> Dict[str, Any]:
        """Handle continue command ('')."""
        if current_state == "IDLE":
            return {
                "success": False,
                "output": "",
                "message": "tool error: no active process to continue\nStart an interactive command first"
            }

        if current_state == "RUNNING" and new_state == "IDLE":
            # Process completed during gap
            unread_output = self._get_unread_output()
            stdout_lines = unread_output.get("stdout", [])
            stderr_lines = unread_output.get("stderr", [])
            stdout = "\n".join(stdout_lines) if stdout_lines else ""
            stderr = "\n".join(stderr_lines) if stderr_lines else ""
            exit_code = unread_output.get("return_code", 0)
            duration = unread_output.get("duration", 0)

            self._force_cleanup_and_reset()

            output = self._combine_output(stdout, stderr, exit_code)
            message = f"executed in {self._format_duration(duration)}\nProcess completed during wait and cleaned"

            return {
                "success": True,
                "output": output,
                "message": message
            }

        # Process still running, wait for timeout
        return self._wait_and_collect_output(timeout)

    def _handle_kill(self, current_state: str, new_state: str) -> Dict[str, Any]:
        """Handle kill command ('C-c')."""
        if current_state == "IDLE":
            return {
                "success": False,
                "output": "",
                "message": "tool error: no active process to kill\nNo process is currently running"
            }

        if current_state == "RUNNING" and new_state == "IDLE":
            # Process already completed
            unread_output = self._get_unread_output()
            stdout_lines = unread_output.get("stdout", [])
            stderr_lines = unread_output.get("stderr", [])
            stdout = "\n".join(stdout_lines) if stdout_lines else ""
            stderr = "\n".join(stderr_lines) if stderr_lines else ""
            exit_code = unread_output.get("return_code", 0)
            duration = unread_output.get("duration", 0)

            self._force_cleanup_and_reset()

            output = self._combine_output(stdout, stderr, exit_code)
            message = f"executed in {self._format_duration(duration)}\nProcess had already completed and cleaned"

            return {
                "success": True,
                "output": output,
                "message": message
            }

        # Process is still running, kill it
        return self._kill_process()

    def _handle_input(self, input_text: str, timeout: int, current_state: str, new_state: str) -> Dict[str, Any]:
        """Handle input command ('>>> text')."""
        if current_state == "IDLE":
            return {
                "success": False,
                "output": "",
                "message": "tool error: no active process to send input to\nStart an interactive command first"
            }

        if current_state == "RUNNING" and new_state == "IDLE":
            # Process completed, input not applicable
            unread_output = self._get_unread_output()
            stdout_lines = unread_output.get("stdout", [])
            stderr_lines = unread_output.get("stderr", [])
            stdout = "\n".join(stdout_lines) if stdout_lines else ""
            stderr = "\n".join(stderr_lines) if stderr_lines else ""
            exit_code = unread_output.get("return_code", 0)

            self._force_cleanup_and_reset()

            output = self._combine_output(stdout, stderr, exit_code)
            message = "tool error: command completed, input not applicable\nProcess finished before input could be sent"

            return {
                "success": False,
                "output": output,
                "message": message
            }

        # Send input and wait for timeout
        return self._send_input_and_wait(input_text, timeout)

    def _run_non_interactive(self, command: str, timeout: int) -> Dict[str, Any]:
        """Execute command in non-interactive mode with complete cleanup and simplified output."""
        start_time = datetime.now()
        process = None

        try:
            # Use Popen for better control
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            try:
                # Try to complete normally within timeout
                stdout, stderr = process.communicate(timeout=timeout)
                duration = (datetime.now() - start_time).total_seconds()

                # Successful execution (regardless of exit code)
                output = self._combine_output(stdout, stderr, process.returncode)
                message = f"executed in {self._format_duration(duration)}\nProcess finished and cleaned"

                return {
                    "success": True,
                    "output": output,
                    "message": message
                }

            except subprocess.TimeoutExpired:
                # Timeout - collect what we can and force cleanup
                duration = (datetime.now() - start_time).total_seconds()
                collected_stdout = ""
                collected_stderr = ""

                try:
                    # Try gentle termination first
                    process.terminate()
                    stdout, stderr = process.communicate(timeout=2.0)
                    collected_stdout = stdout or ""
                    collected_stderr = stderr or ""
                except subprocess.TimeoutExpired:
                    # Force kill
                    try:
                        process.kill()
                        stdout, stderr = process.communicate(timeout=1.0)
                        collected_stdout = stdout or ""
                        collected_stderr = stderr or ""
                    except:
                        pass

                # Tool error - timeout
                output = self._combine_output(collected_stdout, collected_stderr, -1)
                message = f"tool error: timeout after {self._format_duration(timeout)}\nProcess killed and cleaned"

                return {
                    "success": False,
                    "output": output,
                    "message": message
                }

        except Exception as e:
            # Tool error - execution failed
            duration = (datetime.now() - start_time).total_seconds()
            return {
                "success": False,
                "output": "",
                "message": f"tool error: execution failed - {str(e)}\nDuration: {self._format_duration(duration)}"
            }

        finally:
            # Ensure complete cleanup
            if process is not None:
                try:
                    if process.poll() is None:  # Still running
                        process.kill()
                        process.wait(timeout=1.0)
                except:
                    pass

            # Force reset tool state
            self._force_cleanup_and_reset()

    def _start_interactive(self, command: str, timeout: int) -> Dict[str, Any]:
        """Start interactive command with simplified output format."""
        start_time = datetime.now()

        try:
            # Start process
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Store active process info
            self.active_process = {
                "process": process,
                "command": command,
                "start_time": start_time,
                "timeout": timeout,
                "stdout_lines": [],
                "stderr_lines": [],
                "last_output_time": start_time
            }

            # Wait for timeout and collect output
            return self._wait_and_collect_output(timeout)

        except Exception as e:
            # Ensure cleanup
            self._force_cleanup_and_reset()
            duration = (datetime.now() - start_time).total_seconds()

            return {
                "success": False,
                "output": "",
                "message": f"tool error: failed to start command - {str(e)}\nDuration: {self._format_duration(duration)}"
            }

    def _wait_and_collect_output(self, timeout: int) -> Dict[str, Any]:
        """Simplified output collection with timeout for interactive mode."""
        if self.active_process is None:
            return {
                "success": False,
                "output": "",
                "message": "tool error: no active process"
            }

        process = self.active_process["process"]
        proc_info = self.active_process
        start_time = proc_info.get("start_time", datetime.now())

        # Track what output we had before this timeout period
        gap_start_lines_stdout = len(proc_info.get("stdout_lines", []))
        gap_start_lines_stderr = len(proc_info.get("stderr_lines", []))

        timeout_start = datetime.now()
        timeout_end = timeout_start + timedelta(seconds=timeout)

        try:
            # Wait and collect output until timeout or completion
            while datetime.now() < timeout_end:
                return_code = process.poll()
                if return_code is not None:
                    # Process completed - collect final output and cleanup
                    try:
                        remaining_stdout, remaining_stderr = process.communicate(timeout=2.0)
                        if remaining_stdout and remaining_stdout.strip():
                            for line in remaining_stdout.split('\n'):
                                if line.strip():
                                    proc_info.setdefault("stdout_lines", []).append(line.rstrip())
                        if remaining_stderr and remaining_stderr.strip():
                            for line in remaining_stderr.split('\n'):
                                if line.strip():
                                    proc_info.setdefault("stderr_lines", []).append(line.rstrip())
                    except:
                        self._collect_available_output()

                    # Get all output and calculate duration
                    all_stdout = "\n".join(proc_info.get("stdout_lines", []))
                    all_stderr = "\n".join(proc_info.get("stderr_lines", []))
                    duration = (datetime.now() - start_time).total_seconds()

                    # Force cleanup
                    self._force_cleanup_and_reset()

                    output = self._combine_output(all_stdout, all_stderr, return_code)
                    message = f"executed in {self._format_duration(duration)}\nProcess completed and cleaned"

                    return {
                        "success": True,
                        "output": output,
                        "message": message
                    }

                # Collect available output periodically
                self._collect_available_output()
                time.sleep(0.1)

            # Timeout reached - process still running
            # Get output since the start of this timeout period
            all_stdout = proc_info.get("stdout_lines", [])
            all_stderr = proc_info.get("stderr_lines", [])
            new_stdout = all_stdout[gap_start_lines_stdout:]
            new_stderr = all_stderr[gap_start_lines_stderr:]

            # Final collection attempt
            for _ in range(3):
                self._collect_available_output()
                time.sleep(0.05)

            # Update with any additional output collected
            updated_stdout = proc_info.get("stdout_lines", [])
            updated_stderr = proc_info.get("stderr_lines", [])
            final_new_stdout = updated_stdout[gap_start_lines_stdout:]
            final_new_stderr = updated_stderr[gap_start_lines_stderr:]

            # Combine new output from this timeout period
            stdout_text = "\n".join(final_new_stdout) if final_new_stdout else ""
            stderr_text = "\n".join(final_new_stderr) if final_new_stderr else ""

            output = self._combine_output(stdout_text, stderr_text, None)

            elapsed = (datetime.now() - timeout_start).total_seconds()
            message = f"timeout after {self._format_duration(elapsed)}\nUse '' to continue, 'C-c' to kill, or '>>> input' to send input"

            return {
                "success": True,
                "output": output,
                "message": message
            }

        except Exception as e:
            self._force_cleanup_and_reset()
            return {
                "success": False,
                "output": "",
                "message": f"tool error: output collection failed - {str(e)}\nForced cleanup completed"
            }

    def _send_input_and_wait(self, input_text: str, timeout: int) -> Dict[str, Any]:
        """Send input to process and wait for timeout with simplified output."""
        if self.active_process is None:
            return {
                "success": False,
                "output": "",
                "message": "tool error: no active process"
            }

        try:
            process = self.active_process["process"]

            # Send input
            process.stdin.write(input_text + '\n')
            process.stdin.flush()

            # Give time for input processing
            time.sleep(0.5)

            # Wait for timeout and collect output
            return self._wait_and_collect_output(timeout)

        except Exception as e:
            self._force_cleanup_and_reset()
            return {
                "success": False,
                "output": "",
                "message": f"tool error: failed to send input - {str(e)}\nForced cleanup completed"
            }

    def _kill_process(self) -> Dict[str, Any]:
        """Kill the active process with simplified output format."""
        if self.active_process is None:
            return {
                "success": False,
                "output": "",
                "message": "tool error: no active process to kill"
            }

        try:
            process = self.active_process["process"]
            start_time = self.active_process.get("start_time", datetime.now())
            proc_info = self.active_process

            # Collect any final output before killing
            self._collect_available_output()
            stdout_lines = proc_info.get("stdout_lines", [])
            stderr_lines = proc_info.get("stderr_lines", [])

            # Progressive termination with output collection
            collected_stdout = ""
            collected_stderr = ""
            method = "terminated"

            try:
                # First try terminate
                process.terminate()
                stdout, stderr = process.communicate(timeout=2.0)
                collected_stdout = stdout or ""
                collected_stderr = stderr or ""
                method = "terminated"
            except subprocess.TimeoutExpired:
                try:
                    # Force kill if terminate didn't work
                    process.kill()
                    stdout, stderr = process.communicate(timeout=1.0)
                    collected_stdout = stdout or ""
                    collected_stderr = stderr or ""
                    method = "force killed"
                except:
                    method = "force killed (no response)"

            # Combine all output
            all_stdout = "\n".join(stdout_lines)
            all_stderr = "\n".join(stderr_lines)
            if collected_stdout.strip():
                all_stdout += "\n" + collected_stdout.strip() if all_stdout else collected_stdout.strip()
            if collected_stderr.strip():
                all_stderr += "\n" + collected_stderr.strip() if all_stderr else collected_stderr.strip()

            duration = (datetime.now() - start_time).total_seconds()

            # Force cleanup
            self._force_cleanup_and_reset()

            output = self._combine_output(all_stdout, all_stderr, -9)
            message = f"executed in {self._format_duration(duration)}\nProcess {method} and cleaned"

            return {
                "success": True,
                "output": output,
                "message": message
            }

        except Exception as e:
            self._force_cleanup_and_reset()
            return {
                "success": False,
                "output": "",
                "message": f"tool error: failed to kill process - {str(e)}\nForced cleanup completed"
            }

    # Legacy methods for compatibility (these should not be used with new 2-state design)
    def get_output(self, max_lines: int = 100) -> Dict[str, Any]:
        """Legacy method - should not be used with 2-state design."""
        return {
            "success": False,
            "output": "",
            "message": "tool error: get_output() is deprecated\nUse '' to continue, 'C-c' to kill, or '>>> input' to send input"
        }

    def send_input(self, input_text: str) -> Dict[str, Any]:
        """Legacy method - should not be used with 2-state design."""
        return {
            "success": False,
            "output": "",
            "message": f"tool error: send_input() is deprecated\nUse run_command('>>> {input_text}', timeout, True) instead"
        }

    def stop_process(self, force: bool = False) -> Dict[str, Any]:
        """Legacy method - should not be used with 2-state design."""
        return {
            "success": False,
            "output": "",
            "message": "tool error: stop_process() is deprecated\nUse run_command('C-c', timeout, True) instead"
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current tool status with simplified output."""
        state = self._get_state()

        if state == "IDLE":
            return {
                "success": True,
                "output": "State: IDLE",
                "message": "No active process"
            }

        # Refresh state first
        self._refresh_state()
        current_state = self._get_state()

        if current_state == "IDLE":
            return {
                "success": True,
                "output": "State: IDLE",
                "message": "Process just completed"
            }

        proc_info = self.active_process
        if proc_info:
            runtime = (datetime.now() - proc_info["start_time"]).total_seconds()
            pid = proc_info["process"].pid
            command = proc_info["command"]
            stdout_lines = len(proc_info.get("stdout_lines", []))
            stderr_lines = len(proc_info.get("stderr_lines", []))

            output = f"State: RUNNING\nPID: {pid}\nCommand: {command}\nOutput lines: {stdout_lines} stdout, {stderr_lines} stderr"
            message = f"running for {self._format_duration(runtime)}"

            return {
                "success": True,
                "output": output,
                "message": message
            }
        else:
            return {
                "success": True,
                "output": "State: IDLE",
                "message": "Process status unknown"
            }

