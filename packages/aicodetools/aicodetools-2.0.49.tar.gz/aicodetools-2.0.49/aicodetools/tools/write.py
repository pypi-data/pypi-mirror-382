"""
Write Tool - Simplified file writing for AI agents.

Features:
- Single write_file function with automatic backup
- Read-first safety for existing non-empty files
- Fixed UTF-8 encoding (best for Linux)
- Clear error messages with suggestions
"""

import os
import shutil
from typing import Dict, Any, Set
from datetime import datetime


class WriteTool:
    """Simplified file writing tool optimized for AI agents."""

    def __init__(self):
        self.read_files: Set[str] = set()  # Track files that have been read

    def mark_file_as_read(self, file_path: str) -> None:
        """Mark a file as having been read (for safety checks)."""
        self.read_files.add(os.path.abspath(file_path))

    def is_empty_or_new(self, file_path: str) -> bool:
        """Check if file is new or empty."""
        return not os.path.exists(file_path) or os.path.getsize(file_path) == 0

    def has_been_read(self, file_path: str) -> bool:
        """Check if file has been read."""
        return os.path.abspath(file_path) in self.read_files

    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file (creates new or overwrites existing).

        WHEN TO USE:
        - Creating new files: scripts, configs, data files
        - Complete file replacement: when rewriting entire file
        - Writing generated content: code generation, templates

        WHEN NOT TO USE:
        - Small changes to existing files → Use edit_file instead
        - Appending to files → Use edit_file or run_command
        - Partial modifications → Use edit_file for targeted changes

        EXAMPLES:
        # Create new file
        write_file('/workspace/hello.py', 'print("Hello, World!")')

        # Create config file
        write_file('/workspace/config.json', '{"debug": true, "port": 8080}')

        # Write multi-line content
        write_file('/workspace/script.sh', '''#!/bin/bash
echo "Starting script"
python main.py
echo "Done"''')

        # Overwrite existing file (after reading it first)
        write_file('/workspace/settings.py', new_content)

        IMPORTANT NOTES:
        - File path must be absolute (e.g., /workspace/file.py)
        - Overwrites entire file content (not append)
        - Creates parent directories automatically if needed
        - SAFETY: Must read existing non-empty files first before overwriting
        - Preserves file with automatic backup during write

        COMMON USE CASES:
        - Generated code: write_file('/workspace/gen_code.py', generated_code)
        - Test files: write_file('/workspace/test_input.txt', test_data)
        - Configs: write_file('/workspace/.env', env_vars)
        - Scripts: write_file('/workspace/run.sh', bash_script)

        SAFETY MECHANISM:
        If file exists and has content, you MUST read it first using read_file()
        before overwriting. This prevents accidental data loss.

        RETURN FORMAT:
        {
            "success": true/false,
            "message": "File written: /workspace/file.py (123 bytes)"
        }

        Args:
            file_path: Absolute path where to write (e.g., /workspace/file.py)
            content: Complete file content as string
        Returns:
            Dict with success status and confirmation message
        """
        try:
            abs_path = os.path.abspath(file_path)

            # Check if file is empty/new vs has content
            if self.is_empty_or_new(abs_path):
                # Empty or new file - can write directly
                needs_backup = False
                safety_check_passed = True
            else:
                # File has content - check if it's been read first
                if not self.has_been_read(abs_path):
                    return {
                        "success": False,
                        "error": f"File not read first - read the file before modifying: {file_path}",
                        "suggestions": [
                            "Use read_file() to examine content first",
                            "This prevents accidental overwrites of important files"
                        ]
                    }
                needs_backup = True
                safety_check_passed = True

            # Create directory if it doesn't exist
            directory = os.path.dirname(abs_path)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to create directory: {directory}",
                        "details": str(e)
                    }

            # Create backup if needed
            backup_path = None
            if needs_backup:
                backup_path = self._create_backup(abs_path)

            # Write the file with UTF-8 encoding
            try:
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Calculate metadata
                file_size = os.path.getsize(abs_path)
                line_count = content.count('\n') + 1 if content else 0
                bytes_written = len(content.encode('utf-8'))

                # Mark file as read since we just wrote to it
                self.mark_file_as_read(abs_path)

                response = {
                    "success": True,
                    "file_path": file_path,
                    "bytes_written": bytes_written,
                    "file_size": file_size,
                    "line_count": line_count,
                    "created_new": not needs_backup
                }

                if backup_path:
                    response["backup_created"] = backup_path

                action = "created" if not needs_backup else "updated"
                response["message"] = f"File {action} successfully. {line_count} lines, {bytes_written} bytes."

                return response

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to write file: {str(e)}",
                    "suggestions": [
                        "Check file permissions",
                        "Ensure file is not locked by another process",
                        "Verify sufficient disk space"
                    ]
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Write operation failed: {str(e)}",
                "suggestions": [
                    "Check if file path is valid",
                    "Ensure parent directory exists and is writable"
                ]
            }

    def _create_backup(self, file_path: str) -> str:
        """Create a timestamped backup of an existing file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"

        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception:
            # If backup fails, return None but don't prevent the write operation
            return None