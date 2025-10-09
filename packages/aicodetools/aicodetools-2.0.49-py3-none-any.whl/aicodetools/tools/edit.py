"""
Edit Tool - Simplified file editing for AI agents.

Features:
- Simple string find-and-replace with automatic backup
- Read-first safety check
- Support for single or all occurrences
- Clear diff preview of changes
- Fixed UTF-8 encoding
"""

import os
import difflib
import shutil
from typing import Dict, Any, Set
from datetime import datetime


class EditTool:
    """Simplified file editing tool optimized for AI agents."""

    def __init__(self):
        self.read_files: Set[str] = set()

    def mark_file_as_read(self, file_path: str) -> None:
        """Mark a file as having been read (for safety checks)."""
        self.read_files.add(os.path.abspath(file_path))

    def has_been_read(self, file_path: str) -> bool:
        """Check if file has been read."""
        return os.path.abspath(file_path) in self.read_files

    def edit_file(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> Dict[str, Any]:
        """
        Make precise string replacements in files (for targeted changes).

        WHEN TO USE:
        - Small targeted changes: fix bugs, update values, modify specific lines
        - Refactoring: rename variables/functions throughout file
        - Multi-line edits: change function signatures, update blocks

        WHEN NOT TO USE:
        - Creating new files → Use write_file
        - Complete file rewrites → Use write_file
        - Very large replacements (>100 lines) → Use write_file

        CRITICAL REQUIREMENTS FOR SUCCESS:
        1. MUST read the file first using read_file() to see exact formatting
        2. Copy the EXACT text from read output including ALL whitespace
        3. Include enough surrounding context to make old_string unique in the file
        4. Preserve indentation exactly (spaces vs tabs matter!)

        EXAMPLES:
        # Single line change
        edit_file('/workspace/config.py',
                  'DEBUG = True',
                  'DEBUG = False')

        # Multi-line function edit
        edit_file('/workspace/utils.py',
                  '''def process_data(x):
    return x * 2''',
                  '''def process_data(x, multiplier=2):
    return x * multiplier''')

        # Rename all occurrences
        edit_file('/workspace/main.py',
                  'old_function_name',
                  'new_function_name',
                  replace_all=True)

        # Change with context (more reliable)
        edit_file('/workspace/app.py',
                  '''    if user.is_active:
        return True''',
                  '''    if user.is_active and user.verified:
        return True''')

        IMPORTANT NOTES:
        - File path must be absolute (e.g., /workspace/file.py)
        - replace_all=False: Replaces FIRST occurrence only (safer, default)
        - replace_all=True: Replaces ALL occurrences (use for renaming)
        - Always read file first to verify exact formatting
        - Preserves file with automatic backup during edit

        COMMON PITFALLS:
        ❌ Don't guess formatting - read file first
        ❌ Don't forget leading/trailing whitespace
        ❌ Don't use when old_string appears multiple times (unless replace_all=True)
        ✅ Do copy exact text from read_file output
        ✅ Do include context for unique matching
        ✅ Do verify indentation (spaces vs tabs)

        WORKFLOW:
        1. read_file() to see current content
        2. Copy EXACT text you want to change (including whitespace)
        3. Prepare new_string with desired changes
        4. Call edit_file() with exact old_string and new_string
        5. Optionally read_file() again to verify the change

        RETURN FORMAT:
        {
            "success": true/false,
            "message": "Edit completed: 1 replacement made",
            "replacements_made": 1
        }

        Args:
            file_path: Absolute path to file (e.g., /workspace/main.py)
            old_string: Exact text to find and replace (copy from read_file output)
            new_string: New text to insert
            replace_all: False (first only) or True (all occurrences)
        Returns:
            Dict with success status, replacement count, and message
        """
        try:
            abs_path = os.path.abspath(file_path)

            # Check file existence
            if not os.path.exists(abs_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "suggestions": [
                        "Check if file path is correct",
                        "Use write_file() to create the file first"
                    ]
                }

            # Safety check: require read-first
            if not self.has_been_read(abs_path):
                return {
                    "success": False,
                    "error": f"File not read first - read the file before editing: {file_path}",
                    "suggestions": [
                        "Use read_file() to examine content first",
                        "This prevents accidental modifications of important files"
                    ]
                }

            # Read current content with UTF-8
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
            except UnicodeDecodeError:
                return {
                    "success": False,
                    "error": f"Unable to decode file as UTF-8: {file_path}",
                    "suggestions": [
                        "File may be binary or use different encoding",
                        "Ensure file contains valid UTF-8 text"
                    ]
                }

            # Check if old_string exists
            if old_string not in original_content:
                # Show first 100 chars for reference
                old_preview = old_string[:100] + ('...' if len(old_string) > 100 else '')
                return {
                    "success": False,
                    "error": f"Text to replace not found: '{old_preview}'",
                    "suggestions": [
                        "Check that text to replace is exactly correct",
                        "Use read_file() to verify current file content",
                        "Ensure whitespace and line endings match exactly"
                    ]
                }

            # Count occurrences
            occurrence_count = original_content.count(old_string)

            # Perform replacement
            if replace_all:
                new_content = original_content.replace(old_string, new_string)
                replacements_made = occurrence_count
            else:
                new_content = original_content.replace(old_string, new_string, 1)
                replacements_made = 1

            # Create backup before editing
            backup_path = self._create_backup(abs_path)

            # Generate diff preview
            diff_lines = list(difflib.unified_diff(
                original_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"{file_path} (original)",
                tofile=f"{file_path} (modified)",
                lineterm=""
            ))

            preview = ''.join(diff_lines) if diff_lines else "No changes detected"

            # Write the modified content
            try:
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                response = {
                    "success": True,
                    "file_path": file_path,
                    "old_string": old_string,
                    "new_string": new_string,
                    "replacements_made": replacements_made,
                    "total_occurrences": occurrence_count,
                    "replace_all": replace_all,
                    "preview": preview,
                    "bytes_changed": len(new_content.encode('utf-8')) - len(original_content.encode('utf-8'))
                }

                if backup_path:
                    response["backup_created"] = backup_path

                response["message"] = f"File edited successfully. Replaced {replacements_made} occurrence(s)."

                return response

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to write modified content: {str(e)}",
                    "suggestions": [
                        "Check file permissions",
                        "Ensure file is not locked by another process"
                    ]
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Edit operation failed: {str(e)}",
                "suggestions": [
                    "Verify file path is correct",
                    "Check file permissions"
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
            # If backup fails, return None but don't prevent the edit operation
            return None