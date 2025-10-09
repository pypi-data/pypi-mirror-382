"""
Read Tool - Simplified smart file reading for AI agents.

Features:
- Single function with LineArgs or RegexArgs
- Tiered token management (4k/10k modes)
- Smart line truncation for very long lines
- Clear feedback when limits are reached
- Always includes line numbers
"""

import os
import re
from typing import Optional, List, Dict, Any

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


class ReadTool:
    """Simplified file reading tool optimized for AI agents."""

    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding_name = encoding_name
        if HAS_TIKTOKEN:
            try:
                self.encoding = tiktoken.get_encoding(encoding_name)
            except Exception:
                self.encoding = None
        else:
            self.encoding = None

    def count_tokens(self, text: str) -> int:
        """Count tokens in text. Falls back to character count / 4 if tiktoken unavailable."""
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Rough approximation: 1 token ≈ 4 characters
            return len(text) // 4

    def read_file(
        self,
        file_path: str,
        lines_start: Optional[int] = None,
        lines_end: Optional[int] = None,
        regex: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Read file with optional line range and/or regex filtering.

        Args:
            file_path: Absolute path to file (e.g., /workspace/main.py)
            lines_start: Start line number (1-based, optional)
            lines_end: End line number (optional, requires lines_start)
            regex: Regex pattern for search (case-insensitive, optional)

        Reading Modes:
            1. Full file: read_file('/workspace/config.json')
            2. Line range: read_file('/workspace/main.py', lines_start=100, lines_end=200)
            3. From line to end: read_file('/workspace/main.py', lines_start=200)
            4. Regex search: read_file('/workspace/main.py', regex=r'def \w+')
            5. Regex in range: read_file('/workspace/main.py', lines_start=100, lines_end=200, regex='import')
               → Searches regex within line range, shows matches with context, reports outside matches

        Common Patterns:
            - Find functions: regex=r'def \w+'
            - Find classes: regex=r'class \w+'
            - Find imports: regex='import|from'
            - Find errors: regex='error|exception|raise'

        Important Notes:
            - Line numbers are 1-based (first line is 1, not 0)
            - Regex shows 2 lines of context before/after each match (marked with >>>)
            - Context lines can extend outside specified line range
            - Feedback always appended to output with >> prefix

        Returns:
            {
                "success": true/false,
                "content": "numbered file content",
                "output": "content + feedback appended",
                "total_lines": 100,
                "lines_shown": 50,
                "token_count": 1234
            }
        """
        try:
            # Basic file validation
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "suggestions": [
                        "Check if the file path is correct",
                        "Ensure the file exists in the working directory"
                    ]
                }

            if not os.path.isfile(file_path):
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}",
                    "suggestions": ["Ensure the path points to a file, not a directory"]
                }

            # Read file with encoding fallback
            lines = self._read_file_lines(file_path)
            if isinstance(lines, dict):  # Error response
                return lines

            # Route to appropriate processing based on parameters
            if lines_start is not None and regex is not None:
                # Combined mode: regex search within line range
                return self._process_regex_in_range(file_path, lines, lines_start, lines_end, regex)
            elif lines_start is not None:
                # Line range mode
                return self._process_line_read(file_path, lines, lines_start, lines_end)
            elif regex is not None:
                # Full file regex search
                return self._process_regex_read(file_path, lines, regex)
            else:
                # Full file read
                return self._process_full_read(file_path, lines)

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}",
                "suggestions": [
                    "Check file permissions",
                    "Ensure the file is not locked by another process"
                ]
            }

    def _read_file_lines(self, file_path: str):
        """Read file lines with encoding fallback."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except UnicodeDecodeError:
            # Try with different encodings
            for encoding in ['latin1', 'cp1252', 'utf-16']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.readlines()
                except UnicodeDecodeError:
                    continue

            return {
                "success": False,
                "error": f"Unable to decode file: {file_path}",
                "suggestions": [
                    "File may be binary or use unsupported encoding",
                    "Try opening with a text editor to verify content"
                ]
            }

    def _truncate_very_long_line(self, line: str) -> str:
        """Truncate lines > 6k tokens to 1k total (500 front + 500 end)."""
        tokens = self.count_tokens(line)
        if tokens <= 6000:
            return line

        # Calculate approximate character positions for 500 tokens each
        chars_per_token = len(line) // tokens
        front_chars = min(500 * chars_per_token, len(line) // 2)
        end_chars = min(500 * chars_per_token, len(line) // 2)

        front_part = line[:front_chars].rstrip()
        end_part = line[-end_chars:].lstrip()

        return f"{front_part}... [large file caution: line truncated] ...{end_part}"

    def _get_token_limits(self, lines: List[str]) -> Dict[str, int]:
        """Determine token limits based on line sizes."""
        # Check for lines > 2k tokens
        has_long_lines = any(self.count_tokens(line) > 2000 for line in lines)

        if has_long_lines:
            return {
                "total_limit": 10000,
                "per_line_limit": 6000,
                "soft_buffer": 0  # No buffer in 10k mode
            }
        else:
            return {
                "total_limit": 4000,
                "per_line_limit": float('inf'),  # No per-line limit in 4k mode
                "soft_buffer": 1000  # 5k soft buffer
            }

    def _process_lines_with_limits(self, lines: List[str], start_line: int, end_line: Optional[int],
                                   limits: Dict[str, int]) -> Dict[str, Any]:
        """Process lines with token limit management."""
        total_lines = len(lines)

        # Apply line range
        start_idx = max(0, start_line - 1)  # Convert to 0-based
        if end_line is not None:
            end_idx = min(total_lines, end_line)
        else:
            end_idx = total_lines

        selected_lines = lines[start_idx:end_idx]

        # Step 1: Truncate very long lines (> 6k tokens)
        processed_lines = []
        truncated_count = 0
        warnings = []

        for line in selected_lines:
            line_tokens = self.count_tokens(line)
            if line_tokens > 6000:
                processed_lines.append(self._truncate_very_long_line(line))
                truncated_count += 1
            else:
                processed_lines.append(line)

        if truncated_count > 0:
            warnings.append(f"Large file caution: {truncated_count} lines truncated (exceeded 6k tokens each)")

        # Step 2: Apply token limits
        result_lines = []
        current_tokens = 0
        stopped_at_line = None

        for i, line in enumerate(processed_lines):
            line_tokens = self.count_tokens(line)

            # Check if adding this line would exceed limits
            if current_tokens + line_tokens > limits["total_limit"]:
                # Check soft buffer for 4k mode
                if limits["soft_buffer"] > 0 and current_tokens + line_tokens <= limits["total_limit"] + limits["soft_buffer"]:
                    # Check if this completes the content
                    if i == len(processed_lines) - 1:  # Last line
                        result_lines.append(line)
                        current_tokens += line_tokens
                        break

                # Can't include this line
                stopped_at_line = start_idx + i + 1
                warnings.append(f"Line end could not be satisfied - too long chunk at line {stopped_at_line}")
                warnings.append(f"Stopped at line {start_idx + i} due to {limits['total_limit']}k token limit")
                warnings.append(f"Try calling with adjusted line numbers (start from line {stopped_at_line})")
                break

            result_lines.append(line)
            current_tokens += line_tokens

        # Step 3: Add line numbers to all content
        numbered_lines = []
        for i, line in enumerate(result_lines):
            line_num = start_idx + i + 1
            # Remove trailing newline for numbering, add it back
            clean_line = line.rstrip('\n')
            numbered_lines.append(f"   {line_num:4d}: {clean_line}")

        content = '\n'.join(numbered_lines)

        # Prepare response
        response = {
            "success": True,
            "content": content,
            "file_path": "",  # Will be set by caller
            "total_lines": total_lines,
            "lines_shown": len(result_lines),
            "start_line": start_line,
            "end_line": start_idx + len(result_lines),
            "token_count": current_tokens,
            "warnings": warnings,
            "stopped_at_line": stopped_at_line
        }

        # Generate summary message
        if stopped_at_line:
            response["message"] = f"Showing lines {start_line}-{start_idx + len(result_lines)} of {total_lines} total (stopped due to token limit)"
        else:
            response["message"] = f"Showing lines {start_line}-{start_idx + len(result_lines)} of {total_lines} total ({current_tokens} tokens)"

        return response

    def _process_full_read(self, file_path: str, lines: List[str]) -> Dict[str, Any]:
        """Process full file read."""
        limits = self._get_token_limits(lines)
        result = self._process_lines_with_limits(lines, 1, None, limits)
        result["file_path"] = file_path

        # Add feedback
        feedback = f">> Full file ({result['lines_shown']} lines, {result['token_count']} tokens)"
        result["output"] = result.get("content", "") + f"\n{feedback}"
        return result

    def _process_line_read(self, file_path: str, lines: List[str], lines_start: int, lines_end: Optional[int]) -> Dict[str, Any]:
        """Process line-based read."""
        total_lines = len(lines)

        # Validate line range
        if lines_start < 1:
            feedback = f">> Invalid: lines_start={lines_start} must be >= 1. Showing from line 1"
            lines_start = 1
        elif lines_start > total_lines:
            feedback = f">> Invalid: lines_start={lines_start} exceeds file length ({total_lines} lines). Showing full file"
            lines_start = 1
            lines_end = None
        else:
            feedback = None

        if lines_end is not None and lines_end < lines_start:
            feedback = f">> Invalid: lines_end={lines_end} < lines_start={lines_start}. Showing from line {lines_start} to end"
            lines_end = None

        limits = self._get_token_limits(lines)
        result = self._process_lines_with_limits(lines, lines_start, lines_end, limits)
        result["file_path"] = file_path

        # Append feedback to output
        if feedback:
            result["output"] = result.get("content", "") + f"\n{feedback}"
        else:
            actual_end = lines_end if lines_end else total_lines
            feedback = f">> Lines {lines_start}-{min(actual_end, result['end_line'])} ({result['lines_shown']} lines, {result['token_count']} tokens)"
            result["output"] = result.get("content", "") + f"\n{feedback}"

        return result

    def _process_regex_read(self, file_path: str, lines: List[str], regex_pattern: str) -> Dict[str, Any]:
        """Process regex-based read on full file."""
        try:
            # Compile regex pattern
            try:
                regex = re.compile(regex_pattern, re.IGNORECASE | re.MULTILINE)
            except re.error as e:
                return {
                    "success": False,
                    "error": f"Invalid regex pattern: {str(e)}"
                }

            # Find all unique matching lines
            matching_lines = set()
            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    matching_lines.add(line_num)

            matching_lines = sorted(matching_lines)  # Sort by line number

            if not matching_lines:
                feedback = f">> Regex '{regex_pattern}': no matches found in file ({len(lines)} lines)"
                return {
                    "success": True,
                    "content": "",
                    "output": feedback,
                    "file_path": file_path,
                    "pattern": regex_pattern,
                    "total_matches": 0,
                    "matches_shown": 0
                }

            # Determine if we need two-phase approach
            limits = self._get_token_limits(lines)

            # Try to fit all matches with context first
            all_matches_content = self._build_regex_matches(lines, matching_lines, context_lines=2)
            all_tokens = self.count_tokens(all_matches_content)

            # Check if all fits in limit (with soft buffer if applicable)
            max_allowed = limits["total_limit"] + limits["soft_buffer"]

            if all_tokens <= max_allowed:
                # Phase 1 only - all matches fit
                feedback = f">> Regex '{regex_pattern}': {len(matching_lines)} matches found, all shown with context"
                return {
                    "success": True,
                    "content": all_matches_content,
                    "output": all_matches_content + f"\n{feedback}",
                    "file_path": file_path,
                    "pattern": regex_pattern,
                    "total_matches": len(matching_lines),
                    "matches_shown": len(matching_lines),
                    "token_count": all_tokens
                }
            else:
                # Two-phase approach
                return self._two_phase_regex_read(file_path, lines, matching_lines, regex_pattern, limits)

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process regex search: {str(e)}"
            }

    def _build_regex_matches(self, lines: List[str], matching_lines: List[int], context_lines: int = 2) -> str:
        """Build formatted output for regex matches with context."""
        content_parts = []

        for line_num in matching_lines:
            # Calculate context window
            start_ctx = max(1, line_num - context_lines)
            end_ctx = min(len(lines), line_num + context_lines)

            # Add context
            for i in range(start_ctx, end_ctx + 1):
                if i <= len(lines):
                    line_content = lines[i - 1].rstrip('\n')
                    if i == line_num:
                        content_parts.append(f">>> {i:4d}: {line_content}")
                    else:
                        content_parts.append(f"   {i:4d}: {line_content}")

            # Add spacing between match groups
            if line_num != matching_lines[-1]:
                content_parts.append("")

        return '\n'.join(content_parts)

    def _two_phase_regex_read(self, file_path: str, lines: List[str], matching_lines: List[int],
                             pattern: str, limits: Dict[str, int]) -> Dict[str, Any]:
        """Handle regex read with two-phase approach."""
        # Phase 1: Full matches with context (up to 2k tokens)
        phase1_matches = []
        phase1_tokens = 0
        phase1_target = 2000

        for line_num in matching_lines:
            # Try with context=2, fallback to context=1, then just match line
            for context in [2, 1, 0]:
                match_content = self._build_single_match(lines, line_num, context)
                match_tokens = self.count_tokens(match_content)

                if phase1_tokens + match_tokens <= phase1_target:
                    phase1_matches.append(match_content)
                    phase1_tokens += match_tokens
                    break
            else:
                # Can't fit this match in phase 1
                break

        # Phase 2: Line numbers only for remaining matches (up to 2k more tokens)
        phase2_content = []
        phase2_tokens = 0
        phase2_target = 2000
        remaining_matches = matching_lines[len(phase1_matches):]

        for line_num in remaining_matches:
            line_ref = f"   {line_num:4d}: [match]"
            line_tokens = self.count_tokens(line_ref)

            if phase2_tokens + line_tokens <= phase2_target:
                phase2_content.append(line_ref)
                phase2_tokens += line_tokens
            else:
                break

        # Combine phases
        all_content = []
        if phase1_matches:
            all_content.extend(phase1_matches)
        if phase2_content:
            if phase1_matches:
                all_content.append("")  # Separator
            all_content.extend(phase2_content)

        # Calculate remaining matches
        total_shown = len(phase1_matches) + len(phase2_content)
        remaining = len(matching_lines) - total_shown

        if remaining > 0:
            all_content.append("")
            all_content.append(f"+[{remaining}] more lines matched")

        content = '\n'.join(all_content)
        total_tokens = phase1_tokens + phase2_tokens

        feedback = f">> Regex '{pattern}': {len(matching_lines)} matches, showing {len(phase1_matches)} with context + {len(phase2_content)} line references"
        return {
            "success": True,
            "content": content,
            "output": content + f"\n{feedback}",
            "file_path": file_path,
            "pattern": pattern,
            "total_matches": len(matching_lines),
            "matches_shown": total_shown,
            "phase1_matches": len(phase1_matches),
            "phase2_matches": len(phase2_content),
            "remaining_matches": remaining,
            "token_count": total_tokens
        }

    def _process_regex_in_range(self, file_path: str, lines: List[str], lines_start: int,
                                lines_end: Optional[int], regex_pattern: str) -> Dict[str, Any]:
        """Process regex search within a specific line range."""
        try:
            # Compile regex pattern
            try:
                regex = re.compile(regex_pattern, re.IGNORECASE | re.MULTILINE)
            except re.error as e:
                return {
                    "success": False,
                    "error": f"Invalid regex pattern: {str(e)}"
                }

            total_lines = len(lines)
            actual_end = lines_end if lines_end else total_lines

            # Find matches in entire file
            all_matches = set()
            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    all_matches.add(line_num)

            # Separate matches inside and outside range
            matches_in_range = sorted([ln for ln in all_matches if lines_start <= ln <= actual_end])
            matches_outside_range = sorted([ln for ln in all_matches if ln < lines_start or ln > actual_end])

            # Build content with context for matches in range
            if matches_in_range:
                content = self._build_regex_matches(lines, matches_in_range, context_lines=2)
                tokens = self.count_tokens(content)

                # Build feedback
                if matches_outside_range:
                    outside_sample = matches_outside_range[:7]  # Show up to 7 line numbers
                    sample_str = ", ".join(str(ln) for ln in outside_sample)
                    if len(matches_outside_range) > 7:
                        sample_str += f", ... ({len(matches_outside_range) - 7} more)"
                    feedback = f">> Regex '{regex_pattern}' in lines {lines_start}-{actual_end}: {len(matches_in_range)} matches found. {len(matches_outside_range)} additional matches outside range at lines: {sample_str}"
                else:
                    feedback = f">> Regex '{regex_pattern}' in lines {lines_start}-{actual_end}: {len(matches_in_range)} matches found"

                return {
                    "success": True,
                    "content": content,
                    "output": content + f"\n{feedback}",
                    "file_path": file_path,
                    "pattern": regex_pattern,
                    "total_matches": len(all_matches),
                    "matches_shown": len(matches_in_range),
                    "matches_in_range": len(matches_in_range),
                    "matches_outside_range": len(matches_outside_range),
                    "token_count": tokens
                }
            else:
                # No matches in range
                if matches_outside_range:
                    outside_sample = matches_outside_range[:10]  # Show up to 10 line numbers
                    sample_str = ", ".join(str(ln) for ln in outside_sample)
                    if len(matches_outside_range) > 10:
                        sample_str += f", ..."
                    feedback = f">> Regex '{regex_pattern}' in lines {lines_start}-{actual_end}: no matches found. However, found {len(matches_outside_range)} matches outside this range at lines: {sample_str}"
                else:
                    feedback = f">> Regex '{regex_pattern}' in lines {lines_start}-{actual_end}: no matches found in entire file"

                return {
                    "success": True,
                    "content": "",
                    "output": feedback,
                    "file_path": file_path,
                    "pattern": regex_pattern,
                    "total_matches": len(all_matches),
                    "matches_shown": 0,
                    "matches_in_range": 0,
                    "matches_outside_range": len(matches_outside_range)
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process regex in range: {str(e)}"
            }

    def _build_single_match(self, lines: List[str], line_num: int, context_lines: int) -> str:
        """Build formatted output for a single regex match with context."""
        start_ctx = max(1, line_num - context_lines)
        end_ctx = min(len(lines), line_num + context_lines)

        content_parts = []
        for i in range(start_ctx, end_ctx + 1):
            if i <= len(lines):
                line_content = lines[i - 1].rstrip('\n')
                if i == line_num:
                    content_parts.append(f">>> {i:4d}: {line_content}")
                else:
                    content_parts.append(f"   {i:4d}: {line_content}")

        return '\n'.join(content_parts)